"""Deterministic, rule-based scenario agents (no AI at run time; HD-001, FR-ORC-029).

Each agent reads only its declared inputs, the run's isolated workspace and the repository's
scenario files. Change sets are applied, never generated: the agents verify the human lock,
apply the test patch, record the failing (red) result, apply the implementation patch and run
the new tests plus the full shortener regression suite (green).
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml

from orchestrator.agents.base import AgentError

Ctx = dict[str, Any]
PROVENANCE = ("Authored with AI assistance (Claude Code) during development; reviewed and locked by "
              "the human owner (Mani Kumar Vadugu)")
CONTRACT_REL = "specs/001-agentic-sdlc-url-shortener/contracts/shortener-api.openapi.yaml"
LOCK_REL = "scenarios/changesets.lock.yaml"

UNCLEAR_TERMS = ("who", "track", "etc", "some", "various", "fast", "user-friendly", "appropriate")
PERSONAL_DATA_TERMS = ("track who", "who clicks", "ip address", "user agent", "user-agent",
                       "identify visitor", "visitor identity", "cookie", "device id", "geolocation")
EXCLUDED_CAPABILITIES = ("web ui", "billing", "qr code", "bulk import", "referrer breakdown",
                         "unique visitor")
OBSERVABLE = re.compile(r"\b[1-5]\d\d\b|\breturns?\b|\brejects?\b|\bresponds?\b|\bunchanged\b|\bredirects?\b")
PII_CODE = re.compile(r"client\.host|remote_addr|user[_-]agent|x-forwarded-for|ip_address", re.I)


# ---- helpers ------------------------------------------------------------------------------------
def _root(ctx: Ctx) -> Path:
    if not ctx.get("repo_root"):
        raise AgentError("invalid_input", "the run has no repository root")
    return Path(ctx["repo_root"])


def _lf(path: Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(_lf(path).encode("utf-8")).hexdigest()


def parse_requirement(text: str) -> dict[str, Any]:
    title, meta, sections, current = "", {}, {}, None
    for line in text.replace("\r\n", "\n").split("\n"):
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("## "):
            current = line[3:].strip().lower()
            sections[current] = []
        elif current is None and re.match(r"^[a-z_]+:\s", line):
            key, _, value = line.partition(":")
            meta[key] = value.strip()
        elif current is not None and line.strip():
            sections[current].append(line.strip())
    bullets = lambda name: [b[2:].strip() for b in sections.get(name, []) if b.startswith("- ")]  # noqa: E731
    acs = []
    for i, text_ in enumerate(bullets("acceptance criteria"), start=1):
        match = re.match(r"^(AC\d+):\s*(.*)$", text_)
        acs.append({"id": match.group(1) if match else f"AC{i}", "text": match.group(2) if match else text_})
    plain = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
    intent = " ".join(sections.get("intent", [])) or (" ".join(plain) if not sections else "")
    return {"title": title, "change_kind": meta.get("change_kind", "unknown"), "intent": intent,
            "acceptance_criteria": acs, "constraints": bullets("constraints")}


def _changeset(ctx: Ctx) -> tuple[Path, str, dict[str, Any]]:
    facts, params = ctx["facts"], ctx["params"]
    rel = facts.get("selected_change_set")
    if not rel and params.get("change_sets"):
        rel = params["change_sets"].get(facts.get("variant", "normal"))
    rel = rel or params.get("change_set")
    if not rel:
        raise AgentError("no_approved_change_set", "no change set is selected for this run")
    path = _root(ctx) / rel
    if not (path / "manifest.yaml").exists():
        raise AgentError("no_approved_change_set", f"{rel} has no manifest")
    return path, rel, yaml.safe_load((path / "manifest.yaml").read_text(encoding="utf-8"))


def _verify_lock(ctx: Ctx, path: Path, rel: str, manifest: dict[str, Any]) -> dict[str, str]:
    """CHG-001 (lean): patches must match the hashes the human owner locked."""
    if manifest.get("provenance") != PROVENANCE:
        raise AgentError("integrity_mismatch", "manifest provenance label is missing or altered")
    lock_path = _root(ctx) / ctx["params"].get("lock", LOCK_REL)
    lock = yaml.safe_load(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}
    entry = (lock or {}).get("change_sets", {}).get(rel)
    if not entry:
        raise AgentError("integrity_mismatch", f"{rel} is not locked by the human owner",
                         {"lock_file": str(lock_path)})
    actual = {name: sha256_lf(path / manifest[key]) for key, name in
              (("tests_patch", "tests_patch"), ("impl_patch", "impl_patch"))}
    if actual != entry["sha256"]:
        raise AgentError("integrity_mismatch", f"{rel} differs from the locked version",
                         {"locked": entry["sha256"], "actual": actual})
    return {"locked_by": entry.get("locked_by", ""), "locked_at": entry.get("locked_at", "")}


def touched_files(patch_text: str) -> list[str]:
    files = []
    for line in patch_text.splitlines():
        if line.startswith("+++ b/"):
            files.append(line[6:].strip())
    return sorted(set(files))


def _apply_patch(ctx: Ctx, path: Path, name: str) -> list[str]:
    ws = Path(ctx["workspace"])
    if not ws.exists():
        raise AgentError("invalid_input", "isolated workspace is missing")
    text = _lf(path / name)
    staged = Path(ctx["var_dir"]) / "patches" / ctx["run_id"] / name
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(text, encoding="utf-8", newline="\n")
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(ws.parent)}  # never touch the repository
    for args in (["git", "apply", "--check", str(staged)], ["git", "apply", str(staged)]):
        proc = subprocess.run(args, cwd=ws, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            raise AgentError("patch_does_not_apply", proc.stderr.strip()[:500], {"patch": name})
    return touched_files(text)


def _pytest(ctx: Ctx, targets: list[str], label: str) -> dict[str, Any]:
    ws = Path(ctx["workspace"])
    junit = Path(ctx["var_dir"]) / "junit" / ctx["run_id"] / f"{label}.xml"
    junit.parent.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST_", "ORCH_"))}
    env["PYTHONPATH"] = str(ws / "src")
    cmd = [sys.executable, "-m", "pytest", *targets, "-q", "-p", "no:cacheprovider",
           f"--junitxml={junit}"]
    proc = subprocess.run(cmd, cwd=ws, env=env, capture_output=True, text=True, timeout=600)
    if not junit.exists():
        raise AgentError("io_error", "pytest produced no report", {"stderr": proc.stderr[-500:]})
    suites = ET.parse(junit).getroot()
    suites = [suites] if suites.tag == "testsuite" else list(suites)
    failed = [f"{case.get('classname')}::{case.get('name')}" for s in suites for case in s.iter("testcase")
              if case.find("failure") is not None or case.find("error") is not None]
    total = lambda attr: sum(int(s.get(attr, 0)) for s in suites)  # noqa: E731
    return {"phase": label, "command": "python -m pytest " + " ".join(targets), "tests": total("tests"),
            "failures": total("failures"), "errors": total("errors"), "skipped": total("skipped"),
            "failed_tests": failed, "exit_code": proc.returncode}


# ---- requirement agents -------------------------------------------------------------------------
def ingest(ctx: Ctx) -> dict:
    path = _root(ctx) / ctx["params"]["requirement"]
    text = _lf(path)
    return {"artifacts": {"requirement": {"source": ctx["params"]["requirement"], "text": text,
                                          "sha256": hashlib.sha256(text.encode()).hexdigest()}}}


def normalize(ctx: Ctx) -> dict:
    req = ctx["inputs"]["requirement"]
    parsed = parse_requirement(req["text"])
    for i, ac in enumerate(parsed["acceptance_criteria"], start=1):
        ac["rq_id"] = f"RQ-{i:03d}"
    return {"artifacts": {"normalized-requirement": {**parsed, "source": req["source"]}},
            "facts": {"change_kind": parsed["change_kind"]}}


def _words(text: str, terms: tuple[str, ...]) -> list[str]:
    return [t for t in terms if re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", text)]


def quality_check(ctx: Ctx) -> dict:
    """Five requirement-quality checks plus ambiguity classification (FR-ORC-003, SCN-C-AC1)."""
    req = ctx["inputs"]["normalized-requirement"]
    acs = req["acceptance_criteria"]
    body = " ".join([req["intent"], *(a["text"] for a in acs), *req["constraints"]]).lower()
    checks, items = [], []

    def check(name: str, ok: bool, rationale: str, classification: str | None = None,
              detail: str | None = None) -> None:
        checks.append({"check": name, "result": "PASS" if ok else "FAIL", "rationale": rationale})
        if not ok and classification:
            items.append({"classification": classification, "check": name,
                          "affected_text": req["intent"] or "(empty)", "detail": detail or rationale})

    check("completeness", bool(req["intent"]) and bool(acs),
          "intent and acceptance criteria present" if acs else "no acceptance criteria and no stated purpose",
          "missing_information")
    duplicates = len({a["text"] for a in acs}) != len(acs)
    check("consistency", not duplicates, "no duplicated or contradicting criteria" if not duplicates
          else "duplicated acceptance criteria", "internal_conflict")
    untestable = [a["id"] for a in acs if not OBSERVABLE.search(a["text"])]
    check("testability", bool(acs) and not untestable,
          "every criterion has an observable outcome" if acs and not untestable
          else f"criteria without an observable outcome: {untestable or 'none written'}", "missing_information")
    personal = _words(body, PERSONAL_DATA_TERMS)
    check("policy_conformance", not personal,
          "no personal-data capture requested (PRIV-001)" if not personal
          else f"requests visitor personal data ({', '.join(personal)}), conflicting with FR-SHR-012",
          "policy_conflict")
    excluded = _words(body, EXCLUDED_CAPABILITIES)
    check("architecture_boundary", not excluded, "within approved scope" if not excluded
          else f"requests excluded capabilities: {', '.join(excluded)}", "policy_conflict")
    for term in _words(body, UNCLEAR_TERMS):
        items.append({"classification": "unclear_term", "check": "terminology", "affected_text": req["intent"],
                      "detail": f"the term '{term}' has no testable meaning"})
    failed = [c for c in checks if c["result"] == "FAIL"]
    material = len(failed) + sum(1 for i in items if i["classification"] == "unclear_term")
    reason = ("all five requirement-quality checks passed; no clarification required" if not material
              else f"{material} material finding(s): clarification required")
    report = {"checks": checks, "items": items, "material_failures": material,
              "clarification_required": bool(material), "reason": reason}
    return {"artifacts": {"quality-report": report},
            "facts": {"clarification_needed": bool(material), "quality_reason": reason}}


def select_change_set(ctx: Ctx) -> dict:
    """Map the human's clarification answer to an approved change set (catalog keyed by option_id)."""
    answer = ctx["inputs"].get("clarification") or {}
    option = answer.get("option_id")
    catalog = yaml.safe_load((_root(ctx) / ctx["params"]["catalog"]).read_text(encoding="utf-8"))
    entry = (catalog.get("options") or {}).get(option)
    if not entry or not entry.get("change_set"):
        raise AgentError("no_approved_change_set", f"no approved change set for option '{option}'")
    refined = parse_requirement(_lf(_root(ctx) / entry["refined_requirement"]))
    for i, ac in enumerate(refined["acceptance_criteria"], start=1):
        ac["rq_id"] = f"RQ-{i:03d}"
    return {"artifacts": {
                "normalized-requirement": {**refined, "source": entry["refined_requirement"],
                                           "clarified_by_option": option},
                "change-set-selection": {"option_id": option, "change_set": entry["change_set"]}},
            "facts": {"selected_change_set": entry["change_set"], "change_kind": refined["change_kind"]}}


