"""Lean traceability check (CI): `python tools/trace_check.py`.

1. Every requirement ID in docs/scope/lean-slice.md section 1 (built scope) is claimed by a module's
   `Satisfies:` line or named in a test (`Verifies:` docstring or comment).
2. Every source module declares `Satisfies:` (package __init__ files excepted).
3. Scenarios are consistent: registry -> workflow -> agents and policy checks; change-set manifests
   carry the provenance label, their hashes match the patches, and their new tests are in tests.patch.
Exit code 1 on any gap. This checks requirement -> module/test links; it does not prove behavior.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orchestrator.agents.deterministic import AGENTS  # noqa: E402
from orchestrator.agents.scenario import PROVENANCE, sha256_lf  # noqa: E402
from orchestrator.graph import load_workflow  # noqa: E402
from orchestrator.policy import load_policy  # noqa: E402

ID = re.compile(r"\b((?:FR|NFR)-[A-Z]{3}|PVT|SC)-(\d{3})(?:\.\.(\d{3}))?\b")


def ids_in(text: str) -> set[str]:
    out = set()
    for prefix, start, end in ID.findall(text):
        for n in range(int(start), int(end or start) + 1):
            out.add(f"{prefix}-{n:03d}")
    return out


def built_scope_ids(root: Path) -> set[str]:
    text = (root / "docs" / "scope" / "lean-slice.md").read_text(encoding="utf-8")
    return ids_in(text.split("## 1. Built", 1)[1].split("## 2.", 1)[0])


def check(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    sources = [p for p in (root / "src").rglob("*.py") if p.name != "__init__.py"]
    claimed: set[str] = set()
    for path in sources:
        text = path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if "Satisfies:" in line]
        if not lines:
            problems.append(f"module without 'Satisfies:': {path.relative_to(root).as_posix()}")
        # a Satisfies line may wrap; take the docstring paragraph that starts with it
        for match in re.finditer(r"Satisfies:(.*?)(?:\n\s*\n|\"\"\")", text, re.S):
            claimed |= ids_in(match.group(1))
    tested: set[str] = set()
    for path in (root / "tests").rglob("*.py"):
        tested |= ids_in(path.read_text(encoding="utf-8"))
    for rid in sorted(built_scope_ids(root) - claimed - tested):
        problems.append(f"built-scope requirement not traced to a module or test: {rid}")

    policy = load_policy(root / "policy" / "policy-set.yaml")
    registry = yaml.safe_load((root / "scenarios" / "registry.yaml").read_text(encoding="utf-8"))
    for name, entry in registry.items():
        wf_path = root / "scenarios" / entry["workflow"] / "workflow.yaml"
        if not wf_path.exists():
            problems.append(f"{name}: workflow file missing ({wf_path.relative_to(root).as_posix()})")
            continue
        wf = load_workflow(wf_path)
        for node in wf.nodes.values():
            for agent in filter(None, [node.agent, node.fallback and node.fallback.agent,
                                       node.compensate and node.compensate.agent]):
                if agent not in AGENTS:
                    problems.append(f"{name}: node {node.id} uses unknown agent '{agent}'")
            for cid in node.policy_checks:
                if cid not in policy.checks:
                    problems.append(f"{name}: node {node.id} uses unknown policy check '{cid}'")
    for manifest_path in sorted((root / "scenarios").rglob("manifest.yaml")):
        cs = manifest_path.parent
        rel = cs.relative_to(root).as_posix()
        m = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if m.get("provenance") != PROVENANCE:
            problems.append(f"{rel}: provenance label missing or altered")
        actual = {"tests_patch": sha256_lf(cs / m["tests_patch"]), "impl_patch": sha256_lf(cs / m["impl_patch"])}
        if actual != m.get("sha256"):
            problems.append(f"{rel}: patch hashes differ from the manifest")
        tests_patch = (cs / m["tests_patch"]).read_text(encoding="utf-8")
        for test in m.get("new_tests", []):
            if f"+++ b/{test}" not in tests_patch:
                problems.append(f"{rel}: new test {test} is not in tests.patch")
    return problems


if __name__ == "__main__":
    found = check()
    for line in found:
        print(f"TRACE GAP: {line}")
    print(f"traceability check: {'FAIL' if found else 'PASS'} ({len(found)} gap(s))")
    sys.exit(1 if found else 0)
