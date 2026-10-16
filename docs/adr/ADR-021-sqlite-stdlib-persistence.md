# ADR-021: SQLite via the Standard Library

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-16, CR-009)**

Supersedes in part: [ADR-002](ADR-002-persistence-strategy.md) §Decision, §Rationale,
§Consequences (Operational, Testing), §Reversibility, §Validation. ADR-002's choice of SQLite
(WAL, one file per role, append-only triggers) stands.

History: drafted 2026-10-16 with AI assistance (Claude Code) from the final assessment
([docs/reviews/final-assessment.md](../reviews/final-assessment.md) §3). Accepted by the human owner
with CR-009 on 2026-10-16.

## Context

ADR-002 chose SQLite (WAL) via SQLAlchemy Core + Alembic behind repository protocols, with
database files under `var/dev`, `var/staging`, `var/work/<run>/<attempt>` and `var/orchestrator`,
`synchronous=NORMAL`, migration tests and an `orch demo reset` command. The lean slice
(HD-CUT-002) implemented persistence directly with the standard-library `sqlite3` module.

## Decision

SQLite in WAL mode through Python's standard-library `sqlite3` module. No SQLAlchemy, no
Alembic and no repository protocols.

- **Shortener**: `shortener.store.LinkStore` owns tables `links`, `link_stats` and
  `idempotency`. It opens one connection per operation (`timeout=5`) and runs every write in
  `BEGIN IMMEDIATE`. `links.code` is the primary key with a 4–10 character length check;
  `destination` is limited to 2,048 characters.
- **Orchestrator**: `orchestrator.store.Store` owns `runs`, `nodes`, `artifacts`, `decisions`,
  `policy_evaluations`, `exceptions`, `audit` and the shared `keys` table in one file
  (`busy_timeout=5000`). Every state change and its audit event commit in one
  `BEGIN IMMEDIATE` transaction (`Store.tx`).
- **Append-only**: `audit` and `policy_evaluations` carry `BEFORE UPDATE/DELETE` triggers that
  raise `append-only`; `audit` rows are hash-chained per run (ADR-008).
- **Schema changes**: schemas are created idempotently at startup (`CREATE TABLE IF NOT
  EXISTS`). There is no migration framework. Scenario change sets may only add tables or
  columns; CHG-003 is a review rule, not machine-enforced.
- **Files**: runtime files live under `ORCH_HOME` (default `var/`): `orchestrator.db` (also read
  by the shortener for API keys) and `shortener.db`; staging uses `var/staging/shortener.db` and
  `var/staging/keys.db`. Isolated workspaces (`var/work/<run_id>/`) contain code only.
- **Durability**: `synchronous` is left at the SQLite default.
- **Failures**: a shortener storage error returns `503 persistence_unavailable` and never
  redirects; the engine classifies `db_locked` as transient.

## Consequences

- **Positive**: no ORM or migration dependency; the transaction boundaries are visible in a few
  lines of code.
- **Negative**: upgrading an existing database to a changed schema is not supported (recreate
  the database); there is no Postgres path (BL-09); NFR-SCL-002 is documentation only.
- **Operational**: `orch demo reset` does not exist; delete `var/` manually (task T287).
- **Testing**: no migration tests (no migrations exist).

## Traceability

- Requirements: FR-SHR-005, FR-SHR-013, FR-SHR-014, FR-SHR-015, FR-ORC-011, FR-ORC-028,
  FR-OBS-004, NFR-SCL-001, NFR-SCL-002, PVT-003
- Supersedes in part: ADR-002
- CR: CR-009 (plan.md Change Log)
- Tasks: T273 (PVT-003 with 1,000 creations), T277 (audit tamper attempts recorded), T287

## Validation

`tests/orchestrator/test_audit_keys_policy.py::test_hash_chain_verifies`,
`::test_update_and_delete_are_refused`, `::test_out_of_band_tampering_is_detected`;
`tests/shortener/test_api.py::test_storage_outage_never_redirects_and_ready_reports_it`;
`tests/shortener/test_concurrency_serve.py::test_orch_serve_handles_200_parallel_creates_with_unique_codes`.
PVT-003 (1,000 concurrent creations) is still required and not yet tested (T273).
