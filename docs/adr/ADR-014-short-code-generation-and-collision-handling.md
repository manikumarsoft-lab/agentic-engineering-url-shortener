# ADR-014: Short-Code Generation and Collision Handling

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Alias length rule decided by the human owner at Human Gate 4, ruling
1 (2026-10-15): 4–10 characters.

## Context

Codes must be unique, never map to two destinations even under concurrency (FR-SHR-005,
PVT-003), must not be sequentially predictable (FR-SHR-006), and are case-sensitive, URL-safe and
at most 10 characters (A-003). Custom aliases (SCN-B) must satisfy "the same character-set and
length rules as generated codes" and avoid reserved words (FR-SHR-021). Collisions during
generation retry within a bound; exhaustion returns an explicit failure with no partial record
(Edge Cases).

## Decision Drivers

- Enumeration resistance.
- Uniqueness guaranteed by the database, not by application checks.
- Simplicity under SQLite single-writer semantics.

## Options Considered

### Option A — CSPRNG base62, fixed length 7, DB unique constraint, bounded retry
- **Approach**: `secrets.choice` over `[A-Za-z0-9]`, length 7 (62⁷ ≈ 3.5×10¹²); insert relies on PK uniqueness; on `IntegrityError` regenerate, up to 5 attempts; then `503 code_generation_exhausted`, no record.
- **Advantages**: non-sequential; uniqueness enforced atomically; tiny collision probability.
- **Disadvantages**: codes not human-friendly.
- **Risks**: exhaustion only under adversarial or tiny keyspace (not applicable).
- **Implementation impact**: generator + retry loop in domain; Hypothesis tests.
- **Assessment implications**: clear security reasoning.

### Option B — Sequential ID + base62 encoding (optionally obfuscated)
- **Approach**: Sequential ID + base62 encoding (optionally obfuscated).
- **Advantages**: no collisions. **Disadvantages**: predictable/enumerable (violates FR-SHR-006) unless obfuscated; obfuscation is reversible. **Risks**: enumeration. **Implementation impact**: low. **Assessment implications**: fails a derived security requirement.

### Option C — Hash of URL (truncated)
- **Approach**: Hash of URL (truncated).
- **Advantages**: deterministic. **Disadvantages**: same URL → same code conflicts with A-004 (no implicit dedup); truncation collisions; predictable for known URLs. **Risks**: enumeration of known destinations. **Implementation impact**: medium. **Assessment implications**: conflicts with A-004.

## Decision

Option A. Code validity rule for path parameters and aliases: `^[A-Za-z0-9]{4,10}$`; generated
codes are exactly 7. Reserved words (case-insensitive): `api`, `health`, `docs`, `openapi`,
`redoc`, `static`, `admin`, plus any first path segment used by the service.

**Alias length (Human Gate 4, ruling 1, Mani Kumar Vadugu, 2026-10-15)**: FR-SHR-021's "same
length rules as generated codes" means the code *rule*, 4–10 characters; generated codes are one
instance of it (length 7). Aliases are therefore valid at 4–10 characters, not only 7. This
governs SCN-B tests and shortener contract 1.2.0.

## Rationale

Randomness provides enumeration resistance; the database provides the uniqueness guarantee.

## Consequences

- **Positive**: race-free uniqueness; FR-SHR-006 satisfied.
- **Negative**: codes are opaque.
- **Operational**: none.
- **Testing**: property tests (charset, length, no successor predictability statistic), forced-collision test via injected generator, exhaustion test, PVT-003.
- **Governance**: alias rule change after approval is a contract change (MINOR/MAJOR per ADR-007).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Alias squats a future route | Reserved list + contract review on new routes |
| Generator mocked in production by mistake | Generator injected only via config in tests; default CSPRNG |

## Reversibility

High for generated length/charset going forward (existing codes stay valid within 4–10).

## Traceability

- Requirements: FR-SHR-005, FR-SHR-006, FR-SHR-014, FR-SHR-020, FR-SHR-021, NFR-SCL-001, PVT-003, A-003, A-004
- Spec: Edge Cases (collision, concurrent creation)
- Plan: §2.1 (Short-code generation), §8 (Abuse cases); data-model.md ShortLink
- Decisions: HD-002 (SCN-B content)

## Validation

Unit/property tests; concurrency test (1,000 creations, zero collisions); SCN-B alias tests covering
lengths 3 (rejected), 4, 7, 10 (accepted) and 11 (rejected).
