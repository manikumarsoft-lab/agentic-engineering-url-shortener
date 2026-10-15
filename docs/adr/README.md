# Architecture Decision Records: Feature 001

ADR gate for `specs/001-agentic-sdlc-url-shortener` (2026-10-15). **All 19 ADRs are Accepted**
(Mani Kumar Vadugu, human owner, Human Gate 4, 2026-10-15).

Format: Status · Context · Decision Drivers · Options Considered (approach, advantages,
disadvantages, risks, implementation impact, assessment implications) · Decision · Rationale ·
Consequences · Risks and Mitigations · Reversibility · Traceability · Validation.

## Index

| ADR | Decision | ADR-gate topics | Basis | Status |
|-----|----------|-----------------|-------|--------|
| [001](ADR-001-language-and-framework.md) | Python 3.12 + FastAPI + Pydantic v2 (uv) | 2 Language/framework | DQ-008 (human selection) | Accepted |
| [002](ADR-002-persistence-strategy.md) | SQLite (WAL) + SQLAlchemy Core + Alembic; DB per instance; additive migrations | 3 Persistence | DQ-008 (human selection) | Accepted |
| [003](ADR-003-orchestration-model.md) | In-repository engine built from scratch, with the deterministic superstep scheduler | 5 Orchestration model | DQ-008, PD-004 | Accepted |
| [004](ADR-004-application-architecture-and-local-execution.md) | Two services + CLI; layered packages; ports and `var/` layout | 1 Application architecture; 14 Deployment/local execution | DQ-008 (human selection) | Accepted |
| [005](ADR-005-dependency-graph-representation.md) | Versioned YAML graph template plus per-run graph instances | 7 Dependency graph | New | Accepted |
| [006](ADR-006-change-sets-and-isolated-workspaces.md) | Pre-authored diff + manifest + lock change sets, applied with `git apply` in isolated workspaces | 10 (with 012) | PD-009, PD-012; ruling 3 | Accepted |
| [007](ADR-007-contract-first-api-and-schema-versioning.md) | Contract-first OpenAPI/JSON Schema with drift tests; additive-only migrations | (API/schema) | New | Accepted |
| [008](ADR-008-audit-integrity.md) | Append-only audit table + triggers + per-run hash chain | 12 Observability/audit | PD-002b | Accepted |
| [009](ADR-009-policy-model-and-exceptions.md) | Versioned YAML policies + check code; human-gated exceptions | (Compliance) | New | Accepted |
| [010](ADR-010-authentication-and-authorization.md) | Role-mapped API keys stored as SHA-256 hashes; agents limited to declared capabilities | 15 Authn/authz | HD-003 | Accepted |
| [011](ADR-011-observability-metrics-and-mttr.md) | Logs, in-house traces, metrics and MTTR computed from audit events | 12 Observability/audit | PD-005 | Accepted |
| [012](ADR-012-rollback-versus-compensation.md) | Rollback = discard workspace; compensation = re-promote previous release + G-CORRECTIVE | 10 Rollback vs compensation | PD-012 | Accepted |
| [013](ADR-013-retry-fallback-and-safe-stop-policy.md) | Per-node failure classification, retry, timeout, fallback, safe-stop, human resume | 9 Retry/fallback/safe-stop | PD-003, PD-011, PD-012 | Accepted |
| [014](ADR-014-short-code-generation-and-collision-handling.md) | CSPRNG base62 length 7; DB uniqueness; bounded retry; codes and aliases 4–10 characters | 4 Short codes | Ruling 1 | Accepted |
| [015](ADR-015-workflow-state-persistence.md) | Current-state tables + audit history; idempotent transitions; artifact lineage | 6 Workflow state persistence | New | Accepted |
| [016](ADR-016-human-approval-model.md) | Version-bound typed gates; timeouts; bounded rework; no rework at G-RELEASE | 8 Human approval | HD-003, PD-006, PD-007; ruling 4 | Accepted |
| [017](ADR-017-dynamic-replanning.md) | Stale closure, input-hash memoization, approval revocation | 11 Dynamic replanning | New | Accepted |
| [018](ADR-018-testing-strategy.md) | Test-first pyramid, virtual clock, fault injection, requirement-marked tests | 13 Testing strategy | PD-006 | Accepted |
| [019](ADR-019-analytics-consistency.md) | Atomic increment after redirect; exact while storage is healthy; failures counted | 16 Analytics consistency | Ruling 2 | Accepted |

