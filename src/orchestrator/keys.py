"""Orchestrator view of the shared API keys: principals plus audited key creation.

Satisfies: FR-GOV-003, FR-GOV-013, NFR-SEC-004, HD-003.
"""
from __future__ import annotations

from dataclasses import dataclass

from common import apikeys
from common.apikeys import HUMAN_ROLES, ROLES  # noqa: F401  (re-exported)
from orchestrator import audit
from orchestrator.store import Store

SYSTEM_CHAIN = "system"


@dataclass(frozen=True)
class Principal:
    key_id: str
    role: str

    @property
    def actor_type(self) -> str:
        return "agent" if self.role == "agent" else "human"


def create_key(store: Store, role: str, *, ts: float, label: str = "") -> str:
    """Create a key and return its secret once (`sk_<key_id>.<secret>`). Only the hash is stored."""
    with store.tx() as c:
        key_id, presented = apikeys.insert(c, role, label, ts)
        audit.append(c, SYSTEM_CHAIN, "KEY_CREATED", ts=ts, target=key_id, data={"role": role})
    return presented


def resolve(store: Store, presented: str | None) -> Principal | None:
    found = apikeys.resolve(store.conn, presented)
    return Principal(*found) if found else None
