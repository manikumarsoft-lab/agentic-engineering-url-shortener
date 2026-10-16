# Research and Technology Decisions: Agentic Software Engineering System: URL Shortener

**Phase**: 0 (`/speckit-plan`) · **Date**: 2026-10-15 · **Plan**: [plan.md](./plan.md)

Status legend: **SELECTED (human)** = chosen by the human owner (Mani Kumar Vadugu) on
2026-10-15 in the planning session. **PROPOSED** = agent recommendation awaiting the Plan/ADR
gate. Each decision becomes an ADR in `docs/adr/` at the ADR gate.

Common assessment criteria (weights reflect the assessment's focus):

| Code | Criterion |
|------|-----------|
| K1 | Fits the 2–3 day timebox (CST-005) |
| K2 | Runs on one workstation, no extra infrastructure, no AI key (NFR-RUN-001, CST-006) |
| K3 | Demonstrability of governed orchestration (ASMT §4.4) |
| K4 | Testability and determinism (CON IV, NFR-DET-001) |
| K5 | Contract and schema rigor (executable validation) |
| K6 | Security posture and dependency footprint (CON V, DEP/LIC policies) |
| K7 | Replaceability (CON VII) |

Environment facts observed on the reference workstation (2026-10-15): Python 3.12.10, uv 0.13.1,
Node 24.20.0, npm 11.19.0 present; Java, Go, .NET and Docker absent.

---

## R-01: Language and API stack: **SELECTED (human)**

- **Question**: Which language and HTTP framework for both services?
- **Options**: (a) Python 3.12 + FastAPI + Pydantic v2; (b) TypeScript/Node 24 + Fastify +
  TypeBox/Zod; (c) Java/Kotlin + Spring Boot.
- **Assessment**: (a) strong on K1, K2, K4, K5 (OpenAPI 3.1 and JSON Schema from models;
  schemathesis and Hypothesis), adequate on K6. (b) strong on K2, K5, medium on K1 (more
  scaffolding), weaker K4 tooling for property-based contract testing. (c) fails K2 (no JDK) and
  K1.
- **Selected**: (a).
- **Rationale**: fastest test-first loop; contract generation and contract testing tools are
  mature; one language across engine, agents, scanners and tests.
- **Consequences**: async FastAPI with sync SQLAlchemy Core in the threadpool for SQLite
  simplicity; mypy strict + ruff required to offset dynamic typing.
- **Risks**: runtime type errors (mitigated by strict mypy and Pydantic at boundaries); lower
  throughput (PVT-001/002 are non-gating).
- **Reversibility**: medium. The HTTP contracts are language-neutral, so a service could be
  re-implemented behind the same contract.
- **Validation**: slice 1 toolchain green; slice 3 contract drift and schemathesis green.
- **As built (CR-009, proposed; awaiting human owner approval)**: (a) is implemented with pip
  and the pinned `requirements.lock` instead of uv; FastAPI handlers are synchronous and use
  stdlib `sqlite3`, not SQLAlchemy Core; there is no mypy, ruff, Hypothesis or schemathesis.
  Contract conformance is the drift test of the app-generated OpenAPI document (CR-007). See
  [ADR-020](../../docs/adr/ADR-020-python-toolchain-as-built.md).

## R-02: Persistence: **SELECTED (human)**

- **Question**: Where do links, workflow state and audit live?
- **Options**: (a) SQLite (WAL) via SQLAlchemy Core + Alembic behind repository protocols;
  (b) PostgreSQL (Docker or native); (c) SQLite + tested Postgres adapter.
- **Assessment**: (a) best K1/K2/K4; transactions allow state + audit atomically; triggers
  enforce append-only. (b) best production fidelity, fails K2 (no Docker) and risks PVT-009.
  (c) doubles the persistence test matrix (K1).
- **Selected**: (a).
- **Consequences**: single writer per DB file; `BEGIN IMMEDIATE` for write transactions;
  `busy_timeout=5000`; SQLite busy errors classified transient; separate DB file per instance.
  Alembic with `render_as_batch=True` for SQLite ALTER limitations, **except for append-only
  tables** (`audit_events`, `policy_evaluations`): batch mode is prohibited there because it
  recreates the table and would drop the append-only triggers; only plain
  `ALTER TABLE ... ADD COLUMN` is allowed (CR-002, ADR-002, ADR-008).
- **Risks**: write contention under PVT-003 (1,000 concurrent creations). Mitigation: short
  transactions; the test measures it, and STOP-2 applies if it cannot be met. Horizontal scaling
  is not demonstrated (NFR-SCL-002, documented).
- **Reversibility**: high. Repository protocols plus SQLAlchemy Core keep SQL portable; Postgres
  adapter is backlog BL-09.
- **Validation**: persistence suite; PVT-003 concurrency test; audit trigger tests.
- **As built (CR-009, proposed; awaiting human owner approval)**: SQLite (WAL) through stdlib
  `sqlite3`, with no SQLAlchemy, Alembic or repository protocols. Schemas are created with
  `CREATE TABLE IF NOT EXISTS`; there are no migrations or migration tests. Append-only triggers
  are on `audit` and `policy_evaluations`. The concurrency test covers 200 parallel creations,
  not PVT-003's 1,000 (T273). See [ADR-021](../../docs/adr/ADR-021-sqlite-stdlib-persistence.md).

## R-03: Orchestration engine: **SELECTED (human)**

- **Question**: How is the executable orchestration engine built (it must live in this repo)?
- **Options**: (a) from scratch: versioned DAG + persisted state machines + scheduler;
  (b) own DAG with `transitions` library for node state machines; (c) build on LangGraph
  graph and checkpointing.
- **Assessment**: (a) maximal K3/K4, highest code volume. (b) small saving, and persistence and
  replay of library state are awkward. (c) gives execution and checkpointing, but the library
  would own the governed semantics being assessed and couples to an AI framework (conflicts with
  the HD-001 deterministic default).
- **Selected**: (a).
- **Consequences**: transition tables are data (testable by parametrization); the graph is a
  versioned YAML contract; every transition is one DB transaction with its audit event.
- **Risks**: scope (mitigated by a small core, slice ordering, CP-2 checkpoint).
- **Reversibility**: low-medium. The engine is the product; its public surface is the
  orchestrator API and graph contract.
- **Validation**: state-transition, governance, reliability and replanning suites; e2e scenarios.

## R-04: Deployment topology: **SELECTED (human)**

- **Question**: How are processes laid out?
- **Options**: (a) two services (shortener, orchestrator) + CLI in one repo; (b) single process;
  (c) CLI-only orchestrator.
- **Selected**: (a).
- **Rationale**: FR-ORC-032/040 need separate shortener processes anyway (isolated copies,
  staging); a clear trust boundary (TB-4); HTTP gates with role keys (HD-003).
- **Consequences**: process supervision (`StagingManager`) with port allocation and readiness
  polling; W3C traceparent across services.
- **Risks**: Windows process lifecycle quirks (mitigation: `subprocess` with
  `CREATE_NEW_PROCESS_GROUP`, explicit terminate-then-kill, integration tests).
- **Reversibility**: medium.
- **Validation**: integration tests for staging promote/compensate; e2e.

## R-05: Scheduler model: approved at plan gate (Mani Kumar Vadugu, 2026-10-15) (PD-004)

- **Question**: How do parallel branches execute while keeping evidence reproducible?
- **Options**: (a) superstep scheduler: run all ready nodes concurrently, commit results in
  node-ID order; (b) free-running asyncio tasks committing on completion; (c) strictly
  sequential topological execution.
- **Assessment**: (a) real concurrency and deterministic committed order (K3, K4). (b)
  nondeterministic audit order breaks NFR-DET-001 comparisons. (c) fails FR-ORC-006 in spirit
  (no true parallelism).
- **Selected**: (a).
- **Consequences**: a branch may wait up to one sibling's step duration; timers (retry,
  gate timeout) advance the scheduler independently of steps.
