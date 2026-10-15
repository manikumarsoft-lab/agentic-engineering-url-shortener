"""`orch`: drive workflow runs, decide gates, inspect audit and metrics, serve the shortener.

Paths come from the environment: ORCH_HOME (runtime data, default ./var), ORCH_WORKFLOWS
(workflow YAML directory, default ./workflows), ORCH_POLICY (policy set, default
./policy/policy-set.yaml). Keys are passed with --key or ORCH_KEY and are never written to disk.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Annotated, Optional

import typer

from orchestrator import audit, keys
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
for sub, name in ((keys_app, "keys"), (run_app, "run"), (gate_app, "gate"), (audit_app, "audit")):
    app.add_typer(sub, name=name)

KeyOpt = Annotated[Optional[str], typer.Option("--key", envvar="ORCH_KEY", help="API key (sk_...)")]
ReasonOpt = Annotated[str, typer.Option("--reason", help="Rationale recorded with the decision")]


def _home() -> Path:
    return Path(os.environ.get("ORCH_HOME", ROOT / "var"))


def _store() -> Store:
    return Store(_home() / "orchestrator.db")


def _engine(store: Store, workflow: str) -> Engine:
    wf_dir = Path(os.environ.get("ORCH_WORKFLOWS", ROOT / "workflows"))
    path = wf_dir / f"{workflow}.yaml"
    if not path.exists():
        raise typer.BadParameter(f"no workflow '{workflow}' in {wf_dir}")
    policy_path = Path(os.environ.get("ORCH_POLICY", ROOT / "policy" / "policy-set.yaml"))
    policy = load_policy(policy_path) if policy_path.exists() else None
    return Engine(store, load_workflow(path), policy, var_dir=_home())


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
    """Create a run of a workflow and execute it until it needs a human or finishes."""
    facts = {}
    for item in fact or []:
        k, _, v = item.partition("=")
        try:
            facts[k] = json.loads(v)
        except json.JSONDecodeError:
            facts[k] = v
    store = _store()
    engine = _engine(store, scenario)
    run_id = engine.submit(facts)
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
    typer.echo(json.dumps({
        "gate": gate_id, "state": row["state"], "required_roles": roles,
        "escalated": bool(row["escalated"]), "bound_artifacts": json.loads(row["bound"] or "{}"),
        "deadline": row["deadline"], "rework_cycles": row["rework"]}, indent=2))


def _decide(gate_id: str, key: Optional[str], choice: str, reason: str) -> None:
    run_id, node_id = _split(gate_id)
    store = _store()
    engine = _run_engine(store, run_id)
    try:
        engine.decide(run_id, node_id, key, choice, reason)
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
