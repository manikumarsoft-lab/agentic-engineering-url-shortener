# ADR-015: Workflow State Persistence, Idempotent Transitions and Artifact Lineage

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. IDs and time handling (research R-14) pending this ADR.

## Context

Workflow state, stage outputs, cross-stage context and artifact versions must survive
interruption (FR-ORC-011); every artifact carries provenance (FR-ORC-012); decisions carry
lineage (FR-ORC-013); duplicate completion/decision events apply at most once (FR-ORC-028);
replanning needs input-version records (FR-ORC-020).

## Decision Drivers

- Atomic state + audit commits.
- At-most-once transitions under retries and duplicate submissions.
- Reconstructable lineage without external stores.
- Deterministic IDs/time in tests.

## Options Considered

### Option A — Current-state tables + append-only history (audit), one transaction per transition
- **Approach**: tables `runs`, `graph_instances`, `node_states`, `node_attempts`, `gates`, `decisions`, `artifacts`/`artifact_versions`, `replans` (data-model.md). Each transition: conditional update on `row_version` + audit append + unique `transition_key` in one transaction. Artifacts versioned immutably with content hash and `input_versions`.
- **Advantages**: fast reads of current state; full history in audit; simple queries.
- **Disadvantages**: two representations (state tables and events) must agree.
- **Risks**: divergence bugs.
- **Implementation impact**: transition helper is the only writer of state tables.
- **Assessment implications**: easy inspection plus reconstructability.

### Option B — Pure event sourcing (state = fold over events)
- **Approach**: Pure event sourcing (state = fold over events).
- **Advantages**: single source of truth. **Disadvantages**: projection code, replay cost, more complexity in timebox. **Risks**: projection bugs. **Implementation impact**: high. **Assessment implications**: elegant but slower to deliver.

### Option C — Serialized run object (JSON blob) per run
- **Approach**: Serialized run object (JSON blob) per run.
- **Advantages**: simple. **Disadvantages**: no concurrency control per node; poor queryability; lineage hard. **Risks**: lost updates across parallel branches. **Implementation impact**: low. **Assessment implications**: weak.

## Decision

Option A. A consistency test rebuilds node/run states from audit events and compares with state
tables for every e2e run. IDs: prefixed ULID-style (`run_`, `nod_`, `gat_`, `art_`, `dec_`,
`evt_`, `exc_`, `eps_`, `pev_`) from an injectable `IdGenerator`; `Clock` injectable (UTC).
Large artifact content stored under `var/` with hash in DB. Run identifier is also the trace ID.

## Rationale

Gives atomicity and fast inspection now, with an audit-based cross-check that guards against
divergence — the pragmatic middle ground to full event sourcing.

## Consequences

- **Positive**: survives crashes; idempotent; lineage queries straightforward.
- **Negative**: dual representation requires the consistency test.
- **Operational**: single DB file; backups = file copy while stopped.
- **Testing**: duplicate event/decision tests, claim race tests, crash-mid-transition tests, state-vs-audit consistency test.
- **Governance**: provenance labels on change-set artifacts (FR-ORC-034).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| State/audit divergence | Single transition helper; consistency test |
| Double claim of a READY node | Conditional update on `row_version`; loser aborts |

## Reversibility

Medium. Moving to event sourcing later is possible because the audit already contains all transitions.

## Traceability

- Requirements: FR-ORC-001, FR-ORC-011, FR-ORC-012, FR-ORC-013, FR-ORC-020, FR-ORC-028, FR-ORC-034, NFR-RCV-001, NFR-DET-001
- Spec: Key Entities (Workflow Run, Stage Execution, Artifact, Decision)
- Plan: §4, §3.1 `engine/transitions.py`, §12 R-14; data-model.md §1.2, §2
- Decisions: PD-011

## Validation

Persistence and concurrency suites; interruption tests (PVT-006); consistency test in e2e.
