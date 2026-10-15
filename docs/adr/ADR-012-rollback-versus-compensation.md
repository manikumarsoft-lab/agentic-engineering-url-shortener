# ADR-012: Rollback versus Compensation and Staging Promotion

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Related plan-gate approval: PD-012 (Mani Kumar Vadugu, 2026-10-15).

## Context

Rollback (restore prior state) must be distinguished from compensation (corrective action after a
committed effect) and the applied mechanism recorded (CON VIII, FR-ORC-017). Failed validation on
the isolated copy must restore last known-good (SCN-B-AC4, FR-ORC-035). After a human "ready"
decision the change is promoted to local staging; a failed smoke check must be compensated by
re-promoting the previous release, and non-rollbackable data effects require human-approved
corrective action (Clarification Q5, FR-ORC-040..042).

## Decision Drivers

- Clear, testable separation of the two mechanisms.
- No destructive data operations without human approval.
- Deterministic terminal outcomes.

## Options Considered

### Option A — Rollback = discard isolated workspace; Compensation = re-promote previous immutable release + listed effects + G-CORRECTIVE
- **Approach**: before promotion all effects are confined to `var/work/...` → rollback deletes the workspace and marks artifacts `rolled_back`. After promotion, REL-02 stops staging, starts the previous release snapshot (compatible with migrated schema per ADR-007), verifies its smoke check, queries staging for data created in `[promoted_at, compensated_at)`, and opens G-CORRECTIVE for human-approved action (`disable_listed_links` or `retain_data_accept_risk`). Audit is never altered.
- **Advantages**: semantics map exactly to spec; destructive data correction always human-approved.
- **Disadvantages**: staging keeps migrated (additive) schema after compensation.
- **Risks**: previous release fails smoke (compensation failure).
- **Implementation impact**: `ReleaseStore`, `StagingManager`, effects query, G-CORRECTIVE gate.
- **Assessment implications**: shows both mechanisms with distinct evidence.

### Option B — Database snapshot restore on smoke failure
- **Approach**: copy staging DB before promotion and restore it on failure.
- **Advantages**: full state restore.
- **Disadvantages**: silently deletes data created during the failed interval (irreversible, unapproved).
- **Risks**: violates CON III (destructive action without approval).
- **Implementation impact**: simple file copy.
- **Assessment implications**: conflicts with FR-ORC-042.

### Option C — Automatic rework loop on test failure
- **Approach**: re-run ST-08/ST-09 automatically.
- **Advantages**: may self-heal transient issues.
- **Disadvantages**: test failures are permanent; loop adds no information.
- **Risks**: non-deterministic outcomes.
- **Implementation impact**: loop control.
- **Assessment implications**: rejected by PD-012.

## Decision

Option A. Terminal outcomes: test failure → rollback → `FAILED` (PD-012); smoke failure →
compensation → G-CORRECTIVE → ST-13 → `FAILED` (compensated); compensation failure →
`SAFE_STOPPED` with staging marked degraded. Promotion is idempotent by `release_id`. Fault
injection `smoke_fail` / `compensation_fail` exists only in labeled runs/tests.

## Rationale

Matches the spec's definitions and keeps every irreversible effect behind a human decision.

## Consequences

- **Positive**: distinct, evidenced recovery paths; MTTR mechanism attribution.
- **Negative**: schema may retain unused additive columns after compensation.
- **Operational**: exactly one active release; release history under `var/releases/`.
- **Testing**: defective change-set e2e (rollback); injected smoke failure e2e (compensation + G-CORRECTIVE); compensation-failure test (safe-stop, degraded).
- **Governance**: G-CORRECTIVE approver role; corrective actions audited.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Previous release incompatible with migrated schema | Additive-only migrations (CHG-003); migration test runs previous release against new schema |
| Effects list incomplete | Effects defined by timestamps on created rows (links, stats); audit is excluded by design; documented scope |
| Staging left half-started | Readiness polling; transient retry; safe-stop on exhaustion |

## Reversibility

Medium. Release snapshot mechanism is local; switching to blue/green with two staging instances later is possible.

## Traceability

- Requirements: FR-ORC-017, FR-ORC-035, FR-ORC-040, FR-ORC-041, FR-ORC-042, FR-ORC-043, NFR-CHG-001, SCN-B-AC4, A-012
- Spec: Clarifications Q1, Q5; Edge Cases (smoke fails, compensation fails)
- Plan: §3.2, §6.1 (Rollback, Compensation), §11.2; workflow-graph ST-09, REL-01, REL-02, G-CORRECTIVE
- Decisions: PD-012, PD-009

## Validation

Reliability suite and e2e variants listed above; evidence shows `ROLLBACK_*` vs `COMPENSATION_*`
events with distinct episode mechanisms.
