from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import audit, keys
from orchestrator.engine import Engine, FakeClock
from orchestrator.graph import load_workflow_text
from orchestrator.policy import PolicySet
from orchestrator.store import Store


@pytest.fixture
def env(tmp_path: Path) -> SimpleNamespace:
    store = Store(tmp_path / "orch.db")
    clock = FakeClock()
    roles = ("engineer", "approver", "release-owner", "agent")
    k = {role: keys.create_key(store, role, ts=clock.now()) for role in roles}
    ns = SimpleNamespace(store=store, clock=clock, keys=k, tmp=tmp_path)

    def engine(yaml_text: str, policy: PolicySet | None = None,
               source_dir: Path | None = None) -> Engine:
        return Engine(store, load_workflow_text(yaml_text), policy, var_dir=tmp_path / "var",
                      clock=clock, source_dir=source_dir)

    def actions(run_id: str) -> list[str]:
        return [e["action"] for e in audit.events(store.conn, run_id)]

    def states(run_id: str) -> dict[str, str]:
        return {nid: row["state"] for nid, row in store.nodes(run_id).items()}

    ns.engine, ns.actions, ns.states = engine, actions, states
    return ns