def decompose(ctx: Ctx) -> dict:
    req = ctx["inputs"]["normalized-requirement"]
    tasks, impl_ids = [], []
    for ac in req["acceptance_criteria"]:
        n = len(tasks) + 1
        tasks.append({"id": f"T{n}", "title": f"Write a failing test for {ac['id']}",
                      "requirement": ac["rq_id"], "acceptance": ac["text"], "depends_on": []})
        tasks.append({"id": f"T{n + 1}", "title": f"Implement {ac['id']}", "requirement": ac["rq_id"],
                      "acceptance": ac["text"], "depends_on": [f"T{n}"]})
        impl_ids.append(f"T{n + 1}")
    n = len(tasks) + 1
    tasks.append({"id": f"T{n}", "title": "Regenerate the OpenAPI contract", "depends_on": impl_ids})
    tasks.append({"id": f"T{n + 1}", "title": "Update documentation", "depends_on": [f"T{n}"]})
    return {"artifacts": {"task-plan": {"tasks": tasks, "ordering": [t["id"] for t in tasks]}}}


def impact_analysis(ctx: Ctx) -> dict:
    """Impact from the requirement and the baseline import graph only (plan §16.1 C2):
    the change set is never read here."""
    ws = Path(ctx["workspace"])
    req = ctx["inputs"]["normalized-requirement"]
    text = " ".join([req["intent"], *(a["text"] for a in req["acceptance_criteria"])])
    pkg = ws / "src" / "shortener"
    modules = {f"shortener.{p.stem}": p for p in pkg.glob("*.py") if p.stem != "__init__"}
    imports: dict[str, set[str]] = {}
    routes: dict[str, str] = {}
    for mod, path in modules.items():
        tree = ast.parse(_lf(path))
        deps = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "shortener":
                    deps.update(f"shortener.{a.name}" for a in node.names)
                elif node.module.startswith("shortener."):
                    deps.add(node.module)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in {"get", "post", "put", "delete", "patch"} and node.args \
                    and isinstance(node.args[0], ast.Constant) and str(node.args[0].value).startswith("/"):
                routes[f"{node.func.attr.upper()} {node.args[0].value}"] = mod
        imports[mod] = deps & set(modules)
    interfaces = sorted(r for r in routes if r in text)
    if not interfaces:
        raise AgentError("invalid_input", "the requirement names no existing interface")
    entry = {routes[i] for i in interfaces}
    impacted = entry | {d for m in entry for d in imports[m]} | {m for m, deps in imports.items() if deps & entry}
    tests = []
    for test in sorted((ws / "tests" / "shortener").glob("test_*.py")):
        src = _lf(test)
        if any(m in src for m in impacted) or any(i.split(" ", 1)[1] in src for i in interfaces):
            tests.append(test.relative_to(ws).as_posix())
    files = sorted(modules[m].relative_to(ws).as_posix() for m in impacted)
    risks = {"shortener.codes": "generated-code path must stay unchanged (random 7-character codes)",
             "shortener.store": "uniqueness, idempotency and transaction semantics of link creation",
             "shortener.validation": "URL validation rules must not change",
             "shortener.app": "public contract: additive minor version only; existing responses unchanged",
             "shortener.config": "configuration defaults must not change"}
    return {"artifacts": {"impact-analysis": {
        "method": "requirement text + baseline import graph (AST); change set not consulted",
        "inputs_used": ["normalized-requirement", "baseline source in the isolated workspace"],
        "interfaces": interfaces,
        "components": [{"module": m, "file": modules[m].relative_to(ws).as_posix(),
                        "reason": "defines the interface" if m in entry else "imported by or imports the entry module"}
                       for m in sorted(impacted)],
        "files": files, "tests": tests,
        "data_flows": [f"{i} -> {' -> '.join(sorted(imports[routes[i]]))}" for i in interfaces],
        "regression_risks": [risks[m] for m in sorted(impacted) if m in risks],
        "rollout_rollback": "applied only to an isolated workspace; rollback = discard the workspace; "
                            "contract change must be additive (minor version)",
        "requirement_links": [a["rq_id"] for a in req["acceptance_criteria"]]}}}


