"""Dependency audit snapshot and secret scan.

Verifies: FR-GOV-012, NFR-SEC-002, PVT-012 (SEC-003 never PASS without evidence; secrets detected).
"""
import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.main import app
from orchestrator import security_scan

ROOT = Path(__file__).resolve().parents[2]


def test_secret_scan_finds_keys_without_recording_them(tmp_path):
    aws = "AKIA" + "ABCDEFGHIJKLMNOP"
    orch_key = "sk_" + "0123456789ab." + "x" * 40
    (tmp_path / "leak.py").write_text(f"KEY = '{aws}'\nother = '{orch_key}'\nok = 1\n", encoding="utf-8")
    header = "-----BEGIN RSA " + "PRIVATE KEY-----"  # split so this file itself stays clean
    (tmp_path / "id_rsa.txt").write_text(header + "\n", encoding="utf-8")
    (tmp_path / "clean.md").write_text("nothing to see\n", encoding="utf-8")
    result = security_scan.secret_scan(tmp_path, security_scan.tree_files(tmp_path, ["."]))
    rules = {(f["file"], f["rule"]) for f in result["findings"]}
    assert ("leak.py", "aws-access-key") in rules and ("leak.py", "orch-api-key") in rules
    assert ("id_rsa.txt", "private-key") in rules and not result["clean"]
    assert aws not in json.dumps(result) and orch_key not in json.dumps(result)


@pytest.fixture
def repo(tmp_path):
    for rel in ("policy", "requirements.lock"):
        src = ROOT / rel
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, tmp_path / rel)
    return tmp_path


def test_pinned_snapshot_passes_and_records_its_evidence(repo):
    result = security_scan.check_snapshot(repo)
    assert result["ok"] and "pip-audit" in result["reason"] and "0 known vulnerabilities" in result["reason"]


def test_tampered_snapshot_or_changed_lock_fails(repo):
    snap = repo / security_scan.SNAPSHOT_REL
    snap.write_text(snap.read_text(encoding="utf-8").replace('"vulnerabilities": []', '"vulnerabilities": [ ]'),
                    encoding="utf-8")
    assert security_scan.check_snapshot(repo) == {"ok": False,
                                                  "reason": "advisory snapshot differs from the pinned hash"}
    shutil.copy2(ROOT / security_scan.SNAPSHOT_REL, snap)
    with (repo / "requirements.lock").open("a", encoding="utf-8") as fh:
        fh.write("evil==1.0\n")
    assert "requirements.lock changed" in security_scan.check_snapshot(repo)["reason"]


def test_snapshot_with_a_vulnerability_fails_even_when_pinned(repo):
    snap = repo / security_scan.SNAPSHOT_REL
    data = json.loads(snap.read_text(encoding="utf-8"))
    data["result"]["vulnerabilities"] = [{"name": "demo", "version": "1.0", "id": "PYSEC-0000-0", "fix_versions": []}]
    snap.write_text(json.dumps(data), encoding="utf-8")
    policy = repo / "policy" / "policy-set.yaml"
    text = policy.read_text(encoding="utf-8")
    old_pin = text.split("sha256: ", 1)[1].split()[0]
    policy.write_text(text.replace(old_pin, security_scan.sha256_lf(snap)), encoding="utf-8")
    result = security_scan.check_snapshot(repo)
    assert result["ok"] is False and len(result["vulnerabilities"]) == 1


def test_release_check_fails_on_a_live_vulnerability(monkeypatch):
    monkeypatch.delenv("ORCH_ROOT", raising=False)
    fake = {"tool": "pip-audit (fake)", "dependencies": 49,
            "vulnerabilities": [{"name": "demo", "version": "1.0", "id": "GHSA-demo", "fix_versions": ["1.1"]}]}
    monkeypatch.setattr(security_scan, "run_pip_audit", lambda lock: fake)
    result = CliRunner().invoke(app, ["release", "check"])
    assert result.exit_code == 1 and "FAIL  SEC-003" in result.output and "GHSA-demo" in result.output
    monkeypatch.setattr(security_scan, "run_pip_audit", lambda lock: {**fake, "vulnerabilities": []})
    result = CliRunner().invoke(app, ["release", "check"])
    assert result.exit_code == 0, result.output
    assert "PASS  SEC-004 secret scan" in result.output and "PASS  traceability check" in result.output
