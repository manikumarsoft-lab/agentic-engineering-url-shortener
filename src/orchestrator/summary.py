"""Final engineering summary, produced by the engine for every terminal outcome and safe-stop.

Satisfies: FR-ORC-026 (plan and rationale, artifacts, risks, trade-offs, validation results,
assumptions, limitations), plus the outcome and why it happened.
"""
from __future__ import annotations

import json
from typing import Any

from orchestrator import audit
from orchestrator.store import Store

TRADE_OFFS = [
    "deterministic rule-based agents apply human-locked change sets instead of generating code at run time",
    "scenario runs evaluate SEC-003 against a pinned pip-audit snapshot (no network); the live audit runs in `orch release check`",
    "releases are local (snapshot or local staging); merging into the repository stays a manual human action",
]
LIMITATIONS = ["metrics are demonstration data from a single workstation",
               "planned-but-not-implemented scope: docs/scope/lean-slice.md section 2"]
RESUME_HINTS = {
    "gate_timeout": "no decision arrived before the gate deadline; an approver may resume, which re-opens the same gate on the same artifact versions",
    "clarification_limit_exceeded": "two free-text answers could not be interpreted; resume and choose an offered option",
    "rework_limit_exceeded": "the gate was sent back for rework more than twice",
    "integrity_mismatch": "the change set is not locked or differs from the locked version; lock it with `orch changeset lock`, then resume",
    "retry_exhausted": "a transient failure persisted through the retry budget; an approver may resume (the budget is reset and audited)",
    "interrupted": "the engine stopped while a stage was running; an approver may resume",
    "compensation_failed": "the previous release could not be restored; staging needs manual attention",
}


def _latest_artifacts(store: Store, run_id: str) -> dict[str, tuple[int, Any]]:
    rows = store.conn.execute(
        "SELECT name, version, content FROM artifacts a WHERE run_id = ? AND version = "
        "(SELECT MAX(version) FROM artifacts b WHERE b.run_id = a.run_id AND b.name = a.name)",
        (run_id,)).fetchall()
    return {r["name"]: (r["version"], json.loads(r["content"])) for r in rows if r["name"] != "engineering-summary"}


def _why(outcome: str, reason: str | None, events: list[dict], decisions: list[dict]) -> str:
    failures = [e for e in events if e["action"] == "NODE_ATTEMPT_FAILED"]
    last = failures[-1] if failures else None
    detail = ""
    if last:
        tests = last["data"].get("failed_tests")
        detail = f"{last['target']} failed ({last['reason']}" + (f": {', '.join(tests[:5])}" if tests else "") + ")"
    if outcome == "COMPLETED":
        approvals = [f"{d['node_id']} by {d['role']} key {d['key_id']}" for d in decisions if d["choice"] == "approve"]
        return "all stages succeeded and every gate was decided by a human (" + "; ".join(approvals) + ")"
    if outcome == "ABORTED":
        ended = [d for d in decisions if d["choice"] in ("reject_terminate", "answer")]
        d = ended[-1] if ended else None
        return (f"terminated by a human at {d['node_id']} ({d['role']} key {d['key_id']}): {reason}" if d
                else f"terminated: {reason}")
    if outcome == "FAILED":
        if (reason or "").startswith("rolled_back"):
            return (f"{detail}; ROLLBACK before promotion: the isolated workspace was discarded, nothing was "
                    "promoted, the last known-good release is unchanged")
        if (reason or "").startswith("compensated"):
            corrective = [d for d in decisions if d["node_id"] == "approve-corrective"]
            action = (f"; corrective action approved by {corrective[-1]['role']} key {corrective[-1]['key_id']}"
                      if corrective else "")
            return (f"{detail}; COMPENSATION after promotion: the previous release was restored and verified{action}")
        return f"{detail or reason}"
    hint = RESUME_HINTS.get(reason or "", "")
    if (reason or "").startswith("policy_fail:"):
        hint = f"mandatory policy {reason.split(':', 1)[1]} failed; release is blocked until a human-approved exception exists, then an approver resumes"
    return f"safe-stopped ({reason}){': ' + detail if detail and not hint else ''}; {hint or 'resumable by an approver key'}"


def build(store: Store, run_id: str, outcome: str, reason: str | None) -> dict[str, Any]:
    run = store.run(run_id)
    events = audit.events(store.conn, run_id)
    decisions = [dict(r) for r in store.conn.execute(
        "SELECT node_id, key_id, role, choice, reason FROM decisions WHERE run_id = ? ORDER BY created_at", (run_id,))]
    arts = _latest_artifacts(store, run_id)
    get = lambda name: arts.get(name, (0, {}))[1] or {}  # noqa: E731
    red, green = get("test-red"), get("test-results")
    policy = {r["check_id"]: r["outcome"] for r in store.conn.execute(
        "SELECT check_id, outcome FROM policy_evaluations WHERE run_id = ? ORDER BY rowid", (run_id,))}
    recoveries = [e["data"].get("mechanism") for e in events if e["action"] == "RECOVERY_COMPLETED"]
    return {
        "workflow": run["workflow"], "run_id": run_id, "labels": run["labels"],
        "outcome": outcome, "reason": reason, "why": _why(outcome, reason, events, decisions),
        "plan_and_rationale": {"requirement": get("normalized-requirement").get("title"),
                               "approach": get("design").get("approach"),
                               "tasks": len(get("task-plan").get("tasks", [])),
                               "impact_analysis": "impact-analysis" in arts},
        "artifacts": {name: version for name, (version, _) in sorted(arts.items())},
        "decisions": decisions,
        "risks": [f"{t['id']} {t['category']} ({t['severity']}, {t['status']})"
                  for t in get("threat-review").get("threats", [])],
        "trade_offs": TRADE_OFFS,
        "validation_results": {"red": {k: red.get(k) for k in ("tests", "failures", "errors")},
                               "green": {k: green.get(k) for k in ("tests", "failures", "errors")},
                               "policy": policy},
        "recovery": {"rollbacks": sum(1 for e in events if e["action"] == "ROLLBACK_COMPLETED"),
                     "compensations": sum(1 for e in events if e["action"] == "COMPENSATION_COMPLETED"),
                     "mechanisms": recoveries},
        "assumptions": ["change sets apply to the baseline they were authored against (docs/scope/lean-slice.md)"],
        "limitations": LIMITATIONS,
    }
