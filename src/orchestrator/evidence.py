"""Evidence export: everything a reviewer needs to check a run without the database.

`export` writes evidence/<run_id>/ and rewrites evidence/index.md, which lists every run in the
store (including failed, aborted and safe-stopped runs) so no run can be silently left out.
Satisfies: SC-002, SC-003, FR-ORC-031, FR-OBS-001..008, CON X.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator import audit
from orchestrator.metrics import run_metrics
from orchestrator.store import Store

STATE_EVENTS = ("RUN_", "NODE_", "GATE_", "STEP_STARTED", "CLARIFICATION_", "ROLLBACK_", "COMPENSATION_",
                "RETRY_", "FAILURE_DETECTED", "RECOVERY_COMPLETED", "TIMEOUT", "POLICY_EVALUATED", "EXCEPTION_",
                "SUMMARY_PRODUCED")
RECOVERY_MEANING = {
    "rollback": "pre-promotion: the isolated workspace was discarded; nothing was promoted, so the last "
                "known-good release never changed",
    "compensation": "post-promotion: the change was live on staging; the previous release was re-promoted and "
                    "verified, and effects that cannot be rolled back are corrected only after human approval",
}


def _recovery(events: list[dict[str, Any]]) -> dict[str, Any]:
    pick = lambda prefix: [e for e in events if e["action"].startswith(prefix)]  # noqa: E731
    episodes = {}
    for e in events:
        ep = e["data"].get("episode")
        if e["action"] == "FAILURE_DETECTED":
            episodes[ep] = {"episode": ep, "node": e["target"], "cause": e["reason"], "detected_at": e["ts"]}
        elif e["action"] == "RECOVERY_COMPLETED" and ep in episodes:
            episodes[ep].update(mechanism=e["data"].get("mechanism"), recovered_at=e["ts"],
                                meaning=RECOVERY_MEANING.get(e["data"].get("mechanism"), ""))
    return {"rollback_events": pick("ROLLBACK_"), "compensation_events": pick("COMPENSATION_"),
            "episodes": list(episodes.values()), "meaning": RECOVERY_MEANING}


class EvidenceError(ValueError):
    pass


def _iso(ts: float | None) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).isoformat() if ts else ""


def _dump(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def _rows(store: Store, sql: str, run_id: str) -> list[dict[str, Any]]:
    return [dict(r) for r in store.conn.execute(sql, (run_id,)).fetchall()]


def export(store: Store, run_id: str, out_root: Path, *, allow_test: bool = False) -> Path:
    run = store.run(run_id)
    if "test" in run["labels"] and not allow_test:
        raise EvidenceError(f"{run_id} is labelled 'test' (scripted); it is never scenario evidence")
    out = out_root / run_id
    out.mkdir(parents=True, exist_ok=True)
    events = audit.events(store.conn, run_id)
    valid, bad = audit.verify_chain(store.conn, run_id)
    _dump(out / "audit.json", events)
    _dump(out / "chain.json", {"valid": valid, "first_bad_seq": bad, "events": len(events),
                               "head_hash": events[-1]["hash"] if events else None})
    _dump(out / "transitions.json", [e for e in events if e["action"].startswith(STATE_EVENTS)])
    _dump(out / "decisions.json", {
        "decisions": _rows(store, "SELECT * FROM decisions WHERE run_id = ? ORDER BY created_at", run_id),
        "exceptions": _rows(store, "SELECT * FROM exceptions WHERE run_id = ? ORDER BY created_at", run_id),
        "policy_evaluations": _rows(store, "SELECT * FROM policy_evaluations WHERE run_id = ? ORDER BY rowid",
                                    run_id)})
    _dump(out / "metrics.json", run_metrics(store, run_id))
    artifacts = _rows(store, "SELECT name, version, content, produced_by, created_at FROM artifacts "
                             "WHERE run_id = ? ORDER BY created_at, name, version", run_id)
    for a in artifacts:
        a["content"] = json.loads(a["content"])
    _dump(out / "test-results.json", [a for a in artifacts if a["name"] in ("test-red", "test-results")]
          + [{"name": "failed-attempt", **e["data"], "node": e["target"]} for e in events
             if e["action"] == "NODE_ATTEMPT_FAILED" and "phase" in e["data"]])
    _dump(out / "artifacts.json", artifacts)
    _dump(out / "recovery.json", _recovery(events))
    summaries = [a for a in artifacts if a["name"] == "engineering-summary"]
    if summaries:
        _dump(out / "engineering-summary.json", summaries[-1]["content"])
    _dump(out / "run.json", {**run, "nodes": store.nodes(run_id)})
    write_index(store, out_root)
    return out


def write_index(store: Store, out_root: Path) -> Path:
    out_root.mkdir(parents=True, exist_ok=True)
    rows = store.conn.execute("SELECT * FROM runs ORDER BY created_at").fetchall()
    lines = ["# Evidence index", "",
             "Every run recorded in the orchestrator database, including failed, aborted and safe-stopped",
             "runs. Runs labelled `test` are scripted test runs and are not scenario evidence.", "",
             "| Run | Workflow | Labels | State | Reason | Created (UTC) | Evidence |",
             "|-----|----------|--------|-------|--------|---------------|----------|"]
    for r in rows:
        exported = (out_root / r["run_id"]).exists()
        link = f"[{r['run_id']}/]({r['run_id']}/)" if exported else "not exported"
        lines.append(f"| {r['run_id']} | {r['workflow']} | {', '.join(json.loads(r['labels']))} | "
                     f"{r['state']} | {r['reason'] or ''} | {_iso(r['created_at'])} | {link} |")
    path = out_root / "index.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
