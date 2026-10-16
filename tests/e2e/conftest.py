"""Scripted end-to-end harness. TEST-ONLY: runs are labelled `test`/`scripted`, decisions come from
test keys, and nothing here is scenario evidence (the human records evidence runs with `orch`)."""
from __future__ import annotations

import shutil
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import audit, changesets, keys
from orchestrator.agents.scenario import CONTRACT_REL
from orchestrator.engine import Engine
from orchestrator.graph import load_workflow
from orchestrator.policy import load_policy
from orchestrator.store import Store

ROOT = Path(__file__).resolve().parents[2]
COPY = ("src", "tests/shortener", CONTRACT_REL, "pyproject.toml", "requirements.lock", "scenarios", "policy")
LABELS = ("test", "scripted")
CHANGE_SETS = ("scenarios/scn-a/changeset", "scenarios/scn-b/changeset",
               "scenarios/scn-b/changeset-defective", "scenarios/scn-c/changeset")


@pytest.fixture
def repo(tmp_path: Path) -> SimpleNamespace:
    root = tmp_path / "repo"
    for rel in COPY:
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, root / rel, ignore=shutil.ignore_patterns("__pycache__", "changesets.lock.yaml"))
        else:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, root / rel)
    store = Store(tmp_path / "orch.db")
    k = {role: keys.create_key(store, role, ts=time.time())
         for role in ("engineer", "approver", "release-owner", "agent")}
    ns = SimpleNamespace(root=root, store=store, keys=k, tmp=tmp_path)

    def lock_all(skip: tuple[str, ...] = ()) -> None:
        approver = keys.resolve(store, k["approver"])
        for rel in CHANGE_SETS:
            if rel not in skip:
                changesets.lock(root, rel, approver)

    def engine(workflow: str) -> Engine:
        workflow_file = root / "scenarios" / workflow / "workflow.yaml"
        return Engine(store, load_workflow(workflow_file),
                      load_policy(root / "policy" / "policy-set.yaml"), var_dir=tmp_path / "var",
                      source_dir=root)

    def events(run_id: str, action: str | None = None) -> list[dict]:
        evs = audit.events(store.conn, run_id)
        return [e for e in evs if action is None or e["action"] == action]

    def artifact(run_id: str, name: str):
        found = store.artifact(run_id, name)
        return found[1] if found else None

    ns.lock_all, ns.engine, ns.events, ns.artifact = lock_all, engine, events, artifact
    return ns
