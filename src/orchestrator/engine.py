"""Workflow engine: superstep scheduler with fork/join, gates, retry, recovery and replanning.

Each step runs every READY node at once in isolated subprocesses (fork), then commits the
results in node-ID order. A node becomes READY only when all its predecessors are SUCCEEDED or
SKIPPED (join). Every state change is committed together with its audit event.

Satisfies: FR-ORC-005..008, FR-ORC-011, FR-ORC-014..025, FR-ORC-028, FR-GOV-001..004,
FR-GOV-007, FR-GOV-014..016 (lean slice, HD-CUT-002).
"""
from __future__ import annotations

import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from orchestrator import audit, keys, workspace
from orchestrator.graph import DEFAULT_PERMANENT, DEFAULT_TRANSIENT, AgentCall, Node, Workflow
from orchestrator.keys import Principal
from orchestrator.policy import PolicySet
from orchestrator.store import Store

TERMINAL = frozenset({"COMPLETED", "FAILED", "ABORTED"})
DONE = frozenset({"SUCCEEDED", "SKIPPED"})
DECISIONS = ("approve", "reject_rework", "reject_terminate")
SRC_ROOT = Path(__file__).resolve().parents[1]


class Clock:
    """Wall clock with an adjustable offset."""

    def __init__(self) -> None:
        self.offset = 0.0

    def now(self) -> float:
        return time.time() + self.offset

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class FakeClock(Clock):
    """Test clock: sleeping and advancing move time forward instantly."""

    def sleep(self, seconds: float) -> None:
        self.offset += seconds

    def advance(self, seconds: float) -> None:
        self.offset += seconds


class EngineError(Exception):
    """A request refused because of run or node state."""


class AuthError(PermissionError):
    """A request refused because of the presented key or its role. Always audited."""


@dataclass
class Outcome:
    ok: bool
    code: str | None = None
    outputs: dict[str, Any] = field(default_factory=dict)
    started: float = 0.0
    ended: float = 0.0


def _condition_holds(cond: dict[str, Any], facts: dict[str, Any]) -> bool:
    value = facts.get(cond["fact"])
    if "equals" in cond:
        return value == cond["equals"]
    if "not_equals" in cond:
        return value != cond["not_equals"]
    raise EngineError(f"unsupported condition {cond}")


def _kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        os.killpg(proc.pid, signal.SIGKILL)
    proc.wait()


