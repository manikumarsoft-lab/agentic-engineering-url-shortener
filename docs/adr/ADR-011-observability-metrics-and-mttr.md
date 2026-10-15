# ADR-011: Observability — Logs, Traces, Metrics and MTTR Derived from Audit Events

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Related plan-gate approval: PD-005 in-house tracing (Mani Kumar
Vadugu, 2026-10-15). Logging (research R-11) pending this ADR.

## Context

Logs, metrics, traces and workflow history must suffice to reconstruct an execution; reliability
metrics (success rate, retry and rollback frequency, MTTR, latency) must be computed from recorded
events; demonstration metrics must be labeled (CON IX, FR-OBS-006/007, NFR-RCV-002). The brief
defines MTTR = total recovery duration of recovered failures ÷ number of recovered failures,
excluding unrecovered failures from the denominator.

## Decision Drivers

- Single source of truth (audit events) for metrics.
- Correlation across services (run ID = trace ID).
- Minimal dependencies; deterministic tests.
- Honest labeling of synthetic measurements.

## Options Considered

### Option A — In-house spans + W3C traceparent; stdlib JSON logging; metrics computed from audit
- **Approach**: `spans` table (trace = run, span = node attempt / subprocess / HTTP call); `traceparent` propagated to shortener; JSON log formatter with redaction; `observability/metrics.py` computes all metrics from audit events, including failure episodes (`FAILURE_DETECTED` → `RECOVERY_STARTED` → `RECOVERY_COMPLETED`, keyed by `episode_id`).
- **Advantages**: zero extra deps; metrics reproducible from data; deterministic tests.
- **Disadvantages**: no standard exporter/UI.
- **Risks**: reviewers expect OpenTelemetry.
- **Implementation impact**: small modules; span fields mirror OTel for later export.
- **Assessment implications**: every number is traceable to events.

### Option B — OpenTelemetry SDK + file exporter; Prometheus client
- **Approach**: OpenTelemetry SDK + file exporter; Prometheus client.
- **Advantages**: standards; tooling. **Disadvantages**: more deps; custom ID generator to align trace ID with run ID; metrics would live outside audit. **Risks**: timebox; metrics not derivable from audit alone. **Implementation impact**: moderate. **Assessment implications**: realism vs time.

### Option C — Logs only
- **Approach**: Logs only.
- **Advantages**: trivial. **Disadvantages**: weak reconstruction; metrics ad hoc. **Risks**: fails CON IX. **Implementation impact**: low. **Assessment implications**: insufficient.

## Decision

Option A. MTTR model (plan §7.3): episode fields `failure_detected_at`, `recovery_started_at`,
`recovery_completed_at`, `recovery_duration = completed − detected`, `mechanism`
(retry/rollback/compensation/human_resume/fallback), `status` (recovered/unrecovered/open),
`includes_human_wait`, `fault_injected`. MTTR over recovered episodes only; unrecovered and open
reported separately; breakdown by mechanism and with/without human wait. Every metrics response
carries `measurement_class: demonstration`, population definition, exclusions and disclaimer.
OpenTelemetry export (BL-06) and Prometheus endpoint (BL-07) are deferred.

## Rationale

Metrics that derive only from the audit log are verifiable and cannot diverge from the history
reviewers inspect.

## Consequences

- **Positive**: one consistent evidence base; reconstruction from run ID alone (SC-003).
- **Negative**: no dashboards; CLI/API views only (acceptable per EXC-001/A-011).
- **Operational**: logs in `var/logs/*.jsonl`; metrics on demand.
- **Testing**: MTTR arithmetic with hand-built event sequences (recovered/unrecovered/open); label presence; secret-free logs.
- **Governance**: synthetic numbers can never be presented as production statistics (schema `const: demonstration`).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Fault-injected episodes dominate MTTR | Flag counts and allow `include_fault_injection=false`; disclose |
| Human-wait inflates MTTR | Report MTTR excluding human wait alongside |
| Missing `RECOVERY_COMPLETED` emission paths | Completeness tests per mechanism |

## Reversibility

High. Span model mirrors OTel; exporters can be added without changing the audit source.

## Traceability

- Requirements: FR-OBS-001, FR-OBS-006, FR-OBS-007, FR-OBS-009, NFR-OBS-001, NFR-RCV-002, SC-003
- Spec: US-5; Constitution IX
- Plan: §7, §12 R-10, R-11; orchestrator-api ReliabilityMetrics schema
- Decisions: PD-005; CST-008 #5 (aggregate MTTR deferrable)

## Validation

Observability suite; e2e metrics output for scenario runs contains labeled demonstration
measurements and per-mechanism MTTR.
