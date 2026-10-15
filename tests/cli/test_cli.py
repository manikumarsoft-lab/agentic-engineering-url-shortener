"""`orch` commands: happy paths plus agent-key refusal."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.main import app
from orchestrator import audit
from orchestrator.store import Store

ROOT = Path(__file__).resolve().parents[2]
FLAKY = """
name: flaky
version: 1.0.0
defaults: {backoff_s: 0}
nodes:
  - {id: work, agent: flaky, params: {fail_times: 3}}
"""


@pytest.fixture
def cli(tmp_path, monkeypatch):
    wf_dir = tmp_path / "workflows"
    wf_dir.mkdir()
    (wf_dir / "demo.yaml").write_text((ROOT / "workflows" / "demo.yaml").read_text(), encoding="utf-8")
    (wf_dir / "flaky.yaml").write_text(FLAKY, encoding="utf-8")
    monkeypatch.setenv("ORCH_HOME", str(tmp_path / "var"))
    monkeypatch.setenv("ORCH_WORKFLOWS", str(wf_dir))
    monkeypatch.setenv("ORCH_POLICY", str(ROOT / "policy" / "policy-set.yaml"))
    monkeypatch.delenv("ORCH_KEY", raising=False)
    runner = CliRunner()

    def orch(*args: str, code: int = 0) -> str:
        result = runner.invoke(app, list(args))
        assert result.exit_code == code, result.output
        return result.output

    def key(role: str) -> str:
        return orch("keys", "create", "--role", role).strip().splitlines()[0]

    def store() -> Store:
        return Store(tmp_path / "var" / "orchestrator.db")

    return orch, key, store


def _run_id(output: str) -> str:
    return re.search(r"run_[0-9a-f]{16}", output).group(0)


def test_keys_create_prints_once_and_stores_only_a_hash(cli):
    orch, key, store = cli
    secret = key("approver")
    assert secret.startswith("sk_")
    db = (Path(store().conn.execute("PRAGMA database_list").fetchone()[2])).read_bytes()
    assert secret.split(".", 1)[1].encode() not in db
    orch("keys", "create", "--role", "root", code=2)


def test_submit_status_gate_flow_audit_and_metrics(cli):
    orch, key, _ = cli
    approver, agent = key("approver"), key("agent")
    out = orch("run", "submit", "demo")
    run_id = _run_id(out)
    assert "AWAITING_APPROVAL" in out
    assert "approve-design           AWAITING_APPROVAL" in orch("run", "status", run_id)
    gate = f"{run_id}:approve-design"
    assert gate in orch("gate", "list")
    shown = json.loads(orch("gate", "show", gate))
    assert shown["required_roles"] == ["approver"] and shown["bound_artifacts"] == {"design": 1}

    refused = orch("gate", "approve", gate, "--key", agent, "--reason", "agent tries", code=2)
    assert "refused" in refused
    assert "AUTH_REFUSED" in orch("audit", "show", run_id)

    out = orch("gate", "approve", gate, "--key", approver, "--reason", "design ok")
    assert f"{run_id} COMPLETED" in out
    assert orch("audit", "verify", run_id).strip() == "valid"
    metrics = json.loads(orch("metrics", run_id))
    assert metrics["label"] == "demonstration data" and metrics["success"] is True


def test_escalate_then_release_owner_decides(cli):
    orch, key, _ = cli
    approver, owner, agent = key("approver"), key("release-owner"), key("agent")
    gate = f"{_run_id(orch('run', 'submit', 'demo'))}:approve-design"
    orch("gate", "escalate", gate, "--key", agent, "--reason", "x", code=2)
    orch("gate", "escalate", gate, "--key", approver, "--reason", "risk above my authority")
    assert json.loads(orch("gate", "show", gate))["required_roles"] == ["release-owner"]
    assert "escalated" in orch("gate", "list")
    orch("gate", "approve", gate, "--key", approver, code=2)
    assert "COMPLETED" in orch("gate", "approve", gate, "--key", owner, "--reason", "accepted")


def test_reject_terminates_or_reworks(cli):
    orch, key, _ = cli
    approver = key("approver")
    gate = f"{_run_id(orch('run', 'submit', 'demo'))}:approve-design"
    out = orch("gate", "reject", gate, "--rework", "--key", approver, "--reason", "redo design")
    assert "AWAITING_APPROVAL" in out
    assert "ABORTED" in orch("gate", "reject", gate, "--key", approver, "--reason", "stop")
    assert "no open gates" in orch("gate", "list")


def test_watch_and_resume_with_agent_refusal(cli):
    orch, key, store = cli
    approver, agent = key("approver"), key("agent")
    run_id = _run_id(orch("run", "submit", "flaky"))
    assert store().run(run_id)["state"] == "SAFE_STOPPED"
    orch("run", "resume", run_id, "--key", agent, code=2)
    events = audit.events(store().conn, run_id)
    assert events[-1]["action"] == "AUTH_REFUSED" and events[-1]["actor_type"] == "agent"
    assert "COMPLETED" in orch("run", "resume", run_id, "--key", approver, "--reason", "retry")

    fresh = _run_id(orch("run", "submit", "demo"))
    watched = orch("run", "watch", fresh)
    assert "AWAITING_APPROVAL" in watched
