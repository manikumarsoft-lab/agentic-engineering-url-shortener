# Implementation Plan: Agentic Software Engineering System: URL Shortener

**Branch**: `main` (no feature branch, per human instruction) | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Approved feature specification `specs/001-agentic-sdlc-url-shortener/spec.md`
(Human Gate 3, 2026-10-15) and the planning brief with human-owner additions of 2026-10-15.

**Status**: **Approved at plan gate; ADRs pending.** Proposals PD-001 to PD-012 (including
PD-002b) were approved at plan gate (Mani Kumar Vadugu, 2026-10-15). Items still marked
**PROPOSED** are not binding until the human owner approves them. Technology selections in §12 marked **SELECTED
(human)** were chosen by Mani Kumar Vadugu on 2026-10-15 in this planning session and will be
formalized as ADRs in `docs/adr/` at the ADR gate. No ADR files are created by this step.

**Companion artifacts**: [research.md](./research.md) · [data-model.md](./data-model.md) ·
[contracts/](./contracts/README.md) · [quickstart.md](./quickstart.md)

---

## Summary

Build two cooperating, locally runnable Python services in one repository:

1. **`shortener`**: the demonstration-domain URL shortener (FastAPI + SQLite), built directly
   through SpecKit with TDD as the brownfield baseline (CST-007).
2. **`orchestrator`**: an **executable agentic SDLC orchestration engine implemented in this
   repository** (human-owner addition). It is not SpecKit. It has its own versioned dependency
   graph, a persisted run and node state machine, a deterministic superstep scheduler with
   fork/join, conditional nodes, human gates, bounded retries, fallback, rollback, compensation,
   safe-stop, resume, dynamic replanning, a versioned policy evaluator, an append-only
   hash-chained audit log, reliability metrics (including MTTR) and traceability. A CLI (`orch`)
   and an HTTP API expose it.

