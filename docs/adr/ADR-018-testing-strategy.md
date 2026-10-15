# ADR-018: Testing Strategy (TDD, Fault Injection, Determinism, Requirement-Marked Tests)

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Related plan-gate approval: PD-006 (Mani Kumar Vadugu, 2026-10-15).

## Context

Red-green-refactor TDD is mandatory where practical; the portfolio must include unit,
integration, API contract, orchestration transition, reliability, security and e2e tests; task
completion requires executed validation (CON IV; NFR-TST-001; PVT-007). Scenario evidence must
come from deterministic mode only (FR-ORC-029) and be reproducible (NFR-DET-001). Traceability
requires tests linked to requirements (CON X, SC-007).

## Decision Drivers

- Executed tests as primary evidence.
- Failure paths testable without real outages.
- Fast, deterministic suites.
- Machine-readable requirement links.

## Options Considered

### Option A — pytest pyramid + virtual clock + fault-injection capability + `req` markers
- **Approach**: unit/property tests (Hypothesis) for domain and engine tables; in-process ASGI for API; real subprocesses for integration/e2e; `FaultInjector` capability (test config and labeled runs only); virtual `Clock`; `@pytest.mark.req(...)` + JUnit properties; coverage ≥ 85% on domain/engine/policy/observability.
- **Advantages**: covers all categories; deterministic; traceable.
- **Disadvantages**: fault-injection code exists in product (gated).
- **Risks**: injector accidentally enabled.
- **Implementation impact**: test plugin for markers; injector wiring.
- **Assessment implications**: direct evidence for SC-005, SC-006, SC-007.

### Option B — Mock-heavy unit tests only
- **Approach**: Mock-heavy unit tests only.
- **Advantages**: fast. **Disadvantages**: no real process/DB behavior. **Risks**: false confidence. **Implementation impact**: low. **Assessment implications**: insufficient.

### Option C — Chaos-style random fault injection
- **Approach**: Chaos-style random fault injection.
- **Advantages**: discovers unknowns. **Disadvantages**: nondeterministic. **Risks**: flaky evidence. **Implementation impact**: medium. **Assessment implications**: conflicts with NFR-DET-001.

## Decision

Option A. Red phase failure messages recorded in the task log as genuine output. Fault injection
disabled by default; enabling it labels runs `fault-injection` and audits `FAULT_INJECTED`.
Scripted decisions only in tests (PD-006). Where TDD is impractical (scanner binaries, process
timing on Windows, doc templates), the reason is recorded (plan §10.4).

## Rationale

Deterministic, injected failure paths are the only reliable way to evidence retry, rollback,
compensation, safe-stop and resume within the timebox.

## Consequences

- **Positive**: complete portfolio; reproducible e2e.
- **Negative**: e2e suite slower (subprocesses).
- **Operational**: `tools/check.py` is the single command.
- **Testing**: as above.
- **Governance**: REL-001 consumes JUnit results; traceability tool consumes markers.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Injector enabled outside tests | Requires explicit config flag + run label; policy/test asserts default off |
| Flaky subprocess tests on Windows | Readiness polling, generous timeouts, retries only in harness setup (never in assertions) |
| Coverage gaming | Coverage scope fixed to logic packages; mutation testing not in scope (documented) |

## Reversibility

High.

## Traceability

- Requirements: NFR-TST-001, NFR-DET-001, NFR-REL-001, NFR-RCV-001, FR-ORC-029, SC-005, SC-006, SC-007, SC-010, PVT-006, PVT-007
- Spec: Constitution IV, X, XI
- Plan: §10, §13, §14.2 slice exits
- Decisions: PD-006

## Validation

`tools/check.py` green at each slice; coverage report; traceability `--check` shows every C/D
requirement with ≥1 test.
