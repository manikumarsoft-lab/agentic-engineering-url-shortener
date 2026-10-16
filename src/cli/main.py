"""`orch`: drive workflow runs, decide gates, inspect audit and metrics, serve the shortener.

Paths come from the environment: ORCH_ROOT (repository root: scenarios/, policy/, the baseline
copied into isolated workspaces; default: this checkout), ORCH_HOME (runtime data, default
<root>/var), ORCH_WORKFLOWS (extra workflow YAML directory, default <root>/workflows), ORCH_POLICY
(policy set, default <root>/policy/policy-set.yaml), ORCH_EVIDENCE (evidence output, default
<root>/evidence). Keys are passed with --key or ORCH_KEY and are never written to disk.

Satisfies: FR-ORC-001, FR-ORC-024, FR-GOV-003, FR-OBS-005, NFR-RUN-001 (CLI interface; A-011).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Annotated, Optional

import typer
import yaml

from orchestrator import audit, changesets, evidence, keys, security_scan
from orchestrator.engine import AuthError, Engine, EngineError
from orchestrator.graph import load_workflow
from orchestrator.metrics import run_metrics
from orchestrator.policy import load_policy
from orchestrator.store import Store

ROOT = Path(__file__).resolve().parents[2]

app = typer.Typer(no_args_is_help=True, help="Agentic SDLC orchestrator (lean slice).")
keys_app = typer.Typer(no_args_is_help=True, help="Manage API keys.")
run_app = typer.Typer(no_args_is_help=True, help="Submit, watch and resume workflow runs.")
gate_app = typer.Typer(no_args_is_help=True, help="List and decide human gates.")
audit_app = typer.Typer(no_args_is_help=True, help="Show and verify the audit trail.")
exception_app = typer.Typer(no_args_is_help=True, help="Request and approve policy exceptions.")
changeset_app = typer.Typer(no_args_is_help=True, help="Lock reviewed change sets (human approver).")
evidence_app = typer.Typer(no_args_is_help=True, help="Export run evidence.")
advisory_app = typer.Typer(no_args_is_help=True, help="Dependency advisory snapshot (pip-audit).")
release_app = typer.Typer(no_args_is_help=True, help="Repository release checks.")
for sub, name in ((keys_app, "keys"), (run_app, "run"), (gate_app, "gate"), (audit_app, "audit"),
                  (exception_app, "exception"), (changeset_app, "changeset"), (evidence_app, "evidence"),
                  (advisory_app, "advisory"), (release_app, "release")):
    app.add_typer(sub, name=name)

KeyOpt = Annotated[Optional[str], typer.Option("--key", envvar="ORCH_KEY", help="API key (sk_...)")]
ReasonOpt = Annotated[str, typer.Option("--reason", help="Rationale recorded with the decision")]


def _root() -> Path:
    return Path(os.environ.get("ORCH_ROOT", ROOT))


def _home() -> Path:
    return Path(os.environ.get("ORCH_HOME", _root() / "var"))


def _store() -> Store:
    return Store(_home() / "orchestrator.db")


def _engine(store: Store, workflow: str) -> Engine:
    """Scenario workflows live in <root>/scenarios/<name>/workflow.yaml; others in ORCH_WORKFLOWS."""
    wf_dir = Path(os.environ.get("ORCH_WORKFLOWS", _root() / "workflows"))
    for path in (_root() / "scenarios" / workflow / "workflow.yaml", wf_dir / f"{workflow}.yaml"):
        if path.exists():
            break
    else:
        raise typer.BadParameter(f"no workflow '{workflow}' in {_root() / 'scenarios'} or {wf_dir}")
    policy_path = Path(os.environ.get("ORCH_POLICY", _root() / "policy" / "policy-set.yaml"))
    policy = load_policy(policy_path) if policy_path.exists() else None
    wf = load_workflow(path)
    return Engine(store, wf, policy, var_dir=_home(), source_dir=_root() if wf.workspace_include else None)


def _run_engine(store: Store, run_id: str) -> Engine:
    try:
        return _engine(store, store.run(run_id)["workflow"])
    except KeyError:
        raise typer.BadParameter(f"unknown run '{run_id}'") from None


def _refused(err: Exception) -> typer.Exit:
    typer.secho(f"refused: {err}", err=True, fg=typer.colors.RED)
    return typer.Exit(code=2)


def _print_run(store: Store, run_id: str) -> None:
    run = store.run(run_id)
    reason = f" ({run['reason']})" if run["reason"] else ""
    typer.echo(f"{run_id} {run['state']}{reason}  workflow={run['workflow']} v{run['workflow_version']}"
               f" policy={run['policy_version']}")
    for nid, row in store.nodes(run_id).items():
        extra = f" error={row['last_error']}" if row["last_error"] else ""
        typer.echo(f"  {nid:<24} {row['state']:<18} attempts={row['attempts']}{extra}")


# ---- keys -------------------------------------------------------------------------------------
@keys_app.command("create")
def keys_create(role: Annotated[str, typer.Option("--role")], label: str = "") -> None:
    """Create a key. The secret is printed once and never stored in plain text."""
    try:
        secret = keys.create_key(_store(), role, ts=time.time(), label=label)
    except ValueError as err:
        raise typer.BadParameter(str(err)) from None
    typer.echo(secret)
    typer.secho("Shown once. Keep it outside the repository.", err=True, fg=typer.colors.YELLOW)


# ---- runs -------------------------------------------------------------------------------------
@run_app.command("submit")
def run_submit(scenario: str,
               fact: Annotated[Optional[list[str]], typer.Option("--fact", help="key=value (JSON value)")] = None,
               ) -> None:
    """Create a run of a scenario (scenarios/registry.yaml) or workflow and execute it until it
    needs a human or finishes."""
    registry_path = _root() / "scenarios" / "registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {}
    entry = (registry or {}).get(scenario, {"workflow": scenario})
    facts = dict(entry.get("facts", {}))
    for item in fact or []:
        k, _, v = item.partition("=")
        try:
            facts[k] = json.loads(v)
        except json.JSONDecodeError:
            facts[k] = v
    store = _store()
    engine = _engine(store, entry["workflow"])
    run_id = engine.submit(facts, labels=tuple(entry.get("labels", ("demonstration",))))
    engine.run(run_id)
    _print_run(store, run_id)


@run_app.command("status")
def run_status(run_id: str) -> None:
    store = _store()
    _run_engine(store, run_id)
    _print_run(store, run_id)


@run_app.command("watch")
def run_watch(run_id: str) -> None:
    """Drive the run step by step, printing every node state change until it blocks or ends."""
    store = _store()
    engine = _run_engine(store, run_id)
    seen = {nid: row["state"] for nid, row in store.nodes(run_id).items()}
    while True:
        progressed = engine.step(run_id)
        for nid, row in store.nodes(run_id).items():
            if seen[nid] != row["state"]:
                typer.echo(f"{nid}: {seen[nid]} -> {row['state']}")
                seen[nid] = row["state"]
        if not progressed:
            break
    _print_run(store, run_id)


@run_app.command("resume")
def run_resume(run_id: str, key: KeyOpt = None, reason: ReasonOpt = "") -> None:
    """Resume a SAFE_STOPPED run (approver key)."""
    store = _store()
    engine = _run_engine(store, run_id)
    try:
        engine.resume(run_id, key, reason)
    except (AuthError, EngineError) as err:
        raise _refused(err) from None
    engine.run(run_id)
    _print_run(store, run_id)


@run_app.command("recover")
def run_recover(workflow: str) -> None:
    """After an engine crash: mark runs with interrupted attempts SAFE_STOPPED."""
    for run_id in _engine(_store(), workflow).recover():
        typer.echo(f"{run_id} SAFE_STOPPED (interrupted)")


# ---- gates ------------------------------------------------------------------------------------
def _split(gate_id: str) -> tuple[str, str]:
    run_id, sep, node_id = gate_id.partition(":")
    if not sep:
        raise typer.BadParameter("gate id must be <run_id>:<node_id>")
    return run_id, node_id


@gate_app.command("list")
def gate_list() -> None:
    rows = _store().conn.execute(
        "SELECT n.run_id, n.node_id, n.deadline, n.escalated FROM nodes n JOIN runs r USING (run_id) "
        "WHERE n.state = 'AWAITING_APPROVAL' AND r.state NOT IN ('COMPLETED','FAILED','ABORTED') "
        "ORDER BY n.run_id, n.node_id").fetchall()
    for r in rows:
        flag = " escalated" if r["escalated"] else ""
        typer.echo(f"{r['run_id']}:{r['node_id']}{flag}")
    if not rows:
        typer.echo("no open gates")


@gate_app.command("show")
def gate_show(gate_id: str) -> None:
    run_id, node_id = _split(gate_id)
    store = _store()
    engine = _run_engine(store, run_id)
    node, row = engine.wf.nodes[node_id], store.nodes(run_id)[node_id]
    roles = ["release-owner"] if row["escalated"] else list(node.gate.roles) if node.gate else []
    bound = json.loads(row["bound"] or "{}")
    contents = {name: (store.artifact(run_id, name) or (0, None))[1] for name in bound}
    typer.echo(json.dumps({
        "gate": gate_id, "kind": node.gate.kind if node.gate else None, "state": row["state"],
        "required_roles": roles, "escalated": bool(row["escalated"]),
        "options": node.gate.options if node.gate else {}, "bound_artifacts": bound,
        "deadline": row["deadline"], "rework_cycles": row["rework"], "artifacts": contents},
        indent=2, default=str))


def _decide(gate_id: str, key: Optional[str], choice: str, reason: str, **answer: Optional[str]) -> None:
    run_id, node_id = _split(gate_id)
    store = _store()
    engine = _run_engine(store, run_id)
    try:
        engine.decide(run_id, node_id, key, choice, reason, **answer)
    except (AuthError, EngineError) as err:
        raise _refused(err) from None
    engine.run(run_id)
    _print_run(store, run_id)


@gate_app.command("approve")
def gate_approve(gate_id: str, key: KeyOpt = None, reason: ReasonOpt = "") -> None:
    _decide(gate_id, key, "approve", reason)


@gate_app.command("reject")
def gate_reject(gate_id: str, key: KeyOpt = None, reason: ReasonOpt = "",
                rework: Annotated[bool, typer.Option("--rework", help="Re-run the producing stage")] = False,
                ) -> None:
    """Reject: terminate the run (default) or send the producing stage back for rework."""
    _decide(gate_id, key, "reject_rework" if rework else "reject_terminate", reason)


@gate_app.command("escalate")
def gate_escalate(gate_id: str, key: KeyOpt = None, reason: ReasonOpt = "") -> None:
    """Escalate: the gate stays blocking and the next decision needs a release-owner key."""
    _decide(gate_id, key, "escalate", reason)


@gate_app.command("answer")
def gate_answer(gate_id: str, key: KeyOpt = None, reason: ReasonOpt = "",
                option: Annotated[Optional[str], typer.Option("--option", help="Offered option id")] = None,
                text: Annotated[Optional[str], typer.Option("--text", help="Free text (reopens the gate)")] = None,
                ) -> None:
    """Answer a clarification gate with an offered option; free text is recorded but never interpreted."""
    _decide(gate_id, key, "answer", reason, option=option, text=text)


# ---- exceptions, change sets and evidence -----------------------------------------------------
@exception_app.command("request")
def exception_request(run_id: str, check_id: str, key: KeyOpt = None, reason: ReasonOpt = "",
                      control: Annotated[str, typer.Option("--control", help="Compensating control")] = "",
                      ) -> None:
    store = _store()
    try:
        exception_id = _run_engine(store, run_id).request_exception(run_id, check_id, key, reason, control)
    except (AuthError, EngineError) as err:
        raise _refused(err) from None
    typer.echo(exception_id)


@exception_app.command("approve")
def exception_approve(run_id: str, exception_id: str, key: KeyOpt = None, reason: ReasonOpt = "") -> None:
    store = _store()
    try:
        _run_engine(store, run_id).approve_exception(run_id, exception_id, key, reason)
    except (AuthError, EngineError) as err:
        raise _refused(err) from None
    typer.echo(f"{exception_id} APPROVED")


@changeset_app.command("lock")
def changeset_lock(path: str, key: KeyOpt = None) -> None:
    """Record the reviewed patch hashes in scenarios/changesets.lock.yaml (human approver key)."""
    principal = keys.resolve(_store(), key)
    if principal is None:
        raise _refused(ValueError("unknown or invalid key"))
    rel = Path(path).as_posix().rstrip("/")
    try:
        entry = changesets.lock(_root(), rel, principal)
    except (changesets.LockError, FileNotFoundError) as err:
        raise _refused(err) from None
    typer.echo(f"locked {rel}: tests {entry['sha256']['tests_patch'][:12]} impl {entry['sha256']['impl_patch'][:12]}")


@evidence_app.command("export")
def evidence_export(run_id: str, out: Annotated[Optional[Path], typer.Option("--out")] = None) -> None:
    """Write evidence/<run_id>/ and refresh evidence/index.md (lists every run)."""
    target = out or Path(os.environ.get("ORCH_EVIDENCE", _root() / "evidence"))
    try:
        path = evidence.export(_store(), run_id, target)
    except (evidence.EvidenceError, KeyError) as err:
        raise _refused(err) from None
    typer.echo(f"wrote {path}")


@advisory_app.command("snapshot")
def advisory_snapshot() -> None:
    """Run pip-audit live over requirements.lock and write policy/advisory-snapshot.json.
    The new hash must then be pinned in policy/policy-set.yaml (a reviewed policy change)."""
    try:
        path, digest = security_scan.make_snapshot(_root())
    except security_scan.ScanUnavailable as err:
        raise _refused(err) from None
    typer.echo(f"wrote {path}\npin in policy/policy-set.yaml -> advisory_snapshot.sha256: {digest}")


@release_app.command("check")
def release_check(out: Annotated[Optional[Path], typer.Option("--out", help="Write the report as JSON")] = None,
                  ) -> None:
    """Repository release check: live pip-audit, secret scan, traceability. Exit 1 on any FAIL."""
    root = _root()
    report: dict[str, dict] = {}
    try:
        audit_result = security_scan.run_pip_audit(root / security_scan.LOCK_REL)
        report["SEC-003 dependency audit (live pip-audit)"] = {
            "outcome": "PASS" if not audit_result["vulnerabilities"] else "FAIL", **audit_result}
    except security_scan.ScanUnavailable as err:
        report["SEC-003 dependency audit (live pip-audit)"] = {"outcome": "FAIL", "reason": str(err)}
    secrets = security_scan.secret_scan(root, security_scan.repo_files(root))
    report["SEC-004 secret scan (repository)"] = {"outcome": "PASS" if secrets["clean"] else "FAIL", **secrets}
    trace = subprocess.run([sys.executable, str(root / "tools" / "trace_check.py")], cwd=root,
                           capture_output=True, text=True)
    report["traceability check"] = {"outcome": "PASS" if trace.returncode == 0 else "FAIL",
                                    "output": trace.stdout.strip().splitlines()}
    for name, result in report.items():
        typer.echo(f"{result['outcome']:<5} {name}")
        for finding in result.get("findings", []) + result.get("vulnerabilities", []):
            typer.echo(f"      {finding}")
    if out:
        out.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    if any(r["outcome"] != "PASS" for r in report.values()):
        raise typer.Exit(code=1)


# ---- audit and metrics ------------------------------------------------------------------------
@audit_app.command("show")
def audit_show(run_id: str) -> None:
    for e in audit.events(_store().conn, run_id):
        who = f"{e['actor_type']}:{e['actor_id']}" if e["actor_id"] else e["actor_type"]
        detail = " ".join(x for x in (e["target"], e["result"], e["reason"]) if x)
        typer.echo(f"{e['seq']:>4} {e['action']:<24} {who:<24} {detail}")


@audit_app.command("verify")
def audit_verify(run_id: str) -> None:
    valid, bad = audit.verify_chain(_store().conn, run_id)
    if not valid:
        typer.secho(f"INVALID: hash chain broken at seq {bad}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    typer.echo("valid")


@app.command("metrics")
def metrics(run_id: str) -> None:
    typer.echo(json.dumps(run_metrics(_store(), run_id), indent=2))


# ---- shortener --------------------------------------------------------------------------------
@app.command("serve")
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the URL shortener (DB under ORCH_HOME; accepts keys created with `orch keys create`)."""
    import uvicorn

    from shortener.app import create_app
    from shortener.config import Settings

    os.environ.setdefault("ORCH_HOME", str(_home()))
    uvicorn.run(create_app(Settings.from_env()), host=host, port=port, log_level="warning")


if __name__ == "__main__":
    app()