The three required scenarios (SCN-A expiration and analytics, SCN-B custom aliases, SCN-C "track
who clicks links") are **executions of the engine**. Deterministic agents apply **change sets
authored with AI assistance (Claude Code) during development and reviewed and locked by the human
owner** (CR-004) to **isolated copies** of the shortener, run real tests, and promote
validated releases to a **local staging instance** after a human release decision. The developer
working tree is never modified by a run (FR-ORC-032, FR-ORC-043).

Guiding stance: production-grade **discipline** (contracts, TDD, governance, audit, failure
semantics) on demonstration-scale **infrastructure** (one workstation, SQLite, local processes).

---

## Technical Context

**Language/Version**: Python 3.12 (installed: 3.12.10), managed with `uv` (installed: 0.13.1)

**Primary Dependencies**: FastAPI + Uvicorn (HTTP), Pydantic v2 (schemas), SQLAlchemy Core +
Alembic (persistence and migrations), httpx (HTTP client), Typer (CLI), PyYAML (graph and policy
definitions), jsonschema (contract validation). Dev and security tooling: pytest, Hypothesis,
schemathesis, pytest-cov, mypy (strict), ruff, pip-audit, detect-secrets, pip-licenses. Exact
versions are pinned in `uv.lock` at implementation time and every dependency must appear in
`policy/approved-dependencies.yaml` (policy DEP-001).

**Storage**: SQLite (WAL mode, `busy_timeout`, `BEGIN IMMEDIATE` writes) behind repository
interfaces. Each shortener instance (dev, isolated copy, staging) and the orchestrator have
**separate database files** under `var/` (gitignored).

**Testing**: pytest (unit, integration, state-transition, reliability, security, e2e),
schemathesis + jsonschema (contract), Hypothesis (property-based validation and codes), an
in-process ASGI client plus real subprocess services for integration and e2e.

**Target Platform**: Single developer workstation (Windows 11 reference machine; Linux and macOS
expected to work). No Docker, no cloud, no AI API key (CST-006, NFR-RUN-001). `git` is a
prerequisite (used read-only for the baseline snapshot and for `git apply` inside isolated
workspaces).

**Project Type**: Two web services plus a CLI in a single Python project (monorepo, one
`pyproject.toml`).

**Performance Goals**: PVT-001/PVT-002 measured and reported as **non-gating demonstration
targets**; PVT-003 (1,000 concurrent creations, zero collisions) is gating.

**Constraints**: 2–3 day timebox (CST-005); deterministic, reproducible scenario evidence
(NFR-DET-001); reviewer setup under 30 minutes (PVT-009); no secrets committed (CON V).

**Scale/Scope**: Demonstration scale: one orchestrator, up to tens of runs, one staging instance,
SQLite single-writer. Horizontal scaling is documented, not built (NFR-SCL-002, deferrable).

No `NEEDS CLARIFICATION` items remain. DQ-008 was resolved by human selection; DQ-005, DQ-007 and
DQ-010 are resolved below and were approved at plan gate (Mani Kumar Vadugu, 2026-10-15).

---

## Constitution Check

*Gate: evaluated before Phase 0 research and re-evaluated after Phase 1 design (Governance §1).*

| Principle | Pre-design | Post-design | Justification (post-design) |
|-----------|-----------|-------------|-----------------------------|
| I. Specification Before Implementation | PASS | PASS | No code exists or is planned before task approval. Every component, node and test category maps to FR/NFR IDs (§13). Plan-level additions are isolated as PD-nnn proposals, not silent requirements. |
| II. Explicit Agentic Orchestration | PASS | PASS | Versioned graph contract (`contracts/workflow-graph.v2.yaml`) defines each node's inputs, outputs, entry/exit criteria, owner, permissions, timeout, retry, failure classification, fallback and audit events. There are two forks, two sync points, conditional and dynamic nodes, replanning, interruption and resume (§3). |
| III. Human Governance | PASS | PASS | Seven gate types, each with approve/reject-rework/reject-terminate/escalate/timeout semantics. Timeout leads to `SAFE_STOPPED` and never to approval. Agent-role credentials are refused at the API and at the engine (§5). |
| IV. Test-Driven Engineering | PASS | PASS | Red-green-refactor for domain, engine, policy and governance. All seven required test categories are planned (§10). Places where TDD is not practical are recorded in §10.4. |
| V. Security and Privacy by Design | PASS | PASS | Scheme allow-list, validation at trust boundaries, self/private-address rejection (PD-001), hashed API keys, rate limiting, secret and dependency scans, threat model, no personal data (§8). |
| VI. Compliance and Change-Control Policy Enforcement | PASS | PASS | Versioned policy set with seven domains. Every check yields exactly one of the four outcomes. A mandatory FAIL blocks progression and release. Exceptions run through a human gate with expiry. Contract and schema change records (§9). |
| VII. Architecture and Maintainability | PASS | PASS | Domain, API, persistence, orchestration, policy, telemetry and infrastructure are in separate packages. External tools (git, scanners, subprocess, clock) sit behind interfaces. 19 ADRs are recorded in `docs/adr/`. Complexity is justified in Complexity Tracking. |
| VIII. Reliability and Recovery | PASS | PASS | Per-stage failure classification table (PD-003), bounded retries with backoff, timeouts, idempotent transitions, fallback, rollback distinct from compensation, safe-stop, human-authorized resume (§6). |
| IX. Observability and Auditability | PASS | PASS | Run ID used as the correlation and trace ID. Append-only, hash-chained audit with all required fields. Metrics (including MTTR) computed only from recorded events and labeled as demonstration data (§7). |
| X. Traceability and Repository Integrity | PASS | PASS | Requirement → … → evidence chain built by tooling from spec IDs, task references, pytest markers, JUnit results, doc front matter and run evidence (§13). Evidence comes only from real runs. Scripted decisions are labeled (PD-006). |
| XI. Evidence-Based Completion | PASS | PASS | Release-readiness node evaluates all ten conditions. The human release decision is recorded. The minimum defensible outcome is defined (§14.5). |

**Gate result**: PASS. No violations and no exceptions requested. Complexity Tracking records
justified complexity, not violations.

---

## 1. System Context

### 1.1 System boundary and actors

```text
                         ┌──────────────────────── Workstation (single host) ─────────────────────────┐
  Human actors           │                                                                             │
  ─────────────          │  ┌─────────────────────── Control plane ────────────────────────┐            │
  engineer ──┐           │  │ orchestrator service (FastAPI :8200) + orch CLI               │            │
  approver ──┼─ API key ─┼─▶│  engine · scheduler · gates · policy · audit · metrics       │            │
  release-   │  (human   │  │  agents (deterministic; AI-backed stub disabled)              │            │
  owner    ──┘   roles)  │  │  SUT adapter: workspace · change-set · test-runner · staging  │            │
                         │  │  DB: var/orchestrator/orchestrator.db  (owned)                │            │
                         │  └───────┬───────────────┬─────────────────────┬────────────────┘            │
                         │          │ spawn/copy    │ spawn + HTTP        │ read-only                    │
                         │          ▼               ▼                     ▼                              │
                         │  ┌──────────────┐ ┌──────────────────┐ ┌──────────────────────────┐           │
                         │  │ isolated     │ │ staging shortener│ │ repo (read-only to runs):│           │
                         │  │ workspaces   │ │ :8100            │ │ changesets/, scenarios/, │           │
                         │  │ var/work/... │ │ var/staging/*.db │ │ policy/, baseline git ref│           │
                         │  └──────────────┘ └──────────────────┘ └──────────────────────────┘           │
                         │  ┌─────────────────────── Application plane ─────────────────────┐            │
  consumer ── API key ───┼─▶│ shortener service (FastAPI :8000) · DB var/dev/shortener.db    │            │
  public   ── redirect ──┼─▶│  (developer baseline; never modified by runs)                  │            │
                         │  └────────────────────────────────────────────────────────────────┘            │
                         └─────────────────────────────────────────────────────────────────────────────────┘
  External (optional, release checks only): vulnerability advisory source used by pip-audit.
```

| Actor | Type | Credential | Can do |
|-------|------|-----------|--------|
| API consumer | human/system | `consumer` key | Create links, read analytics (from SCN-A on) |
| Public visitor | anonymous | none | Resolve redirects |
| Engineer | human | `engineer` key | Submit runs, answer clarifications, request exceptions, inspect |
| Approver | human | `approver` key | Approve/reject/escalate gates, approve exceptions, resume, abort, approve corrective actions |
| Release owner | human | `release-owner` key | Record release decisions and accept residual risks |
| Agent | agent | `agent` key (API) / capability set (in-process) | Execute its declared stage only; never human-reserved actions |
| System | system | n/a | Scheduler, timers, policy evaluator; recorded as `actor_type=system` |

### 1.2 Trust boundaries

| ID | Boundary | Controls |
|----|----------|----------|
| TB-1 | Internet/LAN → shortener API | Input validation, key auth (except redirect), rate limit, problem+json without internals |
| TB-2 | Humans → orchestrator API/CLI | Role-mapped keys, role check per action, idempotency keys, audit of refusals |
| TB-3 | Engine → agents | Capability-based permissions (agents receive only declared capability objects); out-of-permission calls refused and audited |
| TB-4 | Engine → system under change (workspaces, staging) | Separate processes and DBs, writes confined to `var/`, path-traversal guard, integrity check of change sets |
| TB-5 | Repository → engine | Read-only access to `changesets/`, `scenarios/`, `policy/`, baseline git ref; never writes to `src/`, `tests/`, `specs/`, `docs/` |
| TB-6 | Engine → external advisory source | Optional and outbound only. Unavailability is a classified failure and never a silent PASS |

### 1.3 Runtime components and data ownership

| Component | Plane | Owns data | Notes |
|-----------|-------|-----------|-------|
| `shortener` (dev instance) | application | `var/dev/shortener.db` | Baseline; runs never touch it |
| `shortener` (staging instance) | application | `var/staging/shortener.db` | Promotion target (FR-ORC-040) |
| `shortener` (isolated copies) | application | `var/work/<run>/<attempt>/shortener.db` | Ephemeral, discarded on rollback |
| `orchestrator` engine + API | control | `var/orchestrator/orchestrator.db` | Runs, nodes, gates, artifacts, decisions, policy evaluations, exceptions, audit, spans |
| Release store | control | `var/releases/<release-id>/` | Immutable source snapshots per release (R0 = baseline) |
| Key store | control/app | `var/secrets/api-keys.json` (hashed) | Generated by `orch keys init`; never committed |

**Application-plane responsibilities**: serving link creation, redirects, analytics, health.
**Control-plane responsibilities**: workflow state, agent execution, governance, policy, change
application in isolation, testing, promotion, compensation, audit, metrics, traceability.
Control-plane failures never alter application-plane data except through gated promotion and
human-approved corrective actions.

---

## 2. URL Shortener Architecture

### 2.1 Components (package `src/shortener/`)

| Component | Module | Responsibility | Requirements |
|-----------|--------|----------------|--------------|
| API delivery | `api/` (routers, problem+json, auth dependency, idempotency middleware) | HTTP mapping only; no domain logic | FR-SHR-001, -018, -019 |
| Domain | `domain/links.py` | Create/resolve use cases, invariants | FR-SHR-001, -005, -007 |
| Short-code generation | `domain/codes.py` | CSPRNG base62, length 7, collision retry ≤5 | FR-SHR-005, -006 |
| URL validation | `domain/validation.py` | Parse, normalize, allow-list, length, credentials, self/private host | FR-SHR-002–004, PD-001 |
| Redirect resolution | `domain/resolve.py` | Lookup → outcome (`redirect`/`not_found`/`expired`†/`unavailable`) | FR-SHR-007, -015 |
| Persistence | `persistence/` (repository protocols, SQLAlchemy Core impl, Alembic migrations) | Atomic writes, uniqueness, idempotency records | FR-SHR-005, -013–-015 |
| Analytics† | `domain/analytics.py` | Atomic counters, fallback on failure | FR-SHR-010–-012 |
| Expiration† | `domain/expiration.py` | UTC, expired when now ≥ expires_at | FR-SHR-008, -009, A-014 |
| Health/readiness | `api/health.py` | Liveness vs readiness (DB ping) | FR-SHR-016 |
| Rate limiting | `api/ratelimit.py` | Token bucket per key ID, 60/min | FR-SHR-017, PVT-011 |
| Telemetry | `telemetry/` | JSON logs, request correlation ID, W3C `traceparent` | FR-OBS-009 |
| Configuration | `config.py` | Typed settings, secure defaults, env overrides | CON V |

† Delivered by scenario change sets, not the baseline (CST-007): SCN-A adds expiration and
analytics; SCN-B adds custom aliases; SCN-C (conforming option) adds daily aggregate counts
(PD-008).

### 2.2 Contract deliverables (see [contracts/README.md](./contracts/README.md))

| Contract | File | Version | Owner |
|----------|------|---------|-------|
| Shortener HTTP API | `contracts/shortener-api.openapi.yaml` | 1.0.0 (baseline) | Human owner (API owner role) |
| Orchestrator HTTP API | `contracts/orchestrator-api.openapi.yaml` | 2.1.0 (CR-003) | Human owner |
| Workflow graph definition | `contracts/workflow-graph.v2.yaml` | 2.1.0 (CR-003) | Human owner (workflow owner) |
| Policy set | `contracts/policy-set.v1.yaml` | 1.0.0 | Human owner (policy owner) |
| Problem (error) schema | `contracts/schemas/problem.schema.json` | 1.0.0 | Shared |
| Workflow-state schema | `contracts/schemas/workflow-state.schema.json` | 1.0.0 | Orchestrator |
| Approval/decision schema | `contracts/schemas/gate-decision.schema.json` | 2.0.0 (CR-002) | Orchestrator |
| Audit-event schema | `contracts/schemas/audit-event.schema.json` | 1.0.0 | Orchestrator |
| Policy-evaluation schema | `contracts/schemas/policy-evaluation.schema.json` | 1.0.0 | Orchestrator |
| Exception schema | `contracts/schemas/policy-exception.schema.json` | 1.0.0 | Orchestrator |
| Persistence schemas | [data-model.md](./data-model.md) §3, realized as Alembic revisions | 1.0.0 | Each service owns its own |

Representative examples live in `contracts/examples/`. **Executable validation**:

1. **Drift test**: the app-generated OpenAPI, normalized, must equal the committed contract.
   The committed contract is authoritative (contract-first).
2. **schemathesis** property-based contract tests against the running ASGI app.
3. **jsonschema** validation of every emitted audit event, policy evaluation, gate decision and
   workflow-state document in tests. Examples are validated in CI.
4. Graph and policy YAML are validated against their meta-schemas at engine start and in tests.
   Invalid definitions refuse to load.

### 2.3 Compatibility and migration rules (summary; full rules in contracts/README.md)

- SemVer per contract. **MINOR**: additive optional request fields, new response fields, new
  endpoints, new error `code` values. **MAJOR**: removals, renames, type or semantic changes,
  new required request fields. Consumers must ignore unknown response fields.
- Database migrations within a MAJOR are **additive only** (expand/contract). Destructive
  operations (`drop_*`, `alter_column` type/nullability narrowing, renames) require a MAJOR
  version, a policy exception (CHG-003) and human approval. This guarantees that the **previous
  release can run against the migrated schema**, which is what makes staging compensation
  (re-promotion) safe.
- Every contract or schema change carries a **Change Record** (template in contracts/README.md)
  with ownership, version impact, backward-compatibility impact, affected consumers, tests, docs,
  rollout/migration steps and required approval. In scenario runs, ST-05/ST-07 produce this
  record as an artifact and G-DESIGN approves it.

Planned scenario contract increments (delivered only through runs):

| Scenario | Shortener API | Schema | Compat |
|----------|---------------|--------|--------|
| SCN-A | 1.1.0: optional `expires_at` on create; `410 link_expired`; `GET /api/v1/links/{code}/analytics` | add `expires_at` column (nullable); add `link_stats` table | additive |
| SCN-B | 1.2.0: optional `alias` on create; `409 alias_conflict`; `422 alias_invalid`/`alias_reserved` | add `code_origin` column (default `generated`) | additive |
| SCN-C (option A) | 1.3.0: `daily` buckets (UTC date → count) in the analytics response | add `link_daily_stats` table | additive |

---

## 3. Agentic Orchestration Architecture

Authoritative definition: [`contracts/workflow-graph.v2.yaml`](./contracts/workflow-graph.v2.yaml)
(each node's purpose, inputs, outputs, preconditions, postconditions, actor, permissions,
timeout, retry, failure classification, fallback, failure behavior, audit events, prohibited
transitions). State machines: [data-model.md §2](./data-model.md).

### 3.1 Engine modules (`src/orchestrator/`)

| Module | Responsibility |
|--------|----------------|
| `engine/graph.py` | Load and validate the graph template; instantiate a per-run **graph instance** (versioned); resolve conditions; compute ready set; downstream closure for replanning |
| `engine/state.py` | Run, node and gate state machines as explicit transition tables. Illegal transitions raise and are audited |
| `engine/scheduler.py` | Deterministic **superstep scheduler** (PD-004): each step collects ready nodes, executes them concurrently (`asyncio`), then commits results in node-ID order |
| `engine/transitions.py` | One DB transaction per transition: state update + audit append + idempotency key (`transition_key` unique) |
| `engine/gates.py` | Gate lifecycle, role checks, artifact-version binding, timeouts, rework bounds |
| `engine/retry.py` | Failure classification lookup, retry budget, backoff schedule, timeout enforcement |
| `engine/criteria.py` | Entry/exit criteria and conditional-skip evaluation with recorded refusal and skip reasons |
| `engine/fallback.py` | Graph-declared fallbacks; degraded marking; `FALLBACK_USED` |
| `engine/faults.py` | Fault injector (test configuration and labeled runs only) |
| `engine/replan.py` | Artifact supersession → stale closure → approval revocation → graph instance v+1 → re-run affected nodes |
| `engine/recovery.py` | Startup recovery (interrupted runs → `SAFE_STOPPED`), resume, compensation orchestration |
| `policy/` | Policy-set loader, evaluator, checks, exceptions |
| `agents/` | `Agent` protocol; `deterministic/` implementations per role; `ai_backed/` disabled stub (FR-ORC-027/030) |
| `sut/` | `WorkspaceManager`, `ChangeSetStore` (integrity), `PatchApplier` (git apply), `TestRunner` (pytest subprocess + JUnit), `StagingManager` (process control, migrate, smoke), `ReleaseStore` |
| `audit/` | Append-only store, hash chain, query, tamper refusal |
| `observability/` | Metrics (success, failure, retry, rollback/compensation, MTTR, latency), spans, JSON logs |
| `trace/` | Run-level traceability graph and queries (FR-OBS-008) |
| `security/` | Key store, roles, permission guard |
| `api/`, `cli/` | FastAPI app and Typer CLI (thin; call engine services) |

### 3.2 Default graph topology

```text
ST-01 Ingest ─▶ ST-02 Normalize ─▶ ST-03 Quality+policy ─┬─[any material failure]─▶ G-CLARIFY (ST-04) ─┐
                                                         └─[all pass: SKIP gate]────────────────────────┤
                                                                                                        ▼
                                   ┌─[change_kind = new_capability]─▶ ST-05a Additive-change check (SCN-A-AC6) ┐
                                   └─[otherwise: SKIP]─────────────────────────────────────────────────────────┤
                                                                                                        ▼
                                   ┌─[change_kind = modification OR ST-05a failed (reroute, reason recorded) OR replanning]─▶ ST-05 Impact analysis ┐
                                   └─[otherwise: SKIP]───────────────────────────────────────────────────┤
                                                                                                        ▼
                                                      ST-06 Decomposition ─▶ ST-07 Design ─▶ G-DESIGN (approver;
                                                                                              design + change control)
                                                                                                        │
                        ┌────────────────────────── FORK F1 ────────────────────────────────────────────┤
                        ▼                                      ▼                                        ▼
              ST-08 Implement (isolated copy)       ST-10a Docs draft                     ST-11a Threat/risk draft
                        ▼
              ST-09 Test (new + regression) ──[fail]─▶ ROLLBACK (discard copy) ─▶ run FAILED path
                        └──────────────────────────────┬───────────────────────────────────────────────┘
                                                     SP-1 (join: all three successful)
                                       ┌─────────────── FORK F2 ───────────────┐
                                       ▼                                       ▼
                              ST-10b Docs finalize                 ST-11b Security validation
                                                                   ─▶ G-SECURITY [if security-sensitive]
                                       └───────────────────┬───────────────────┘
                                                         SP-2 (join)
                                                           ▼
                                        ST-12 Readiness assessment ─▶ G-RELEASE (release-owner)
                                                           │ [not_ready] ─▶ ST-13 Summary ─▶ FAILED (blocking reasons recorded; CR-002)
                                                           ▼ [ready]
                                        REL-01 Promote to staging + smoke
                                          ├─[pass]─▶ ST-13 Summary ─▶ COMPLETED
                                          └─[fail]─▶ REL-02 Compensate (re-promote previous)
                                                       ├─[ok]─▶ G-CORRECTIVE (approver) ─▶ ST-13 ─▶ FAILED (compensated)
                                                       └─[compensation fails]─▶ SAFE_STOPPED (staging degraded)

Run-scoped dynamic gates (not static nodes): G-EXCEPTION (policy exception), G-CLARIFY-n (late
ambiguity raised by any agent node), G-RESUME (resume from safe-stop; API action, approver role).
```

Topology properties: **sequential** (ST-01→ST-02→ST-03), **conditional** (G-CLARIFY, ST-05,
G-SECURITY, REL-02/G-CORRECTIVE), **parallel fan-out** (F1 with three branches, F2 with two),
**synchronization** (SP-1, SP-2), **gates** (G-*), **dynamic insertion** (G-CLARIFY-n,
G-EXCEPTION, replanning nodes), **compensation path** (REL-02).

### 3.3 State machines (summary; full tables in data-model.md §2)

- **Run**: `CREATED → RUNNING ⇄ AWAITING_HUMAN → {COMPLETED | FAILED | ABORTED | SAFE_STOPPED}`;
  `SAFE_STOPPED → RESUMING → RUNNING` (approver only). `REPLANNING` is a transient sub-state of
  `RUNNING`. Exactly one terminal outcome per run lifecycle (FR-ORC-023). `SAFE_STOPPED` is
  terminal-but-resumable.
- **Node**: `PENDING → READY → RUNNING → SUCCEEDED`; failure path
  `RUNNING → FAILED_TRANSIENT → RETRY_WAIT → RUNNING` (bounded) or `→ FAILED_PERMANENT`; plus
  `BLOCKED` (entry refused), `SKIPPED` (condition false), `SUSPENDED` (awaiting late
  clarification), `STALE` (invalidated by replanning), `ROLLED_BACK`, `COMPENSATED`,
  `INTERRUPTED`. Gate nodes use `AWAITING_DECISION`.
- **Gate**: `OPEN → {APPROVED | REJECTED_REWORK | REJECTED_TERMINATE | ESCALATED | TIMED_OUT |
  REVOKED}`; `ESCALATED → {APPROVED | REJECTED_* | TIMED_OUT}`; `REVOKED`/`REJECTED_REWORK` lead
  to a new gate instance bound to the new artifact version.

**Prohibited transitions** (enforced, tested, audited when attempted): any agent or system actor
→ gate `APPROVED`/`REJECTED_*`; `TIMED_OUT → APPROVED`; node `PENDING → RUNNING` bypassing entry
criteria; dependent node `READY` while any predecessor is not `SUCCEEDED`/`SKIPPED`; sync point
release while any branch is `SUSPENDED`/`FAILED_*`/`BLOCKED`; `FAILED_PERMANENT → RETRY_WAIT`;
`SAFE_STOPPED → RUNNING` without `RESUMING` by an approver; any transition out of `COMPLETED`,
`FAILED` or `ABORTED`.

### 3.4 Node specification table (abridged; authoritative in the graph contract)

| Node | Actor | Key inputs → outputs | Timeout / retry | Permanent failure → | Fallback |
|------|-------|----------------------|-----------------|---------------------|----------|
| ST-01 Ingest | agent `intake` | run request → `raw-requirement` v1 | 300 s / 3 | run `FAILED` (invalid input) | none |
| ST-02 Normalize | agent `analyst` | raw → `normalized-requirement` (IDs, FR/NFR, AC candidates, `change_kind`) | 300 s / 3 | `SAFE_STOPPED` | none |
| ST-03 Quality+policy | agent `quality` + policy | normalized → `quality-report` (5 checks + PRIV-001, ARCH-001) | 300 s / 3 | `SAFE_STOPPED` | none |
| G-CLARIFY (ST-04) | human `engineer`/`approver` | quality report → `clarification-decision` | 24 h (demo cfg) / n/a | timeout → `SAFE_STOPPED` | none |
| ST-05a Additive-change check | agent `impact` | normalized + change-set manifest + contract diff + existing-test diff → `additive-change-check` (PASS: only optional fields/new endpoints, additive migration, no existing test modified or removed; FAIL: reason recorded, `change_kind` reclassified to `modification`) | 300 s / 3 | `SAFE_STOPPED` | none |
| ST-05 Impact | agent `impact` | normalized + change-set manifest + component registry + import graph → `impact-analysis`, `change-record` | 300 s / 3 | `SAFE_STOPPED` | none |
| ST-06 Decompose | agent `planner` | normalized (+impact) → `task-plan` (tasks, deps, req links, AC) | 300 s / 3 | `SAFE_STOPPED` | none |
| ST-07 Design | agent `architect` | task plan + contracts + change-set manifest → `design` (API/schema delta, components, test plan) | 300 s / 3 | `SAFE_STOPPED` | none |
| G-DESIGN | human `approver` | design, task plan, impact, change-set fingerprint → `design-approval` | 24 h / n/a | timeout → `SAFE_STOPPED` | none |
| ST-08 Implement | agent `implementer` | approved design + change set + release base → `workspace` (patched copy), `change-application-record` | 300 s / 3 | integrity/scope FAIL → `SAFE_STOPPED`; patch reject → rollback → `FAILED` | none |
| ST-09 Test | agent `tester` | workspace → `test-results` (JUnit, new + regression) | 300 s / 3 | tests fail → **ROLLBACK** → `FAILED` | none |
| ST-10a Docs draft | agent `writer` | design → `docs-draft` | 300 s / 3 | `SAFE_STOPPED` | template-only draft flagged `degraded` |
| ST-11a Threat draft | agent `security` | design + impact → `threat-review` (STRIDE-lite) | 300 s / 3 | `SAFE_STOPPED` | none |
| SP-1 | system | all F1 outputs | n/a | n/a | n/a |
| ST-10b Docs finalize | agent `writer` | draft + test results + OpenAPI diff → `docs` | 300 s / 3 | `SAFE_STOPPED` | OpenAPI diff unavailable → manual-review section, `degraded` |
| ST-11b Security validation | agent `security` + policy | workspace + lockfile → `security-report` (secret scan, pip-audit, licenses, policy evals) | 300 s / 3 | mandatory FAIL → `SAFE_STOPPED` | none (scanner unavailable → FAIL, never PASS) |
| G-SECURITY | human `approver` | security report (cond: security-sensitive components touched) | 24 h | timeout → `SAFE_STOPPED` | none |
| SP-2 | system | F2 outputs | n/a | n/a | n/a |
| ST-12 Readiness | agent `release` + policy | all artifacts → `readiness-assessment` (CON XI's 10 conditions, evaluated through REL-001..005, AUD-001/002 and prior-node policy outcomes) | 300 s / 3 | `SAFE_STOPPED` | none |
| G-RELEASE | human `release-owner` | assessment (must be non-FAIL), per-risk acceptance → `release-decision` | 24 h | timeout → `SAFE_STOPPED`; `not_ready` → ST-13 → `FAILED` (no rework; CR-002) | none |
| REL-01 Promote+smoke | agent `deployer` | release decision + workspace → `release` R(n+1), `smoke-result` | 300 s / 3 (transient only, idempotent by release ID) | smoke fail → REL-02 | none |
| REL-02 Compensate | agent `deployer` | previous release → `compensation-record` (re-promotion + non-rollbackable effects) | 300 s / 3 | `SAFE_STOPPED` (staging degraded) | none |
| G-CORRECTIVE | human `approver` | compensation record → `corrective-action-decision` | 24 h | timeout → `SAFE_STOPPED` | none |
| ST-13 Summary | agent `reporter` | run state + all artifacts → `engineering-summary` | 300 s / 3 | `SAFE_STOPPED` | none |

### 3.5 Scheduling, parallelism and determinism (PD-004)

The **superstep (bulk-synchronous) scheduler** runs every `READY` node of a step concurrently
(`asyncio.gather` with a per-node timeout), then **commits results in lexicographic node-ID
order** in one transaction per transition. Retry waits and gate waits are timers. A step does
not wait for them; the scheduler advances when any node becomes ready or any timer fires. The
`Clock` and `IdGenerator` are injected, so tests run with a virtual clock. The result is real
concurrency with a reproducible committed event order (NFR-DET-001). The trade-off is that a
fast branch can wait up to one sibling's step duration. This is acceptable at demo scale and
recorded in ADR-003.

### 3.6 Dynamic replanning (FR-ORC-020/021/022)

1. Trigger: a new artifact version (for example, clarification answer → `normalized-requirement`
   v2), a late ambiguity raised by a node, a G-DESIGN `reject_rework`, or a CHG-002 scope
   violation followed by resume.
2. `replan.py` computes the **downstream closure** from the graph instance and recorded
   input-artifact versions. Every node whose recorded inputs include a superseded version, or a
   transitive dependent, becomes `STALE`. Gates bound to stale artifacts become `REVOKED`
   (audited `GATE_REVOKED`; approvals must be re-requested).
3. A new **graph instance version** is created when topology changes (for example, ST-05 is now
   required). Otherwise the version stays and only node states change.
4. Re-execution is **memoized by input hash**. A node is re-run only if it is `STALE`. Unaffected
   `SUCCEEDED` nodes keep their outputs (SC-006).
5. Late ambiguity (SCN-A-AC4): the raising node becomes `SUSPENDED`, a run-scoped G-CLARIFY-n
   opens, and siblings continue to the next sync point, which does not release (FR-ORC-039).
   After the answer, ST-05 runs in *replanning mode*, the suspended node resumes from its saved
   state, and the sync point releases when all branches succeed.
6. Events: `REPLAN_STARTED`, `ARTIFACT_STALE`, `GATE_REVOKED`, `GRAPH_VERSION_CREATED`,
   `REPLAN_COMPLETED`.

### 3.7 Agents and controlled autonomy

- One `Agent` protocol: `execute(ctx: StageContext) -> StageResult`. `StageContext` exposes only
  the **capability objects** declared for the role in the graph contract (for example
  `workspace.write`, `changeset.read`, `process.run_tests`, `staging.promote`). A request outside
  the declared set raises `PermissionRefused`, which is recorded as `PERMISSION_REFUSED`
  (FR-ORC-025).
- **Deterministic agents** (default and the only mode for tests and evidence; FR-ORC-029) are
  rule-based and labeled honestly in artifacts as "deterministic rule-based agent":
  - lexicon and structure rules for normalization and quality checks;
  - static analysis (component registry + Python `ast` import graph + change-set manifest) for
    impact analysis;
  - template-based decomposition and design from ACs × impacted components;
  - `git apply` for change application, pytest for testing, scanners for security.
- **AI-backed mode**: the interface plus a disabled stub (CST-008 deferrable #1). Requesting it
  returns `422 agent_mode_unavailable`. Its absence never blocks other capabilities (FR-ORC-030).

---

## 4. State and Decision Lineage

All of the following are persisted in `orchestrator.db` ([data-model.md §1](./data-model.md)),
each change in the same transaction as its audit event:

| Item | Entity | Lineage mechanism |
|------|--------|-------------------|
| Workflow instance state | `runs`, `graph_instances`, `node_states`, `node_attempts` | Versioned graph instance; per-attempt records |
| Normalized requirements | `artifacts` (type `normalized-requirement`) + `requirements` | Stable run-level IDs `RQ-<run>-nnn`, each linked to spec IDs where matched |
| Task decomposition and dependencies | `artifacts` (type `task-plan`) | Tasks carry `depends_on`, `requirement_ids`, `acceptance_criteria` |
| Decisions | `decisions` | `bound_artifact_versions[]`, `rationale`, actor, role, key ID |
| Assumptions | `artifacts` (type `assumption-register`) | Produced by ST-02/ST-07; changes re-versioned |
| Approvals / rejections | `gates` + `decisions` | Gate bound to exact artifact versions; refusals audited |
| Artifact versions | `artifacts`, `artifact_versions` | Content hash, `produced_by` (node attempt), `input_versions[]`, status `current/stale/rolled_back/superseded` |
| Test outcomes | `artifacts` (type `test-results`) + JUnit file | Linked to workspace and change-set fingerprint |
| Risk outcomes | `artifacts` (type `threat-review`, `security-report`); risk acceptance in `release-decision` | Per-risk ID acceptance with approver |
| Replanning history | `replans` + audit events | Trigger, superseded artifacts, stale nodes, revoked gates, graph version |
| Correlation identifiers | every row has `run_id`; audit `trace_id` = run ID (128-bit) | Propagated as W3C `traceparent` to the shortener |
| Terminal status | `runs.terminal_outcome`, `runs.terminal_reason` | Set exactly once per lifecycle; `SAFE_STOPPED` can be followed by resume |

Provenance on every artifact version (FR-ORC-012): producing node and attempt, actor, agent mode,
run ID, input artifact versions, timestamp, content hash. Change-set artifacts carry the fixed
label "Authored with AI assistance (Claude Code) during development; reviewed and locked by the human owner (Mani Kumar Vadugu); applied by the deterministic agent, not generated at run time." (FR-ORC-034 as amended by CR-004).

---

## 5. Human-in-the-Loop Controls

### 5.1 Gate catalogue

| Gate | Trigger | Required role | Bound to | Decisions | Timeout | Requirement |
|------|---------|---------------|----------|-----------|---------|-------------|
| G-CLARIFY / G-CLARIFY-n | Material quality-check failure at ST-03, or late ambiguity raised by a node | `engineer` or `approver` | `quality-report` vN / raising artifact | answer (select option or free text), reject_terminate, escalate | → `SAFE_STOPPED` | FR-ORC-004, -022 |
| G-DESIGN | Always before F1 | `approver` | design, task-plan, impact-analysis, change-record, change-set fingerprint | approve, reject_rework, reject_terminate, escalate | → `SAFE_STOPPED` | FR-GOV-001, SCN-B-AC2 |
| G-SECURITY | ST-11b finds security-sensitive components touched (registry flag) or open high/critical threat | `approver` | security-report vN | approve, reject_rework, reject_terminate, escalate | → `SAFE_STOPPED` | FR-GOV-001, CON V (PD-007) |
| G-EXCEPTION | Engineer requests an exception for a FAILed check | `approver`, with a key identity different from the requesting key (FR-GOV-017) | policy evaluation + exception request | approve (with expiry and compensating control), reject | → `SAFE_STOPPED` | FR-GOV-007/008, FR-GOV-017 |
| G-RELEASE | ST-12 produces a non-FAIL assessment | `release-owner` | readiness-assessment vN | ready (with per-risk acceptance), not_ready (terminates the run as `FAILED` with blocking reasons; no rework, CR-002), escalate | → `SAFE_STOPPED` | FR-GOV-010/011 |
| G-CORRECTIVE | Compensation completed with non-rollbackable effects | `approver` | compensation-record | approve listed corrective action, decline (retain data, record risk) | → `SAFE_STOPPED` | FR-ORC-042 |
| G-RESUME (action) | Resume from `SAFE_STOPPED` | `approver` | safe-stop record; for non-timeout causes, evidence the cause is resolved or excepted | resume | n/a | FR-ORC-019, FR-GOV-014, A-016 |

### 5.2 Mapping of brief-required gates

| Required gate | Realized by |
|---------------|-------------|
| Unresolved ambiguity | G-CLARIFY, G-CLARIFY-n |
| Architecture approval | G-DESIGN (engine); Plan/ADR gate (SpecKit lifecycle) |
| Security-sensitive action | G-SECURITY; key issuance (`orch keys init`) is a local operator action, documented |
| Destructive or irreversible action | G-CORRECTIVE (data correction in staging); promotion is gated by G-RELEASE; `orch demo reset` requires interactive confirmation and refuses to touch anything outside `var/` |
| Constitutional exception | SpecKit-level: Governance §2 written exception approved by the human owner. Engine-level: G-EXCEPTION for policy exceptions |
| Material risk acceptance | G-RELEASE per-risk acceptance (every open risk ≥ medium must be explicitly accepted or the decision is refused); G-EXCEPTION compensating control |
| Release readiness | G-RELEASE (engine); repository release-readiness sign-off (SpecKit lifecycle) |
| Final submission | SpecKit/process gate only: the human owner signs `docs/release-readiness.md` and creates the annotated tag `assessment-submission-v1.0` on GitHub (CST-009). Never performed by an agent |

### 5.3 Decision semantics (all gates)

- **approve**: bound artifact versions must be current (else `409 stale_artifact_version`;
  FR-GOV-004). Records approver, role, key ID, timestamp, rationale.
- **reject_rework**: requires a reason. The producing node is re-executed with the reason as
  input. Dependents stay `PENDING`. At most **2** rework cycles per gate per run (PVT-013); the
  third leads to `SAFE_STOPPED` "rework limit exceeded" (FR-GOV-016).
- **reject_terminate**: run → `ABORTED` and ST-13 produces the summary.
- **not_ready** (G-RELEASE only; CR-002, Human Gate 4 ruling 4): there is no rework option at
  G-RELEASE. The run ends as `FAILED` with the blocking reasons recorded, after ST-13 produces the
  summary. After fixing the cause, a human starts a new run (consistent with PD-012). `FAILED`
  rather than `ABORTED` because a release decision is a distinct decision category from an
  approval rejection (FR-GOV-003 lists them separately), so FR-GOV-015's "reject and terminate →
  `ABORTED`" does not govern it.
- **Separation of duties (FR-GOV-017, CR-003)**: a decision on an exception, or on any request,
  by the same key identity that submitted that request is refused with
  `403 separation_of_duties_violation` and audited (`GATE_DECISION_REFUSED`). One person may
  still hold several roles (A-008), but only through different key identities.
- **escalate**: gate → `ESCALATED` (still blocking). The escalation reason is recorded and the
  next decision requires `approver` (release-owner for G-RELEASE). Routing beyond recording is
  deferred (CST-008 #4).
- **timeout**: `GATE_TIMED_OUT` is audited as "no decision" and the run → `SAFE_STOPPED`.
  Resume re-opens the **same gate on the same artifact version** (FR-GOV-014).
- A decision without a choice, by an agent-role key, by a wrong role, or a duplicate with the
  same `decision_id`, is refused or applied at most once. Every refusal is audited.

---

## 6. Reliability

### 6.1 Definitions

| Term | Definition in this system |
|------|---------------------------|
| Transient failure | A failure for which a retry with the same inputs can plausibly succeed: `TimeoutExpired`, `sqlite3.OperationalError: database is locked` after busy timeout, subprocess killed or crashed without producing a report, staging not ready within the readiness window, advisory source unreachable, `INTERRUPTED` attempt of an idempotent node |
| Permanent failure | A deterministic failure: schema or validation error, missing or invalid input artifact, integrity mismatch, patch does not apply, test assertions fail, policy FAIL, permission refusal, illegal transition |
| Unclassified | Any exception not in the node's classification map → **safe-stop** (FR-ORC-018) |
| Retry eligibility | Transient only (FR-ORC-014) and idempotent nodes only. REL-01 is idempotent by `release_id` (promote is a no-op if staging already serves that release) |
| Retry bound | `max_attempts = 3` per node (PVT-004); exhausted on a mandatory node → `SAFE_STOPPED` |
| Backoff | Exponential, base 1 s, ×2, cap 30 s. Jitter seeded from `(run_id, node_id, attempt)` so it is deterministic |
| Timeout | Per node (default 300 s; PVT-005); gate timeout configurable (default 24 h; demo profile 120 s). Node timeout counts as transient |
| Idempotency | API: `Idempotency-Key` on POSTs (shortener create; orchestrator run creation and decisions). Engine: unique `transition_key` per state transition; decisions carry `decision_id` (FR-ORC-028) |
| Duplicate execution protection | A node attempt row is claimed with a conditional update (`state='READY' → 'RUNNING'` where version matches). A second claimant fails the update |
| Fallback | Declared per node (ST-10a, ST-10b; analytics in the shortener). Use is recorded (`FALLBACK_USED`), sets `degraded=true` on the artifact and appears in readiness as an advisory (REL-005) |
| Rollback | **Restore prior state with no committed external effect**: discard the isolated workspace and mark artifacts `rolled_back`. The system under change is back at the last known-good release (SCN-B-AC4, FR-ORC-035) |
| Compensation | **Corrective action after a committed effect**: re-promote the previous release to staging after a failed smoke check. Non-rollbackable data is listed and corrected only with G-CORRECTIVE approval (FR-ORC-042) |
| Safe-stop | Run → `SAFE_STOPPED` with reason code. No node is `RUNNING`. Workspaces are retained for inspection. State is consistent and resumable. Triggers per FR-ORC-018 plus rework limit, compensation failure, scheduler stall (no node runnable, no timer pending and no gate open while the run is not terminal) and interruption detected at startup (PD-011) (CR-002) |
| Resumption | `POST /runs/{id}/resume` (approver). Requires the cause resolved or excepted (A-016). Re-opens timed-out gates on the same version. Re-runs only non-succeeded nodes. Interrupted idempotent nodes are retried within budget |
| Partial failure | One F1/F2 branch fails or is suspended: siblings finish, the sync point holds (FR-ORC-039), and the run outcome follows the failed branch's failure behavior |
| Dependency unavailability | Shortener DB unavailable → `503 persistence_unavailable` (create) / `503` (redirect, never a stale redirect). Staging process fails to start → transient. Advisory source unavailable → transient, then SEC-003 `FAIL` (exception possible), never a silent PASS |

### 6.2 Failure classification by stage: **PD-003 (resolves DQ-007; approved at plan gate (Mani Kumar Vadugu, 2026-10-15))**

| Node | Transient (retry ≤3) | Permanent | On exhaustion / permanent |
|------|----------------------|-----------|---------------------------|
| ST-01 | DB locked, timeout | Malformed request, unknown scenario/change set | `FAILED` (bad input) |
| ST-02, ST-03, ST-06, ST-07 | DB locked, timeout, interrupted | Input artifact invalid against schema | `SAFE_STOPPED` |
| ST-05, ST-05a | DB locked, timeout, interrupted | Change-set manifest invalid, registry missing component (an additive-check FAIL is a valid result that reroutes the run to ST-05, not a node failure) | `SAFE_STOPPED` |
| ST-08 | Workspace copy I/O error, timeout, interrupted | Integrity mismatch (CHG-001 FAIL), undeclared scope (CHG-002 FAIL) → `SAFE_STOPPED`; `git apply --check` fails → rollback → `FAILED` | as stated |
| ST-09 | pytest crashed or killed without JUnit, timeout | Any test failure or error in JUnit | Rollback → `FAILED` |
| ST-10a/b | Timeout, interrupted | Template render error | Fallback (degraded) if declared, else `SAFE_STOPPED` |
| ST-11a/b | Scanner process crash, advisory source unreachable, timeout | Mandatory policy FAIL | `SAFE_STOPPED` (exception path available) |
| ST-12, ST-13 | DB locked, timeout | Input artifact missing | `SAFE_STOPPED` |
| REL-01 | Port busy, readiness window exceeded, process crash | Migration refused (destructive op), smoke assertion fails | Smoke fail → REL-02; migration refusal → `SAFE_STOPPED` |
| REL-02 | Same as REL-01 | Previous release smoke fails | `SAFE_STOPPED`, staging marked degraded |
| Gates | n/a | n/a | Timeout → `SAFE_STOPPED` |

Approved by the human owner at the Plan gate, this table becomes the `failure_classification`
map in the graph contract (already drafted there).

### 6.3 Interruption and recovery

On orchestrator start, `recovery.py` scans runs in `RUNNING`/`AWAITING_HUMAN`. Attempts in
`RUNNING` become `INTERRUPTED` and the run becomes `SAFE_STOPPED` (reason `interrupted`;
FR-ORC-019 requires an authorized human resume). Gates past their deadline become `TIMED_OUT`.
On resume, interrupted idempotent nodes retry within budget. Completed nodes are not re-run
(PVT-006: one interruption test per stage boundary, run with a kill-switch fault injector at each
node boundary).

---

## 7. Observability

### 7.1 Signals

| Signal | Mechanism | Where |
|--------|-----------|-------|
| Logs | stdlib `logging` + JSON formatter; fields `ts, level, service, run_id, trace_id, span_id, node_id, event, msg`; secrets redacted by key-name and pattern filter | stdout + `var/logs/*.jsonl` |
| Traces | In-house minimal spans (PD-005): `spans` table (run = trace, node attempt = span, outbound HTTP/subprocess = child span). W3C `traceparent` propagated to the shortener, whose logs carry the same trace ID | `orchestrator.db`; `GET /runs/{id}/trace` |
| Audit events | Append-only, per-run `seq`, hash-chained ([audit-event schema](./contracts/schemas/audit-event.schema.json)) | `audit_events` table; `GET /audit` |
| State-transition history | Audit `RUN_STATE_CHANGED`, `NODE_STATE_CHANGED` (from → to, cause) | timeline view |
| Decision / approval history | `decisions` + `GATE_*` events | `GET /runs/{id}/decisions` |
| Retry evidence | `NODE_ATTEMPT_FAILED` (classification), `RETRY_SCHEDULED` (attempt, delay) | timeline, metrics |
| Rollback / compensation evidence | `ROLLBACK_*`, `COMPENSATION_*`, workspace disposal record, re-promotion smoke result, non-rollbackable effects list | timeline, evidence pack |
| Replanning evidence | `REPLAN_*`, `ARTIFACT_STALE`, `GATE_REVOKED`, `GRAPH_VERSION_CREATED` | timeline, graph versions |
| Metrics | Computed **only from audit events** (CON IX) by `observability/metrics.py` | `GET /metrics/reliability`, `orch metrics` |

### 7.2 Metric definitions (population = runs selected by filter; default all runs in the DB)

| Metric | Formula |
|--------|---------|
| Workflow success rate | `COMPLETED ÷ runs with a terminal outcome`. `SAFE_STOPPED` counts as not completed but is reported separately as "resumable" |
| Failure rate | `(FAILED + ABORTED + SAFE_STOPPED) ÷ runs with a terminal outcome`, broken down by outcome |
| Retry frequency | `retry attempts ÷ total node attempts`; also retries per run |
| Rollback / compensation frequency | `runs with ≥1 ROLLBACK_COMPLETED ÷ runs`; same for `COMPENSATION_COMPLETED`; also raw counts |
| End-to-end latency | `terminal_ts − created_ts`, split into **active time** and **human-wait time** (sum of gate open intervals); p50/p95 over the population |
| Per-stage latency | Attempt `ended − started` per node ID, p50/p95 |
| Unrecovered failure count | Failure episodes with no `RECOVERY_COMPLETED` by the time the run terminated or the query ran |

### 7.3 Mean Time to Recovery

A **failure episode** starts at `FAILURE_DETECTED` (one per failed attempt, failed smoke check,
failed tests or safe-stop entry) and carries an `episode_id` reused by its recovery events:

| Field | Source event |
|-------|--------------|
| `failure_detected_at` | `FAILURE_DETECTED.ts` |
| `recovery_started_at` | First of `RETRY_SCHEDULED` / `ROLLBACK_STARTED` / `COMPENSATION_STARTED` / `RESUME_REQUESTED` for the episode |
| `recovery_completed_at` | `RECOVERY_COMPLETED.ts`, emitted when: the retried node attempt succeeds; rollback completes with workspace disposed and last known-good verified; compensation completes with previous-release smoke passing; or the resumed run's failed node succeeds |
| `recovery_duration` | `recovery_completed_at − failure_detected_at` (NFR-RCV-002) |
| `mechanism` | `retry` / `rollback` / `compensation` / `human_resume` / `fallback` |
| `status` | `recovered` / `unrecovered` / `open` (run not terminal and no recovery yet) |
| `includes_human_wait` | true for `human_resume` and any episode spanning an open gate |

**MTTR = Σ recovery_duration (recovered episodes) ÷ count(recovered episodes).**
Unrecovered and open episodes are **excluded from the denominator** and reported separately with
counts. Reported per run and in aggregate (aggregate across runs is deferrable, CST-008 #5), plus
broken down by mechanism and with/without human wait. **Exclusions** are stated in every output:
AI-backed runs (none expected), open episodes. **Labels**: every metric response carries
`measurement_class: "demonstration"`, the population definition, the run count, a fault-injection
flag count and the statement "synthetic demonstration measurements on a single workstation; not
production statistics" (FR-OBS-007). Fault-injected episodes are included and flagged, because
they are the only failures a deterministic demo produces. That limitation is disclosed.

---

## 8. Security

| Area | Control | Req |
|------|---------|-----|
| Input validation | Pydantic models at every API edge. URL parsed with `urllib.parse`, IDNA-encoded host, lowercase scheme/host, default port removed, fragment preserved, control and non-printable characters rejected, max 2,048 chars (PVT-010) | FR-SHR-002/004, NFR-SEC-001 |
| Allowed schemes | `http`, `https` only (config allow-list; secure default; cannot be widened without a policy exception, SEC-001) | FR-SHR-003 |
| Malicious redirect | No user-info credentials. Self-referential host (configured public base host and aliases) rejected. 302 (not 301) so links are not cached permanently (PD-002). Redirect sets `Cache-Control: no-store` and `Referrer-Policy: no-referrer` | FR-SHR-004 |
| Internal/local addresses | **PD-001 (approved at plan gate (Mani Kumar Vadugu, 2026-10-15))**: reject IP-literal hosts in loopback, private, link-local (incl. 169.254.169.254), unique-local, unspecified and multicast ranges, and the name `localhost`. No DNS resolution is done (the shortener never fetches destinations, so there is no SSRF), so DNS-based internal names are an accepted residual risk | CON V |
| Abuse cases | Enumeration: non-sequential 7-char base62 codes (62⁷ ≈ 3.5×10¹²), uniform 404 without existence hints for unauthenticated reads. Volume: rate limit. Phishing/malware: no reputation lookup (EXC-006, documented limitation) | FR-SHR-006/017 |
| Rate limiting | In-memory token bucket per API key ID, 60/min, `429` + `Retry-After`. Single-instance trade-off documented | FR-SHR-017, PVT-011 |
| Authentication | Static role-mapped API keys `sk_<key_id>.<secret>`. Server stores SHA-256 of the secret (secrets are 256-bit random, so a slow KDF is unnecessary) with constant-time compare. `key_id` is the audit identity. Issuance via `orch keys init` writes `var/secrets/api-keys.json` (gitignored) and prints secrets once. Rotation and revocation are manual (HD-003 accepted limitation) | FR-SHR-019, FR-GOV-003/013, NFR-SEC-004 |
| Authorization | Role matrix per endpoint (orchestrator OpenAPI `x-required-roles`). Agent keys and in-process agent actors refused for human-reserved actions, and refusals audited | FR-GOV-003, NFR-AUT-001, SC-011 |
| Secrets management | No secrets in repo; `.gitignore` covers `var/`; `detect-secrets` baseline in CI and in ST-11b; log redaction filter; problem+json never echoes input secrets | NFR-SEC-002 |
| Dependency risk | Minimal approved dependency list (DEP-001), license allow-list (LIC-001), `pip-audit` with zero high/critical (PVT-012), `uv.lock` pinned | FR-GOV-012 |
| Audit integrity | Append-only table with SQLite triggers rejecting UPDATE/DELETE. Per-run SHA-256 hash chain over canonical JSON. `orch audit verify` and AUD-002 at ST-12. API exposes no mutation endpoints (attempts → 405 + `AUDIT_TAMPER_REFUSED`) | FR-OBS-004 |
| Least privilege | Agent capability sets per role; workspace writes confined to `var/work/<run>/`; path-traversal guard; staging manager is the only component allowed to start/stop staging; runs have no write access to `src/`, `tests/`, `specs/`, `docs/` | CON V, FR-ORC-025 |
| Secure defaults | AI mode off; demo gate-timeout profile off by default; bind to `127.0.0.1`; debug off; docs UI off in staging; strict CORS (none) | CON V |
| Threat modeling | `docs/threat-model.md` (STRIDE per trust boundary TB-1..TB-6): open-redirect abuse, enumeration, injection, abuse volume, approval spoofing, audit tampering, change-set tampering, workspace escape, scanner unavailability. Per-run threat review by ST-11a | NFR-SEC-003 |

---

## 9. Compliance and Change Control

### 9.1 Policy model

Authoritative: [`contracts/policy-set.v1.yaml`](./contracts/policy-set.v1.yaml) (version 1.0.0,
semver; the version is recorded on every run and every evaluation, FR-GOV-006).

| Domain | Checks | Mandatory? | Evaluated at |
|--------|--------|------------|--------------|
| Security (SEC) | SEC-001 scheme allow-list unchanged; SEC-002 secret scan zero findings; SEC-003 dependency vulns zero high/critical; SEC-004 security-sensitive change requires G-SECURITY; SEC-005 threat review covers every impacted interface | all mandatory | ST-11b (SEC-005 at SP-1) |
| Privacy (PRIV) | PRIV-001 no personal-data capture (requirement text and change-set schema/code lexicon) | mandatory | ST-03 and ST-11b |
| Architecture boundary (ARCH) | ARCH-001 requirement does not request an excluded capability (EXC-001..006) | mandatory | ST-03 |
| Audit retention (AUD) | AUD-001 retention ≥ 365 days configured, no auto-deletion (PD-002b / DQ-005); AUD-002 audit hash chain verifies | mandatory | ST-12 |
| Approved dependencies (DEP) | DEP-001 every locked dependency in the approved list | mandatory | ST-11b |
| Licensing (LIC) | LIC-001 licenses in allow-list (MIT, BSD-2/3, Apache-2.0, PSF, ISC); LIC-002 MPL-2.0/LGPL flagged | LIC-001 mandatory, LIC-002 advisory | ST-11b |
| Change control (CHG) | CHG-001 change-set integrity vs approved lock and gate-bound fingerprint; CHG-002 touched components ⊆ approved impact analysis; CHG-003 migrations additive-only; CHG-004 approvals bound to current artifact versions | mandatory | ST-08 (001, 002, 004), ST-11b (003), ST-12 (004) |
| Release criteria (REL) | REL-001 required tests executed and passing; REL-002 run traceability complete; REL-003 no unapproved or expired exception; REL-004 docs finalized against the tested change; REL-005 fallback used (advisory) | REL-001..004 mandatory, REL-005 advisory | ST-12 |

**Evaluation input**: `{policy_set_version, check_id, run_id, node_id, subject artifact versions,
facts}`. **Output**: one record per check with `outcome ∈ {PASS, FAIL, EXCEPTION-REQUESTED,
NOT-APPLICABLE}`, `mandatory`, `evidence` (hashes and paths), `reason`, and `exception_id` when
applicable ([schema](./contracts/schemas/policy-evaluation.schema.json)). Re-evaluations append
new records and never overwrite.

**Blocking rule** (FR-GOV-007): a node's exit criteria fail if any mandatory check evaluated at
that node is `FAIL`, or is `EXCEPTION-REQUESTED` without an `APPROVED`, unexpired exception. A
mandatory FAIL makes the run `SAFE_STOPPED` with reason `policy_fail:<check_id>`.
**One routing rule applies at ST-03**: requirement-level checks (PRIV-001, ARCH-001) that FAIL
on a *requirement that has not yet been clarified* route to G-CLARIFY (FR-ORC-004), because the
human may clarify the requirement into conformance. Progression is still blocked. If the check
still FAILs after clarification (re-evaluated on the new requirement version), the normal rule
applies and the run becomes `SAFE_STOPPED`.

### 9.2 Exception workflow

1. Engineer: `POST /runs/{id}/exceptions` for a FAILed evaluation, with policy, reason, scope
   (run / artifact / check), compensating control, and requested expiry or review condition.
2. A new evaluation is appended with `EXCEPTION-REQUESTED` and a G-EXCEPTION gate opens (blocks).
3. An approver whose key identity differs from the requester's (FR-GOV-017) approves (records approving authority, timestamp, expiry, compensating control) or
   rejects (evaluation remains blocking and the run remains safe-stopped).
4. Resume (approver) is allowed once the cause is excepted (A-016).
5. ST-12 re-checks expiry. An expired exception makes REL-003 FAIL, so release readiness is FAIL
   (edge case in spec). Exceptions under the non-waivable list (Governance §3) are refused at
   request time (for example, an exception to "agents cannot approve").

### 9.3 How a failed mandatory check prevents release readiness (demonstrated)

- **Test path** `test_release_blocked_by_mandatory_fail`: inject SEC-002 finding → ST-11b FAIL →
  run `SAFE_STOPPED` → SP-2 never releases → ST-12 never runs → G-RELEASE never opens.
- **Assessment path** `test_readiness_fail_lists_blocking_reasons`: an exception expires between
  ST-11b and ST-12 → REL-003 FAIL → assessment `FAIL` with reasons → G-RELEASE refuses `ready`
  (`409 assessment_not_eligible`) (US-4 AC2, SC-008).
- Scenario evidence: the SCN-C option-B variant (personal-data answer without exception) produces
  PRIV-001 FAIL → `SAFE_STOPPED`.

### 9.4 Change requests and upstream impact

| Change type | Engine (run-level) | Repository (SpecKit-level) |
|-------------|--------------------|-----------------------------|
| Requirement change in a run | New `normalized-requirement` version → replanning (§3.6), approvals revoked | n/a |
| Contract or schema change | Change Record artifact from ST-05/ST-07; CHG-003 additive check; G-DESIGN approval; contract version bump in workspace | Contract change → Change Record in PR + contract version bump + drift test update + ADR if material |
| Architecture change | Design artifact versioned; G-DESIGN re-approval | ADR new or superseding; Plan gate re-approval |
| Workflow graph or policy set change | Graph/policy version is immutable per run (a run pins the versions it started with) | Bump semver; Change Record; tests; human approval (FR-GOV-009) |
| Tests or docs | Re-run ST-09 / ST-10b via staleness | Same change set as code (CON X) |

**Upstream to downstream impact (repository)**: any change to spec, plan, contract, ADR or policy
requires a recorded impact note (which tasks, tests, docs and evidence become stale). Affected
items are re-run and re-validated before release; the traceability tool flags evidence older
than its source artifact (hash comparison).

---

## 10. Testing

### 10.1 Portfolio

| Category | Location | Examples (non-exhaustive) | Req |
|----------|----------|---------------------------|-----|
| Domain unit | `tests/shortener/unit` | Validation table and property tests (Hypothesis), code generator (charset, length, non-sequential), resolve outcomes | FR-SHR-002–007 |
| API contract | `tests/*/contract` | Drift test, schemathesis, problem+json shape, examples valid | §2.2 |
| Persistence | `tests/shortener/persistence`, `tests/orchestrator/persistence` | Uniqueness constraint, idempotency record, migrations up from empty, audit triggers reject UPDATE/DELETE | FR-SHR-005/013, FR-OBS-004 |
| Integration | `tests/*/integration` | Real SQLite file, uvicorn subprocess, redirect + headers, health readiness with DB down | FR-SHR-015/016 |
| Orchestration state transitions | `tests/orchestrator/state` | Transition tables (allowed and prohibited, parametrized), fork/join, conditional skip, sync holds on suspended branch | FR-ORC-005–008, -037–039 |
| Approval and rejection | `tests/orchestrator/governance` | Approve, rework (bounded at 2), terminate → ABORTED, escalate, stale version refused, agent key refused, self-approval of an exception by the requesting key refused and audited | FR-GOV-001–004, -014–017 |
| Documentation accuracy | `tests/e2e/test_quickstart.py` | Executes every quickstart command against a fresh `var/` and asserts the documented outcome; release review records docs-vs-behavior discrepancies | NFR-DOC-001 |
| Additive-change check | `tests/orchestrator/state`, `tests/e2e` | SCN-A PASS skips ST-05; a change set that modifies existing behavior FAILs the check, reroutes to ST-05 with the reason recorded, and never proceeds as greenfield | SCN-A-AC6 |
| Retry | `tests/orchestrator/reliability` | Transient retried with backoff schedule (virtual clock), permanent never retried, budget exhaustion → SAFE_STOPPED | FR-ORC-014 |
| Timeout | same | Node timeout = transient; gate timeout → SAFE_STOPPED "no decision" | FR-ORC-015, FR-GOV-014 |
| Fallback | same | ST-10b degraded docs, analytics failure does not block redirect | FR-ORC-016, FR-SHR-011 |
| Rollback / compensation | same + e2e | Defective change set → tests fail → workspace discarded; smoke failure → re-promote; compensation failure → SAFE_STOPPED degraded | FR-ORC-017, -035, -042 |
| Safe-stop | same | Each FR-ORC-018 trigger | FR-ORC-018 |
| Resumption | same | Kill at every node boundary → resume → same terminal outcome, no duplicate side effects (PVT-006) | FR-ORC-019, NFR-RCV-001 |
| Replanning | `tests/orchestrator/replan` | Artifact v2 → only closure re-runs; approvals revoked; unaffected nodes untouched (SC-006) | FR-ORC-020–022 |
| Concurrency | `tests/shortener/concurrency`, `tests/orchestrator/concurrency` | 1,000 concurrent creates (PVT-003); concurrent redirects count exactly (A-013); duplicate decision applied once | FR-SHR-014, FR-ORC-028 |
| Security | `tests/*/security` | Scheme/credential/self/private-address rejection, auth/role matrix, no secrets in logs (log capture scan), error bodies leak nothing, path-traversal guard, permission refusal audited | NFR-SEC-*, NFR-AUT-001 |
| Policy | `tests/orchestrator/policy` | Each check PASS/FAIL/N-A; exception lifecycle; expiry → REL-003 FAIL; non-waivable refusal | FR-GOV-005–012 |
| Observability | `tests/orchestrator/observability` | Audit completeness (PVT-008), hash chain, MTTR math (recovered vs unrecovered), labels | FR-OBS-* |
| End-to-end | `tests/e2e` | SCN-A, SCN-B (normal and defective), SCN-C (options A/B/timeout) with scripted decisions; determinism repeat-run comparison | SC-002, SC-010, NFR-DET-001 |
| Release readiness | `tests/release` + `orch release check` | Traceability completeness (SC-007), scans executed, coverage ≥ 85% (PVT-007) | FR-GOV-010/012 |

Every test carries `@pytest.mark.req("<ID>", ...)`. Coverage is measured for `shortener.domain`,
`orchestrator.engine`, `orchestrator.policy` and `orchestrator.observability`.

### 10.2 TDD protocol

Red (write the test, run it, record the failure reason in the task log) → Green (minimum code)
→ Refactor (suite green). The task log in `tasks.md` notes the observed failure message per task
(CON IV), as genuine command output.

### 10.3 Fault-injection harness

A `FaultInjector` capability is available **only** in test configuration and in runs explicitly
labeled `fault-injection`. Faults: `transient_n(node, n)`, `permanent(node)`, `timeout(node)`,
`kill_after(node)`, `scanner_unavailable`, `smoke_fail`, `compensation_fail`, `db_locked`, and
`raise_ambiguity(node)`. `raise_ambiguity` labels the run `finding-injection` instead of
`fault-injection` (analysis finding M1). It is never enabled by default and every injected fault
is audited.

### 10.4 Where TDD is not practical (recorded per CON IV)

- External scanner binaries (pip-audit, detect-secrets): thin adapters are TDD'd against fakes;
  real execution is verified once in an integration test and in ST-11b runs (not
  red-green-able deterministically because of network-dependent advisories).
- Process supervision timing (uvicorn start/stop on Windows): tested with integration tests and
  generous readiness polling rather than strict test-first micro-steps.
- Docs rendering templates: snapshot-tested after the first render.

---

## 11. Scenario Designs

Scenario packs live in `scenarios/<id>/` (requirement input, scripted-decision file for the
automated tests, expected-outcome manifest). Change sets live in `changesets/<id>/<variant>/`
(`manifest.yaml`, `patch.diff`, `REVIEW.md` signed off by the human) and are locked in
`changesets/approved.lock.yaml` (SHA-256 per variant), which the human commits after review.
Releases chain: **R0** (baseline snapshot from git ref `shortener-baseline-v1`, PD-009) → SCN-A
→ R1 → SCN-B → R2 → SCN-C → R3. `orch demo reset` rebuilds `var/` from R0 for repeatable demos.

### 11.1 SCN-A: Greenfield (expiration + basic analytics)

| Aspect | Design |
|--------|--------|
| Initial input | `scenarios/scn-a/requirement.md`: "Link creators can set an optional expiration (UTC). Expired links return a distinct 'expired' outcome. Each link exposes total redirects and last redirect time; analytics must never block redirects and must store no personal data." with 5 explicit ACs |
| Interpretation | ST-02: 4 FR statements, 1 NFR (privacy), `change_kind = new_capability`, links to FR-SHR-008..012. ST-03: all 5 quality checks PASS, PRIV-001 PASS, ARCH-001 PASS → **G-CLARIFY SKIPPED** with recorded reasons (SCN-A-AC1, AC5) |
| Decomposition | ST-06: tasks T-A1 schema (expires_at, link_stats), T-A2 create validation for expiry, T-A3 resolve expired → 410, T-A4 analytics counter with fallback, T-A5 analytics endpoint, T-A6 tests, T-A7 docs, with dependencies and AC links (SCN-A-AC2) |
| Orchestration path | ST-01→02→03→(G-CLARIFY skipped)→05a (additive-change check PASS, SCN-A-AC6)→(ST-05 skipped)→06→07→G-DESIGN→F1{08→09, 10a, 11a}→SP-1→F2{10b, 11b, (G-SECURITY skipped: no security-sensitive component)}→SP-2→12→G-RELEASE→REL-01→13 |
| Approvals | G-DESIGN (approver), G-RELEASE (release-owner) |
| Failure paths | Variant **A-late-ambiguity** (labeled finding-injection): ST-11a raises "Should analytics of expired links remain retrievable?" → ST-11a `SUSPENDED`, G-CLARIFY-1 opens, branches a/b continue to SP-1, which holds; answer → ST-05 replanning mode → only ST-11a (+ ST-10b downstream) re-run → SP-1 releases (SCN-A-AC4). Test-level: transient fault at ST-07 → retry |
| Validation | ST-09 runs baseline regression + new tests in the workspace; smoke on staging: create with expiry in the near future, redirect 302, wait or virtual-clock → 410, analytics count |
| Evidence | EV-001 timeline, EV-002 quality report, EV-003 task plan, EV-004 decision lineage (G-DESIGN, G-RELEASE; + G-CLARIFY-1 in variant), EV-006 JUnit, EV-007 readiness + policy + summary + metrics |
| Terminal outcome | `COMPLETED` (staging = R1) |

### 11.2 SCN-B: Brownfield (custom aliases)

| Aspect | Design |
|--------|--------|
| Initial input | `scenarios/scn-b/requirement.md`: "Add optional custom alias to the existing link-creation flow; conflicting alias → conflict, existing mapping unchanged; aliases follow generated-code rules and exclude reserved words; requests without alias unchanged." |
| Interpretation | `change_kind = modification` (existing creation flow) → **ST-05 required**. Quality checks PASS |
| Impact analysis | ST-05 (static): impacted components `api.links`, `domain.links`, `domain.codes`, `domain.validation`, `persistence.links` (via registry + import graph); interfaces `POST /api/v1/links` (minor bump to 1.2.0); data flows create→persist; tests `tests/shortener/unit/test_codes.py`, `.../test_links.py`, contract tests; docs API reference; regression risks (generated-code path unchanged, reserved-word collisions with `/health`); rollout additive column with default; rollback = discard workspace / re-promote R1 (SCN-B-AC1). Change Record produced |
| Decomposition | T-B1 schema `code_origin`, T-B2 alias validation + reserved list, T-B3 conflict handling (409), T-B4 regression guard, T-B5 tests, T-B6 docs |
| Orchestration path | As SCN-A plus ST-05 and **G-SECURITY** (input-validation component is flagged security-sensitive → conditional gate fires) |
| Approvals | G-DESIGN (design + change control, bound to the change-set fingerprint) (SCN-B-AC2), G-SECURITY, G-RELEASE |
| Failure paths | **B-defective** variant (labeled fault-injection, FR-ORC-036): patch makes alias conflict overwrite the mapping → new conflict test fails in ST-09 → ROLLBACK (workspace discarded, artifacts `rolled_back`, staging still R1) → run `FAILED` with summary (SCN-B-AC4). **B-undeclared-scope** (integration test): patch also touches `api/health.py` → CHG-002 FAIL at ST-08 → `SAFE_STOPPED` "re-analysis required" (SCN-B-AC5). Integrity: modify `patch.diff` after lock → CHG-001 FAIL → `SAFE_STOPPED` |
| Validation | Regression: full baseline + SCN-A tests pass on the workspace; new alias tests pass (SCN-B-AC3); smoke on staging |
| Evidence | EV-001..007 with EV-005 impact analysis; rollback evidence from the defective run |
| Terminal outcome | Normal: `COMPLETED` (R2). Defective: `FAILED` (rolled back, R1 intact) |

### 11.3 SCN-C: Ambiguous ("track who clicks links")

| Aspect | Design |
|--------|--------|
| Initial input | `scenarios/scn-c/requirement.md`: "We need to track who clicks links." |
| Interpretation | ST-03 classifies each item (SCN-C-AC1): completeness FAIL (*missing information*: no acceptance criteria, no purpose); "who" (*unclear term*); testability FAIL; PRIV-001 `FAIL` (*policy conflict* with FR-SHR-012/A-005). At ST-03, failures route to G-CLARIFY rather than safe-stop (§9.1 rule). G-CLARIFY opens with the classified items and the affected requirement text |
| Clarification | Questions with options (SCN-C-AC3): Q1 "What does 'who' mean?" A) aggregate counts per day per link (no personal data) — recommended; B) per-visitor identity (IP/user agent) — requires a privacy exception; C) withdraw the request. Q2 (if A) "Retention of daily buckets?" default: same as link lifetime |
| Path while unresolved | No ST-06+ node starts (SCN-C-AC2); run `AWAITING_HUMAN` |
| After answer A | Decision recorded with lineage → `normalized-requirement` v2 → replanning: ST-02/03 re-run on v2 (all PASS), ST-05 runs (modifies analytics) → rest of graph with change set `scn-c/aggregate-daily` (PD-008) → resume at earliest affected stage (SCN-C-AC4) |
| Failure paths | Option B without exception → PRIV-001 FAIL → `SAFE_STOPPED` (exception may be requested; the human may reject). Option C → `reject_terminate` → `ABORTED`. No answer → timeout → `SAFE_STOPPED` "no decision" (SCN-C-AC5) |
| Validation | Regression (baseline + A + B tests), new daily-bucket tests, PRIV-001 PASS on the change set (no PII fields) |
| Evidence | EV-001..004, EV-006, EV-007; the decision lineage shows question → answer → re-versioned artifacts → resumed stages |
| Terminal outcome | Primary (option A): `COMPLETED` (R3). Variants: `SAFE_STOPPED` (B, timeout), `ABORTED` (C) |

### 11.4 Decisions in scenario runs

Recorded scenario evidence uses **interactive human decisions** via `orch gate decide` with the
human owner's keys. Automated e2e tests use **scripted decision files** with test-only human-role
keys; such decisions are audited with `decision_source = "scripted"` and `labels: ["test"]`, and
are never presented as scenario evidence (PD-006).

---

## 12. Technology Decisions

Full option analyses (question, options, criteria, choice, rationale, consequences, risks,
reversibility, validation) are in [research.md](./research.md). ADRs will be written at the ADR
gate.

| ID | Decision | Choice | Status |
|----|----------|--------|--------|
| R-01 | Language and API stack | Python 3.12, FastAPI, Pydantic v2, uv | **SELECTED (human), 2026-10-15** |
| R-02 | Persistence | SQLite (WAL) via SQLAlchemy Core + Alembic, behind repositories | **SELECTED (human), 2026-10-15** |
| R-03 | Orchestration engine | In-repo engine from scratch, explicit versioned DAG + persisted state machines | **SELECTED (human), 2026-10-15** |
| R-04 | Deployment topology | Two services + CLI in one repo | **SELECTED (human), 2026-10-15** |
| R-05 | Scheduler model | Deterministic superstep scheduler (PD-004) | Approved at plan gate (Mani Kumar Vadugu, 2026-10-15) |
| R-06 | Change-set format and application | Unified diff + manifest + lock, `git apply` into isolated workspace | Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15) |
| R-07 | Contract strategy | Contract-first OpenAPI 3.1 + drift test + schemathesis | Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15) |
| R-08 | Audit integrity | Append-only table + triggers + per-run hash chain | Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15) |
| R-09 | API key scheme | `sk_<id>.<secret>`, SHA-256 at rest, role map file | Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15) |
| R-10 | Tracing | In-house spans + W3C traceparent (OpenTelemetry deferred) (PD-005) | Approved at plan gate (Mani Kumar Vadugu, 2026-10-15) |
| R-11 | Logging | stdlib logging + JSON formatter + redaction | Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15) |
| R-12 | Security scanners | pip-audit, detect-secrets, pip-licenses | Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15) |
| R-13 | CLI | Typer | Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15) |
| R-14 | IDs and time | ULID-style sortable IDs, injectable `IdGenerator` and `Clock` | Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15) |

