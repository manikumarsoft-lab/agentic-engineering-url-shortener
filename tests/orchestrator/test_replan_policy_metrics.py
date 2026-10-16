"""Replanning, policy blocking with exceptions, and metrics.

Verifies: FR-ORC-020, FR-ORC-021, SC-006 (only stale nodes re-run), FR-GOV-005..008, FR-OBS-006, FR-OBS-007.
"""
import pytest

from orchestrator import audit
from orchestrator.engine import AuthError, EngineError
from orchestrator.metrics import LABEL, compute_mttr, run_metrics
from orchestrator.policy import load_policy_text

REPLAN = """
name: replan
version: 1.0.0
nodes:
  - {id: intake, agent: emit, params: {artifacts: {requirement: {text: v1}}}, produces: [requirement]}
  - {id: docs, agent: noop, depends_on: [intake]}
  - {id: design, agent: transform, params: {from: requirement, to: design}, consumes: [requirement], produces: [design], depends_on: [intake]}
  - {id: approve, gate: {roles: [approver], binds: [design]}, depends_on: [design]}
  - {id: build, agent: noop, depends_on: [approve, docs]}
"""


def test_new_artifact_version_reruns_only_stale_nodes_and_revokes_approval(env):
    eng = env.engine(REPLAN)
    run_id = eng.submit()
    eng.run(run_id)
    eng.decide(run_id, "approve", env.keys["approver"], "approve")
    eng.run(run_id)
    assert env.store.run(run_id)["state"] == "COMPLETED"
    with pytest.raises(EngineError):  # finished runs are not replanned
        eng.new_artifact_version(run_id, "requirement", {"text": "v2"}, env.keys["engineer"], "late")

    run_id = eng.submit()
    eng.run(run_id)
    eng.decide(run_id, "approve", env.keys["approver"], "approve")
    with pytest.raises(AuthError):
        eng.new_artifact_version(run_id, "requirement", {"text": "v2"}, env.keys["agent"], "x")
    eng.new_artifact_version(run_id, "requirement", {"text": "v2"}, env.keys["engineer"], "clarified")
    assert env.states(run_id)["design"] == "STALE"
    assert "GATE_REVOKED" in env.actions(run_id)
    assert eng.run(run_id) == "AWAITING_APPROVAL"  # approval must be re-requested
    eng.decide(run_id, "approve", env.keys["approver"], "approve")
    assert eng.run(run_id) == "COMPLETED"
    rows = env.store.nodes(run_id)
    assert rows["intake"]["runs_total"] == 1 and rows["docs"]["runs_total"] == 1
    assert rows["design"]["runs_total"] == 2 and rows["build"]["runs_total"] == 1
    assert env.store.artifact(run_id, "design") == (2, {"derived_from": {"text": "v2"}})


POLICY = """
version: 1.0.0
checks:
  - {id: PRIV-001, fact: captures_personal_data, expect: false, mandatory: true}
"""

RELEASE = """
name: release
version: 1.0.0
nodes:
  - {id: validate, agent: emit, params: {facts: {captures_personal_data: true}}, policy_checks: [PRIV-001]}
  - {id: release, agent: noop, depends_on: [validate]}
"""


def test_policy_fail_blocks_release_until_exception_is_approved(env):
    eng = env.engine(RELEASE, policy=load_policy_text(POLICY))
    run_id = eng.submit()
    assert eng.run(run_id) == "SAFE_STOPPED"
    assert env.store.run(run_id)["reason"] == "policy_fail:PRIV-001"
    assert env.store.run(run_id)["policy_version"] == "1.0.0"
    assert env.states(run_id)["release"] == "PENDING"
    with pytest.raises(EngineError, match="no approved exception"):
        eng.resume(run_id, env.keys["approver"])

    exc = eng.request_exception(run_id, "PRIV-001", env.keys["engineer"], "pilot only", "7-day purge")
    with pytest.raises(AuthError):
        eng.approve_exception(run_id, exc, env.keys["agent"], "agent tries")
    eng.approve_exception(run_id, exc, env.keys["approver"], "accepted for pilot")
    eng.resume(run_id, env.keys["approver"], "exception approved")
    assert eng.run(run_id) == "COMPLETED"
    outcomes = [r[0] for r in env.store.conn.execute(
        "SELECT outcome FROM policy_evaluations WHERE run_id = ? ORDER BY rowid", (run_id,))]
    assert outcomes == ["FAIL", "EXCEPTION-REQUESTED", "EXCEPTION-REQUESTED"]


def test_requesting_key_cannot_approve_its_own_exception(env):
    """Verifies: FR-GOV-017 (separation of duties between key identities)."""
    eng = env.engine(RELEASE, policy=load_policy_text(POLICY))
    run_id = eng.submit()
    assert eng.run(run_id) == "SAFE_STOPPED"
    exc = eng.request_exception(run_id, "PRIV-001", env.keys["approver"], "pilot only", "7-day purge")
    with pytest.raises(AuthError, match="separation of duties"):
        eng.approve_exception(run_id, exc, env.keys["approver"], "approving my own request")
    status = env.store.conn.execute("SELECT status FROM exceptions WHERE exception_id = ?", (exc,)).fetchone()
    assert status[0] == "REQUESTED"
    refusals = [e for e in audit.events(env.store.conn, run_id) if e["action"] == "AUTH_REFUSED"]
    assert refusals and refusals[-1]["data"]["action"] == "exception.approve"
    assert refusals[-1]["data"]["violation"] == "separation_of_duties_violation"
    assert "separation of duties" in refusals[-1]["reason"]
    assert audit.verify_chain(env.store.conn, run_id) == (True, None)


def test_mttr_counts_recovered_episodes_only():
    ev = lambda action, ts, ep: {"action": action, "ts": ts, "data": {"episode": ep}}  # noqa: E731
    events = [ev("FAILURE_DETECTED", 10, "e1"), ev("RECOVERY_COMPLETED", 14, "e1"),
              ev("FAILURE_DETECTED", 20, "e2"), ev("RECOVERY_COMPLETED", 30, "e2"),
              ev("FAILURE_DETECTED", 40, "e3")]
    assert compute_mttr(events) == {"mttr_s": 7.0, "recovered": 2, "unrecovered": 1}
    assert compute_mttr([]) == {"mttr_s": None, "recovered": 0, "unrecovered": 0}


def test_run_metrics_are_labelled_and_complete(env):
    eng = env.engine("name: m\nversion: 1\ndefaults: {backoff_s: 2}\nnodes:\n"
                     "  - {id: a, agent: flaky, params: {fail_times: 1}}\n")
    run_id = eng.submit()
    eng.run(run_id)
    m = run_metrics(env.store, run_id)
    assert m["label"] == LABEL == "demonstration data"
    assert m["success"] and m["retries"] == 1 and m["rollbacks"] == 0
    assert m["recovered"] == 1 and m["mttr_s"] >= 2.0  # includes the 2 s backoff
    assert m["end_to_end_s"] > 0 and m["node_latency_s"]["a"] > 0
    assert audit.verify_chain(env.store.conn, run_id) == (True, None)
