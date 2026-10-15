# ADR-013: Failure Classification, Retry, Timeout, Fallback, Safe-Stop and Resumption

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Classification table approved at plan gate as PD-003 (DQ-007);
interruption handling PD-011; test-failure handling PD-012 (Mani Kumar Vadugu, 2026-10-15).

## Context

Failures must be classified transient or permanent; only transient ones are retried with bounded
retries, backoff and timeouts; fallback where acceptable; safe-stop when continuation is unsafe;
deterministic terminal outcomes; controlled resumption (CON VIII; FR-ORC-014..019, -023;
PVT-004/005/006; FR-GOV-014).

## Decision Drivers

- Retrying only what can succeed on retry.
- Never proceeding on unsafe state; never silently passing.
- Human-authorized resumption.
- Determinism under a virtual clock.

## Options Considered

### Option A — Per-node classification maps + engine-wide defaults; unclassified ⇒ safe-stop
- **Approach**: defaults (transient: timeout, db_locked, interrupted, subprocess_crashed; permanent: schema/input/permission/illegal transition) extended per node in the graph contract; `max_attempts=3`, exponential backoff 1s×2 cap 30s with seeded jitter; node timeout 300 s (transient); gate timeout → safe-stop; declared fallbacks only (ST-10a/b).
- **Advantages**: explicit, reviewable, testable per node.
- **Disadvantages**: maps must be maintained as nodes evolve.
- **Risks**: misclassification causing useless retries or premature failure.
- **Implementation impact**: classifier lookup, retry scheduler, timers.
- **Assessment implications**: precise reliability evidence.

### Option B — Retry everything N times
- **Approach**: Retry everything N times.
- **Advantages**: simple. **Disadvantages**: retries permanent failures (violates FR-ORC-014). **Risks**: masks defects. **Implementation impact**: low. **Assessment implications**: fails CON VIII.

### Option C — Exception-type heuristics without per-node maps
- **Approach**: Exception-type heuristics without per-node maps.
- **Advantages**: less config. **Disadvantages**: same exception can be transient in one node and permanent in another (e.g., process exit). **Risks**: misclassification. **Implementation impact**: low. **Assessment implications**: weaker.

### Interruption sub-options
- **I1 park in `SAFE_STOPPED`, human resume (PD-011)** — chosen; satisfies FR-ORC-019 "authorized human action".
- **I2 auto-resume on restart** — rejected: no human authorization.

## Decision

Option A with I1 and the table in plan §6.2. Safe-stop triggers: mandatory policy FAIL, retry
budget exhausted on a mandatory node, gate timeout, integrity violation, unclassified failure,
rework limit exceeded, compensation failure, interruption detected at startup, scheduler stall.
Resume requires an approver key and, for non-timeout causes, evidence of resolution or an approved
exception (A-016); timed-out gates reopen on the same artifact version (FR-GOV-014). Scanner
unavailability exhausts to a policy FAIL (never PASS). Fallback use is audited, marks artifacts
`degraded` and surfaces as REL-005 advisory.

## Rationale

Explicit per-node semantics make every recovery path testable and auditable.

## Consequences

- **Positive**: deterministic outcomes; no silent degradation.
- **Negative**: more configuration in the graph contract.
- **Operational**: safe-stop report artifact explains cause and resume preconditions.
- **Testing**: transient-then-success, permanent-no-retry, exhaustion→safe-stop, node/gate timeouts, fallback, interruption at each node boundary (PVT-006), resume preconditions.
- **Governance**: resume is a human-reserved action (FR-GOV-001).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Misclassified failure | Unclassified ⇒ safe-stop (fail safe); classification reviewed with tests |
| Long backoffs slow demos | Virtual clock in tests; caps at 30 s |
| PVT-006 per-boundary coverage too costly | Pre-agreed reduction requires explicit human change decision (plan §14.1) |

## Reversibility

High. Values live in the graph contract; logic is centralized in `engine/retry.py`.

## Traceability

- Requirements: FR-ORC-014, FR-ORC-015, FR-ORC-016, FR-ORC-018, FR-ORC-019, FR-ORC-023, FR-GOV-014, NFR-REL-001, NFR-RCV-001, PVT-004, PVT-005, PVT-006, SC-005, A-016
- Spec: Edge Cases (interruption, retry exhausted, permanent failure)
- Plan: §6; workflow-graph `defaults` and per-node `failure_classification`
- Decisions: PD-003, PD-011, PD-012

## Validation

Reliability suite with fault injector (plan §10.3); SC-005 coverage: each injected fault reaches
its specified recovery path and a deterministic terminal outcome.