---

## 13. Traceability

Chain: **Requirement → Scenario → Design → ADR → Task → Code → Test → Validation →
Documentation → Evidence**.

| Link | Carrier |
|------|---------|
| Requirement (FR/NFR/SC/PVT/HD) | `spec.md` stable IDs |
| → Scenario | `SCN-*` sections list requirement IDs; scenario packs carry `satisfies:` front matter |
| → Design | `plan.md` section tables cite requirement IDs; contracts carry `x-requirements` on operations and schemas |
| → ADR | `docs/adr/ADR-nnn-*.md` front matter `requirements:` and `plan_sections:` |
| → Task | `tasks.md` entries cite requirement IDs and test IDs (constitution workflow rule) |
| → Code | Module docstring `Satisfies: FR-…` on domain, engine and policy modules (lightweight; not per function) |
| → Test | `@pytest.mark.req(...)` |
| → Validation | JUnit XML with markers (pytest plugin writes `properties`) + run test-results artifacts |
| → Documentation | Docs front matter `satisfies:` |
| → Evidence | `docs/evidence/<scenario>/<run-id>/manifest.json` exported by `orch evidence export` (real runs only), listing EV-IDs and the hashes of the source audit range |

Tooling: `tools/trace/build_matrix.py` parses all of the above and produces
`docs/traceability.md` (EV-008) plus a JSON matrix. `--check` fails if any C/D requirement lacks
≥1 test **and** ≥1 doc or evidence item (SC-007), or if evidence is older than its source
artifact hash. It also flags orphans and includes them in EV-008 (FR-OBS-010, CR-003):
**tests without a requirement ID tag** (no `@pytest.mark.req`) and **source modules under
`src/` that no task in `tasks.md` references**. A non-empty orphan list fails `--check`. At run level, `GET /trace/requirements/{id}` provides the bidirectional view
inside the engine (FR-OBS-008).

