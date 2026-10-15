# ADR-008: Audit Model and Integrity (Append-Only, Hash-Chained)

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Research R-08 pending this ADR. Related plan-gate approval: PD-002b
audit retention (Mani Kumar Vadugu, 2026-10-15).

## Context

Audit records must be append-only, carry required fields, include the run ID as correlation ID
and be sufficient to reconstruct any run (CON IX — non-waivable per Governance §3; FR-OBS-001..005;
SC-003). Attempted modification must be refused and itself audited (FR-OBS-004). Retention is
≥ 365 days with no automated deletion (PD-002b).

## Decision Drivers

- Atomicity with state transitions (no dual-write).
- Tamper resistance and tamper evidence.
- Queryability by run, requirement, actor, event type.
- Schema-validated events.

## Options Considered

### Option A — Append-only DB table + triggers + per-run SHA-256 hash chain
- **Approach**: `audit_events` in the orchestrator DB, written in the same transaction as the state change; `BEFORE UPDATE/DELETE` triggers abort; each event stores `prev_hash` and `hash = sha256(canonical_json(event − hash))`; gapless per-run `seq`; unique `transition_key`.
- **Advantages**: atomic with state; DB-level refusal; out-of-band edits detectable; queryable.
- **Disadvantages**: a full consistent rewrite of a chain by someone with file access is undetectable without an external anchor.
- **Risks**: canonicalization bugs break verification.
- **Implementation impact**: canonical JSON function; verifier (`orch audit verify`, AUD-002).
- **Assessment implications**: verifiable rather than asserted auditability.

### Option B — Triggers only
- **Approach**: Triggers only.
- **Advantages**: simple. **Disadvantages**: no detection of edits made outside SQLite triggers (e.g., file-level edits). **Risks**: weaker claim. **Implementation impact**: minimal. **Assessment implications**: weaker.

### Option C — Separate append-only JSONL log
- **Approach**: Separate append-only JSONL log.
- **Advantages**: easy export. **Disadvantages**: dual-write with DB state (inconsistency on crash). **Risks**: lost/duplicated events. **Implementation impact**: outbox or fsync logic. **Assessment implications**: violates atomicity.

## Decision

Option A. Event schema `contracts/schemas/audit-event.schema.json` v1.0.0. Mutation endpoints
return 405 and emit `AUDIT_TAMPER_REFUSED`. `orch audit export` writes JSONL plus head hash for
external anchoring. Events never contain secrets or personal data (redaction applied before
hashing). Audit-table migrations use non-batch `ADD COLUMN` only (ADR-002).

## Rationale

Combines prevention (triggers), detection (hash chain) and atomicity (same transaction).

## Consequences

- **Positive**: reconstructable runs; tamper evidence; schema validation of every event in tests.
- **Negative**: verification cost grows with run length (negligible at demo scale).
- **Operational**: export provides archival copy; no deletion (PD-002b).
- **Testing**: trigger refusal, hash-chain break detection, completeness test (PVT-008), schema validation of all emitted events.
- **Governance**: AUD-001/AUD-002 at ST-12; AUD-002 is non-waivable.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Whole-chain rewrite | Head hash recorded in evidence manifest and release-readiness doc (external anchor); documented residual risk |
| Canonicalization mismatch | Single canonical function; property test round-trip |
| Secrets leaking into `data` | Redaction filter + secret-pattern scan over exported audit in tests |

## Reversibility

Medium. Event schema is versioned; storage could move to another store, but chain semantics should be preserved.

## Traceability

- Requirements: FR-OBS-001, FR-OBS-002, FR-OBS-003, FR-OBS-004, FR-OBS-005, NFR-AUD-001, NFR-OBS-001, PVT-008, SC-003, A-007
- Spec: US-5; Constitution IX
- Plan: §4, §7.1, §8 (Audit integrity), §12 R-08; data-model.md AuditEvent; policy AUD-001/002
- Decisions: PD-002b

## Validation

Observability suite: completeness per transition, chain verification, tamper tests; e2e: evidence
export with head hash for each scenario run.