- **Risks**: perceived latency at the joins (acceptable at demo scale).
- **Reversibility**: high (scheduler is one module behind an interface).
- **Validation**: repeat-run determinism test; fork/join tests with virtual clock.

## R-06: Change-set format and application: Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15)

- **Question**: How does ST-08 apply, in isolation, a change set authored with AI assistance
  (Claude Code) during development and reviewed and locked by the human owner (FR-ORC-032–036,
  CR-004)?
- **Options**: (a) unified diff + `manifest.yaml` + `approved.lock.yaml`, applied with
  `git apply --check` then `git apply` inside a copied workspace; (b) full-file overlay
  directories; (c) Python AST transforms.
- **Assessment**: (a) human-reviewable, precise scope extraction for CHG-002, standard tool;
  (b) simpler application but hides intent and makes scope reviews harder; (c) over-engineered.
- **Selected**: (a). The manifest declares `scenario`, `variant`, `base_release`,
  `declared_components`, `contract_version_after`, `migration_class`, `ai_assistance_disclosure`
  (fixed required text equal to the FR-ORC-034 label, CR-004), and the human reviewer. The lock stores the SHA-256 of the manifest+patch bundle. ST-08 verifies
  lock == bundle == gate-bound fingerprint (CHG-001), then compares actually-touched files with
  approved impact components (CHG-002).
