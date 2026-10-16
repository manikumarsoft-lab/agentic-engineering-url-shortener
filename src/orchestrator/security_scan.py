"""Dependency audit (pip-audit) and secret scanning.

Scenario runs never call the network: they evaluate SEC-003 against an advisory snapshot that a
real `pip-audit` run produced for `requirements.lock`, pinned by SHA-256 in the policy set.
`orch release check` runs pip-audit live. Satisfies: FR-GOV-012, NFR-SEC-002, PVT-012, plan §16.1 C5.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

LOCK_REL = "requirements.lock"
SNAPSHOT_REL = "policy/advisory-snapshot.json"
POLICY_REL = "policy/policy-set.yaml"
SECRET_RULES = {
    "orch-api-key": re.compile(r"sk_[0-9a-f]{12}\.[A-Za-z0-9_-]{32,}"),
    "aws-access-key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github-token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    "secret-assignment": re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{20,}['\"]"),
}
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".txt", ".cfg", ".ini", ".patch", ".lock", ""}


class ScanUnavailable(RuntimeError):
    """The scanner could not run; the outcome is FAIL, never PASS without evidence."""


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().decode("utf-8").replace("\r\n", "\n").encode()).hexdigest()


def secret_scan(root: Path, files: list[Path]) -> dict[str, Any]:
    """Regex secret scan. Findings record file, line and rule only, never the matched value."""
    findings, scanned = [], 0
    for path in files:
        if path.suffix not in TEXT_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rule, pattern in SECRET_RULES.items():
                if pattern.search(line):
                    findings.append({"file": path.relative_to(root).as_posix(), "line": lineno, "rule": rule})
    return {"tool": "regex secret scan", "files_scanned": scanned, "findings": findings, "clean": not findings}


def tree_files(root: Path, rels: list[str]) -> list[Path]:
    out: list[Path] = []
    for rel in rels:
        p = root / rel
        out.extend([p] if p.is_file() else sorted(f for f in p.rglob("*")
                                                  if f.is_file() and "__pycache__" not in f.parts))
    return out


def repo_files(root: Path) -> list[Path]:
    """Tracked plus untracked-but-not-ignored files; outside a git checkout, walk the tree."""
    proc = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root,
                          capture_output=True, text=True)
    if proc.returncode == 0:
        return [root / line for line in proc.stdout.splitlines() if line]
    skip = {".git", ".venv", "var", "__pycache__", ".pytest_cache"}
    return [p for p in root.rglob("*") if p.is_file() and not skip.intersection(p.relative_to(root).parts)]


def run_pip_audit(lock: Path) -> dict[str, Any]:
    """Run pip-audit (live advisory lookup) against the pinned requirements lock."""
    cmd = [sys.executable, "-m", "pip_audit", "-r", str(lock), "--no-deps", "--disable-pip",
           "--format", "json", "--progress-spinner", "off"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        report = json.loads(proc.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as err:
        raise ScanUnavailable(f"pip-audit did not produce a report: {type(err).__name__}") from None
    version = subprocess.run([sys.executable, "-m", "pip_audit", "--version"], capture_output=True,
                             text=True).stdout.strip()
    vulns = [{"name": d["name"], "version": d.get("version"), "id": v["id"],
              "fix_versions": v.get("fix_versions", [])}
             for d in report.get("dependencies", []) for v in d.get("vulns", [])]
    return {"tool": version or "pip-audit", "dependencies": len(report.get("dependencies", [])),
            "vulnerabilities": vulns}


def make_snapshot(root: Path) -> tuple[Path, str]:
    """Run pip-audit for real and store the result as the advisory snapshot. Returns (path, sha256)."""
    result = run_pip_audit(root / LOCK_REL)
    snapshot = {"generated_at": datetime.now(timezone.utc).isoformat(), "lock": LOCK_REL,
                "lock_sha256": sha256_lf(root / LOCK_REL), "result": result}
    path = root / SNAPSHOT_REL
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path, sha256_lf(path)


def check_snapshot(root: Path) -> dict[str, Any]:
    """SEC-003 for scenario runs: pinned snapshot intact, lock unchanged, zero known vulnerabilities."""
    pin = (yaml.safe_load((root / POLICY_REL).read_text(encoding="utf-8")) or {}).get("advisory_snapshot", {})
    path = root / pin.get("path", SNAPSHOT_REL)
    if not pin.get("sha256") or not path.exists():
        return {"ok": False, "reason": "no pinned advisory snapshot"}
    if sha256_lf(path) != pin["sha256"]:
        return {"ok": False, "reason": "advisory snapshot differs from the pinned hash"}
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    if snapshot["lock_sha256"] != sha256_lf(root / snapshot["lock"]):
        return {"ok": False, "reason": "requirements.lock changed since the snapshot; re-run the audit"}
    vulns = snapshot["result"]["vulnerabilities"]
    return {"ok": not vulns, "vulnerabilities": vulns, "snapshot_sha256": pin["sha256"],
            "generated_at": snapshot["generated_at"], "tool": snapshot["result"]["tool"],
            "reason": (f"{snapshot['result']['tool']} snapshot of {snapshot['generated_at']}: "
                       f"{snapshot['result']['dependencies']} pinned dependencies, {len(vulns)} known vulnerabilities")}
