"""Fork/join and human gates.

Verifies: FR-ORC-006, FR-ORC-037..039 (parallel fork, join waits), FR-GOV-001..003, FR-GOV-014..016,
NFR-AUT-001 and SC-011 (agent keys refused and audited).
"""
import pytest

from orchestrator import audit
from orchestrator.engine import AuthError, EngineError

FORK = """
name: fork
version: 1.0.0
defaults: {timeout_s: 30}
nodes:
  - {id: start, agent: noop}
  - {id: left, agent: sleep, params: {seconds: 1.0}, depends_on: [start]}
  - {id: right, agent: sleep, params: {seconds: 1.0}, depends_on: [start]}
  - {id: join, agent: noop, depends_on: [left, right]}
  - {id: optional, agent: noop, depends_on: [join], conditional: {fact: brownfield, equals: true}}
"""

GATED = """
name: gated
version: 1.0.0
nodes:
  - {id: design, agent: emit, params: {artifacts: {design: {v: 1}}}, produces: [design]}
  - {id: approve, gate: {roles: [approver], timeout_s: 3600, binds: [design], rework_target: design}, depends_on: [design]}
  - {id: build, agent: noop, depends_on: [approve]}
"""


def test_fork_runs_branches_together_and_join_waits(env):
    eng = env.engine(FORK)
    run_id = eng.submit({"brownfield": False})
    assert eng.run(run_id) == "COMPLETED"
    rows = env.store.nodes(run_id)
    left, right, join = rows["left"], rows["right"], rows["join"]
    assert left["started_at"] < right["ended_at"] and right["started_at"] < left["ended_at"]
    assert join["started_at"] >= max(left["ended_at"], right["ended_at"])
    steps = [e["data"]["nodes"] for e in audit.events(env.store.conn, run_id)
             if e["action"] == "STEP_STARTED"]
    assert ["left", "right"] in steps
    assert rows["optional"]["state"] == "SKIPPED"


def test_gate_blocks_downstream_until_approved(env):
    eng = env.engine(GATED)
    run_id = eng.submit()
    assert eng.run(run_id) == "AWAITING_APPROVAL"
    assert env.states(run_id) == {"design": "SUCCEEDED", "approve": "AWAITING_APPROVAL", "build": "PENDING"}
    eng.decide(run_id, "approve", env.keys["approver"], "approve", "looks right")
    assert eng.run(run_id) == "COMPLETED"
    decision = env.store.conn.execute("SELECT key_id, role, bound FROM decisions").fetchone()
    assert decision["role"] == "approver" and '"design": 1' in decision["bound"]


@pytest.mark.parametrize("key", ["agent", "engineer", None])
def test_non_approver_decisions_are_refused_and_audited(env, key):
    eng = env.engine(GATED)
    run_id = eng.submit()
    eng.run(run_id)
    with pytest.raises(AuthError):
        eng.decide(run_id, "approve", env.keys.get(key), "approve")
    refused = [e for e in audit.events(env.store.conn, run_id) if e["action"] == "AUTH_REFUSED"]
    assert refused and refused[-1]["result"] == "refused"
    if key == "agent":
        assert refused[-1]["actor_type"] == "agent"
    assert env.states(run_id)["approve"] == "AWAITING_APPROVAL"


def test_escalate_keeps_gate_blocking_and_requires_release_owner(env):
    eng = env.engine(GATED)
    run_id = eng.submit()
    eng.run(run_id)
    with pytest.raises(EngineError, match="reason"):
        eng.decide(run_id, "approve", env.keys["approver"], "escalate")
    eng.decide(run_id, "approve", env.keys["approver"], "escalate", "needs release-owner judgement")
    assert env.store.run(run_id)["state"] == "AWAITING_APPROVAL"
    assert env.states(run_id)["approve"] == "AWAITING_APPROVAL"
    escalated = [e for e in audit.events(env.store.conn, run_id) if e["action"] == "GATE_ESCALATED"]
    assert escalated[0]["data"]["next_roles"] == ["release-owner"]
    assert eng.run(run_id) == "AWAITING_APPROVAL"  # still blocked
    with pytest.raises(AuthError):  # the escalating role can no longer decide
        eng.decide(run_id, "approve", env.keys["approver"], "approve")
    with pytest.raises(EngineError, match="already escalated"):
        eng.decide(run_id, "approve", env.keys["release-owner"], "escalate", "again")
    eng.decide(run_id, "approve", env.keys["release-owner"], "approve", "accepted")
    assert eng.run(run_id) == "COMPLETED"
    choices = [r[0] for r in env.store.conn.execute("SELECT choice FROM decisions ORDER BY created_at")]
    assert choices == ["escalate", "approve"]


def test_reject_terminate_aborts(env):
    eng = env.engine(GATED)
    run_id = eng.submit()
    eng.run(run_id)
    with pytest.raises(EngineError, match="reason"):
        eng.decide(run_id, "approve", env.keys["approver"], "reject_terminate")
    eng.decide(run_id, "approve", env.keys["approver"], "reject_terminate", "wrong direction")
    assert env.store.run(run_id)["state"] == "ABORTED"
    assert env.states(run_id)["build"] == "PENDING"


def test_reject_rework_reruns_producer_and_is_bounded(env):
    eng = env.engine(GATED)
    run_id = eng.submit()
    eng.run(run_id)
    for cycle in (1, 2):
        eng.decide(run_id, "approve", env.keys["approver"], "reject_rework", f"redo {cycle}")
        assert eng.run(run_id) == "AWAITING_APPROVAL"
        assert env.store.nodes(run_id)["design"]["runs_total"] == 1 + cycle
    eng.decide(run_id, "approve", env.keys["approver"], "reject_rework", "third time")
    run = env.store.run(run_id)
    assert (run["state"], run["reason"]) == ("SAFE_STOPPED", "rework_limit_exceeded")


def test_gate_timeout_safe_stops_and_resume_reopens_same_version(env):
    eng = env.engine(GATED)
    run_id = eng.submit()
    eng.run(run_id)
    env.clock.advance(3601)
    assert eng.run(run_id) == "SAFE_STOPPED"
    assert env.store.run(run_id)["reason"] == "gate_timeout"
    timed_out = [e for e in audit.events(env.store.conn, run_id) if e["action"] == "GATE_TIMED_OUT"]
    assert timed_out[0]["result"] == "no decision"
    assert "GATE_APPROVED" not in env.actions(run_id)
    with pytest.raises(EngineError):
        eng.decide(run_id, "approve", env.keys["approver"], "approve")
    eng.resume(run_id, env.keys["approver"], "approver available again")
    reopened = [e for e in audit.events(env.store.conn, run_id) if e["action"] == "GATE_REOPENED"]
    assert reopened[0]["data"]["bound"] == {"design": 1}
    eng.decide(run_id, "approve", env.keys["approver"], "approve")
    assert eng.run(run_id) == "COMPLETED"
