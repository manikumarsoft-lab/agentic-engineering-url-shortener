"""Workflow graph: load and validate a YAML dependency graph.

Satisfies: FR-ORC-005, FR-ORC-006, FR-ORC-007.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_TRANSIENT = frozenset({"timeout", "io_error", "db_locked"})
DEFAULT_PERMANENT = frozenset({"invalid_input", "tests_failed", "policy_fail", "permission_refused",
                               "integrity_mismatch", "undeclared_scope", "tests_not_red",
                               "patch_does_not_apply", "no_approved_change_set"})
GATE_KINDS = frozenset({"approval", "clarify"})
ON_FAILURE = frozenset({"safe_stop", "fail_run", "rollback", "compensate"})


class GraphError(ValueError):
    """The workflow definition is invalid and refuses to load."""


@dataclass(frozen=True)
class AgentCall:
    agent: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Gate:
    roles: tuple[str, ...] = ("approver",)
    timeout_s: float = 86400.0
    binds: tuple[str, ...] = ()
    rework_target: str | None = None
    max_rework: int = 2
    kind: str = "approval"  # approval | clarify
    options: dict[str, dict[str, Any]] = field(default_factory=dict)  # clarify: option_id -> {label, action?}
    max_rounds: int = 2  # clarify: free-text answers reopen the gate up to this many rounds


@dataclass(frozen=True)
class Node:
    id: str
    agent: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
    gate: Gate | None = None
    timeout_s: float = 300.0
    max_attempts: int = 3
    backoff_s: float = 1.0
    transient: frozenset[str] = frozenset()
    permanent: frozenset[str] = frozenset()
    on_failure: str = "safe_stop"
    fallback: AgentCall | None = None
    compensate: AgentCall | None = None
    condition: dict[str, Any] | None = None
    skip_reason: str | None = None
    consumes: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()
    policy_checks: tuple[str, ...] = ()

    @property
    def is_gate(self) -> bool:
        return self.gate is not None


@dataclass(frozen=True)
class Workflow:
    name: str
    version: str
    nodes: dict[str, Node]
    workspace_include: tuple[str, ...] = ()  # repo paths copied into each run's isolated workspace

    def downstream(self, start: set[str]) -> set[str]:
        """All nodes reachable from `start` along dependency edges, excluding `start`."""
        children: dict[str, list[str]] = {n: [] for n in self.nodes}
        for node in self.nodes.values():
            for dep in node.depends_on:
                children[dep].append(node.id)
        seen: set[str] = set()
        stack = list(start)
        while stack:
            for child in children[stack.pop()]:
                if child not in seen:
                    seen.add(child)
                    stack.append(child)
        return seen - start

    def consumers(self, artifact: str) -> set[str]:
        return {n.id for n in self.nodes.values() if artifact in n.consumes}


def _call(value: Any) -> AgentCall | None:
    if value is None:
        return None
    if isinstance(value, str):
        return AgentCall(value)
    return AgentCall(value["agent"], dict(value.get("params", {})))


def _node(raw: dict[str, Any], defaults: dict[str, Any]) -> Node:
    gate = raw.get("gate")
    return Node(
        id=raw["id"],
        agent=raw.get("agent"),
        params=dict(raw.get("params", {})),
        depends_on=tuple(raw.get("depends_on", ())),
        gate=Gate(
            roles=tuple(gate.get("roles", ("approver",))),
            timeout_s=float(gate.get("timeout_s", defaults.get("gate_timeout_s", 86400))),
            binds=tuple(gate.get("binds", ())),
            rework_target=gate.get("rework_target"),
            max_rework=int(gate.get("max_rework", 2)),
            kind=gate.get("kind", "approval"),
            options={str(k): dict(v) for k, v in gate.get("options", {}).items()},
            max_rounds=int(gate.get("max_rounds", 2)),
        ) if gate is not None else None,
        timeout_s=float(raw.get("timeout_s", defaults.get("timeout_s", 300))),
        max_attempts=int(raw.get("retry", {}).get("max_attempts", defaults.get("max_attempts", 3))),
        backoff_s=float(raw.get("retry", {}).get("backoff_s", defaults.get("backoff_s", 1.0))),
        transient=frozenset(raw.get("retry", {}).get("transient", ())),
        permanent=frozenset(raw.get("retry", {}).get("permanent", ())),
        on_failure=raw.get("on_failure", "safe_stop"),
        fallback=_call(raw.get("fallback")),
        compensate=_call(raw.get("compensate")),
        condition=raw.get("conditional"),
        skip_reason=raw.get("skip_reason"),
        consumes=tuple(raw.get("consumes", ())),
        produces=tuple(raw.get("produces", ())),
        policy_checks=tuple(raw.get("policy_checks", ())),
    )


def _validate(wf: Workflow) -> None:
    for node in wf.nodes.values():
        if (node.agent is None) == (node.gate is None):
            raise GraphError(f"{node.id}: exactly one of 'agent' or 'gate' is required")
        if node.on_failure not in ON_FAILURE:
            raise GraphError(f"{node.id}: unknown on_failure '{node.on_failure}'")
        if node.max_attempts < 1:
            raise GraphError(f"{node.id}: retry.max_attempts must be >= 1")
        for dep in node.depends_on:
            if dep not in wf.nodes:
                raise GraphError(f"{node.id}: unknown dependency '{dep}'")
        if node.gate and node.gate.rework_target and node.gate.rework_target not in wf.nodes:
            raise GraphError(f"{node.id}: unknown rework_target '{node.gate.rework_target}'")
        if node.gate and node.gate.kind not in GATE_KINDS:
            raise GraphError(f"{node.id}: unknown gate kind '{node.gate.kind}'")
        if node.gate and node.gate.kind == "clarify" and not node.gate.options:
            raise GraphError(f"{node.id}: a clarify gate needs options")
    state: dict[str, int] = {}  # 1 = visiting, 2 = done

    def visit(nid: str, path: list[str]) -> None:
        if state.get(nid) == 2:
            return
        if state.get(nid) == 1:
            raise GraphError("cycle: " + " -> ".join(path + [nid]))
        state[nid] = 1
        for dep in wf.nodes[nid].depends_on:
            visit(dep, path + [nid])
        state[nid] = 2

    for nid in wf.nodes:
        visit(nid, [])


def load_workflow_text(text: str) -> Workflow:
    raw = yaml.safe_load(text)
    defaults = raw.get("defaults", {})
    nodes: dict[str, Node] = {}
    for item in raw["nodes"]:
        node = _node(item, defaults)
        if node.id in nodes:
            raise GraphError(f"duplicate node id '{node.id}'")
        nodes[node.id] = node
    wf = Workflow(name=raw["name"], version=str(raw["version"]), nodes=nodes,
                  workspace_include=tuple(raw.get("workspace", {}).get("include", ())))
    _validate(wf)
    return wf


def load_workflow(path: str | Path) -> Workflow:
    return load_workflow_text(Path(path).read_text(encoding="utf-8"))