---

## 14. Delivery Sequence, Scope and Schedule

### 14.1 Final scope cut: **PD-010 (resolves DQ-010; approved at plan gate (Mani Kumar Vadugu, 2026-10-15))**

**Must-have (cannot be cut; minimum defensible release)**: CST-008 must-have list **plus**:
SCN-A late-ambiguity variant (SCN-A-AC4 is an acceptance criterion), SCN-B defective and
undeclared-scope variants (AC4/AC5), G-SECURITY conditional gate, compensation path with
injected smoke failure (FR-ORC-042), traceability tool `--check`, evidence export.

**Simplified must-have (allowed reduction if CP-3 is at risk)**:
- SCN-B undeclared-scope demonstrated by integration test only (no recorded scenario run).
- ST-10a/b docs agents render minimal templates (still versioned and traced).
- Per-stage interruption tests for the main path nodes only, if every node boundary is not
  feasible; PVT-006 must then be re-scoped by an explicit human change decision.

**Deferred backlog (disclosed as limitations; may start only after CP-4 with all must-have
evidence produced)**:

| ID | Item | Source |
|----|------|--------|
| BL-01 | AI-backed agent adapter beyond disabled stub | CST-008 #1 |
| BL-02 | PVT-001/002 load tests beyond a simple measured run | CST-008 #2 |
| BL-03 | Horizontal scaling (shared rate limiter, multi-writer DB) | CST-008 #3, NFR-SCL-002 |
| BL-04 | Escalation routing beyond recording | CST-008 #4 |
| BL-05 | Aggregate MTTR across runs (per-run remains) | CST-008 #5 |
| BL-06 | OpenTelemetry exporter | PD-005 |
| BL-07 | Prometheus `/metrics` endpoint | — |
| BL-08 | Read-only reviewer web view | EXC-001 |
| BL-09 | PostgreSQL adapter | R-02 |
| BL-10 | Key rotation and revocation tooling | HD-003 limitation |
| BL-11 | Malware/phishing reputation checks | EXC-006 |
| BL-12 | Durable analytics outbox (no lost increments when the analytics write fails) | Human Gate 4 ruling 2; ADR-019 |
| BL-13 | Unauthenticated redirect rate limiting | CR-003; Spec §NFR-SEC-003 (accepted risk) |
| BL-14 | Full end-to-end interruption test at every node boundary (beyond engine-level stub-agent tests and 3 full E2E interruptions) — *planned, not implemented* | HD-CUT-001 #1 |
| BL-15 | OpenAPI drift normalizer and schemathesis contract tests (T019; drift parts of T035/T099) — *planned, not implemented* | HD-CUT-001 #2 |
| BL-16 | W3C `traceparent` propagation and spans table (T016, T092) — *planned, not implemented* | HD-CUT-001 #3 |
| BL-17 | Full metrics set beyond per-run counts and simple MTTR (T093–T095) — *planned, not implemented* | HD-CUT-001 #4 |
| BL-18 | CI on a second OS (windows-latest) — *planned, not implemented* | HD-CUT-001 #5 |
| BL-19 | Separate evidence-assembly tasks (T138–T145) instead of one generated evidence index — *planned, not implemented* | HD-CUT-001 #6 |
| BL-20 | G-SECURITY conditional gate (PD-007) — *planned, not implemented* | HD-CUT-001 #7 |
| BL-21 | SCN-C option-B-with-exception path (exception shown once via another check instead) — *planned, not implemented* | HD-CUT-001 #8 |