All 16 ADR-gate topics are covered. These minor choices have no standalone ADR: logging (in ADR-011),
security scanners (ADR-009), CLI framework (ADR-001), IDs and time (ADR-015).

## Human Gate 4 rulings (Mani Kumar Vadugu, 2026-10-15)

| # | Question | Ruling | Applied in |
|---|----------|--------|------------|
| 1 | Alias length (FR-SHR-021) | 4–10 characters | ADR-014 |
| 2 | Exact counts (A-013) vs non-blocking redirect (FR-SHR-011) | Counts are exact while analytics storage is healthy; failed writes are counted, visible in metrics and disclosed as a limitation; no durable outbox (backlog BL-12) | ADR-019; plan §14.1 |
| 3 | May change sets add or change dependencies? | No | ADR-006 |
| 4 | G-RELEASE `not_ready` | No rework; the run ends `FAILED` with blocking reasons; a human starts a new run after fixing (consistent with PD-012) | ADR-016; plan §3.2, §3.4, §5.1, §5.3; data-model §2; contracts (CR-002) |
| 5 | Network during recorded scenario runs | Runs execute with network access. If the vulnerability database is unreachable, SEC-003 FAILs and the real policy-exception path is followed and recorded | ADR-009 behavior unchanged (tool unavailable ⇒ FAIL) |

## Conflicts with the plan found at the ADR gate: resolved by CR-002

| # | Conflict | Resolution (CR-002) |
|---|----------|---------------------|
| 1 | Plan named the scheduler "ADR-005" and listed 13 candidates | Scheduler = ADR-003; graph representation = ADR-005; 19 ADRs listed in plan |
| 2 | research.md R-02 used Alembic batch mode everywhere, which would drop append-only triggers | Batch mode prohibited for append-only tables; plain `ADD COLUMN` only |
| 3 | G-RELEASE `not_ready → rework` re-ran ST-12 on unchanged inputs | Rework removed (ruling 4); graph 2.0.0, gate-decision schema 2.0.0, orchestrator API 2.0.0 |
| 4 | Plan §6.1 lacked "scheduler stall" and "interruption detected at startup" safe-stop triggers | Added to plan §6.1 and data-model §2.1 |
| 5 | `core.autocrlf=true`, no `.gitattributes` | Slice 1 task added to plan §14.2 |

Details and impact analysis: [plan.md Change Log](../../specs/001-agentic-sdlc-url-shortener/plan.md#change-log)
and contracts Change Record in
[contracts/README.md](../../specs/001-agentic-sdlc-url-shortener/contracts/README.md#change-history).

## Decisions that can safely wait (no ADR needed before implementation)

OpenTelemetry exporter (BL-06), Prometheus endpoint (BL-07), PostgreSQL adapter (BL-09), AI-backed
adapter beyond the disabled stub (BL-01), horizontal scaling (BL-03), key rotation and revocation
(BL-10), escalation routing (BL-04), durable analytics outbox (BL-12). Each is disclosed as a
limitation.

## Acceptance

ADR-001 to ADR-019 were reviewed and accepted by Mani Kumar Vadugu (human owner) on 2026-10-15
(Human Gate 4). Also confirmed at that gate: the FR-GOV-003/FR-GOV-015 interpretation (a release
decision of "not ready" ends the run `FAILED`; `ABORTED` is reserved for a human "reject and
terminate" at an approval gate) and the three MAJOR contract bumps of CR-002.