- **Consequences**: `git` CLI is a prerequisite (behind a `PatchApplier` interface); workspaces
  live under `var/work/`.
- **Risks**: line-ending (CRLF) differences on Windows. Mitigation: `.gitattributes` enforcing LF
  for `src/`, `tests/`, `changesets/`; `git apply --whitespace=nowarn`; integration test on
  Windows.
- **Reversibility**: high.
- **Validation**: integrity and scope tests; defective-variant rollback test.

## R-07: Contract strategy: Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15)

- **Question**: How are API and schemas specified and validated?
- **Options**: (a) contract-first OpenAPI 3.1 + JSON Schema committed, with app-generated spec
  drift test, schemathesis and jsonschema validation of emitted documents; (b) code-first
  (generated spec is the contract); (c) prose-only.
- **Selected**: (a).
- **Rationale**: committed contracts are reviewable change-control objects (CON VI) with semver
  and Change Records; drift tests make them executable.
- **Consequences**: Pydantic models must reproduce the contract exactly. The drift test
  normalizes ordering and ignores FastAPI cosmetic fields.
- **Risks**: normalization friction (time-boxed; fallback is a structural subset comparison of
  paths, methods, status codes and schemas, recorded as a limitation).
- **Reversibility**: high.
- **Validation**: contract test suites.

## R-08: Audit integrity: Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15)

- **Options**: (a) append-only table + SQLite `BEFORE UPDATE/DELETE` triggers raising errors +
  per-run SHA-256 hash chain over canonical JSON (sorted keys, UTF-8, no whitespace); (b) triggers
  only; (c) separate append-only JSONL file.
- **Selected**: (a). Event and hash are written in the same transaction as the state change.
  `orch audit verify` recomputes the chain (AUD-002).
- **Risks**: someone with file access can rewrite the entire chain consistently. This is a
  documented residual risk; the export includes a head hash to record externally.
- **Validation**: tamper tests (direct SQL UPDATE refused; out-of-band modification detected).

## R-09: API key scheme: Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15)

- **Options**: (a) `sk_<key_id>.<secret>`, SHA-256(secret) at rest, constant-time compare, role
  map JSON in `var/secrets/`; (b) bcrypt/argon2 hashed keys; (c) JWTs.
- **Selected**: (a). Secrets are 256-bit random, so a slow KDF adds no meaningful protection; the
  key ID gives a non-secret audit identity (FR-GOV-013).
- **Risks**: manual rotation (HD-003 accepted limitation; BL-10).
- **Validation**: auth matrix tests; log and audit scans for secret patterns.

## R-10: Tracing: approved at plan gate (Mani Kumar Vadugu, 2026-10-15) (PD-005)

- **Options**: (a) in-house spans table + W3C traceparent propagation, trace ID = run ID;
  (b) OpenTelemetry SDK with file exporter; (c) logs only.
- **Selected**: (a). It meets the reconstruction requirement with zero extra dependencies and
  deterministic tests; OpenTelemetry export is backlog BL-06.