**Scope-control rule**: optional work must not displace mandatory validation or reviewer
evidence. At each checkpoint, any slipping must-have item triggers the cut list above. A backlog
item may start only after recording "CP-4 met" in the task log.

### 14.2 Vertical slices

| # | Slice | Contents | Exit evidence |
|---|-------|----------|---------------|
| 1 | Engineering baseline | `pyproject.toml`, uv lock, ruff, mypy strict, pytest config with `req` marker plugin, `.gitignore` (`var/`), `.gitattributes` enforcing LF (`eol=lf`) for `src/`, `tests/`, `changesets/` (incl. `*.diff` patches) and `specs/**/contracts/` (CR-002; the reference workstation has `core.autocrlf=true`), detect-secrets baseline, `make`-equivalent `tools/check.py` (lint, type, test, coverage), GitHub Actions workflow `.github/workflows/ci.yml` running `tools/check.py` (the test suite) on push and pull request (CST-009) | `tools/check.py` green on empty skeleton, locally and in CI |
| 2 | Walking skeleton | Shortener: create + redirect happy path through API → domain → SQLite. Orchestrator: create run with a 2-node graph, persisted state, one audit event, CLI `orch run show` | e2e test: run created, audit visible; link redirects |
| 3 | Core URL behavior | Validation (incl. PD-001), codes, idempotency, rate limit, auth, health/readiness, persistence-failure handling, problem+json, contract drift and schemathesis, concurrency PVT-003; tag `shortener-baseline-v1` (human) | Shortener suites green; contract v1.0.0 drift-free |
| 4 | Orchestration state model | Graph contract loader, run/node/gate state tables, superstep scheduler, fork/join, conditions, entry/exit criteria, idempotent transitions, artifacts and provenance | State-transition suite green |
| 5 | Approval governance | Keys and roles, gate lifecycle, decisions, timeouts, rework bound, agent refusal, policy evaluator + exceptions | Governance and policy suites green |
| 6 | Reliability controls | Retry/backoff/timeout, classification, safe-stop, resume, interruption recovery, SUT adapter (workspace, change-set integrity, patch, test runner), rollback, staging promotion, compensation, replanning | Reliability and replanning suites green |
| 7 | Observability | Audit hash chain + verify, query API, spans, metrics + MTTR, traceability views | Observability suite green |
| 8 | Three scenarios | Deterministic agents, scenario packs, change sets authored and reviewed by the human, locked; scripted e2e; then **interactive recorded runs** by the human | EV-001..007 per scenario from real runs |
| 9 | Release readiness | Scans, traceability `--check` (including FR-OBS-010 orphan checks), coverage, automated quickstart test and a recorded docs-vs-behavior release review (NFR-DOC-001), README (setup, architecture, testing, limitations, trade-offs, and the section "How AI assistance was used and governed", CST-009), threat model, final summaries, `docs/release-readiness.md` for human sign-off; the human owner creates and pushes the annotated tag `assessment-submission-v1.0` after sign-off (CST-009) | Release check report; CI green on the tagged commit; human sign-off |

