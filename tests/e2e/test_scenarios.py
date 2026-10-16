"""Scripted end-to-end scenario tests (TEST-ONLY, labelled `test`; never scenario evidence).

Verifies: FR-ORC-031 (each scenario runs through the engine), FR-ORC-026, FR-ORC-040..042.
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from orchestrator import audit
from orchestrator.engine import AuthError, EngineError
from orchestrator.evidence import EvidenceError, export

LABELS = ("test", "scripted")


def _assert_chain(repo, run_id):
    assert audit.verify_chain(repo.store.conn, run_id) == (True, None)


def _to_release(repo, eng, run_id):
    """Approve the design gate and run to the release gate."""
    assert eng.run(run_id) == "AWAITING_APPROVAL"
    eng.decide(run_id, "approve-design", repo.keys["approver"], "approve", "design reviewed (scripted)")
    return eng.run(run_id)


def test_scn_a_greenfield_runs_test_first_to_completed(repo):
    repo.lock_all()
    eng = repo.engine("scn-a")
    run_id = eng.submit(labels=LABELS)
    assert _to_release(repo, eng, run_id) == "AWAITING_APPROVAL"
    skipped = repo.events(run_id, "NODE_SKIPPED")
    assert skipped[0]["target"] == "clarify" and "all five" in skipped[0]["reason"]
    assert all(c["result"] == "PASS" for c in repo.artifact(run_id, "quality-report")["checks"])
    red, green = repo.artifact(run_id, "test-red"), repo.artifact(run_id, "test-results")
    assert red["failures"] + red["errors"] > 0 and red["phase"] == "red"
    assert green["failures"] == 0 and green["errors"] == 0 and green["tests"] > red["tests"]
    threats = repo.artifact(run_id, "threat-review")
    assert [t["status"] for t in threats["threats"] if t["id"] == "TH-1"] == ["mitigated"]
    sec3 = repo.store.conn.execute("SELECT outcome, reason FROM policy_evaluations WHERE run_id = ? "
                                   "AND check_id = 'SEC-003'", (run_id,)).fetchone()
    assert sec3[0] == "PASS" and "pip-audit" in sec3[1] and "0 known vulnerabilities" in sec3[1]
    with pytest.raises(AuthError):
        eng.decide(run_id, "approve-release", repo.keys["approver"], "approve")  # release-owner only
    eng.decide(run_id, "approve-release", repo.keys["release-owner"], "approve", "ready (scripted)")
    assert eng.run(run_id) == "COMPLETED"
    steps = [e["data"]["nodes"] for e in repo.events(run_id, "STEP_STARTED")]
    assert ["docs", "threat-review"] in steps  # parallel fork after tests, joined by validate
    summary = repo.artifact(run_id, "engineering-summary")
    assert summary["validation_results"]["green"]["failures"] == 0
    assert repo.artifact(run_id, "release")["contract_version"] == "2.1.0"
    _assert_chain(repo, run_id)


def test_scn_b_impact_analysis_precedes_change_and_ignores_the_patch(repo):
    repo.lock_all()
    eng = repo.engine("scn-b")
    run_id = eng.submit({"variant": "normal"}, labels=LABELS)
    assert eng.run(run_id) == "AWAITING_APPROVAL"
    impact = repo.artifact(run_id, "impact-analysis")
    assert impact["interfaces"] == ["POST /api/v1/links"]
    assert "src/shortener/app.py" in impact["files"] and "change set not consulted" in impact["method"]
    assert any("test_api.py" in t for t in impact["tests"])
    actions = [e["action"] + ":" + str(e["target"]) for e in repo.events(run_id)]
    assert actions.index("NODE_SUCCEEDED:impact") < len(actions)
    assert "NODE_STARTED:tdd-red" not in actions  # no change before the design decision
    opened = repo.events(run_id, "GATE_OPENED")[-1]
    assert opened["target"] == "approve-design" and "impact-analysis" in opened["data"]["bound"]
    eng.decide(run_id, "approve-design", repo.keys["approver"], "approve", "impact reviewed (scripted)")
    assert eng.run(run_id) == "AWAITING_APPROVAL"
    assert "within the approved impact" in repo.artifact(run_id, "change-application")["scope_check"]
    eng.decide(run_id, "approve-release", repo.keys["release-owner"], "approve", "ready")
    assert eng.run(run_id) == "COMPLETED"
    _assert_chain(repo, run_id)


def test_scn_b_compensate_restores_previous_release_and_corrects_after_approval(repo):
    repo.lock_all()
    eng = repo.engine("scn-b-compensate")
    run_id = eng.submit({"fault_injection": "smoke_fail"}, labels=(*LABELS, "fault-injection"))
    assert _to_release(repo, eng, run_id) == "AWAITING_APPROVAL"
    eng.decide(run_id, "approve-release", repo.keys["release-owner"], "approve", "ready (scripted)")
    assert eng.run(run_id) == "AWAITING_APPROVAL"  # waiting for the corrective-action decision
    states = {n: r["state"] for n, r in repo.store.nodes(run_id).items()}
    assert states["smoke"] == "COMPENSATED" and states["approve-corrective"] == "AWAITING_APPROVAL"
    failed = repo.events(run_id, "NODE_ATTEMPT_FAILED")[-1]
    assert failed["target"] == "smoke" and failed["data"]["phase"] == "post-promotion"
    record = repo.artifact(run_id, "compensation-record")
    assert record["phase"] == "post-promotion" and record["restored_release"] == "baseline"
    assert len(record["non_rollbackable_effects"]) == 2  # aliases created while the change was live
    staging = repo.tmp / "var" / "staging"
    assert json.loads((staging / "state.json").read_text())["active"] == "baseline"
    with pytest.raises(AuthError):
        eng.decide(run_id, "approve-corrective", repo.keys["agent"], "approve")
    eng.decide(run_id, "approve-corrective", repo.keys["approver"], "approve", "disable listed aliases")
    assert eng.run(run_id) == "FAILED"
    assert repo.store.run(run_id)["reason"] == "compensated:smoke_failed"
    codes = [e["code"] for e in record["non_rollbackable_effects"]]
    with sqlite3.connect(staging / "shortener.db") as db:
        assert db.execute(f"SELECT COUNT(*) FROM links WHERE code IN ({','.join('?' * len(codes))})",
                          codes).fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM links_quarantine").fetchone()[0] == 2
    actions = [e["action"] for e in repo.events(run_id)]
    assert "COMPENSATION_COMPLETED" in actions and "ROLLBACK_STARTED" not in actions
    summary = repo.artifact(run_id, "engineering-summary")
    assert "COMPENSATION after promotion" in summary["why"]
    assert summary["recovery"] == {"rollbacks": 0, "compensations": 1, "mechanisms": ["compensation"]}
    _assert_chain(repo, run_id)


def test_scn_b_defective_variant_fails_regression_and_rolls_back(repo):
    repo.lock_all()
    eng = repo.engine("scn-b")
    run_id = eng.submit({"variant": "defective"}, labels=(*LABELS, "fault-injection"))
    assert _to_release(repo, eng, run_id) == "FAILED"
    assert repo.store.run(run_id)["reason"] == "rolled_back:tests_failed"
    failed = repo.events(run_id, "NODE_ATTEMPT_FAILED")[-1]["data"]
    assert any("test_code_collisions_retry" in t for t in failed["failed_tests"])
    assert repo.events(run_id, "ROLLBACK_COMPLETED")[0]["data"]["workspace_discarded"] is True
    assert not eng.workspace_path(run_id).exists()
    assert repo.artifact(run_id, "test-red")["failures"] > 0  # red was still recorded first
    summary = repo.artifact(run_id, "engineering-summary")
    assert summary["outcome"] == "FAILED" and "ROLLBACK before promotion" in summary["why"]
    assert "test_code_collisions_retry" in summary["why"]
    assert summary["recovery"]["rollbacks"] == 1 and summary["recovery"]["compensations"] == 0
    _assert_chain(repo, run_id)


def test_scn_c_option_a_selects_change_set_from_catalog(repo):
    repo.lock_all()
    eng = repo.engine("scn-c")
    run_id = eng.submit(labels=LABELS)
    assert eng.run(run_id) == "AWAITING_APPROVAL"
    report = repo.artifact(run_id, "quality-report")
    kinds = {i["classification"] for i in report["items"]}
    assert {"missing_information", "unclear_term", "policy_conflict"} <= kinds
    assert repo.store.nodes(run_id)["decompose"]["state"] == "PENDING"  # nothing past the gate
    with pytest.raises(AuthError):
        eng.decide(run_id, "clarify", repo.keys["agent"], "answer", option="A")
    eng.decide(run_id, "clarify", repo.keys["engineer"], "answer", option="A")
    assert _to_release(repo, eng, run_id) == "AWAITING_APPROVAL"
    assert repo.artifact(run_id, "change-set-selection") == {"option_id": "A",
                                                            "change_set": "scenarios/scn-c/changeset"}
    eng.decide(run_id, "approve-release", repo.keys["release-owner"], "approve", "ready")
    assert eng.run(run_id) == "COMPLETED"
    _assert_chain(repo, run_id)


def test_scn_c_option_c_aborts(repo):
    eng = repo.engine("scn-c")
    run_id = eng.submit(labels=LABELS)
    eng.run(run_id)
    eng.decide(run_id, "clarify", repo.keys["approver"], "answer", option="C")
    run = repo.store.run(run_id)
    assert run["state"] == "ABORTED" and "option C" in run["reason"]
    assert "terminated by a human at clarify" in repo.artifact(run_id, "engineering-summary")["why"]


def test_scn_c_free_text_reopens_then_safe_stops_after_two_rounds(repo):
    eng = repo.engine("scn-c")
    run_id = eng.submit(labels=LABELS)
    eng.run(run_id)
    with pytest.raises(EngineError):
        eng.decide(run_id, "clarify", repo.keys["engineer"], "answer", option="B")  # not offered
    eng.decide(run_id, "clarify", repo.keys["engineer"], "answer", text="count the visitors somehow")
    assert repo.store.run(run_id)["state"] == "AWAITING_APPROVAL"
    assert repo.events(run_id, "CLARIFICATION_REOPENED")[0]["data"]["round"] == 2
    eng.decide(run_id, "clarify", repo.keys["engineer"], "answer", text="still free text")
    run = repo.store.run(run_id)
    assert (run["state"], run["reason"]) == ("SAFE_STOPPED", "clarification_limit_exceeded")
    assert repo.store.nodes(run_id)["select"]["state"] == "PENDING"


def test_scn_c_catalog_miss_ends_failed(repo):
    (repo.root / "scenarios" / "scn-c" / "catalog.yaml").write_text("options: {}\n", encoding="utf-8")
    eng = repo.engine("scn-c")
    run_id = eng.submit(labels=LABELS)
    eng.run(run_id)
    eng.decide(run_id, "clarify", repo.keys["engineer"], "answer", option="A")
    assert eng.run(run_id) == "FAILED"
    assert repo.store.run(run_id)["reason"] == "no_approved_change_set"


def test_scanner_down_policy_fail_blocks_release_until_exception_approved(repo):
    repo.lock_all()
    eng = repo.engine("scn-c")
    run_id = eng.submit({"fault_injection": "scanner_unavailable"}, labels=(*LABELS, "fault-injection"))
    eng.run(run_id)
    eng.decide(run_id, "clarify", repo.keys["engineer"], "answer", option="A")
    assert _to_release(repo, eng, run_id) == "SAFE_STOPPED"
    assert repo.store.run(run_id)["reason"] == "policy_fail:SEC-003"
    assert repo.store.nodes(run_id)["approve-release"]["state"] == "PENDING"  # release gate never opened
    evaluations = {r["check_id"]: (r["outcome"], r["reason"]) for r in repo.store.conn.execute(
        "SELECT check_id, outcome, reason FROM policy_evaluations WHERE run_id = ?", (run_id,))}
    assert evaluations["SEC-003"][0] == "FAIL" and "unavailable" in evaluations["SEC-003"][1]
    assert evaluations["SEC-004"][0] == "PASS" and "no findings" in evaluations["SEC-004"][1]
    assert "SEC-003" in repo.artifact(run_id, "engineering-summary")["why"]
    with pytest.raises(EngineError, match="no approved exception"):
        eng.resume(run_id, repo.keys["approver"])
    exc = eng.request_exception(run_id, "SEC-003", repo.keys["engineer"], "scanner outage during demo",
                                "dependency list unchanged; rerun scan before merge")
    with pytest.raises(AuthError):
        eng.approve_exception(run_id, exc, repo.keys["agent"], "agent tries")
    eng.approve_exception(run_id, exc, repo.keys["approver"], "accepted with compensating control")
    eng.resume(run_id, repo.keys["approver"], "exception approved")
    assert eng.run(run_id) == "AWAITING_APPROVAL"
    eng.decide(run_id, "approve-release", repo.keys["release-owner"], "approve", "ready with exception")
    assert eng.run(run_id) == "COMPLETED"
    _assert_chain(repo, run_id)


def test_unlocked_change_set_is_never_applied(repo):
    repo.lock_all(skip=("scenarios/scn-a/changeset",))
    eng = repo.engine("scn-a")
    run_id = eng.submit(labels=LABELS)
    assert _to_release(repo, eng, run_id) == "SAFE_STOPPED"
    assert repo.store.run(run_id)["reason"] == "integrity_mismatch"
    assert repo.store.nodes(run_id)["implement"]["state"] == "PENDING"


def test_tampered_patch_after_lock_is_refused(repo):
    repo.lock_all()
    patch = repo.root / "scenarios" / "scn-a" / "changeset" / "impl.patch"
    patch.write_text(patch.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    eng = repo.engine("scn-a")
    run_id = eng.submit(labels=LABELS)
    assert _to_release(repo, eng, run_id) == "SAFE_STOPPED"
    assert repo.store.run(run_id)["reason"] == "integrity_mismatch"


def test_evidence_export_refuses_test_runs_and_indexes_every_run(repo):
    eng = repo.engine("scn-c")
    aborted = eng.submit(labels=LABELS)
    eng.run(aborted)
    eng.decide(aborted, "clarify", repo.keys["engineer"], "answer", option="C")
    other = eng.submit(labels=("demonstration",))
    eng.run(other)
    out = repo.tmp / "evidence"
    with pytest.raises(EvidenceError):
        export(repo.store, aborted, out)
    path = export(repo.store, other, out)
    assert {p.name for p in path.iterdir()} >= {"audit.json", "chain.json", "transitions.json",
                                               "decisions.json", "metrics.json", "test-results.json"}
    index = (out / "index.md").read_text(encoding="utf-8")
    assert aborted in index and "ABORTED" in index and other in index
