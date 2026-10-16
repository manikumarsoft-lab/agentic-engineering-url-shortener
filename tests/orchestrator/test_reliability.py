"""Retry, timeout, fallback, rollback, compensation, safe-stop and resume.

Verifies: FR-ORC-014..019, PVT-004 (at most 3 attempts with backoff).
"""
import time

import pytest

from orchestrator import audit
from orchestrator.engine import AuthError


def _single(node: str) -> str:
    return f"name: rel\nversion: 1.0.0\ndefaults: {{backoff_s: 0.5}}\nnodes:\n  - {node}\n"


def test_transient_failure_is_retried_with_backoff(env):
    eng = env.engine(_single("{id: a, agent: flaky, params: {fail_times: 2}}"))
    run_id = eng.submit()
    assert eng.run(run_id) == "COMPLETED"
    row = env.store.nodes(run_id)["a"]
    assert row["attempts"] == 3
    delays = [e["data"]["delay_s"] for e in audit.events(env.store.conn, run_id)
              if e["action"] == "RETRY_SCHEDULED"]
    assert delays == [0.5, 1.0]


def test_retry_budget_is_bounded_then_safe_stop(env):
    eng = env.engine(_single("{id: a, agent: flaky, params: {fail_times: 5}}"))
    run_id = eng.submit()
    assert eng.run(run_id) == "SAFE_STOPPED"
    assert env.store.nodes(run_id)["a"]["attempts"] == 3
    assert env.store.run(run_id)["reason"] == "retry_exhausted"


def test_permanent_failure_is_never_retried(env):
    eng = env.engine(_single("{id: a, agent: fail, params: {code: invalid_input}, on_failure: fail_run}"))
    run_id = eng.submit()
    assert eng.run(run_id) == "FAILED"
    assert env.store.nodes(run_id)["a"]["attempts"] == 1
    assert "RETRY_SCHEDULED" not in env.actions(run_id)


def test_unclassified_failure_safe_stops(env):
    eng = env.engine(_single("{id: a, agent: crash}"))
    run_id = eng.submit()
    assert eng.run(run_id) == "SAFE_STOPPED"
    assert env.store.run(run_id)["reason"] == "unclassified_failure"
    assert env.store.nodes(run_id)["a"]["attempts"] == 1


def test_timeout_kills_the_agent_process(env):
    marker = env.tmp / "finished.txt"
    eng = env.engine(_single(
        f"{{id: a, agent: sleep, params: {{seconds: 4, marker: '{marker.as_posix()}'}}, timeout_s: 1.5,"
        " retry: {max_attempts: 1}}"))
    run_id = eng.submit()
    assert eng.run(run_id) == "SAFE_STOPPED"
    assert "TIMEOUT" in env.actions(run_id)
    assert env.store.run(run_id)["reason"] == "retry_exhausted"  # timeout is transient
    time.sleep(3.5)
    assert not marker.exists(), "timed-out agent kept running"


def test_fallback_marks_node_degraded(env):
    eng = env.engine(_single("{id: a, agent: fail, fallback: {agent: emit, params: {facts: {docs: template}}}}"))
    run_id = eng.submit()
    assert eng.run(run_id) == "COMPLETED"
    assert env.store.nodes(run_id)["a"]["degraded"] == 1
    assert "FALLBACK_USED" in env.actions(run_id)
    assert env.store.run(run_id)["facts"]["docs"] == "template"


ROLLBACK = """
name: rollback
version: 1.0.0
nodes:
  - {id: apply, agent: write_file, params: {path: app.py, content: "conflict = 'defective'"}}
  - {id: test, agent: check_file, params: {path: app.py, forbidden: defective}, depends_on: [apply], on_failure: rollback}
"""


def test_rollback_discards_the_isolated_workspace(env):
    source = env.tmp / "baseline"
    source.mkdir()
    (source / "app.py").write_text("conflict = 'reject'", encoding="utf-8")
    eng = env.engine(ROLLBACK, source_dir=source)
    run_id = eng.submit()
    assert eng.workspace_path(run_id).exists()
    assert eng.run(run_id) == "FAILED"
    assert env.store.run(run_id)["reason"] == "rolled_back:tests_failed"
    assert not eng.workspace_path(run_id).exists()
    assert (source / "app.py").read_text(encoding="utf-8") == "conflict = 'reject'"
    assert {"ROLLBACK_STARTED", "ROLLBACK_COMPLETED"} <= set(env.actions(run_id))


def _compensation_flow(ledger, smoke_agent, undo_agent):
    return f"""
name: compensation
version: 1.0.0
nodes:
  - id: promote
    agent: record
    params: {{file: '{ledger}', line: promoted R2}}
    compensate: {{agent: {undo_agent}, params: {{file: '{ledger}', line: re-promoted R1}}}}
  - {{id: smoke, agent: {smoke_agent}, params: {{code: tests_failed}}, depends_on: [promote], on_failure: compensate}}
"""


def test_compensation_hook_undoes_committed_effect(env):
    ledger = (env.tmp / "staging.log").as_posix()
    eng = env.engine(_compensation_flow(ledger, "fail", "record"))
    run_id = eng.submit()
    assert eng.run(run_id) == "FAILED"
    assert env.store.run(run_id)["reason"] == "compensated:tests_failed"
    assert (env.tmp / "staging.log").read_text().splitlines() == ["promoted R2", "re-promoted R1"]
    assert "COMPENSATION_COMPLETED" in env.actions(run_id)


def test_failed_compensation_safe_stops(env):
    ledger = (env.tmp / "staging.log").as_posix()
    eng = env.engine(_compensation_flow(ledger, "fail", "fail"))
    run_id = eng.submit()
    assert eng.run(run_id) == "SAFE_STOPPED"
    assert env.store.run(run_id)["reason"] == "compensation_failed"


def test_safe_stop_resume_needs_a_human_approver(env):
    eng = env.engine(_single("{id: a, agent: flaky, params: {fail_times: 3}}"))
    run_id = eng.submit()
    assert eng.run(run_id) == "SAFE_STOPPED"
    for role in ("agent", "engineer"):
        with pytest.raises(AuthError):
            eng.resume(run_id, env.keys[role])
    eng.resume(run_id, env.keys["approver"], "transient cause cleared")
    assert eng.run(run_id) == "COMPLETED"  # 4th attempt overall succeeds after the budget reset
    assert "RETRY_BUDGET_RESET" in env.actions(run_id)


def test_restart_marks_interrupted_run_safe_stopped_and_resume_completes(env):
    flow = _single("{id: a, agent: noop}") + "  - {id: b, agent: noop, depends_on: [a]}\n"
    eng = env.engine(flow)
    run_id = eng.submit()
    eng.step(run_id)  # a -> READY
    eng.step(run_id)  # a runs
    with env.store.tx() as c:  # simulate a crash while b was running
        env.store.set_node(c, run_id, "b", state="RUNNING", attempts=1)
    restarted = env.engine(flow)
    assert restarted.recover() == [run_id]
    run = env.store.run(run_id)
    assert (run["state"], run["reason"]) == ("SAFE_STOPPED", "interrupted")
    restarted.resume(run_id, env.keys["approver"])
    assert restarted.run(run_id) == "COMPLETED"
    assert env.store.nodes(run_id)["a"]["runs_total"] == 1  # completed node not re-executed