### 14.3 Day-level milestones and checkpoints

| Day | Slices | Checkpoint (end of window) |
|-----|--------|-----------------------------|
| Day 1 (AM) | 1, 2 | — |
| Day 1 (PM) | 3 | **CP-1**: shortener baseline green and tagged; contract drift-free. Otherwise cut-list review |
| Day 2 (AM) | 4, 5 | **CP-2 (midday)**: engine runs a full graph with deterministic stub agents, gates and policy blocking. If not met, apply simplified must-have reductions immediately |
| Day 2 (PM) | 6, 7 (core) | **CP-3**: retry/safe-stop/resume/rollback/compensation/replanning suites green; MTTR computed from events |
| Day 3 (AM) | 8 | **CP-4 (midday)**: SCN-A/B/C pass scripted e2e; interactive recorded runs started. Feature freeze |
| Day 3 (PM) | 9 | **CP-5**: release check executed; readiness doc ready for human decision |

### 14.4 Critical path and stop conditions

**Critical path**: slice 1 → 3 (SUT must exist and be tagged) → 4 → 5 → 6 (SUT adapter +
rollback/compensation) → deterministic agents → change sets (human review and lock) → scenario
runs → readiness. Off-path (fill gaps): docs agents, metrics views, threat model writing, README.

**Human-dependent steps on the critical path**: tag the baseline; review and lock change sets;
interactive gate decisions for recorded runs; release sign-off. Waiting on these is blocking by
design.

