"""Append-only, hash-chained audit log (one chain per run).

Satisfies: FR-OBS-001, FR-OBS-002, FR-OBS-003, FR-OBS-004, NFR-AUD-001.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any

GENESIS = "0" * 64


def _canonical(body: dict[str, Any]) -> str:
    return json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prev_hash: str, body: dict[str, Any]) -> str:
    return hashlib.sha256((prev_hash + _canonical(body)).encode("utf-8")).hexdigest()


def append(
    conn: sqlite3.Connection,
    run_id: str,
    action: str,
    *,
    ts: float,
    actor_type: str = "system",
    actor_id: str | None = None,
    target: str | None = None,
    result: str = "ok",
    reason: str | None = None,
    data: dict[str, Any] | None = None,
) -> int:
    """Append one event. Must run inside the transaction that changes the audited state."""
    if not conn.in_transaction:
        raise RuntimeError("audit.append must share the state transition's transaction")
    last = conn.execute(
        "SELECT seq, hash FROM audit WHERE run_id = ? ORDER BY seq DESC LIMIT 1", (run_id,)
    ).fetchone()
    seq, prev_hash = (last[0] + 1, last[1]) if last else (1, GENESIS)
    body = {
        "run_id": run_id, "seq": seq, "ts": ts, "actor_type": actor_type, "actor_id": actor_id,
        "action": action, "target": target, "result": result, "reason": reason, "data": data or {},
    }
    conn.execute(
        "INSERT INTO audit (run_id, seq, ts, actor_type, actor_id, action, target, result, reason,"
        " data, prev_hash, hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (run_id, seq, ts, actor_type, actor_id, action, target, result, reason,
         _canonical(data or {}), prev_hash, _digest(prev_hash, body)),
    )
    return seq


def events(conn: sqlite3.Connection, run_id: str) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM audit WHERE run_id = ? ORDER BY seq", (run_id,)).fetchall()
    return [{**dict(r), "data": json.loads(r["data"])} for r in rows]


def verify_chain(conn: sqlite3.Connection, run_id: str) -> tuple[bool, int | None]:
    """Recompute the chain. Returns (valid, first_bad_seq)."""
    prev_hash = GENESIS
    for i, ev in enumerate(events(conn, run_id), start=1):
        body = {k: ev[k] for k in ("run_id", "seq", "ts", "actor_type", "actor_id", "action",
                                   "target", "result", "reason", "data")}
        if ev["seq"] != i or ev["prev_hash"] != prev_hash or ev["hash"] != _digest(prev_hash, body):
            return False, ev["seq"]
        prev_hash = ev["hash"]
    return True, None
