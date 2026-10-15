"""SQLite persistence for runs, nodes, artifacts, decisions, policy, keys and audit.

Satisfies: FR-ORC-011, FR-ORC-012, FR-ORC-013, FR-OBS-004.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY, workflow TEXT, workflow_version TEXT, policy_version TEXT,
    state TEXT, reason TEXT, labels TEXT, facts TEXT, created_at REAL, ended_at REAL);
CREATE TABLE IF NOT EXISTS nodes (
    run_id TEXT, node_id TEXT, state TEXT, attempts INTEGER DEFAULT 0,
    runs_total INTEGER DEFAULT 0, not_before REAL DEFAULT 0, deadline REAL,
    started_at REAL, ended_at REAL, active_s REAL DEFAULT 0, rework INTEGER DEFAULT 0,
    last_error TEXT, degraded INTEGER DEFAULT 0, bound TEXT, episode TEXT, recovery_mech TEXT,
    PRIMARY KEY (run_id, node_id));
CREATE TABLE IF NOT EXISTS artifacts (
    run_id TEXT, name TEXT, version INTEGER, content TEXT, produced_by TEXT, created_at REAL,
    PRIMARY KEY (run_id, name, version));
CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY, run_id TEXT, node_id TEXT, key_id TEXT, role TEXT,
    choice TEXT, reason TEXT, bound TEXT, status TEXT, created_at REAL);
CREATE TABLE IF NOT EXISTS policy_evaluations (
    run_id TEXT, node_id TEXT, check_id TEXT, policy_version TEXT, outcome TEXT,
    mandatory INTEGER, reason TEXT, exception_id TEXT, created_at REAL);
CREATE TABLE IF NOT EXISTS exceptions (
    exception_id TEXT PRIMARY KEY, run_id TEXT, check_id TEXT, requested_by TEXT, reason TEXT,
    compensating_control TEXT, status TEXT, decided_by TEXT, created_at REAL, decided_at REAL);
CREATE TABLE IF NOT EXISTS keys (
    key_id TEXT PRIMARY KEY, secret_sha256 TEXT, role TEXT, label TEXT, created_at REAL);
CREATE TABLE IF NOT EXISTS audit (
    run_id TEXT, seq INTEGER, ts REAL, actor_type TEXT, actor_id TEXT, action TEXT,
    target TEXT, result TEXT, reason TEXT, data TEXT, prev_hash TEXT, hash TEXT,
    PRIMARY KEY (run_id, seq));
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit
    BEGIN SELECT RAISE(ABORT, 'append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit
    BEGIN SELECT RAISE(ABORT, 'append-only'); END;
CREATE TRIGGER IF NOT EXISTS policy_no_update BEFORE UPDATE ON policy_evaluations
    BEGIN SELECT RAISE(ABORT, 'append-only'); END;
CREATE TRIGGER IF NOT EXISTS policy_no_delete BEFORE DELETE ON policy_evaluations
    BEGIN SELECT RAISE(ABORT, 'append-only'); END;
"""


class Store:
    def __init__(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), isolation_level=None, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.executescript(SCHEMA)

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        """One transaction: every state change and its audit event commit together or not at all."""
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        self.conn.execute("COMMIT")

    # -- reads -------------------------------------------------------------------------------
    def run(self, run_id: str) -> dict[str, Any]:
        row = self.conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(run_id)
        return {**dict(row), "facts": json.loads(row["facts"]), "labels": json.loads(row["labels"])}

    def runs(self, states: tuple[str, ...]) -> list[str]:
        marks = ",".join("?" * len(states))
        return [r[0] for r in self.conn.execute(f"SELECT run_id FROM runs WHERE state IN ({marks})", states)]

    def nodes(self, run_id: str) -> dict[str, dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM nodes WHERE run_id = ?", (run_id,)).fetchall()
        return {r["node_id"]: dict(r) for r in rows}

    def artifact(self, run_id: str, name: str) -> tuple[int, Any] | None:
        row = self.conn.execute(
            "SELECT version, content FROM artifacts WHERE run_id = ? AND name = ? "
            "ORDER BY version DESC LIMIT 1", (run_id, name)).fetchone()
        return (row[0], json.loads(row[1])) if row else None

    # -- writes (call inside tx) --------------------------------------------------------------
    @staticmethod
    def set_node(c: sqlite3.Connection, run_id: str, node_id: str, **fields: Any) -> None:
        cols = ", ".join(f"{k} = ?" for k in fields)
        c.execute(f"UPDATE nodes SET {cols} WHERE run_id = ? AND node_id = ?",
                  (*fields.values(), run_id, node_id))

    @staticmethod
    def set_run(c: sqlite3.Connection, run_id: str, **fields: Any) -> None:
        if "facts" in fields:
            fields["facts"] = json.dumps(fields["facts"])
        cols = ", ".join(f"{k} = ?" for k in fields)
        c.execute(f"UPDATE runs SET {cols} WHERE run_id = ?", (*fields.values(), run_id))

    @staticmethod
    def add_artifact(c: sqlite3.Connection, run_id: str, name: str, content: Any,
                     produced_by: str, ts: float) -> int:
        row = c.execute("SELECT MAX(version) FROM artifacts WHERE run_id = ? AND name = ?",
                        (run_id, name)).fetchone()
        version = (row[0] or 0) + 1
        c.execute("INSERT INTO artifacts VALUES (?,?,?,?,?,?)",
                  (run_id, name, version, json.dumps(content), produced_by, ts))
        return version
