# ADR-007: Contract-First API and Schema Versioning with Additive Migrations

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Research R-07 pending this ADR.

## Context

The brief requires explicit, versioned API and schema deliverables with executable validation,
and every change must identify ownership, version impact, compatibility, consumers, tests, docs,
rollout and approval (plan §2.2–2.3). Scenarios deliver MINOR increments to the shortener API
(1.1.0–1.3.0). Staging compensation re-promotes the previous release against a schema that the
failed release may already have migrated (FR-ORC-042).

## Decision Drivers

- Contracts as reviewable change-control objects (CON VI).
- Drift between code and contract must be caught automatically.
- Previous release must run on the migrated schema (safe compensation).
- Low tooling overhead.

## Options Considered

### Option A — Contract-first (committed OpenAPI 3.1 + JSON Schema) with drift test, schemathesis, jsonschema
- **Approach**: committed contracts in `specs/001-…/contracts/` are authoritative; tests assert app-generated OpenAPI equals the contract (normalized); schemathesis exercises the running app; emitted documents validated with jsonschema.
- **Advantages**: contracts reviewed before code; drift is a failing test; examples validated.
- **Disadvantages**: Pydantic models must mirror contracts exactly; normalization effort.
- **Risks**: FastAPI cosmetic differences cause false drift.
- **Implementation impact**: drift normalizer; fallback structural comparison if normalization exceeds timebox (documented limitation).
- **Assessment implications**: strongest API/schema evidence.

### Option B — Code-first (generated OpenAPI is the contract)
- **Approach**: export spec from code into docs.
- **Advantages**: no drift by construction.
- **Disadvantages**: contract changes are side-effects of code; no pre-implementation review.
- **Risks**: unreviewed breaking changes.
- **Implementation impact**: minimal.
- **Assessment implications**: weaker change control.

### Option C — Prose-only API documentation
- **Approach**: Prose-only API documentation.
- **Advantages**: fastest. **Disadvantages**: not executable. **Risks**: silent drift. **Implementation impact**: none. **Assessment implications**: fails the brief.

### Migration sub-options
- **M1 additive-only within a MAJOR (expand/contract)** — previous release always compatible with migrated schema; destructive ops need MAJOR + exception. **Chosen.**
- **M2 down-migrations on compensation** — restoring schema risks data loss and is itself a destructive action requiring approval each time. Rejected.

## Decision

Option A with M1. SemVer rules, Change Record template and planned increments as in
`contracts/README.md`. Consumers ignore unknown response fields; producers emit no undeclared
fields. Runs pin graph and policy versions. CHG-003 enforces additive migrations statically
(disallowed Alembic ops: `drop_*`, narrowing `alter_column`, renames).

## Rationale

Contract-first turns API changes into governed artifacts; additive migrations make compensation
(re-promotion) safe without down-migrations.

## Consequences

- **Positive**: executable contracts; safe compensation; clear MINOR/MAJOR rules.
- **Negative**: schema accumulates nullable/defaulted columns; contract upkeep.
- **Operational**: workspace contains a copy of the shortener contract; change sets bump it.
- **Testing**: drift, schemathesis, example validation, migration-from-previous-release tests.
- **Governance**: every contract/schema change carries a Change Record; G-DESIGN approves run-level ones.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| False drift from FastAPI output | Normalizer; time-boxed fallback to structural comparison (disclosed) |
| Contract location duplication | Single source in `specs/001-…/contracts/`; workspaces copy it; released versions live in release snapshots |

## Reversibility

High. Validation tooling is test-only; contracts remain useful under any implementation.

## Traceability

- Requirements: FR-SHR-001..019 (API surface), FR-GOV-009, FR-ORC-042, NFR-TST-001, CST-003
- Spec: Key Entities; Clarification Q5
- Plan: §2.2, §2.3, §9.4, §12 R-07; contracts/README.md; data-model.md §3
- Decisions: PD-002 (302 status in contract)

## Validation

Contract suites green at slice 3; OpenAPI files pass `openapi-spec-validator` (already executed
during planning, 2026-10-15); migration test runs previous-release smoke against migrated schema.
