"""SQLite persistence for links, click stats and idempotency records.

Satisfies: FR-SHR-005, FR-SHR-010, FR-SHR-013, FR-SHR-014, A-013.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
    code TEXT PRIMARY KEY CHECK (length(code) BETWEEN 4 AND 10),
    destination TEXT NOT NULL CHECK (length(destination) <= 2048),
    created_at TEXT NOT NULL, expires_at TEXT, creator_key_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS link_stats (
    code TEXT PRIMARY KEY, clicks INTEGER NOT NULL, last_click_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS idempotency (
    key_id TEXT, idem_key TEXT, fingerprint TEXT, response TEXT, created_at TEXT,
    PRIMARY KEY (key_id, idem_key));
"""


class LinkStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            conn.execute("COMMIT")

    def create(self, *, key_id: str, destination: str, created_at: str, expires_at: str | None,
               idem_key: str | None, fingerprint: str, new_code: Callable[[], str], attempts: int,
               render: Callable[[str], dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:
        """Create a link atomically. Returns (status, body): created | replayed | conflict | exhausted."""
        with self._tx() as conn:
            if idem_key:
                row = conn.execute("SELECT fingerprint, response FROM idempotency "
                                   "WHERE key_id = ? AND idem_key = ?", (key_id, idem_key)).fetchone()
                if row:
                    if row["fingerprint"] != fingerprint:
                        return "conflict", None
                    return "replayed", json.loads(row["response"])
            for _ in range(attempts):
                code = new_code()
                try:
                    conn.execute("INSERT INTO links VALUES (?,?,?,?,?)",
                                 (code, destination, created_at, expires_at, key_id))
                    break
                except sqlite3.IntegrityError:
                    continue
            else:
                return "exhausted", None
            body = render(code)
            if idem_key:
                conn.execute("INSERT INTO idempotency VALUES (?,?,?,?,?)",
                             (key_id, idem_key, fingerprint, json.dumps(body), created_at))
            return "created", body

    def get(self, code: str) -> sqlite3.Row | None:
        with closing(self._connect()) as conn:
            return conn.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()

    def record_click(self, code: str, at: str) -> None:
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO link_stats VALUES (?, 1, ?) ON CONFLICT(code) DO UPDATE SET "
                "clicks = clicks + 1, last_click_at = excluded.last_click_at", (code, at))

    def stats(self, code: str) -> sqlite3.Row | None:
        with closing(self._connect()) as conn:
            return conn.execute("SELECT clicks, last_click_at FROM link_stats WHERE code = ?",
                                (code,)).fetchone()

    def ping(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute("SELECT 1 FROM links LIMIT 1").fetchall()
