# ADR-002: Persistence Strategy

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

Superseded in part by [ADR-021](ADR-021-sqlite-stdlib-persistence.md) (stdlib `sqlite3`, no
SQLAlchemy, Alembic or repositories; file layout) — **approved, CR-009 (Mani Kumar Vadugu, human owner,
2026-10-16)**. Where the two differ, ADR-021 describes the implementation; the differences are
listed in [docs/reviews/final-assessment.md](../reviews/final-assessment.md) §4.

History: Proposed 2026-10-15. Underlying selection made by the human owner (Mani Kumar Vadugu)
during `/speckit-plan` (research R-02, DQ-008).

## Context

The shortener needs unique short codes under concurrency (FR-SHR-005, PVT-003), idempotency
records (FR-SHR-013), exact analytics (A-013) and explicit behavior when persistence is down
(FR-SHR-015). The engine needs every state transition and its audit event committed atomically
(FR-OBS-004, FR-ORC-028) and recoverable after interruption (FR-ORC-011). Several shortener
instances run at once: dev, staging, isolated copies (FR-ORC-032/040). No extra infrastructure
may be required (NFR-RUN-001).

## Decision Drivers

- ACID transactions for "state change + audit append" in one commit.
- Zero-install for reviewers; one DB file per instance for isolation.
- Unique constraints for code uniqueness; triggers for append-only audit.
- Replaceability (CON VII).

## Options Considered

### Option A — SQLite (WAL) via SQLAlchemy Core + Alembic, behind repository protocols
- **Approach**: one SQLite file per service instance under `var/`; `journal_mode=WAL`, `busy_timeout=5000`, `BEGIN IMMEDIATE` for writes; repositories expose domain operations.
- **Advantages**: no server; transactional; triggers; trivial isolation per instance; portable SQL via Core.
- **Disadvantages**: single writer per file; limited `ALTER TABLE` (Alembic batch mode recreates tables).
- **Risks**: write contention at PVT-003; batch-mode table recreation would drop append-only triggers on audit tables.
- **Implementation impact**: short write transactions; `database is locked` classified transient (ADR-013); audit-table migrations restricted to plain `ADD COLUMN`.
- **Assessment implications**: demonstrates discipline without infrastructure; scaling is a documented trade-off.

### Option B — PostgreSQL (Docker or native)
- **Approach**: one Postgres server, schemas per instance.
- **Advantages**: real multi-writer concurrency; production fidelity.
- **Disadvantages**: Docker absent; native install adds steps.
- **Risks**: PVT-009 setup target; reviewer environment failures.
- **Implementation impact**: service lifecycle management, credentials (secrets) handling.
- **Assessment implications**: stronger scaling story, weaker runnability.

### Option C — SQLite default + tested Postgres adapter
- **Approach**: both adapters behind repositories; test matrix on both.
- **Advantages**: proves replaceability.
- **Disadvantages**: doubles persistence tests in the timebox.
- **Risks**: displaces mandatory evidence (violates plan §14.1 scope rule).
- **Implementation impact**: CI matrix, Postgres availability.
- **Assessment implications**: nice-to-have; backlog BL-09.

## Decision

Option A. Each service owns its schema and Alembic environment; each instance owns its DB file
(`var/dev`, `var/staging`, `var/work/<run>/<attempt>`, `var/orchestrator`). Migrations are
**additive-only within a major version** (CHG-003; ADR-007). Audit and policy-evaluation tables
carry `BEFORE UPDATE/DELETE` triggers raising `append-only`; their migrations use plain
`ALTER TABLE ... ADD COLUMN` (never batch recreation).

## Rationale

Meets atomicity, isolation and runnability with the least moving parts; repository protocols and
SQLAlchemy Core keep the Postgres path open.

## Consequences

- **Positive**: atomic state+audit commits; isolation by file; zero setup.
- **Negative**: no multi-writer scaling; NFR-SCL-002 is documentation only.
- **Operational**: `var/` holds all runtime data (gitignored); `orch demo reset` rebuilds it.
- **Testing**: migration tests up-from-empty and up-from-previous-release; trigger tamper tests; PVT-003 concurrency test.
- **Governance**: destructive migrations require MAJOR version + approved exception (CHG-003).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| PVT-003 fails due to lock contention | Short transactions, retry on busy within request; if still failing → STOP-2, report with evidence, propose change |
| Batch migration drops audit triggers | Rule: no batch ops on append-only tables; migration test asserts triggers present after upgrade |
| File corruption on crash | WAL + `synchronous=NORMAL`; recovery test kills process mid-write |

## Reversibility

High for the shortener and engine data access (Core + repositories); Postgres adapter is BL-09.

## Traceability

- Requirements: FR-SHR-005, FR-SHR-013, FR-SHR-014, FR-SHR-015, FR-ORC-011, FR-ORC-028, FR-OBS-004, NFR-SCL-001, NFR-SCL-002, NFR-RUN-001, PVT-003
- Spec: Key Entities; Edge Cases (persistence unavailable)
- Plan: Technical Context; §1.3; §2.3; §12 R-02; data-model.md §3
- Decisions: DQ-008, A-013

## Validation

Persistence suites (uniqueness, idempotency, triggers, migrations); PVT-003 test (1,000
concurrent creations, zero collisions); persistence-down integration tests (503, no redirect).