def design(ctx: Ctx) -> dict:
    req, plan = ctx["inputs"]["normalized-requirement"], ctx["inputs"]["task-plan"]
    impact = ctx["inputs"].get("impact-analysis")
    path, rel, manifest = _changeset(ctx)
    return {"artifacts": {"design": {
        "title": req["title"], "approach": manifest.get("summary"),
        "acceptance_criteria": req["acceptance_criteria"],
        "components": impact["files"] if impact else manifest.get("touched_files", []),
        "impact_analysis_used": bool(impact), "test_plan": manifest.get("new_tests", []),
        "regression_suite": "tests/shortener", "contract_version_after": manifest.get("contract_version_after"),
        "change_set": rel, "provenance": manifest.get("provenance"), "tasks": len(plan["tasks"])}}}


# ---- change application (test-first) ------------------------------------------------------------
def apply_tests(ctx: Ctx) -> dict:
    path, rel, manifest = _changeset(ctx)
    lock = _verify_lock(ctx, path, rel, manifest)
    touched = _apply_patch(ctx, path, manifest["tests_patch"])
    result = _pytest(ctx, manifest["new_tests"], "red")
    if result["failures"] == 0 and result["errors"] == 0:
        raise AgentError("tests_not_red", "new tests pass before the implementation exists", result)
    return {"artifacts": {"test-red": {**result, "change_set": rel, "touched_files": touched, "lock": lock}},
            "facts": {"test_first_red": True}}