- **Reversibility**: high (span model mirrors OTel fields: trace_id, span_id, parent_span_id,
  name, start, end, attributes, status).

## R-11: Logging: Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15)

- **Selected**: stdlib `logging` with a JSON formatter and a redaction filter (key names:
  `authorization`, `x-api-key`, `secret`, `password`, `token`; pattern `sk_[A-Za-z0-9]+\.[A-Za-z0-9_-]+`).
- **Alternative**: structlog (rejected: extra dependency without a needed capability).

## R-12: Security scanners: Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15)

- **Selected**: `pip-audit` (dependency vulnerabilities; OSV/PyPI advisory source), `detect-secrets`
  (secret scan with committed baseline), `pip-licenses` (license inventory against allow-list).
- **Alternatives**: gitleaks, trivy, osv-scanner (rejected: extra binaries that are not installed;
  K2).
- **Risk**: advisory source needs network. Unavailability → transient retries → SEC-003 FAIL →
  exception path. Never a silent PASS.

## R-13: CLI: Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15)

- **Selected**: Typer (typed, small, consistent with Pydantic). Alternative: argparse (more
  boilerplate), Click (Typer builds on it).

## R-14: IDs and time: Accepted via ADRs (Mani Kumar Vadugu, 2026-10-15)

- **Selected**: sortable ULID-style IDs with prefixes (`run_`, `nod_`, `gat_`, `art_`, `dec_`,
  `evt_`, `exc_`, `eps_`), generated by an injectable `IdGenerator`; injectable `Clock` (UTC,
  `datetime` with tzinfo). Tests use deterministic generators and a virtual clock.
- **Note**: `uuid.uuid7` is only in Python ≥ 3.14, so a small in-house ULID generator avoids a
  dependency.

---

## Deferred-question resolutions

### DQ-005: Audit retention (PD-002b): approved at plan gate (Mani Kumar Vadugu, 2026-10-15)

- **Decision**: Policy AUD-001 requires a configured retention of **≥ 365 days**. The prototype
  performs **no automated deletion** (A-007). `orch audit export` produces JSONL plus a head hash
  for archival. Any purge is a destructive action requiring human approval and is out of scope.
- **Rationale**: covers the assessment review period with margin; a production retention figure
  is an organizational and legal decision, documented as such.
- **Alternatives**: 90 days (too short for review cycles); 7 years (regulatory-style figure
  without a source requirement).

### DQ-007: Failure classification (PD-003): approved at plan gate (Mani Kumar Vadugu, 2026-10-15)

- **Decision**: the per-stage table in plan §6.2, encoded as `failure_classification` maps in
  `contracts/workflow-graph.v2.yaml`. Unclassified exceptions → safe-stop.
- **Rationale**: only failures that a retry with identical inputs can fix are transient; all
  deterministic outcomes are permanent.

### DQ-008: Technology stack

- **Decision**: R-01..R-04, SELECTED by the human owner on 2026-10-15.

### DQ-010: Final scope cut (PD-010): approved at plan gate (Mani Kumar Vadugu, 2026-10-15)

- **Decision**: plan §14.1. Must-have = CST-008 must-have + acceptance-criteria variants + G-SECURITY +
  compensation path + traceability check; simplified reductions are pre-agreed for CP-2/CP-3
  slippage; the backlog BL-01..BL-11 is disclosed as limitations.

---

## Best-practice notes applied

- **SQLite concurrency**: WAL, `synchronous=NORMAL`, `busy_timeout`, short write transactions,
  `BEGIN IMMEDIATE` to avoid deadlock-prone lock upgrades.
- **Idempotency keys**: store `(key_id, idempotency_key) → (request_fingerprint, response)`;
  same key with a different fingerprint → `409`; records expire after 24 h.
- **Redirect safety**: 302 + `Cache-Control: no-store`; never redirect when persistence state
  cannot be verified.
- **Outbox-free design**: the engine has no external message broker, so state and audit share a
  transaction. No dual-write problem exists except for the system-under-change effects, which are
  handled through rollback (workspace) and compensation (staging).
- **Windows**: path handling via `pathlib`; LF enforcement for patches; process groups for clean
  termination.
