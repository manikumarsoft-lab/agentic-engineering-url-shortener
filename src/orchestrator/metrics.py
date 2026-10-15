"""Per-run reliability metrics computed only from recorded state and audit events.

Satisfies: FR-OBS-006, FR-OBS-007, NFR-RCV-002.
"""
from __future__ import annotations

from typing import Any

from orchestrator import audit
from orchestrator.store import Store

LABEL = "demonstration data"


def compute_mttr(events: list[dict[str, Any]]) -> dict[str, Any]:
    """MTTR = mean(recovery_completed - failure_detected) over recovered episodes only."""
    detected: dict[str, float] = {}
    durations: list[float] = []
    for ev in events:
        episode = ev["data"].get("episode")
        if ev["action"] == "FAILURE_DETECTED" and episode not in detected:
            detected[episode] = ev["ts"]
        elif ev["action"] == "RECOVERY_COMPLETED" and episode in detected:
            durations.append(ev["ts"] - detected.pop(episode))
    return {
        "mttr_s": sum(durations) / len(durations) if durations else None,
        "recovered": len(durations),
        "unrecovered": len(detected),
    }


def run_metrics(store: Store, run_id: str) -> dict[str, Any]:
    run = store.run(run_id)
    events = audit.events(store.conn, run_id)
    count = lambda action: sum(1 for e in events if e["action"] == action)  # noqa: E731
    end = run["ended_at"] or events[-1]["ts"]
    return {
        "label": LABEL,
        "run_id": run_id,
        "state": run["state"],
        "success": run["state"] == "COMPLETED",
        "retries": count("RETRY_SCHEDULED"),
        "rollbacks": count("ROLLBACK_COMPLETED"),
        "compensations": count("COMPENSATION_COMPLETED"),
        **compute_mttr(events),
        "end_to_end_s": end - run["created_at"],
        "node_latency_s": {nid: row["active_s"] for nid, row in store.nodes(run_id).items()},
    }
