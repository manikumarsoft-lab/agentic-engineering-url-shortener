# ADR-019: Analytics Consistency (Exact Counts vs Non-Blocking Redirects)

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. The tension between A-013 and FR-SHR-011 was ruled by the human
owner at Human Gate 4, ruling 2 (2026-10-15).

## Context

Analytics (delivered by SCN-A, extended by SCN-C option A) must count successful redirects and
last redirect time (FR-SHR-010), must be exact under concurrency with no lost increments (A-013,
approved), must never block or fail a redirect, with analytics failures recorded (FR-SHR-011,
NFR-REL-002), and must contain no personal data (FR-SHR-012). Persistence is SQLite with a single
writer (ADR-002).

**Tension**: if the analytics write fails (e.g., lock timeout) while the redirect succeeds, the
count misses that redirect. FR-SHR-011 requires the redirect to succeed; A-013 requires no lost
increments.

## Decision Drivers

- Redirect availability first (FR-SHR-011 is derived from FI + CON VIII).
- Exactness in the absence of analytics failures.
- Transparent accounting of any loss.

## Options Considered

### Option A — Synchronous atomic increment after resolution, separate transaction, fallback with recorded failure
- **Approach**: resolve link (read) → issue redirect decision → `UPDATE link_stats SET redirect_count = redirect_count + 1, last_redirect_at = :now` (and daily upsert for SCN-C) in its own short transaction; on failure log + increment the `analytics_write_failures` counter (metric and logs) and still return 302.
- **Advantages**: exact under concurrency (atomic SQL increment); redirect never blocked; losses are counted and visible.
- **Disadvantages**: each redirect is a write (SQLite contention with creates).
- **Risks**: PVT-001 latency under load (non-gating).
- **Implementation impact**: small; fault-injection test for analytics failure.
- **Assessment implications**: honest, testable semantics.

### Option B — Same transaction as resolution (redirect fails if analytics fails)
- **Approach**: Same transaction as resolution (redirect fails if analytics fails).
- **Advantages**: never loses a count. **Disadvantages**: violates FR-SHR-011. **Risks**: availability. **Implementation impact**: low. **Assessment implications**: rejected.

### Option C — Asynchronous in-memory buffer flushed periodically
- **Approach**: Asynchronous in-memory buffer flushed periodically.
- **Advantages**: fast redirects. **Disadvantages**: process crash loses buffered counts (violates A-013 more often); non-exact reads. **Risks**: data loss. **Implementation impact**: medium. **Assessment implications**: weaker.

### Option D — Durable outbox/retry queue for failed increments
- **Approach**: Durable outbox/retry queue for failed increments.
- **Advantages**: eventual exactness. **Disadvantages**: extra write path that can also fail; complexity. **Risks**: timebox. **Implementation impact**: medium–high. **Assessment implications**: over-engineering for prototype.

## Decision

Option A, as ruled at **Human Gate 4, ruling 2 (Mani Kumar Vadugu, 2026-10-15)**:
- A-013 ("exact, no lost increments") applies to concurrent redirects **while analytics storage is
  healthy**.
- When the analytics write fails, FR-SHR-011 takes precedence and the redirect succeeds.
- The missed increment is counted as an analytics write failure, logged with its correlation ID,
  exposed as the `analytics_write_failures` metric (delivered with the SCN-A change set), and
  disclosed as a documented limitation.
- No durable outbox. Option D is recorded as backlog item BL-12.

## Rationale

Availability of redirects is the user-facing priority; exactness is guaranteed for the
concurrency case A-013 was written for; residual loss is transparent rather than hidden.

## Consequences

- **Positive**: exact counts under concurrency; redirect resilience.
- **Negative**: counts may under-report during analytics outages (measured).
- **Operational**: `analytics_write_failures` metric and log events; limitation disclosed in `docs/limitations.md`.
- **Testing**: concurrent redirect exactness test; analytics-failure fault injection (NFR-REL-002, 100% redirects succeed); failure-count assertion.
- **Governance**: SCN-A change set must implement this ADR; PRIV-001 checks the schema.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Write contention slows redirects | Short transactions; busy timeout; measure PVT-001 (non-gating) |
| Silent loss | Failure counter + log event with correlation ID |

## Reversibility

High. An outbox (Option D, backlog BL-12) can be added later without a contract change.

## Traceability

- Requirements: FR-SHR-010, FR-SHR-011, FR-SHR-012, FR-SHR-014, FR-SHR-023, NFR-REL-002, A-005, A-013
- Spec: SCN-A; Edge Cases (analytics recording fails); DQ-002
- Plan: §2.1 (Analytics), §11.1, §11.3; data-model LinkAnalytics, LinkDailyStats
- Decisions: HD-002, PD-008, PD-002 (302 keeps counting accurate)

## Validation

SCN-A ST-09 tests in the workspace (concurrency exactness, fallback); SCN-C daily-bucket tests.