class Engine:
    def __init__(self, store: Store, workflow: Workflow, policy: PolicySet | None = None, *,
                 var_dir: str | Path, clock: Clock | None = None,
                 source_dir: str | Path | None = None) -> None:
        self.store = store
        self.wf = workflow
        self.policy = policy
        self.clock = clock or Clock()
        self.var = Path(var_dir)
        self.work_root = self.var / "work"
        self.io_root = self.var / "agent-io"
        self.source_dir = Path(source_dir) if source_dir else None

    # ---- run lifecycle -----------------------------------------------------------------------
    def submit(self, facts: dict[str, Any] | None = None,
               labels: tuple[str, ...] = ("demonstration",)) -> str:
        run_id = f"run_{uuid.uuid4().hex[:16]}"
        policy_version = self.policy.version if self.policy else None
        with self.store.tx() as c:
            c.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (run_id, self.wf.name, self.wf.version, policy_version, "RUNNING", None,
                       json.dumps(list(labels)), json.dumps(facts or {}), self.clock.now(), None))
            c.executemany("INSERT INTO nodes (run_id, node_id, state) VALUES (?, ?, 'PENDING')",
                          [(run_id, nid) for nid in self.wf.nodes])
            self._audit(c, run_id, "RUN_CREATED", data={
                "workflow": self.wf.name, "workflow_version": self.wf.version,
                "policy_version": policy_version, "labels": list(labels)})
        if self.source_dir:
            path = workspace.create(self.work_root, run_id, self.source_dir)
            with self.store.tx() as c:
                self._audit(c, run_id, "WORKSPACE_CREATED", target=str(path))
        return run_id

    def run(self, run_id: str, max_steps: int = 500) -> str:
        """Step until the run is blocked (gate, safe-stop) or terminal; return the run state."""
        for _ in range(max_steps):
            if not self.step(run_id):
                break
        return self.store.run(run_id)["state"]

    def step(self, run_id: str) -> bool:
        run = self.store.run(run_id)
        if run["state"] in TERMINAL or run["state"] == "SAFE_STOPPED":
            return False
        now = self.clock.now()
        rows = self.store.nodes(run_id)
        for nid in sorted(rows):
            row = rows[nid]
            if row["state"] == "AWAITING_APPROVAL" and row["deadline"] and now >= row["deadline"]:
                with self.store.tx() as c:
                    self._failure_detected(c, run_id, nid, row, "gate_timeout")
                    self._audit(c, run_id, "GATE_TIMED_OUT", target=nid, result="no decision")
                    self._safe_stop(c, run_id, "gate_timeout", nid)
                return False
        if self._resolve(run_id, rows, run["facts"]):
            return True
        rows = self.store.nodes(run_id)
        ready = sorted(n for n, r in rows.items() if r["state"] == "READY" and r["not_before"] <= now)
        if ready:
            self._execute_step(run_id, ready)
            return True
        waiting = [r["not_before"] for r in rows.values() if r["state"] == "READY"]
        if waiting:
            self.clock.sleep(max(0.0, min(waiting) - now))
            return True
        with self.store.tx() as c:
            if all(r["state"] in DONE for r in rows.values()):
                self._finish(c, run_id, "COMPLETED", None)
            elif any(r["state"] == "AWAITING_APPROVAL" for r in rows.values()):
                if run["state"] != "AWAITING_APPROVAL":
                    self.store.set_run(c, run_id, state="AWAITING_APPROVAL")
                    self._audit(c, run_id, "RUN_AWAITING_APPROVAL")
            else:
                self._safe_stop(c, run_id, "scheduler_stalled")
        return False

    def recover(self) -> list[str]:
        """Startup recovery: runs with an attempt still RUNNING were interrupted -> SAFE_STOPPED."""
        stopped = []
        for run_id in self.store.runs(("RUNNING", "AWAITING_APPROVAL")):
            if self.store.run(run_id)["workflow"] != self.wf.name:
                continue
            rows = self.store.nodes(run_id)
            interrupted = sorted(n for n, r in rows.items() if r["state"] == "RUNNING")
            if not interrupted:
                continue
            with self.store.tx() as c:
                for nid in interrupted:
                    self._audit(c, run_id, "NODE_INTERRUPTED", target=nid)
                    self._failure_detected(c, run_id, nid, rows[nid], "interrupted")
                self._safe_stop(c, run_id, "interrupted")
            stopped.append(run_id)
        return stopped

    def resume(self, run_id: str, presented: str | None, reason: str = "") -> None:
        p = self._principal(run_id, presented, {"approver"}, "run.resume")
        run = self.store.run(run_id)
        if run["state"] != "SAFE_STOPPED":
            raise EngineError(f"run is {run['state']}, not SAFE_STOPPED")
        cause = run["reason"] or ""
        if cause.startswith("policy_fail:") and not self._approved_exception(run_id, cause.split(":", 1)[1]):
            with self.store.tx() as c:
                self._audit(c, run_id, "RESUME_REFUSED", actor_type="human", actor_id=p.key_id,
                            result="refused", reason=f"{cause} has no approved exception")
            raise EngineError(f"cannot resume: {cause} has no approved exception")
        now = self.clock.now()
        with self.store.tx() as c:
            for nid, row in sorted(self.store.nodes(run_id).items()):
                if row["state"] == "RUNNING":
                    self.store.set_node(c, run_id, nid, state="READY", not_before=0)
                    self._audit(c, run_id, "NODE_REQUEUED", target=nid, reason="interrupted attempt")
                elif row["state"] == "FAILED":
                    self.store.set_node(c, run_id, nid, state="READY", attempts=0, not_before=0)
                    self._audit(c, run_id, "RETRY_BUDGET_RESET", target=nid, actor_type="human",
                                actor_id=p.key_id, reason=reason)
                elif row["state"] == "AWAITING_APPROVAL":
                    gate = self.wf.nodes[nid].gate
                    assert gate is not None
                    self.store.set_node(c, run_id, nid, deadline=now + gate.timeout_s)
                    self._audit(c, run_id, "GATE_REOPENED", target=nid,
                                data={"bound": json.loads(row["bound"] or "{}")})
                if row["episode"]:
                    self.store.set_node(c, run_id, nid, recovery_mech="human_resume")
            self.store.set_run(c, run_id, state="RUNNING", reason=None)
            self._audit(c, run_id, "RUN_RESUMED", actor_type="human", actor_id=p.key_id,
                        reason=reason, data={"cause": cause})

    # ---- human gates ---------------------------------------------------------------------------
    def decide(self, run_id: str, node_id: str, presented: str | None, choice: str,
               reason: str = "") -> str:
        node = self.wf.nodes.get(node_id)
        if node is None or node.gate is None:
            raise EngineError(f"{node_id} is not a gate")
        p = self._principal(run_id, presented, set(node.gate.roles), f"gate.{choice}")
        row = self.store.nodes(run_id)[node_id]
        if row["state"] != "AWAITING_APPROVAL" or self.store.run(run_id)["state"] == "SAFE_STOPPED":
            raise EngineError(f"{node_id} is not awaiting a decision")
        if choice not in DECISIONS:
            raise EngineError(f"unknown decision '{choice}'")
        if choice != "approve" and not reason.strip():
            raise EngineError("a rejection needs a reason")
        bound = json.loads(row["bound"] or "{}")
        current = {a: (self.store.artifact(run_id, a) or (0, None))[0] for a in bound}
        if current != bound:
            with self.store.tx() as c:
                self._audit(c, run_id, "DECISION_REFUSED", target=node_id, actor_type="human",
                            actor_id=p.key_id, result="refused", reason="stale artifact version",
                            data={"bound": bound, "current": current})
            raise EngineError("stale artifact version")
        decision_id = f"dec_{uuid.uuid4().hex[:16]}"
        now = self.clock.now()
        actor = {"actor_type": "human", "actor_id": p.key_id}
        data = {"decision_id": decision_id, "role": p.role, "choice": choice, "bound": bound}
        with self.store.tx() as c:
            c.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (decision_id, run_id, node_id, p.key_id, p.role, choice, reason,
                       row["bound"], "ACTIVE", now))
            if choice == "approve":
                self.store.set_node(c, run_id, node_id, state="SUCCEEDED", ended_at=now, deadline=None)
                self._audit(c, run_id, "GATE_APPROVED", target=node_id, reason=reason, data=data, **actor)
                self._recovered(c, run_id, node_id, row)
                self.store.set_run(c, run_id, state="RUNNING")
            elif choice == "reject_terminate":
                self.store.set_node(c, run_id, node_id, state="FAILED", deadline=None)
                self._audit(c, run_id, "GATE_REJECTED", target=node_id, reason=reason, data=data, **actor)
                self._finish(c, run_id, "ABORTED", f"rejected at {node_id}: {reason}")
            else:
                rework = row["rework"] + 1
                self.store.set_node(c, run_id, node_id, rework=rework)
                self._audit(c, run_id, "GATE_REJECTED", target=node_id, reason=reason,
                            data={**data, "rework_cycle": rework}, **actor)
                if rework > node.gate.max_rework:
                    self._safe_stop(c, run_id, "rework_limit_exceeded", node_id)
                else:
                    target = node.gate.rework_target or node.depends_on[0]
                    self._mark_stale(c, run_id, {target} | self.wf.downstream({target}),
                                     f"rework requested at {node_id}")
                    facts = {**self.store.run(run_id)["facts"], "rework_reason": reason}
                    self.store.set_run(c, run_id, facts=facts, state="RUNNING")
        return decision_id

    # ---- replanning ------------------------------------------------------------------------------
    def new_artifact_version(self, run_id: str, name: str, content: Any, presented: str | None,
                             reason: str) -> int:
        """Record a new artifact version; only its consumers and their downstream nodes re-run."""
        p = self._principal(run_id, presented, {"engineer", "approver"}, "artifact.new_version")
        run = self.store.run(run_id)
        if run["state"] in TERMINAL:
            raise EngineError(f"cannot replan a {run['state']} run")
        consumers = self.wf.consumers(name)
        stale = consumers | self.wf.downstream(consumers)
        with self.store.tx() as c:
            version = self.store.add_artifact(c, run_id, name, content, f"human:{p.key_id}",
                                              self.clock.now())
            self._audit(c, run_id, "ARTIFACT_VERSION_CREATED", target=name, actor_type="human",
                        actor_id=p.key_id, reason=reason, data={"version": version})
            self._audit(c, run_id, "REPLAN_STARTED", data={"trigger": f"{name} v{version}",
                                                           "stale": sorted(stale)})
            self._mark_stale(c, run_id, stale, f"input {name} superseded by v{version}")
            if run["state"] == "AWAITING_APPROVAL":
                self.store.set_run(c, run_id, state="RUNNING")
            self._audit(c, run_id, "REPLAN_COMPLETED", data={"rerun": sorted(stale)})
        return version

    # ---- policy exceptions -----------------------------------------------------------------------
    def request_exception(self, run_id: str, check_id: str, presented: str | None, reason: str,
                          compensating_control: str) -> str:
        p = self._principal(run_id, presented, {"engineer", "approver"}, "exception.request")
        failed = self.store.conn.execute(
            "SELECT 1 FROM policy_evaluations WHERE run_id = ? AND check_id = ? AND outcome = 'FAIL'",
            (run_id, check_id)).fetchone()
        if not failed:
            raise EngineError(f"no FAIL evaluation of {check_id} in this run")
        exception_id = f"exc_{uuid.uuid4().hex[:16]}"
        now = self.clock.now()
        with self.store.tx() as c:
            c.execute("INSERT INTO exceptions VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (exception_id, run_id, check_id, p.key_id, reason, compensating_control,
                       "REQUESTED", None, now, None))
            c.execute("INSERT INTO policy_evaluations VALUES (?,?,?,?,?,?,?,?,?)",
                      (run_id, None, check_id, self.policy.version if self.policy else None,
                       "EXCEPTION-REQUESTED", 1, reason, exception_id, now))
            self._audit(c, run_id, "EXCEPTION_REQUESTED", target=check_id, actor_type="human",
                        actor_id=p.key_id, reason=reason,
                        data={"exception_id": exception_id, "compensating_control": compensating_control})
        return exception_id

    def approve_exception(self, run_id: str, exception_id: str, presented: str | None,
                          reason: str) -> None:
        p = self._principal(run_id, presented, {"approver"}, "exception.approve")
        row = self.store.conn.execute(
            "SELECT status, check_id FROM exceptions WHERE exception_id = ? AND run_id = ?",
            (exception_id, run_id)).fetchone()
        if row is None or row["status"] != "REQUESTED":
            raise EngineError(f"exception {exception_id} is not awaiting a decision")
        with self.store.tx() as c:
            c.execute("UPDATE exceptions SET status = 'APPROVED', decided_by = ?, decided_at = ? "
                      "WHERE exception_id = ?", (p.key_id, self.clock.now(), exception_id))
            self._audit(c, run_id, "EXCEPTION_APPROVED", target=row["check_id"], actor_type="human",
                        actor_id=p.key_id, reason=reason, data={"exception_id": exception_id})

    # ---- execution -------------------------------------------------------------------------------
    def workspace_path(self, run_id: str) -> Path:
        return self.work_root / run_id

    def _resolve(self, run_id: str, rows: dict[str, dict], facts: dict[str, Any]) -> bool:
        """Move PENDING/STALE nodes whose predecessors are all done to READY, SKIPPED or a gate."""
        changed = False
        for nid in sorted(rows):
            node, row = self.wf.nodes[nid], rows[nid]
            if row["state"] not in ("PENDING", "STALE"):
                continue
            if not all(rows[d]["state"] in DONE for d in node.depends_on):
                continue
            with self.store.tx() as c:
                if node.condition and not _condition_holds(node.condition, facts):
                    self.store.set_node(c, run_id, nid, state="SKIPPED")
                    self._audit(c, run_id, "NODE_SKIPPED", target=nid,
                                reason=f"condition not met: {node.condition}")
                elif node.gate:
                    bound = {a: (self.store.artifact(run_id, a) or (0, None))[0] for a in node.gate.binds}
                    deadline = self.clock.now() + node.gate.timeout_s
                    self.store.set_node(c, run_id, nid, state="AWAITING_APPROVAL", deadline=deadline,
                                        bound=json.dumps(bound))
                    self._audit(c, run_id, "GATE_OPENED", target=nid, data={
                        "bound": bound, "roles": list(node.gate.roles), "deadline": deadline})
                else:
                    self.store.set_node(c, run_id, nid, state="READY", not_before=0)
                    self._audit(c, run_id, "NODE_READY", target=nid)
            changed = True
        return changed

    def _execute_step(self, run_id: str, ready: list[str]) -> None:
        rows = self.store.nodes(run_id)
        attempts: dict[str, int] = {}
        with self.store.tx() as c:
            self._audit(c, run_id, "STEP_STARTED", data={"nodes": ready})
            for nid in ready:
                attempts[nid] = rows[nid]["attempts"] + 1
                self.store.set_node(c, run_id, nid, state="RUNNING", attempts=attempts[nid],
                                    runs_total=rows[nid]["runs_total"] + 1, started_at=self.clock.now())
                self._audit(c, run_id, "NODE_STARTED", target=nid, data={"attempt": attempts[nid]})
        calls = {nid: AgentCall(self.wf.nodes[nid].agent or "", self.wf.nodes[nid].params) for nid in ready}
        outcomes = self._invoke(run_id, calls, attempts)
        for nid in ready:  # deterministic commit order
            self._commit(run_id, nid, outcomes[nid])

    def _invoke(self, run_id: str, calls: dict[str, AgentCall],
                attempts: dict[str, int]) -> dict[str, Outcome]:
        """Start every call in its own subprocess, then collect each within its node timeout."""
        facts = self.store.run(run_id)["facts"]
        started = {nid: self._spawn(run_id, nid, call, attempts[nid], facts) for nid, call in calls.items()}
        return {nid: self._collect(*started[nid], self.wf.nodes[nid].timeout_s) for nid in calls}

    def _spawn(self, run_id: str, nid: str, call: AgentCall, attempt: int,
               facts: dict[str, Any]) -> tuple[subprocess.Popen, Path, float, float]:
        io = self.io_root / run_id
        io.mkdir(parents=True, exist_ok=True)
        tag = f"{nid}-{attempt}-{uuid.uuid4().hex[:6]}"
        ctx_path, result_path = io / f"{tag}.ctx.json", io / f"{tag}.result.json"
        node = self.wf.nodes[nid]
        inputs = {a: (self.store.artifact(run_id, a) or (0, None))[1] for a in node.consumes}
        execution = self.store.nodes(run_id)[nid]["runs_total"]
        ctx = {"run_id": run_id, "node_id": nid, "attempt": attempt, "execution": execution,
               "params": call.params,
               "inputs": inputs, "facts": facts, "workspace": str(self.workspace_path(run_id))}
        ctx_path.write_text(json.dumps({"agent": call.agent, "ctx": ctx}), encoding="utf-8")
        env = {**os.environ, "PYTHONPATH": str(SRC_ROOT)}
        with (io / f"{tag}.stderr.txt").open("w", encoding="utf-8") as err:
            proc = subprocess.Popen(
                [sys.executable, "-m", "orchestrator.agents.runner", str(ctx_path), str(result_path)],
                env=env, stdout=subprocess.DEVNULL, stderr=err,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
                start_new_session=os.name != "nt")
        return proc, result_path, self.clock.now(), time.monotonic()

    def _collect(self, proc: subprocess.Popen, result_path: Path, started: float, t0: float,
                 timeout_s: float) -> Outcome:
        try:
            proc.wait(timeout=max(0.0, t0 + timeout_s - time.monotonic()))
        except subprocess.TimeoutExpired:
            _kill_tree(proc)
            return Outcome(False, "timeout", started=started, ended=self.clock.now())
        ended = self.clock.now()
        if proc.returncode != 0 or not result_path.exists():
            return Outcome(False, "unclassified", started=started, ended=ended)
        result = json.loads(result_path.read_text(encoding="utf-8"))
        return Outcome(result["ok"], result.get("code"), result.get("outputs", {}), started, ended)

    def _commit(self, run_id: str, nid: str, out: Outcome) -> None:
        node = self.wf.nodes[nid]
        if out.ok:
            facts = {**self.store.run(run_id)["facts"], **out.outputs.get("facts", {})}
            with self.store.tx() as c:
                blocking = self._evaluate_policy(c, run_id, node, facts)
                if blocking is None:
                    self._succeed(c, run_id, nid, out, facts)
                    return
            out = Outcome(False, f"policy_fail:{blocking}", started=out.started, ended=out.ended)
        self._fail(run_id, nid, out)

    def _succeed(self, c: sqlite3.Connection, run_id: str, nid: str, out: Outcome,
                 facts: dict[str, Any], degraded: bool = False) -> None:
        node, row = self.wf.nodes[nid], self.store.nodes(run_id)[nid]
        for name, content in out.outputs.get("artifacts", {}).items():
            if name not in node.produces:
                self._audit(c, run_id, "PERMISSION_REFUSED", target=nid, result="refused",
                            reason=f"artifact '{name}' is not declared in produces")
                continue
            version = self.store.add_artifact(c, run_id, name, content, nid, out.ended)
            self._audit(c, run_id, "ARTIFACT_VERSION_CREATED", target=name,
                        data={"version": version, "produced_by": nid})
        self.store.set_run(c, run_id, facts=facts)
        self.store.set_node(c, run_id, nid, state="SUCCEEDED", ended_at=out.ended, last_error=None,
                            active_s=row["active_s"] + (out.ended - out.started), degraded=int(degraded))
        self._audit(c, run_id, "NODE_SUCCEEDED", target=nid,
                    data={"attempt": row["attempts"], "degraded": degraded})
        self._recovered(c, run_id, nid, row)

    def _classify(self, node: Node, code: str) -> str:
        if code.startswith("policy_fail:"):
            return "permanent"
        if code in node.transient or code in DEFAULT_TRANSIENT:
            return "transient"
        if code in node.permanent or code in DEFAULT_PERMANENT:
            return "permanent"
        return "unclassified"

    def _fail(self, run_id: str, nid: str, out: Outcome) -> None:
        node, row = self.wf.nodes[nid], self.store.nodes(run_id)[nid]
        code = out.code or "unclassified"
        kind = self._classify(node, code)
        with self.store.tx() as c:
            self.store.set_node(c, run_id, nid, last_error=code, ended_at=out.ended,
                                active_s=row["active_s"] + (out.ended - out.started))
            if code == "timeout":
                self._audit(c, run_id, "TIMEOUT", target=nid, data={"timeout_s": node.timeout_s})
            self._audit(c, run_id, "NODE_ATTEMPT_FAILED", target=nid, result="failed", reason=code,
                        data={"attempt": row["attempts"], "classification": kind})
            self._failure_detected(c, run_id, nid, row, code)
            if kind == "transient" and row["attempts"] < node.max_attempts:
                delay = node.backoff_s * 2 ** (row["attempts"] - 1)
                self.store.set_node(c, run_id, nid, state="READY", not_before=self.clock.now() + delay)
                self._audit(c, run_id, "RETRY_SCHEDULED", target=nid,
                            data={"next_attempt": row["attempts"] + 1, "delay_s": delay})
                return
            self.store.set_node(c, run_id, nid, state="FAILED")
            if kind == "transient":
                self._safe_stop(c, run_id, "retry_exhausted", nid)
                return
            if kind == "unclassified":
                self._safe_stop(c, run_id, "unclassified_failure", nid)
                return
            if code.startswith("policy_fail:"):
                self._safe_stop(c, run_id, code, nid)
                return
        if node.fallback and self._run_fallback(run_id, nid, node.fallback):
            return
        self._on_permanent(run_id, nid, code)

    def _run_fallback(self, run_id: str, nid: str, call: AgentCall) -> bool:
        row = self.store.nodes(run_id)[nid]
        out = self._invoke(run_id, {nid: call}, {nid: row["attempts"]})[nid]
        with self.store.tx() as c:
            if not out.ok:
                self._audit(c, run_id, "FALLBACK_FAILED", target=nid, result="failed", reason=out.code)
                return False
            self._audit(c, run_id, "FALLBACK_USED", target=nid, data={"agent": call.agent})
            self.store.set_node(c, run_id, nid, recovery_mech="fallback")
            facts = {**self.store.run(run_id)["facts"], **out.outputs.get("facts", {})}
            self._succeed(c, run_id, nid, out, facts, degraded=True)
        return True

    def _on_permanent(self, run_id: str, nid: str, code: str) -> None:
        mode = self.wf.nodes[nid].on_failure
        if mode == "rollback":
            self._rollback(run_id, nid, code)
        elif mode == "compensate":
            self._compensate(run_id, nid, code)
        else:
            with self.store.tx() as c:
                if mode == "fail_run":
                    self._finish(c, run_id, "FAILED", code)
                else:
                    self._safe_stop(c, run_id, code, nid)

    def _rollback(self, run_id: str, nid: str, code: str) -> None:
        """Restore the last known-good state: discard the isolated workspace copy."""
        with self.store.tx() as c:
            self._audit(c, run_id, "ROLLBACK_STARTED", target=nid, reason=code,
                        data={"workspace": str(self.workspace_path(run_id))})
        discarded = workspace.discard(self.work_root, run_id)
        with self.store.tx() as c:
            self._audit(c, run_id, "ROLLBACK_COMPLETED", target=nid,
                        data={"workspace_discarded": discarded})
            self._recovered(c, run_id, nid, self.store.nodes(run_id)[nid], mechanism="rollback")
            self._finish(c, run_id, "FAILED", f"rolled_back:{code}")

    def _compensate(self, run_id: str, nid: str, code: str) -> None:
        """Undo committed effects: run the compensation hooks of succeeded nodes, newest first."""
        rows = self.store.nodes(run_id)
        done = sorted((r["ended_at"], n) for n, r in rows.items()
                      if r["state"] == "SUCCEEDED" and self.wf.nodes[n].compensate)
        for _, cid in reversed(done):
            call = self.wf.nodes[cid].compensate
            assert call is not None
            with self.store.tx() as c:
                self._audit(c, run_id, "COMPENSATION_STARTED", target=cid, reason=code)
            out = self._invoke(run_id, {cid: call}, {cid: rows[cid]["attempts"]})[cid]
            with self.store.tx() as c:
                if not out.ok:
                    self._audit(c, run_id, "COMPENSATION_FAILED", target=cid, result="failed",
                                reason=out.code)
                    self._safe_stop(c, run_id, "compensation_failed", cid)
                    return
                self._audit(c, run_id, "COMPENSATION_COMPLETED", target=cid)
        with self.store.tx() as c:
            self._recovered(c, run_id, nid, self.store.nodes(run_id)[nid], mechanism="compensation")
            self._finish(c, run_id, "FAILED", f"compensated:{code}")

    def _evaluate_policy(self, c: sqlite3.Connection, run_id: str, node: Node,
                         facts: dict[str, Any]) -> str | None:
        """Record one evaluation per check; return the first blocking mandatory FAIL, if any."""
        if not node.policy_checks or self.policy is None:
            return None
        blocking = None
        for ev in self.policy.evaluate(node.policy_checks, facts):
            outcome, exception_id, reason = ev.outcome, None, ev.reason
            if ev.outcome == "FAIL":
                exception_id = self._approved_exception(run_id, ev.check_id)
                if exception_id:
                    outcome, reason = "EXCEPTION-REQUESTED", f"{ev.reason}; approved exception {exception_id}"
                elif ev.mandatory and blocking is None:
                    blocking = ev.check_id
            c.execute("INSERT INTO policy_evaluations VALUES (?,?,?,?,?,?,?,?,?)",
                      (run_id, node.id, ev.check_id, self.policy.version, outcome, int(ev.mandatory),
                       reason, exception_id, self.clock.now()))
            self._audit(c, run_id, "POLICY_EVALUATED", target=ev.check_id, result=outcome,
                        reason=reason, data={"node": node.id, "policy_version": self.policy.version,
                                             "mandatory": ev.mandatory})
        return blocking

    # ---- shared helpers --------------------------------------------------------------------------
    def _audit(self, c: sqlite3.Connection, run_id: str, action: str, **kw: Any) -> None:
        audit.append(c, run_id, action, ts=self.clock.now(), **kw)

    def _principal(self, run_id: str, presented: str | None, roles: set[str], action: str) -> Principal:
        p = keys.resolve(self.store, presented)
        if p is None or p.actor_type != "human" or p.role not in roles:
            if p is None:
                reason = "unknown or invalid key"
            elif p.actor_type == "agent":
                reason = "agent keys may not perform human-reserved actions"
            else:
                reason = f"role '{p.role}' is not permitted"
            with self.store.tx() as c:
                self._audit(c, run_id, "AUTH_REFUSED", actor_type=p.actor_type if p else "unknown",
                            actor_id=p.key_id if p else None, result="refused", reason=reason,
                            data={"action": action, "required_roles": sorted(roles)})
            raise AuthError(reason)
        return p

    def _approved_exception(self, run_id: str, check_id: str) -> str | None:
        row = self.store.conn.execute(
            "SELECT exception_id FROM exceptions WHERE run_id = ? AND check_id = ? AND status = 'APPROVED'",
            (run_id, check_id)).fetchone()
        return row[0] if row else None

    def _mark_stale(self, c: sqlite3.Connection, run_id: str, nids: set[str], reason: str) -> None:
        rows = self.store.nodes(run_id)
        for nid in sorted(nids):
            if rows[nid]["state"] == "PENDING":
                continue
            self.store.set_node(c, run_id, nid, state="STALE", attempts=0, deadline=None, not_before=0)
            self._audit(c, run_id, "NODE_STALE", target=nid, reason=reason)
            if self.wf.nodes[nid].gate:
                revoked = c.execute(
                    "UPDATE decisions SET status = 'REVOKED' WHERE run_id = ? AND node_id = ? "
                    "AND status = 'ACTIVE' AND choice = 'approve'", (run_id, nid)).rowcount
                if revoked or rows[nid]["state"] == "AWAITING_APPROVAL":
                    self._audit(c, run_id, "GATE_REVOKED", target=nid, reason=reason)

    def _failure_detected(self, c: sqlite3.Connection, run_id: str, nid: str, row: dict,
                          code: str) -> None:
        """Open a failure episode (for MTTR) unless the node already has one open."""
        if row["episode"]:
            return
        episode = f"ep_{uuid.uuid4().hex[:12]}"
        self.store.set_node(c, run_id, nid, episode=episode, recovery_mech="retry")
        self._audit(c, run_id, "FAILURE_DETECTED", target=nid, reason=code, data={"episode": episode})

    def _recovered(self, c: sqlite3.Connection, run_id: str, nid: str, row: dict,
                   mechanism: str | None = None) -> None:
        current = self.store.nodes(run_id)[nid]
        if not current["episode"]:
            return
        self._audit(c, run_id, "RECOVERY_COMPLETED", target=nid, data={
            "episode": current["episode"], "mechanism": mechanism or current["recovery_mech"]})
        self.store.set_node(c, run_id, nid, episode=None, recovery_mech=None)

    def _safe_stop(self, c: sqlite3.Connection, run_id: str, reason: str, nid: str | None = None) -> None:
        self.store.set_run(c, run_id, state="SAFE_STOPPED", reason=reason)
        self._audit(c, run_id, "RUN_SAFE_STOPPED", target=nid, reason=reason)

    def _finish(self, c: sqlite3.Connection, run_id: str, state: str, reason: str | None) -> None:
        self.store.set_run(c, run_id, state=state, reason=reason, ended_at=self.clock.now())
        self._audit(c, run_id, f"RUN_{state}", reason=reason)
