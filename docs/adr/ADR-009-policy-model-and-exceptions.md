# ADR-009: Policy-as-Data Model, Evaluation and Exceptions

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15.

## Context

Policy guardrails must be defined, versioned and cover security, compliance, privacy, audit
retention, approved dependencies, licensing and change control; each check yields exactly one of
PASS/FAIL/EXCEPTION-REQUESTED/NOT-APPLICABLE; mandatory FAIL blocks; exceptions need human
approval with full metadata and expiry (CON VI, FR-GOV-005..012). Scanner tooling for SEC/DEP/LIC
checks must run locally (research R-12).

## Decision Drivers

- Versioned, reviewable policies (change control).
- Deterministic evaluation with evidence.
- Blocking semantics enforced by the engine, not by convention.
- Non-waivable checks protected (Governance §3).

## Options Considered

### Option A — Versioned YAML policy set + Python check implementations + append-only evaluations
- **Approach**: `contracts/policy-set.v1.yaml` declares checks (domain, mandatory, evaluation node, parameters); each check ID maps to a registered Python function returning outcome + evidence; evaluations appended (never overwritten); exceptions via G-EXCEPTION.
- **Advantages**: reviewable; parameters change without code; closed set of tested checks.
- **Disadvantages**: two places per check (YAML declaration + code).
- **Risks**: declaration/implementation mismatch.
- **Implementation impact**: registry with load-time verification that every declared check has an implementation.
- **Assessment implications**: governance visible and testable.

### Option B — General policy engine (e.g., OPA/Rego)
- **Approach**: General policy engine (e.g., OPA/Rego).
- **Advantages**: industry pattern; expressive. **Disadvantages**: extra binary and language; not installed. **Risks**: timebox; reviewer setup. **Implementation impact**: integration layer. **Assessment implications**: more realism, less time for scenarios.

### Option C — Hard-coded checks in stage code
- **Approach**: Hard-coded checks in stage code.
- **Advantages**: fastest. **Disadvantages**: not versioned/reviewable; violates CON VI intent. **Risks**: hidden policy changes. **Implementation impact**: low. **Assessment implications**: weak.

## Decision

Option A. Scanner adapters (behind interfaces): `pip-audit` (SEC-003), `detect-secrets` with
committed baseline (SEC-002), `pip-licenses` (LIC-001/002). Tool unavailability after retries
yields FAIL, never PASS. Blocking rule and the ST-03 routing rule as in plan §9.1. Exceptions:
engineer requests, approver decides at G-EXCEPTION; max expiry 30 days; non-waivable checks
(AUD-002, REL-001, SEC-002, CHG-004) refuse exception requests (`422 check_non_waivable`).

## Rationale

Keeps policy content governed as data while keeping evaluation logic small, tested and local.

## Consequences

- **Positive**: every run records the policy version and full evaluation history.
- **Negative**: adding a new check needs code + YAML + tests.
- **Operational**: SEC-003 needs network; offline runs end in FAIL → exception path.
- **Testing**: each check PASS/FAIL/N-A; exception lifecycle incl. expiry → REL-003 FAIL; non-waivable refusal.
- **Governance**: mandatory FAIL blocks progression and release readiness (plan §9.3).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Declared check without implementation | Loader verification; engine refuses to start |
| Advisory DB unavailable in demos | Documented exception flow; pre-run connectivity note in quickstart |
| Lexicon-based PRIV-001 false positives/negatives | Lexicon versioned in policy parameters; residual risk documented |

## Reversibility

High. Policy file is versioned; check implementations are isolated modules; an OPA adapter could replace evaluation later.

## Traceability

- Requirements: FR-GOV-005, FR-GOV-006, FR-GOV-007, FR-GOV-008, FR-GOV-010, FR-GOV-012, FR-SHR-023, NFR-SEC-002, PVT-012, SC-008
- Spec: Constitution VI; SCN-C-AC5
- Plan: §9, §12 R-12; contracts/policy-set.v1.yaml; schemas policy-evaluation, policy-exception
- Decisions: PD-002b (AUD-001 parameter)

## Validation

Policy suite; `test_release_blocked_by_mandatory_fail`; `test_readiness_fail_lists_blocking_reasons`;
SCN-C option-B variant reaching `SAFE_STOPPED` on PRIV-001 FAIL.
