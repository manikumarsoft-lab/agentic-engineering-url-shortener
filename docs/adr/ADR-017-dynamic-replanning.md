# ADR-017: Dynamic Replanning (Stale Closure, Memoized Re-execution, Approval Revocation)

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15.

## Context

When an upstream artifact changes, dependent stages/artifacts must be marked stale, the affected
subgraph re-planned and only affected stages re-run; approvals of invalidated artifacts revoked;
replanning audited (FR-ORC-020/021, SC-006). Mid-run ambiguity suspends only the dependent path
while siblings continue to the next sync point (FR-ORC-022, FR-ORC-039, SCN-A-AC4). After
clarification the run resumes at the earliest affected stage (SCN-C-AC4).

## Decision Drivers

- Minimal re-execution with provable correctness.
- Governance preserved (revocation, re-approval).
- Topology changes versioned.

## Options Considered

### Option A — Input-version lineage + downstream closure + input-hash memoization
- **Approach**: every node attempt records `input_versions`; a new artifact version triggers computation of the transitive closure of consumers in the graph instance; those nodes → `STALE`; gates binding stale artifacts → `REVOKED`; if topology changes (e.g., ST-05 now required) create graph instance v+1; re-schedule STALE nodes; a node whose recomputed input hash equals its last successful input hash is not re-run.
- **Advantages**: precise and explainable; SC-006 testable.
- **Disadvantages**: requires disciplined input recording.
- **Risks**: missed edge → under-invalidation.
- **Implementation impact**: `engine/replan.py`; closure tests.
- **Assessment implications**: strong non-linear orchestration evidence.

### Option B — Restart the run from the changed stage onward (topological suffix)
- **Approach**: Restart the run from the changed stage onward (topological suffix).
- **Advantages**: simple. **Disadvantages**: re-runs unaffected parallel branches (violates SC-006). **Risks**: wasted work; duplicate side effects. **Implementation impact**: low. **Assessment implications**: weaker.

### Option C — Start a new run
- **Approach**: Start a new run.
- **Advantages**: clean. **Disadvantages**: loses lineage continuity; violates "resume at earliest affected stage". **Risks**: SCN-C-AC4 fails. **Implementation impact**: low. **Assessment implications**: fails ACs.

## Decision

Option A. Triggers: clarification answers, late ambiguity (`needs_clarification` from nodes that
declare `may_raise_ambiguity`), G-DESIGN `reject_rework`, CHG-002 scope violation on resume.
Events: `REPLAN_STARTED`, `ARTIFACT_STALE`, `GATE_REVOKED`, `GRAPH_VERSION_CREATED`,
`REPLAN_COMPLETED`. Late-ambiguity demonstration uses a labeled `finding-injection` variant
(SCN-A `late-ambiguity`), because deterministic agents raise ambiguity only from declared rules
or injected findings.

## Rationale

Lineage-driven invalidation is the only option that satisfies SC-006 and the resume-in-place
acceptance criteria.

## Consequences

- **Positive**: minimal recomputation; approvals stay meaningful.
- **Negative**: closure logic must be correct for optional inputs and conditional nodes.
- **Operational**: graph instance history visible via API.
- **Testing**: closure unit tests, "unaffected nodes untouched" assertions, revocation tests, late-ambiguity e2e.
- **Governance**: replanning cannot bypass gates; revoked approvals must be re-requested.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Under-invalidation | Closure computed from graph edges **and** recorded inputs (union) |
| Over-invalidation of sync points | Sync nodes recomputed from predecessor states only |
| Late ambiguity seen as staged | Labeled `finding-injection`; disclosed limitation of deterministic agents |

## Reversibility

High within the engine module.

## Traceability

- Requirements: FR-ORC-020, FR-ORC-021, FR-ORC-022, FR-ORC-039, SC-006, SCN-A-AC4, SCN-C-AC4
- Spec: Edge Cases (upstream change mid-branch; stale approval)
- Plan: §3.6, §11.1, §11.3; data-model Replan, node `STALE`/`SUSPENDED`
- Decisions: HD-002 (SCN-C), PD-008

## Validation

Replanning suite (SC-006, 100%); SCN-A late-ambiguity and SCN-C option-A e2e runs show resume at
earliest affected stage with revoked/re-requested approvals.