**Stop conditions** (stop, report, await the human):
- STOP-1: any constitution violation or `/speckit-analyze` CRITICAL finding.
- STOP-2: a requirement cannot be met as specified (for example, PVT-003 fails on SQLite). Report
  with evidence and propose a change. Never weaken a test silently.
- STOP-3: evidence can only be produced by fabrication or by hand-editing outputs. Never do either.
- STOP-4: a checkpoint missed by more than half a day after applying the cut list. Re-plan with
  the human.
- STOP-5: end of timebox. Freeze features and spend the remaining time on honest readiness
  reporting.

### 14.5 Minimum defensible release-readiness outcome

A release-readiness report produced **by actual execution** that shows:
1. The baseline shortener passes its suites.
2. The engine demonstrates fork/join, conditional nodes, gates, retry, safe-stop, resume,
   rollback, compensation, replanning and policy blocking in executed tests.
3. SCN-A, SCN-B and SCN-C each have at least one recorded run with EV-001..007.
4. Scans have been executed with results recorded.
5. Traceability `--check` results are recorded.
6. All deviations are listed as limitations or as FAIL items with reasons.

A truthful `FAIL` with documented reasons is defensible. An unsupported `PASS` is not. The human
owner makes the final decision (Governance §6).

---

## 15. Proposals Requiring Human Approval at the Plan Gate

**Plan gate decision**: all 13 proposals below (PD-001, PD-002, PD-002b, PD-003 to PD-012) were
**approved as written**. Approver: Mani Kumar Vadugu (human owner). Date: 2026-10-15.

| ID | Proposal | Section | Rationale |
|----|----------|---------|-----------|
| PD-001 | Reject IP-literal private/loopback/link-local/multicast hosts and `localhost` | §8 | CON V malicious-redirect coverage; not in spec explicitly |
| PD-002 | Redirect status 302 with `Cache-Control: no-store` | §8 | Keeps analytics accurate; avoids permanent caching |
| PD-002b (DQ-005) | Audit retention: ≥ 365 days in policy AUD-001; no automated deletion in the prototype; JSONL export with hash-chain verification; any purge is a destructive action requiring human approval (out of scope) | §9 | Covers the review period with margin (A-007) |
| PD-003 (DQ-007) | Failure classification table | §6.2 | Required by CON VIII |
| PD-004 | Deterministic superstep scheduler | §3.5 | NFR-DET-001 with real concurrency |
| PD-005 | In-house tracing; OpenTelemetry deferred | §7 | Fewer dependencies in the timebox |
| PD-006 | Scripted decisions allowed only in automated tests, labeled; recorded evidence uses interactive human decisions | §11.4 | CON III / CON X integrity |
| PD-007 | G-SECURITY conditional gate (security-sensitive components registry) | §5 | Brief's security-sensitive action gate |
| PD-008 | SCN-C conforming option = daily aggregate counts per link (UTC) via change set `scn-c/aggregate-daily` | §11.3 | Smallest capability satisfying "who" without personal data; outside EXC-005 |
| PD-009 | Baseline snapshot ref `shortener-baseline-v1` (git tag created by the human) as R0 | §11 | Scenario reproducibility after manual merges |
| PD-010 (DQ-010) | Final scope cut and backlog | §14.1 | CST-008 |
| PD-011 | Interruption recovery parks runs in `SAFE_STOPPED` (human resume), not auto-resume | §6.3 | FR-ORC-019 "authorized human action" |
| PD-012 | ST-09 test failure → rollback → run `FAILED` (no automatic rework loop) | §6.2 | Deterministic terminal outcome; rework is a human choice via a new run |

---

## 16. Pre-Implementation Review Rulings (CR-006)

**Source**: [docs/reviews/pre-implementation-review.md](../../docs/reviews/pre-implementation-review.md).
**Ruled by**: Mani Kumar Vadugu (human owner), 2026-10-15, CR-006 step 2. Where this section
conflicts with earlier sections of this plan (§3.4 ST-05 row, §3.6 step 5, §6, §11.1, §11.3,
§11.4), this section governs.

### 16.1 Rulings on critical findings

| Finding | Ruling |
|---------|--------|
| C1 Change-set binding | For runs that open G-CLARIFY, the change set is selected **after** the clarification decision, from a human-locked catalog keyed by `(scenario, option_id)`. No catalog entry for the decided option → run `FAILED` (reason recorded). A `free_text` answer is never interpreted: it reopens clarification with the text recorded. At most **2** clarification rounds per gate per run; a third → `SAFE_STOPPED` ("clarification limit exceeded") |
| C2 Impact independence | ST-05 computes impact only from the normalized requirement, the component registry and the baseline (current release) import graph. The change-set manifest is **never** an ST-05 input, so CHG-002 compares touched files against an analysis made independently of the change |
| C3 Late-ambiguity routing | A G-CLARIFY-n answer is an input **only to the raising node**, which resumes from `SUSPENDED`. No ST-05 replanning occurs, G-DESIGN is not revoked, and ST-08/ST-09 are not re-run (their attempt counts stay unchanged) |
| C5 Scanner determinism | In runs, SEC-003 evaluates against a local, hash-pinned advisory snapshot (hash recorded on every evaluation; no network access). Missing snapshot or hash mismatch → SEC-003 `FAIL`, never PASS. The live scan runs only in `orch release check` |

### 16.2 Join and skip semantics (single authoritative table)

| Predecessor states | Successor effect |
|--------------------|------------------|
| All `SUCCEEDED`/`SKIPPED`, condition true, entry criteria met | `READY` |
| All `SUCCEEDED`/`SKIPPED`, condition false | `SKIPPED` with reason; a skip never counts as a failure downstream |
| All done, entry criteria unmet | `BLOCKED` (`NODE_ENTRY_REFUSED`) |
| Any `PENDING`/`READY`/`RUNNING`/`RETRY_WAIT`/`SUSPENDED`/`BLOCKED`/`STALE` | Stays `PENDING`; sync points hold |
| `FAILED_PERMANENT` with a declared failure edge (e.g. REL-01 `smoke_failed` → REL-02) | Only the edge target may become `READY`; normal successors stay `PENDING` |
| `FAILED_PERMANENT` without a declared edge, or retry budget exhausted | The node's declared failure behavior applies (`safe_stop`, `fail_run`, `rollback_then_fail_run`); no successor becomes `READY` |
| Sync node (SP-1, SP-2) | Releases only when every incoming branch is `SUCCEEDED` (or `SKIPPED` where conditional) |
| ST-13 | `READY` once the run's terminal path (COMPLETED, FAILED or ABORTED) is decided, regardless of other predecessor states |

### 16.3 Runtime and governance specifications

- **Timeout enforcement and attempt fencing**: each agent attempt runs in a child subprocess
  (Windows: new process group, process-tree kill on timeout). Each attempt carries a fencing
  token; artifact writes and transitions with a superseded token are refused and audited.
  Timeout → tree killed → `FAILED_TRANSIENT` → retry per §6.
- **Re-promotion without migration**: REL-02 starts the previous release snapshot against the
  current staging DB without running migrations; readiness and smoke checks never compare
  migration heads. Migrations run only on forward promotion (REL-01), additive-only (CHG-003).
- **Demo reset**: `orch demo reset` never deletes or truncates `var/orchestrator/orchestrator.db`.
- **`decision_source`**: derived server-side from the authenticated key's class (test-only keys →
  `scripted`, human keys → `interactive`); any client-supplied value is ignored.
- **Key custody**: approver (and other human-role) keys are created by the human in their own
  terminal, outside the coding-assistant session; secrets are never stored in the repository.
- **Change-set lock**: `changesets/approved.lock.yaml` is verified against an annotated git tag
  created by the human owner; a missing or lightweight tag, or any difference from the tagged
  content → CHG-001 `FAIL`.