def apply_impl(ctx: Ctx) -> dict:
    path, rel, manifest = _changeset(ctx)
    lock = _verify_lock(ctx, path, rel, manifest)
    touched = _apply_patch(ctx, path, manifest["impl_patch"])
    impact = ctx["inputs"].get("impact-analysis")
    scope = "not applicable (no impact analysis in this workflow)"
    if impact:
        allowed = set(impact["files"]) | {CONTRACT_REL}
        outside = [f for f in touched if f not in allowed and not f.startswith("tests/")]
        if outside:
            raise AgentError("undeclared_scope", "change touches components outside the approved impact analysis",
                             {"outside": outside})
        scope = "all touched files are within the approved impact analysis"
    return {"artifacts": {"change-application": {
        "change_set": rel, "touched_files": touched, "scope_check": scope, "lock": lock,
        "provenance": manifest["provenance"],
        "patch_sha256": {"tests": sha256_lf(path / manifest["tests_patch"]),
                         "impl": sha256_lf(path / manifest["impl_patch"])}}}}


def run_tests(ctx: Ctx) -> dict:
    _, rel, manifest = _changeset(ctx)
    result = _pytest(ctx, ["tests/shortener"], "green")
    result["new_tests"] = manifest["new_tests"]
    if result["failures"] or result["errors"]:
        raise AgentError("tests_failed", f"{result['failures']} failed, {result['errors']} errors", result)
    return {"artifacts": {"test-results": {**result, "change_set": rel}}, "facts": {"tests_passed": True}}


