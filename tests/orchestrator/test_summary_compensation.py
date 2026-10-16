"""Engineering summary for every outcome (FR-ORC-026) and compensation along a failure edge
(FR-ORC-017, FR-ORC-042)."""
from orchestrator.policy import load_policy_text

GATED = """
name: gated
version: 1.0.0
nodes:
  - {id: design, agent: emit, params: {artifacts: {design: {v: 1}}}, produces: [design]}
  - {id: approve, gate: {roles: [approver], binds: [design]}, depends_on: [design]}
"""


def _summary(env, run_id):
    return env.store.artifact(run_id, "engineering-summary")[1]


def test_completed_and_aborted_summaries_say_why(env):
    eng = env.engine(GATED)
    done = eng.submit()
    eng.run(done)
    eng.decide(done, "approve", env.keys["approver"], "approve", "ok")
    eng.run(done)
    s = _summary(env, done)
    assert s["outcome"] == "COMPLETED" and "approve by approver" in s["why"]
    assert {"plan_and_rationale", "artifacts", "risks", "trade_offs", "validation_results",
            "assumptions", "limitations"} <= set(s)
    aborted = eng.submit()
    eng.run(aborted)
    eng.decide(aborted, "approve", env.keys["approver"], "reject_terminate", "wrong direction")
    s = _summary(env, aborted)
    assert s["outcome"] == "ABORTED" and "terminated by a human" in s["why"] and "wrong direction" in s["why"]


def test_safe_stopped_and_failed_summaries_say_why(env):
    policy = load_policy_text("version: 1\nchecks:\n  - {id: PRIV-001, fact: pii, expect: false}\n")
    eng = env.engine("name: p\nversion: 1\nnodes:\n  - {id: v, agent: emit, params: {facts: {pii: true}},"
                     " policy_checks: [PRIV-001]}\n", policy=policy)
    stopped = eng.submit()
    eng.run(stopped)
    s = _summary(env, stopped)
    assert s["outcome"] == "SAFE_STOPPED" and "PRIV-001" in s["why"] and "exception" in s["why"]
    assert s["validation_results"]["policy"] == {"PRIV-001": "FAIL"}
    eng = env.engine("name: f\nversion: 1\nnodes:\n  - {id: a, agent: fail, on_failure: fail_run}\n")
    failed = eng.submit()
    eng.run(failed)
    s = _summary(env, failed)
    assert s["outcome"] == "FAILED" and "a failed (invalid_input" in s["why"]


def _compensation_flow(ledger: str, smoke: str = "fail") -> str:
    return f"""
name: comp
version: 1.0.0
nodes:
  - id: promote
    agent: record
    params: {{file: '{ledger}', line: promoted R2}}
    produces: [compensation-record]
    compensate: {{agent: emit, params: {{artifacts: {{compensation-record: {{effects: [x1]}}}}}}}}
  - {{id: smoke, agent: {smoke}, params: {{code: smoke_failed}}, depends_on: [promote], on_failure: compensate, failure_edge: approve-corrective}}
  - {{id: announce, agent: noop, depends_on: [smoke]}}
  - id: approve-corrective
    gate: {{roles: [approver], binds: [compensation-record]}}
    depends_on: [smoke]
  - {{id: corrective, agent: noop, depends_on: [approve-corrective]}}
"""


def test_compensation_continues_only_along_the_failure_edge(env):
    ledger = (env.tmp / "staging.log").as_posix()
    eng = env.engine(_compensation_flow(ledger))
    run_id = eng.submit()
    assert eng.run(run_id) == "AWAITING_APPROVAL"
    states = env.states(run_id)
    assert states["smoke"] == "COMPENSATED" and states["announce"] == "SKIPPED"
    assert states["approve-corrective"] == "AWAITING_APPROVAL"
    assert env.store.artifact(run_id, "compensation-record") == (1, {"effects": ["x1"]})
    assert "COMPENSATION_COMPLETED" in env.actions(run_id) and "ROLLBACK_STARTED" not in env.actions(run_id)
    eng.decide(run_id, "approve-corrective", env.keys["approver"], "approve", "disable listed links")
    assert eng.run(run_id) == "FAILED"
    assert env.store.run(run_id)["reason"] == "compensated:smoke_failed"
    s = _summary(env, run_id)
    assert "COMPENSATION after promotion" in s["why"] and "corrective action approved" in s["why"]
    assert s["recovery"]["compensations"] == 1 and s["recovery"]["rollbacks"] == 0


def test_successful_smoke_takes_the_normal_path(env):
    eng = env.engine(_compensation_flow((env.tmp / "s.log").as_posix(), smoke="noop"))
    run_id = eng.submit()
    assert eng.run(run_id) == "COMPLETED"
    states = env.states(run_id)
    assert states["announce"] == "SUCCEEDED"
    assert states["approve-corrective"] == "SKIPPED" and states["corrective"] == "SKIPPED"
    assert "COMPENSATION_STARTED" not in env.actions(run_id)
