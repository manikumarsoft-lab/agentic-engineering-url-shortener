"""`orch` scenario commands end to end (TEST-ONLY copy of the repository under tmp_path)."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.main import app
from orchestrator.agents.scenario import CONTRACT_REL

ROOT = Path(__file__).resolve().parents[2]
COPY = ("src", "tests/shortener", CONTRACT_REL, "pyproject.toml", "requirements.lock", "scenarios", "policy")


@pytest.fixture
def orch(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    for rel in COPY:
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, root / rel, ignore=shutil.ignore_patterns("__pycache__", "changesets.lock.yaml"))
        else:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, root / rel)
    for var in ("ORCH_WORKFLOWS", "ORCH_POLICY", "ORCH_KEY", "ORCH_EVIDENCE", "ORCH_HOME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("ORCH_ROOT", str(root))
    runner = CliRunner()

    def run(*args: str, code: int = 0) -> str:
        result = runner.invoke(app, list(args))
        assert result.exit_code == code, result.output
        return result.output

    run.root = root
    return run


def _key(orch, role: str) -> str:
    return orch("keys", "create", "--role", role).strip().splitlines()[0]


def _run_id(output: str) -> str:
    return re.search(r"run_[0-9a-f]{16}", output).group(0)


def test_scanner_down_variant_via_cli_with_exception_and_evidence(orch):
    engineer, approver, owner, agent = (_key(orch, r) for r in ("engineer", "approver", "release-owner", "agent"))
    assert "refused" in orch("changeset", "lock", "scenarios/scn-c/changeset", "--key", agent, code=2)
    assert "locked scenarios/scn-c/changeset" in orch("changeset", "lock", "scenarios/scn-c/changeset",
                                                      "--key", approver)
    out = orch("run", "submit", "scn-c-scanner-down")
    run_id = _run_id(out)
    assert "AWAITING_APPROVAL" in out
    shown = json.loads(orch("gate", "show", f"{run_id}:clarify"))
    assert shown["kind"] == "clarify" and set(shown["options"]) == {"A", "C"}
    assert shown["artifacts"]["quality-report"]["clarification_required"] is True

    orch("gate", "answer", f"{run_id}:clarify", "--option", "A", "--key", agent, code=2)
    out = orch("gate", "answer", f"{run_id}:clarify", "--option", "A", "--key", engineer)
    assert "approve-design" in out and "AWAITING_APPROVAL" in out
    out = orch("gate", "approve", f"{run_id}:approve-design", "--key", approver, "--reason", "design ok")
    assert "SAFE_STOPPED (policy_fail:SEC-003)" in out

    orch("run", "resume", run_id, "--key", approver, code=2)  # no approved exception yet
    exc = orch("exception", "request", run_id, "SEC-003", "--key", engineer, "--reason", "scanner outage",
               "--control", "rerun scan before merge").strip()
    orch("exception", "approve", run_id, exc, "--key", agent, "--reason", "x", code=2)
    orch("exception", "approve", run_id, exc, "--key", approver, "--reason", "accepted")
    assert "AWAITING_APPROVAL" in orch("run", "resume", run_id, "--key", approver, "--reason", "excepted")
    assert f"{run_id} COMPLETED" in orch("gate", "approve", f"{run_id}:approve-release", "--key", owner,
                                         "--reason", "ready")

    assert "wrote" in orch("evidence", "export", run_id)
    evidence_dir = orch.root / "evidence" / run_id
    assert json.loads((evidence_dir / "chain.json").read_text())["valid"] is True
    decisions = json.loads((evidence_dir / "decisions.json").read_text())
    assert decisions["exceptions"][0]["status"] == "APPROVED"
    assert run_id in (orch.root / "evidence" / "index.md").read_text()


def test_option_c_and_free_text_via_cli(orch):
    engineer = _key(orch, "engineer")
    aborted = _run_id(orch("run", "submit", "scn-c"))
    assert f"{aborted} ABORTED" in orch("gate", "answer", f"{aborted}:clarify", "--option", "C", "--key", engineer)
    stopped = _run_id(orch("run", "submit", "scn-c"))
    assert "AWAITING_APPROVAL" in orch("gate", "answer", f"{stopped}:clarify", "--text", "people", "--key", engineer)
    assert "clarification_limit_exceeded" in orch("gate", "answer", f"{stopped}:clarify", "--text", "again",
                                                  "--key", engineer)
    orch("evidence", "export", aborted)
    index = (orch.root / "evidence" / "index.md").read_text()
    assert aborted in index and stopped in index and "SAFE_STOPPED" in index
