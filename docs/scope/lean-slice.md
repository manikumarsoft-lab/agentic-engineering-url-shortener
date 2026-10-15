# Lean Implementation Slice (HD-CUT-002)

**Decision**: HD-CUT-002, Mani Kumar Vadugu (human owner), 2026-10-15 15:55.

> The re-cut schedule cannot meet the 2026-10-16 15:30 deadline. Decision: deliver a lean
> implementation that demonstrates every assessed capability, without per-task ceremony.
> tasks.md is retained as the planning record; implementation follows the lean slice below.

**Records**: plan.md change log (HD-CUT-002); planning record
`specs/001-agentic-sdlc-url-shortener/tasks.md` (not executed task by task); earlier cuts in
plan.md §16.5 (HD-CUT-001).

**Rule**: everything in §1 must work and be covered by automated tests. Everything in §2 is
**planned, not implemented**. It is disclosed as a limitation and never presented as built.

---

## 1. Built (must all work, with tests)

### 1.1 URL shortener API

| Capability | Requirements |
|------------|--------------|
| Create short link | FR-SHR-001, FR-SHR-005, FR-SHR-006 |
| Redirect | FR-SHR-007 |
| Expiry → `410` | FR-SHR-008, FR-SHR-009, A-014 |
| Stats (redirect count, last redirect time) | FR-SHR-010, FR-SHR-011, FR-SHR-012 |
| Health | FR-SHR-016 |
| URL validation | FR-SHR-002, FR-SHR-003, FR-SHR-004 |
| API key on protected operations | FR-SHR-019 |

### 1.2 Orchestrator engine

| Capability | Requirements |
|------------|--------------|
| YAML dependency graph | FR-ORC-005, FR-ORC-007 |
| Parallel fork and join | FR-ORC-006, FR-ORC-037..039 |
| SQLite-persisted state | FR-ORC-011, FR-ORC-012, FR-ORC-013 |
| Human gates: approve, reject, timeout → `SAFE_STOPPED` | FR-GOV-001, FR-GOV-002, FR-GOV-014 |
| Agent key refused and audited | FR-GOV-003, NFR-AUT-001, SC-011 |
| Bounded retry (3) with transient/permanent classification | FR-ORC-014, PVT-004 |
| Stage timeout | FR-ORC-015 |
| Fallback | FR-ORC-016 |
| Rollback by discarding an isolated workspace copy | FR-ORC-017, FR-ORC-032, FR-ORC-035 |
| Compensation step | FR-ORC-017, FR-ORC-042 |
| Safe-stop and human resume | FR-ORC-018, FR-ORC-019 |
| Replanning that re-runs only stale downstream nodes | FR-ORC-020, FR-ORC-021, SC-006 |
| Versioned policy check: FAIL blocks release; an exception needs human approval | FR-GOV-005..008, FR-GOV-010, FR-GOV-011 |
| Append-only, hash-chained audit | FR-OBS-001..004 |
| Per-run metrics: success, retries, rollbacks, MTTR, latency, labelled demonstration | FR-OBS-006, FR-OBS-007 |

### 1.3 CLI `orch`

`run submit`, `run status`, `gate list`, `gate approve`, `gate reject`, `run resume`,
`audit show`, `audit verify`, `metrics`, `keys create`.

### 1.4 Three scenarios (orchestrated runs)

| Scenario | Content |
|----------|---------|
| SCN-A greenfield | Expiry and stats delivered through an orchestrated run |
| SCN-B brownfield | Impact analysis computed from baseline code (plan §16.1 C2); defective variant fails tests and is rolled back by discarding the workspace |
| SCN-C ambiguous | "Track who clicks links": the clarification answer selects the change set, or the run ends `FAILED` when no approved change set exists (plan §16.1 C1) |

---

## 2. Planned, not implemented

### 2.1 Shortener

