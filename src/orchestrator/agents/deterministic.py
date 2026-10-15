"""Deterministic, rule-based agents (the only agent mode; HD-001, FR-ORC-029).

Generic building blocks used by workflows and tests. Scenario agents are added on top of these.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from orchestrator.agents.base import AgentError

Ctx = dict[str, Any]


def noop(ctx: Ctx) -> dict:
    return {}


def emit(ctx: Ctx) -> dict:
    """Emit fixed artifacts and facts from the node's params."""
    p = ctx["params"]
    return {"artifacts": p.get("artifacts", {}), "facts": p.get("facts", {})}


def transform(ctx: Ctx) -> dict:
    """Derive artifact `to` from the current version of input artifact `from`."""
    p = ctx["params"]
    return {"artifacts": {p["to"]: {"derived_from": ctx["inputs"].get(p["from"])}}}


def sleep(ctx: Ctx) -> dict:
    p = ctx["params"]
    if p.get("first_execution_only") and ctx["execution"] > 1:
        return {}
    time.sleep(float(p["seconds"]))
    if "marker" in p:
        Path(p["marker"]).write_text("finished", encoding="utf-8")
    return {}


def flaky(ctx: Ctx) -> dict:
    """Fail with a transient code on the node's first `fail_times` executions, then succeed."""
    p = ctx["params"]
    if ctx["execution"] <= int(p.get("fail_times", 1)):
        raise AgentError(p.get("code", "io_error"))
    return {"facts": p.get("facts", {})}


def fail(ctx: Ctx) -> dict:
    raise AgentError(ctx["params"].get("code", "invalid_input"))


def crash(ctx: Ctx) -> dict:
    raise RuntimeError("unexpected agent crash")


def write_file(ctx: Ctx) -> dict:
    p = ctx["params"]
    path = Path(ctx["workspace"]) / p["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(p["content"], encoding="utf-8")
    return {"artifacts": {p["artifact"]: {"path": p["path"]}}} if "artifact" in p else {}


def check_file(ctx: Ctx) -> dict:
    """Stand-in test runner: fails with tests_failed if the workspace file holds a forbidden token."""
    p = ctx["params"]
    content = (Path(ctx["workspace"]) / p["path"]).read_text(encoding="utf-8")
    if p["forbidden"] in content:
        raise AgentError("tests_failed", f"'{p['forbidden']}' found in {p['path']}")
    return {}


def record(ctx: Ctx) -> dict:
    """Append a line to a file outside the workspace (a committed side effect)."""
    p = ctx["params"]
    with Path(p["file"]).open("a", encoding="utf-8") as fh:
        fh.write(p["line"] + "\n")
    return {}


AGENTS: dict[str, Callable[[Ctx], dict]] = {
    f.__name__: f for f in (noop, emit, transform, sleep, flaky, fail, crash, write_file,
                            check_file, record)
}

from orchestrator.agents.scenario import AGENTS as _SCENARIO_AGENTS  # noqa: E402

AGENTS.update(_SCENARIO_AGENTS)
