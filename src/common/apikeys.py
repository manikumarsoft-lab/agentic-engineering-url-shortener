"""Role-mapped API keys `sk_<key_id>.<secret>`, stored only as SHA-256 hashes.

Shared by the shortener and the orchestrator so both accept the same keys.
Satisfies: FR-SHR-019, FR-GOV-003, FR-GOV-013, NFR-SEC-004, HD-003.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3

HUMAN_ROLES = frozenset({"consumer", "engineer", "approver", "release-owner"})
ROLES = HUMAN_ROLES | {"agent"}

SCHEMA = """CREATE TABLE IF NOT EXISTS keys (
    key_id TEXT PRIMARY KEY, secret_sha256 TEXT, role TEXT, label TEXT, created_at REAL);"""


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def insert(conn: sqlite3.Connection, role: str, label: str, ts: float) -> tuple[str, str]:
    """Insert a new key; return (key_id, presented secret). The secret is never stored."""
    if role not in ROLES:
        raise ValueError(f"unknown role '{role}'")
    key_id = secrets.token_hex(6)
    secret = secrets.token_urlsafe(32)
    conn.execute("INSERT INTO keys VALUES (?,?,?,?,?)", (key_id, hash_secret(secret), role, label, ts))
    return key_id, f"sk_{key_id}.{secret}"


def resolve(conn: sqlite3.Connection, presented: str | None) -> tuple[str, str] | None:
    """Return (key_id, role) for a valid presented key, else None (constant-time comparison)."""
    if not presented or not presented.startswith("sk_") or "." not in presented:
        return None
    key_id, secret = presented[3:].split(".", 1)
    row = conn.execute("SELECT secret_sha256, role FROM keys WHERE key_id = ?", (key_id,)).fetchone()
    if row is None or not hmac.compare_digest(row[0], hash_secret(secret)):
        return None
    return key_id, row[1]