- Idempotency keys (FR-SHR-013).
- Creation rate limiting (FR-SHR-017, PVT-011).
- Explicit persistence-unavailable behavior and readiness vs liveness distinction beyond basic health (FR-SHR-015, FR-SHR-016 readiness part).
- Structured operational logs with correlation IDs (FR-OBS-009).
- PVT-003 concurrency test (1,000 concurrent creations) and PVT-001/002 latency measurement.
- Custom aliases in the baseline API (they exist only as the SCN-B change set, CST-007).
- Contract tests against `shortener-api.openapi.yaml`.

### 2.2 Orchestrator engine and governance

- Orchestrator HTTP API (`orchestrator-api.openapi.yaml`); the CLI is the only interface.
- Gate decisions `escalate`, and the `reject_rework` vs `reject_terminate` distinction with the PVT-013 rework bound (FR-GOV-015, FR-GOV-016).
- Clarification-round limit and `free_text` reopening (plan §16.1 C1, beyond change-set selection).
- Deterministic superstep commit order and the repeat-run determinism test (NFR-DET-001).
- Subprocess runner with process-tree kill and attempt fencing (plan §16.3).
- Startup interruption recovery and per-boundary interruption tests (PVT-006, NFR-RCV-001).
- Retry-budget extension on resume (plan §16.3).
- Full policy set `policy-set.v1.yaml` (SEC, PRIV, ARCH, AUD, DEP, LIC, CHG, REL domains) and the scanner adapters (pip-audit, detect-secrets, pip-licenses); hash-pinned advisory snapshot (plan §16.1 C5).
- Separation of duties between key identities (FR-GOV-017) and exception expiry (FR-GOV-008 expiry part).
- Change-set lock verified against an annotated tag (CHG-001, plan §16.3), and the undeclared-scope check (CHG-002, SCN-B-AC5).
- Additive-change check ST-05a (SCN-A-AC6) and the late-ambiguity variant (SCN-A-AC4).
- Staging service with smoke check, G-CORRECTIVE and the non-rollbackable-effects list (FR-ORC-040..042 beyond the compensation step).
- AI-backed agent stub (FR-ORC-027, FR-ORC-030).

### 2.3 Observability, traceability and evidence

- Audit query filters by requirement, actor and event type (FR-OBS-005).
- Run-level bidirectional traceability and `orch trace` (FR-OBS-008).
- Repository traceability checker and orphan detection (FR-OBS-010, SC-007).
- Evidence export, offline verifier and run index.
- Aggregate metrics across runs; per-stage latency percentiles.

### 2.4 Tooling, documentation and release

- CI workflow (CST-009), `tools/check.py` coverage gate (PVT-007).
- Documents planned in tasks.md: architecture, threat model, testing, limitations, change control, reviewer guide, release-readiness report, automated quickstart test (NFR-DOC-001).
- `orch release check`, `orch demo reset`, `orch staging bootstrap|status`.
- Per-task TDD Evidence Log and per-task ceremony (HD-CUT-002).

### 2.5 Earlier cuts

- BL-01..BL-13 (plan §14.1) and BL-14..BL-21 (HD-CUT-001, plan §16.5).

---

## 3. Open questions for the human owner

1. **Final engineering summary** (FR-ORC-026, ASMT §4.8), **README with setup, architecture, testing, limitations, trade-offs and the AI-governance section** (CST-003, CST-009), and the **submission tag** are not in the lean slice. Are they built?
2. **Expiry and stats** are listed under the shortener API, but CST-007 says scenario capabilities exist only as change sets. Reading taken here: they are delivered by the SCN-A change set and are live in the system under change after the SCN-A run, not in the baseline. Confirm.
3. **Constitution IV (TDD)**: "without per-task ceremony" drops the recorded red phase per task. If CON IV requires that record, a Governance §2 exception is needed.
4. **Release step**: "FAIL blocks release" implies a release-readiness gate (G-RELEASE). It is assumed to be built as part of the policy check. Confirm.
