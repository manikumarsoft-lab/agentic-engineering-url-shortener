"""Role-mapped API keys, stored as SHA-256 hashes.

Satisfies: FR-GOV-003, FR-GOV-013, NFR-SEC-004, HD-003.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from orchestrator import audit
from orchestrator.store import Store

HUMAN_ROLES = frozenset({"consumer", "engineer", "approver", "release-owner"})
ROLES = HUMAN_ROLES | {"agent"}
SYSTEM_CHAIN = "system"


@dataclass(frozen=True)
class Principal:
    key_id: str
    role: str

    @property
    def actor_type(self) -> str:
        return "agent" if self.role == "agent" else "human"


def _hash(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def create_key(store: Store, role: str, *, ts: float, label: str = "") -> str:
    """Create a key and return its secret once (`sk_<key_id>.<secret>`). Only the hash is stored."""
    if role not in ROLES:
        raise ValueError(f"unknown role '{role}'")
    key_id = secrets.token_hex(6)
    secret = secrets.token_urlsafe(32)
    with store.tx() as c:
        c.execute("INSERT INTO keys VALUES (?,?,?,?,?)", (key_id, _hash(secret), role, label, ts))
        audit.append(c, SYSTEM_CHAIN, "KEY_CREATED", ts=ts, target=key_id, data={"role": role})
    return f"sk_{key_id}.{secret}"


def resolve(store: Store, presented: str | None) -> Principal | None:
    if not presented or not presented.startswith("sk_") or "." not in presented:
        return None
    key_id, secret = presented[3:].split(".", 1)
    row = store.conn.execute("SELECT secret_sha256, role FROM keys WHERE key_id = ?",
                             (key_id,)).fetchone()
    if row is None or not hmac.compare_digest(row[0], _hash(secret)):
        return None
    return Principal(key_id=key_id, role=row[1])
