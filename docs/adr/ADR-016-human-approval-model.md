# ADR-016: Human Approval Model (Gates, Version Binding, Timeouts, Rework Bounds)

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Gate semantics fixed by Clarification Q4 (FR-GOV-014..016) and
HD-003; related plan-gate approvals PD-006 and PD-007 (Mani Kumar Vadugu, 2026-10-15); G-RELEASE
`not_ready` semantics ruled at Human Gate 4, ruling 4 (CR-002, 2026-10-15).

## Context

High-impact actions require explicit human approval; approve/reject/escalate/timeout semantics
must be defined; silence is never approval; approvals bind to artifact versions; agents cannot
decide (CON III — non-waivable; FR-GOV-001..004, -011, -014..016; SC-004).

## Decision Drivers

- No path from silence, timeout or agent action to approval.
- Approvals invalidated when their artifacts change.
- Bounded rework loops.
- Evidence integrity of scenario decisions.

## Options Considered

### Option A — First-class gate entities bound to artifact versions; typed gates; human-only decisions via role keys
- **Approach**: gate types clarify/design/security/exception/release/corrective; each gate stores `bound_artifacts` (id, version, hash) and `deadline_at`; decisions must quote current bound versions (`409 stale_artifact_version`); replanning revokes gates; timeout → `SAFE_STOPPED`; `reject_rework` (≤2 per gate per run) / `reject_terminate` (→ `ABORTED`); `escalate` keeps gate blocking and raises required role.
- **Advantages**: precise, auditable, testable.
- **Disadvantages**: more state.
- **Risks**: UX friction quoting versions (CLI fills them from `gate show`).
- **Implementation impact**: `engine/gates.py`, decision schema, CLI helpers.
- **Assessment implications**: strong evidence for controlled autonomy.

### Option B — Approval as a boolean flag on the run/stage
- **Approach**: Approval as a boolean flag on the run/stage.
- **Advantages**: simple. **Disadvantages**: no version binding; stale approvals survive replanning. **Risks**: approving superseded designs. **Implementation impact**: low. **Assessment implications**: fails FR-GOV-004.

### Option C — External ticketing/chat approvals
- **Approach**: External ticketing/chat approvals.
- **Advantages**: realistic workflows. **Disadvantages**: external dependency; auth integration. **Risks**: setup, availability. **Implementation impact**: high. **Assessment implications**: out of scope.

## Decision

Option A. Gate catalogue per plan §5.1 (incl. conditional G-SECURITY, PD-007; G-RELEASE
requires per-risk acceptance for open risks ≥ medium; `ready` refused unless assessment
ELIGIBLE). Scripted decisions are permitted only in automated tests and recorded with
`decision_source=scripted` and label `test`; scenario evidence uses interactive decisions (PD-006).

**G-RELEASE has no rework (Human Gate 4, ruling 4; CR-002)**: decisions are `ready`, `not_ready`,
`escalate`. `not_ready` records the blocking reasons, and the run ends as `FAILED` after ST-13
produces the summary. After fixing the cause, a human starts a new run (consistent with PD-012).
A release decision is a distinct category from an approval rejection (FR-GOV-003 lists them
separately), so FR-GOV-015's "reject and terminate → `ABORTED`" does not govern it. Contracts
bumped to graph 2.0.0, gate-decision schema 2.0.0 and orchestrator API 2.0.0.
Final submission and repository release sign-off are SpecKit-level human gates outside the engine.

## Rationale

Binding approvals to exact artifact versions is the mechanism that keeps human control meaningful
under replanning.

## Consequences

- **Positive**: SC-004/SC-011 directly testable; stale approvals impossible.
- **Negative**: humans must re-approve after replanning (intended).
- **Operational**: gate timeouts configurable (default 24 h; demo profile shorter, recorded on run).
- **Testing**: full decision matrix per gate type, timeout, rework bound, escalation, stale version, agent refusal, duplicate `decision_id`.
- **Governance**: every decision records role and key ID (FR-GOV-013).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Demo timeouts expire during reviewer sessions | Demo profile documented; resume path tested |
| Scripted decisions mistaken for evidence | Labels + evidence export excludes `test`-labeled runs |
| Reviewer expects a rework option after `not_ready` | Resolved by ruling 4: `not_ready` → `FAILED`; a new run is started after the fix; documented in plan §5.3 |
| `FAILED` vs `ABORTED` confusion for release decisions | Interpretation recorded (FR-GOV-003 vs FR-GOV-015); governance test asserts `FAILED` with blocking reasons |

## Reversibility

Medium. Gate model is central to governance; parameters (timeouts, bounds) are configuration.

## Traceability

- Requirements: FR-GOV-001, FR-GOV-002, FR-GOV-003, FR-GOV-004, FR-GOV-011, FR-GOV-013, FR-GOV-014, FR-GOV-015, FR-GOV-016, FR-ORC-004, FR-ORC-021, FR-ORC-042, SC-004, SC-011, PVT-013
- Spec: US-3, US-4; Clarification Q4; HD-003
- Plan: §5 (incl. §5.3 `not_ready`), Change Log CR-002; workflow-graph.v2.yaml gate nodes; schemas gate-decision (2.0.0), workflow-state GateView
- Decisions: PD-006, PD-007, PD-012, HD-003; Human Gate 4 ruling 4; CR-002

## Validation

Governance suite; quickstart §7 negative checks; e2e scenario gate events identical across repeat
runs (NFR-DET-001).