# ---- parallel branch agents ---------------------------------------------------------------------
def write_docs(ctx: Ctx) -> dict:
    d, results = ctx["inputs"]["design"], ctx["inputs"]["test-results"]
    ws = Path(ctx["workspace"])
    doc = ws / "docs" / "changes" / f"{ctx['run_id']}.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {d['title']}", "", d.get("approach") or "", "",
             f"Contract version after this change: {d.get('contract_version_after')}", "",
             "## Acceptance criteria", *[f"- {a['id']}: {a['text']}" for a in d["acceptance_criteria"]], "",
             "## Validation", f"- {results['tests']} tests executed, {results['failures']} failures"]
    doc.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"artifacts": {"docs": {"path": doc.relative_to(ws).as_posix(),
                                   "contract_version": d.get("contract_version_after")}}}


def _operations(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {f"{m.upper()} {p}": op for p, item in spec.get("paths", {}).items() for m, op in item.items()}


def _response_fields(spec: dict[str, Any], op: dict[str, Any]) -> set[str]:
    schema = op.get("responses", {}).get("200", {}).get("content", {}).get("application/json", {}).get("schema", {})
    ref = schema.get("$ref", "")
    return set(spec.get("components", {}).get("schemas", {}).get(ref.split("/")[-1], {}).get("properties", {}))


def threat_review(ctx: Ctx) -> dict:
    """STRIDE-lite review of the new interfaces against the baseline contract."""
    ws = Path(ctx["workspace"])
    before = yaml.safe_load(_lf(_root(ctx) / CONTRACT_REL))
    after = yaml.safe_load(_lf(ws / CONTRACT_REL))
    app_src = _lf(ws / "src" / "shortener" / "app.py")
    new_ops = sorted(set(_operations(after)) - set(_operations(before)))
    threats = [{"id": "TH-0", "category": "Denial of service", "severity": "low", "status": "accepted",
                "detail": "abuse volume on new operations: creation is rate limited; reads are an accepted risk"}]
    for op_id in new_ops:
        fields = _response_fields(after, _operations(after)[op_id])
        if "destination" in fields:
            owner_check = "creator_key_id" in app_src
            threats.append({"id": "TH-1", "category": "Information disclosure", "interface": op_id,
                            "severity": "high", "status": "mitigated" if owner_check else "open",
                            "detail": "any valid API key can read the destination and timestamps of any link"
                                      if not owner_check else "details limited to the creating key"})
    create = _operations(after).get("POST /api/v1/links", {})
    req_ref = create.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {}).get("$ref", "")
    if "alias" in after["components"]["schemas"].get(req_ref.split("/")[-1], {}).get("properties", {}):
        reserved = "RESERVED_ALIASES" in app_src
        threats.append({"id": "TH-2", "category": "Spoofing", "interface": "POST /api/v1/links",
                        "severity": "medium", "status": "mitigated" if reserved else "open",
                        "detail": "creator-chosen aliases could imitate service routes or other links; "
                                  "reserved words are blocked and conflicts never overwrite"})
    if PII_CODE.search(app_src) or PII_CODE.search(_lf(ws / "src" / "shortener" / "store.py")):
        threats.append({"id": "TH-3", "category": "Privacy", "severity": "high", "status": "open",
                        "detail": "code references client addresses or user agents"})
    open_high = sum(1 for t in threats if t["severity"] == "high" and t["status"] == "open")
    return {"artifacts": {"threat-review": {"new_operations": new_ops, "threats": threats,
                                            "open_high_threats": open_high}},
            "facts": {"open_high_threats": open_high}}