- **Retry-budget extension on resume**: an approver may grant additional attempts to named nodes
  when resuming; the grant (approver, key ID, nodes, attempts, reason) is audited. Without a
  grant, a node with an exhausted budget keeps resume refused.

### 16.4 Disclosed limitations (to be listed in `docs/limitations.md`)

- **Separation of duties is single-person**: FR-GOV-017 is enforced between key identities, but
  one person holds all human keys (A-008); this is not organizational segregation of duties.
- **SCN-A-AC4** is demonstrated only through the labelled `finding-injection` variant.
- **NFR-DET-001** holds only for virtual-clock, scripted-decision runs; interactive recorded
  runs are not repeat-comparable.

### 16.5 HD-CUT-001: Scope cut (human decision)

**Decider**: Mani Kumar Vadugu (human owner) · **Date**: 2026-10-15 · **Source**: review file,
"Q21 cut list". Cut items are listed in the §14.1 backlog (BL-14..BL-21) as *planned, not
implemented*. Where this decision conflicts with earlier sections (e.g. the §14.1 must-have
list, PD-005, PD-007), this decision governs.

| # | Cut | Retained instead | Backlog |
|---|-----|------------------|---------|
| 1 | PVT-006 full E2E interruption at every boundary | Engine-level interruption at every boundary with stub agents, plus 3 full E2E interruptions (mid-F1, open gate, REL-01) | BL-14 |
| 2 | OpenAPI drift normalizer and schemathesis (T019, drift parts of T035/T099) | JSON Schema validation and hand-written contract tests | BL-15 |
| 3 | `traceparent` and spans (T016, T092) | `run_id` correlation and attempt timestamps | BL-16 |
| 4 | Full metrics (T093–T095) | Per-run counts and a simple MTTR | BL-17 |
| 5 | CI on two OSes | CI on one OS | BL-18 |
| 6 | Separate evidence assembly (T138–T145) | One generated evidence index | BL-19 |
| 7 | G-SECURITY (PD-007, not a spec requirement) | — | BL-20 |
| 8 | SCN-C option B with exception | SCN-C variants A, C (abort) and timeout; exception path shown once (e.g. SEC-003 offline exception) | BL-21 |

**Never cut**: transitions + audit, fork/join with sync points, gates (timeout, rework,
terminate), policy blocking + exceptions, retry/safe-stop/resume, workspace rollback, staging
compensation, stale-closure replanning, and the human's interactive recorded runs of SCN-A,
SCN-B and SCN-C.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-sdlc-url-shortener/
├── spec.md
├── plan.md              # this file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1 (OpenAPI, graph, policy, JSON Schemas, examples)
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks; not created here)
```

### Source Code (repository root)

```text
pyproject.toml · uv.lock · README.md (incl. "How AI assistance was used and governed", CST-009)
.github/workflows/ci.yml    # GitHub Actions: runs tools/check.py (CST-009)
src/
├── common/                 # JSON logging, correlation/traceparent, Clock, IdGenerator (no domain types)
├── shortener/
│   ├── api/                # routers, auth, idempotency, ratelimit, problem+json, health
│   ├── domain/             # links, codes, validation, resolve (+ expiration/analytics via change sets)
│   ├── persistence/        # repository protocols, sqlalchemy impl, alembic/ migrations
│   ├── telemetry/
│   ├── config.py
│   └── app.py
└── orchestrator/
    ├── engine/             # graph, state, scheduler, transitions, gates, retry, replan, recovery
    ├── policy/             # loader, evaluator, checks/, exceptions
    ├── agents/             # protocol, capabilities, deterministic/, ai_backed/ (disabled stub)
    ├── sut/                # workspace, changeset, patch, testrunner, staging, releases
    ├── audit/              # store, hashchain, query
    ├── observability/      # metrics (MTTR), spans, logging
    ├── trace/              # run-level traceability
    ├── security/           # keys, roles, permission guard
    ├── persistence/        # repositories, alembic/ migrations
    ├── definitions/        # registry/components.yaml (component → paths, interfaces, tests, docs, security_sensitive)
    ├── api/
    ├── cli/
    └── config.py
policy/                     # approved-dependencies.yaml, license-allowlist.yaml (policy set itself: contracts/)
changesets/                 # scn-a/normal, scn-b/{normal,defective,undeclared-scope}, scn-c/aggregate-daily, approved.lock.yaml
scenarios/                  # scn-a, scn-b, scn-c: requirement.md, decisions.scripted.yaml, expected.yaml
tools/                      # check.py, trace/build_matrix.py, perf/measure.py
docs/                       # adr/, architecture.md, threat-model.md, testing.md, limitations.md, release-readiness.md, traceability.md, evidence/
tests/
├── shortener/{unit,contract,persistence,integration,concurrency,security}
├── orchestrator/{unit,state,governance,policy,reliability,replan,observability,security,concurrency,api,contract,persistence}
├── e2e/
└── release/
var/                        # runtime only, gitignored: dev/, staging/, work/, releases/, orchestrator/, logs/, secrets/
```

**Structure Decision**: single Python project with two top-level service packages that share
only `common/` (infrastructure utilities, no domain types) and the versioned contracts. The
shortener package plus `tests/shortener/` and the shortener contract form the **system-under-change
unit** that the engine snapshots into releases and workspaces.

## Complexity Tracking

No constitution violations. Justified complexity (CON VII):

| Complexity | Why needed | Simpler alternative rejected because |
|------------|------------|--------------------------------------|
| Two services + staging + isolated copies | FR-ORC-032/040 require isolation from the working tree and a separate staging instance; trust boundary TB-4 | A single process would host the system under change inside the control plane and blur rollback and compensation evidence |
| Custom orchestration engine | Human-owner requirement; the assessment's critical differentiator | Off-the-shelf engines would own the governed semantics being assessed |
| Superstep scheduler | Real parallelism plus reproducible event order (NFR-DET-001) | A naive `asyncio` free-for-all gives nondeterministic audit order; purely sequential execution fails FR-ORC-006 |
| Hash-chained audit | Tamper evidence for append-only claims (FR-OBS-004) | Triggers alone do not detect out-of-band file edits |
| Release snapshots (R0..Rn) | Compensation needs a previous release to re-promote; brownfield chain | Re-building from the working tree would violate FR-ORC-043 and break reproducibility |

### Constitution exceptions (Governance §2)

| ID | Principle / rule | Scope | Reason | Compensating control | Approver | Approved | Review condition |
|----|------------------|-------|--------|----------------------|----------|----------|------------------|
| CEX-001 (constitution exception) | Development Workflow: "Every task MUST reference … the test(s) that verify it" | tasks.md human-decision and checkpoint tasks | These tasks are human decisions, not code; no automated test can verify a decision | Verification = a recorded human decision (approver, timestamp, artifact version) in the decision/audit log; T127 traceability check confirms each such decision exists | Mani Kumar Vadugu (human owner) | 2026-10-15 | Re-evaluated at `/speckit-converge` |

## Architecture Decision Records

19 ADRs in [`docs/adr/`](../../docs/adr/README.md) (all accepted at Human Gate 4, Mani Kumar Vadugu,
2026-10-15; numbering updated by CR-002):

ADR-001 language and framework (R-01) · ADR-002 persistence (R-02) · ADR-003 orchestration model:
in-repo engine and superstep scheduler (R-03, R-05, PD-004) · ADR-004 application architecture,
topology and local execution (R-04) · ADR-005 dependency graph representation · ADR-006 change
sets and isolated workspaces (R-06) · ADR-007 contract-first versioning and additive migrations
(R-07) · ADR-008 audit integrity (R-08) · ADR-009 policy model and exceptions (R-12) · ADR-010
authentication and authorization (R-09) · ADR-011 observability, metrics and MTTR (R-10, R-11) ·
ADR-012 rollback versus compensation · ADR-013 retry, fallback and safe-stop policy · ADR-014
short-code generation and collision handling · ADR-015 workflow state persistence (R-14) · ADR-016
human approval model · ADR-017 dynamic replanning · ADR-018 testing strategy · ADR-019 analytics
consistency.

## Change Log

| CR | Date | Approver | Change | Impact |
|----|------|----------|--------|--------|
| CR-002 | 2026-10-15 | Mani Kumar Vadugu (Human Gate 4) | Resolve the five ADR-gate conflicts and apply rulings 2 and 4 | See impact analysis below |
| CR-003 follow-up | 2026-10-15 | Mani Kumar Vadugu | plan aligned with CR-003; glossary defined by human owner | Contracts: workflow graph 2.0.0 → 2.1.0 and orchestrator API 2.0.0 → 2.1.0 (MINOR; Change Record in contracts/README.md) |
| CR-004 | 2026-10-15 | Mani Kumar Vadugu | Provenance label replaced with the fixed AI-assistance text (§Summary, §4) | Spec FR-ORC-034, research R-06, data model, ADR-006 and tasks aligned; no contract version change |
| CR-005 | 2026-10-15 | Mani Kumar Vadugu | Spec interruption edge case aligned with §6.3 / PD-011 | No plan change needed |
| CR-006 step 2 | 2026-10-15 | Mani Kumar Vadugu | Pre-implementation review rulings C1, C2, C3, C5; join/skip table; runtime and governance specifications; three disclosed limitations (§16) | plan.md only. Pending alignment: workflow graph (ST-05 inputs, REL-01/REL-02 edge, clarify rounds), gate-decision schema (`decision_source`), ADRs, quickstart, tasks |
| CR-006 step 3 | 2026-10-15 | Mani Kumar Vadugu | HD-CUT-001 scope cut recorded (§16.5); cut items added to backlog BL-14..BL-21 as planned, not implemented | plan.md only. Pending alignment: §14.1 must-have list (G-SECURITY), PD-005, PD-007, policy SEC-004, workflow graph (G-SECURITY node), tasks |
| CR-006 | 2026-10-15 | Mani Kumar Vadugu | Pre-implementation review dispositioned: §16 rulings (steps 2–3); tasks.md regenerated to 54 tasks with false dependencies removed, change sets authored in parallel with the engine and traceability check in CI from Phase 1 (step 4); change-log rows in spec.md and plan.md (steps 5–6) | Contracts, ADRs and quickstart alignment is task T201 (human approval required before T003) |
| HD-CUT-001 | 2026-10-15 | Mani Kumar Vadugu | Human scope-cut decision (§16.5): 8 review cut-list items deferred | Backlog BL-14..BL-21 marked planned, not implemented; disclosed in docs/limitations.md (T248) |
| HD-CUT-002 | 2026-10-15 15:55 | Mani Kumar Vadugu | The re-cut schedule cannot meet the 2026-10-16 15:30 deadline. Deliver a lean implementation that demonstrates every assessed capability, without per-task ceremony. tasks.md is retained as the planning record; implementation follows the lean slice in [docs/scope/lean-slice.md](../../docs/scope/lean-slice.md) | Built scope and items "planned, not implemented" listed in docs/scope/lean-slice.md; T201 relabelled "CR-006 step 7"; open questions for the human owner listed there |
| Analysis remediation | 2026-10-15 | Mani Kumar Vadugu | §3.1 modules added (criteria, fallback, faults; tools/perf); §10.3 `raise_ambiguity` → `finding-injection`; CEX-001 recorded under Complexity Tracking | Tasks regenerated with stable IDs (see tasks.md) |

### CR-002 impact analysis

| # | Change | Artifacts changed | Downstream impact |
|---|--------|-------------------|-------------------|
| 1 | ADR numbering: scheduler is ADR-003, graph representation is ADR-005; 19 ADRs | plan.md (§3.5, Constitution Check VII, Architecture Decision Records list) | References only; no behavior change |
| 2 | Alembic batch mode prohibited for append-only tables; plain `ADD COLUMN` only | research.md R-02 | Constrains future migrations of `audit_events` and `policy_evaluations`; needs a migration test asserting triggers survive (ADR-002/008). No requirement change |
| 3 | G-RELEASE rework removed; `not_ready` → ST-13 → `FAILED` with blocking reasons (ruling 4) | plan.md §3.2, §3.4, §5.1, §5.3; data-model.md §2.1, §2.3; contracts: `workflow-graph` 2.0.0 (file renamed to `.v2.yaml`), `gate-decision.schema.json` 2.0.0, `orchestrator-api.openapi.yaml` 2.0.0 (Change Record in contracts/README.md); ADR-016 | MAJOR contract bumps per contracts/README rule 4; no implementation or run exists, so no migration. Interpretation recorded: a release decision is not an approval rejection (FR-GOV-003), so FR-GOV-015's `ABORTED` rule does not apply. Planned governance tests change accordingly |
| 4 | Safe-stop triggers added: scheduler stall, interruption detected at startup | plan.md §6.1; data-model.md §2.1 | Aligns the plan with ADR-003/ADR-013 and PD-011; adds a scheduler-stall test |
| 5 | Slice 1 adds `.gitattributes` (LF for `src/`, `tests/`, `changesets/` incl. patches, contracts) | plan.md §14.2 | One additional slice-1 task; mitigates CRLF risk for `git apply` (ADR-006) |
| 6 | Backlog BL-12 durable analytics outbox (ruling 2) | plan.md §14.1 | Disclosed limitation; no must-have scope change |

Not affected: spec.md requirements, IDs, targets and scope; policy set; shortener API contract;
other JSON Schemas; quickstart; checklists. ADR statuses remain **Proposed**.