def validate_release(ctx: Ctx) -> dict:
    """Collect the facts the release policy checks evaluate (PRIV-001, SEC-002, REL-001)."""
    path, _, manifest = _changeset(ctx)
    added = [line for line in _lf(path / manifest["impl_patch"]).splitlines()
             if line.startswith("+") and not line.startswith("+++")]
    pii = sorted({m.group(0).lower() for line in added for m in PII_CODE.finditer(line)})
    results, threats = ctx["inputs"]["test-results"], ctx["inputs"]["threat-review"]
    return {"facts": {"captures_personal_data": bool(pii), "personal_data_markers": pii,
                      "open_high_threats": threats["open_high_threats"],
                      "tests_passed": results["failures"] == 0 and results["errors"] == 0}}


def release(ctx: Ctx) -> dict:
    ws = Path(ctx["workspace"])
    dest = Path(ctx["var_dir"]) / "releases" / ctx["run_id"]
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ws / "src" / "shortener", dest / "src" / "shortener",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (dest / "shortener-api.openapi.yaml").write_text(_lf(ws / CONTRACT_REL), encoding="utf-8")
    version = yaml.safe_load(_lf(ws / CONTRACT_REL))["info"]["version"]
    digest = hashlib.sha256("".join(sha256_lf(p) for p in sorted(dest.rglob("*.py"))).encode()).hexdigest()
    return {"artifacts": {"release": {"release_id": f"rel_{ctx['run_id'][4:]}", "path": str(dest),
                                      "contract_version": version, "sources_sha256": digest,
                                      "note": "local release snapshot; merging into the repository is a human action"}}}


def summarize(ctx: Ctx) -> dict:
    """Final engineering summary (FR-ORC-026) built from the run's own artifacts."""
    i, f = ctx["inputs"], ctx["facts"]
    red, green = i.get("test-red") or {}, i.get("test-results") or {}
    threats = (i.get("threat-review") or {}).get("threats", [])
    design_ = i.get("design") or {}
    return {"artifacts": {"engineering-summary": {
        "scenario": ctx["params"].get("scenario"),
        "plan_and_rationale": {"requirement": (i.get("normalized-requirement") or {}).get("title"),
                               "approach": design_.get("approach"),
                               "tasks": len((i.get("task-plan") or {}).get("tasks", [])),
                               "impact_analysis": bool(i.get("impact-analysis"))},
        "artifacts": sorted(k for k, v in i.items() if v),
        "risks": [f"{t['id']} {t['category']} ({t['severity']}, {t['status']})" for t in threats],
        "trade_offs": ["deterministic rule-based agents apply human-locked change sets instead of generating code",
                       "release is a local snapshot; merging into the repository stays a manual human action"],
        "validation_results": {"red": {k: red.get(k) for k in ("tests", "failures", "errors")},
                               "green": {k: green.get(k) for k in ("tests", "failures", "errors")},
                               "policy_facts": {k: f.get(k) for k in ("captures_personal_data",
                                                                      "open_high_threats", "tests_passed")}},
        "assumptions": ["change set applies to the current working-tree baseline"],
        "limitations": ["metrics are demonstration data", "see docs/scope/lean-slice.md section 2"]}}}


AGENTS = {fn.__name__: fn for fn in (ingest, normalize, quality_check, select_change_set, decompose,
                                       impact_analysis, design, apply_tests, apply_impl, run_tests,
                                       write_docs, threat_review, validate_release, release, summarize)}
