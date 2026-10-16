# Lean Implementation Slice (HD-CUT-002)

**Decision**: HD-CUT-002, Mani Kumar Vadugu (human owner), 2026-10-15 15:55.

> The re-cut schedule cannot meet the 2026-10-16 15:30 deadline. Decision: deliver a lean
> implementation that demonstrates every assessed capability, without per-task ceremony.
> tasks.md is retained as the planning record; implementation follows the lean slice below.

**Records**: plan.md change log (HD-CUT-002, HD-SCN-001, CR-007, CR-008); planning record
`specs/001-agentic-sdlc-url-shortener/tasks.md` (status per task added by CR-008); earlier cuts in
plan.md §16.5 (HD-CUT-001).

**Rule**: everything in §1 works and is covered by automated tests (`python -m pytest`, run in CI).
Everything in §2 is **planned, not implemented**. It is disclosed as a limitation and never
presented as built. Status as of CR-008 (2026-10-15).

---

## 1. Built (with tests)

### 1.1 URL shortener API

| Capability | Requirements |
|------------|--------------|
| Create short link (random 7-char base62, collision retry ≤ 5, idempotency key) | FR-SHR-001, FR-SHR-005, FR-SHR-006, FR-SHR-013 |
| Redirect (302, no-cache, no-referrer) | FR-SHR-007 |
| Expiry → `410` | FR-SHR-008, FR-SHR-009, A-014 |
| Stats (redirect count, last redirect time; analytics never block redirects) | FR-SHR-010, FR-SHR-011, FR-SHR-012 |
| Health: live vs ready (DB reachable, analytics write failures); storage outage → 503, never a redirect | FR-SHR-015, FR-SHR-016 |
| URL validation (http/https only, private/loopback/link-local, credentials, self domain, length) | FR-SHR-002, FR-SHR-003, FR-SHR-004 |
| API key on protected operations; rate limit 60 creates/min per key | FR-SHR-017, FR-SHR-019 |
| Errors never leak internals; JSON request logs with `X-Request-ID`, no secrets or personal data | FR-SHR-018, FR-OBS-009 |
| Generated OpenAPI contract as single source, drift test (CR-007) | CST-003 |
| 200 parallel creates → unique codes (real server) | FR-SHR-014 |

### 1.2 Orchestrator engine

| Capability | Requirements |
|------------|--------------|
| YAML dependency graph with conditional nodes | FR-ORC-005, FR-ORC-007 |
| Parallel fork and join (superstep, subprocess-isolated agents) | FR-ORC-006, FR-ORC-037..039 |
| SQLite-persisted state, artifacts with provenance, decision lineage | FR-ORC-011, FR-ORC-012, FR-ORC-013 |
| Human gates: approve, reject (rework ≤ 2 / terminate), escalate, timeout → `SAFE_STOPPED`; clarification gates with options, free text reopens, 2 rounds | FR-GOV-001, FR-GOV-002, FR-GOV-014..016 |
| Agent key refused and audited | FR-GOV-003, NFR-AUT-001, SC-011 |
| Bounded retry (3) with transient/permanent classification | FR-ORC-014, PVT-004 |
| Stage timeout with process-tree kill | FR-ORC-015 |
| Fallback | FR-ORC-016 |
| Rollback (pre-promotion) by discarding an isolated workspace copy | FR-ORC-017, FR-ORC-032, FR-ORC-035 |
| Compensation (post-promotion): previous staging release restored, effects listed, human-approved corrective action | FR-ORC-017, FR-ORC-040..042 |
| Safe-stop, startup interruption recovery, human resume | FR-ORC-018, FR-ORC-019 |
| Replanning that re-runs only stale downstream nodes and revokes approvals | FR-ORC-020, FR-ORC-021, SC-006 |
| Versioned policy (PRIV-001, SEC-002, SEC-003, SEC-004, REL-001): FAIL blocks release; an exception needs human approval | FR-GOV-005..008, FR-GOV-010, FR-GOV-011, FR-GOV-012 |
| SEC-003: real pip-audit snapshot of `requirements.lock`, hash-pinned in the policy set; live pip-audit in `orch release check` and CI | FR-GOV-012, PVT-012 |
| SEC-004: regex secret scan of the released code (scenario runs) and of the repository (`orch release check`) | NFR-SEC-002 |
| Append-only, hash-chained audit | FR-OBS-001..004 |
| Per-run metrics: success, retries, rollbacks, compensations, MTTR, latency, labelled demonstration | FR-OBS-006, FR-OBS-007 |
| Final engineering summary for every outcome (COMPLETED, FAILED, ABORTED, SAFE_STOPPED) stating why | FR-ORC-026 |
| Evidence export per run + index of every run; lean traceability check in CI | FR-ORC-031 |

### 1.3 CLI `orch`

`keys create`, `run submit|status|watch|resume|recover`, `gate list|show|approve|reject|escalate|answer`,
`exception request|approve`, `changeset lock`, `audit show|verify`, `metrics`, `evidence export`,
`advisory snapshot`, `release check`, `serve`.

### 1.4 Scenarios (orchestrated runs, HD-SCN-001)

| Scenario | Content |
|----------|---------|
| `scn-a` greenfield | Link details endpoint `GET /api/v1/links/{code}`, owner-scoped; no clarification gate (reason recorded) |
| `scn-b` brownfield | Custom aliases; impact analysis from the requirement and the baseline import graph before any change |
| `scn-b-defective` | Fault-injection: regression fails **before promotion** → ROLLBACK (workspace discarded) |
| `scn-b-compensate` | Fault-injection: post-promotion smoke fails **after promotion** → COMPENSATION (previous release restored) → human-approved corrective action disables aliases created meanwhile |
| `scn-c` ambiguous | "Track who clicks links": option A selects the change set from the catalog; C aborts; free text reopens, then safe-stops |
| `scn-c-scanner-down` | Fault-injection: SEC-003 FAIL blocks release → human-approved exception → resume → COMPLETED |

Every change set is test-first: the run records the failing new tests (red) before the
implementation patch and the passing full suite (green) after it.

### 1.5 Change-set limitation (applies to all scenarios)

Change sets are authored with `tools/author_changesets.py` against **one baseline** — the
shortener in the commit that contains them (`src/`, `tests/shortener`, the generated contract,
`pyproject.toml`). Each change set applies to that baseline **independently**: SCN-B does not build
on SCN-A's output and there is no R0→R1→R2 release chain. Each manifest records the SHA-256 of the
baseline files it patches. Any later edit to those files makes the patches stop applying
(`patch_does_not_apply`): re-run the authoring tool and lock the change sets again.
**No baseline tag exists yet**: the human owner should tag the commit that holds the baseline and
the locked change sets (for example `shortener-baseline-v1`) before recording evidence.

---

## 2. Planned, not implemented

### 2.1 Shortener

- PVT-001/002 latency measurement under load.

### 2.2 Orchestrator engine and governance

- Orchestrator HTTP API (`orchestrator-api.openapi.yaml`); the CLI is the only interface.
- Repeat-run determinism test (NFR-DET-001); the commit order is deterministic but not verified by a test.
- Attempt fencing tokens on artifact writes (plan §16.3).
- Interruption at **every** stage boundary (PVT-006); one real process-kill test and startup recovery exist.
- Per-node retry-budget grants on resume: resume resets the failed node's budget (audited as `RETRY_BUDGET_RESET`) instead.
- Remaining policy domains: ARCH, AUD, DEP, LIC, CHG-003 migrations; detect-secrets and pip-licenses (a regex secret scan is used).
- Separation of duties between key identities (FR-GOV-017) and exception expiry.
- Change-set lock anchored to an annotated git tag; the lock file written by `orch changeset lock` (approver key) is used instead.
- Undeclared-scope check (CHG-002, SCN-B-AC5): the check exists in `apply_impl` but no test exercises it, so it is not counted as demonstrated.
- Additive-change check ST-05a (SCN-A-AC6) and the late-ambiguity variant (SCN-A-AC4).
- AI-backed agent stub (FR-ORC-027, FR-ORC-030).

### 2.3 Observability, traceability and evidence

- Audit query filters by requirement, actor and event type (FR-OBS-005); `orch audit show` lists a run's events.
- Bidirectional requirement ↔ test traceability and `orch trace` (FR-OBS-008); the CI check links requirements to modules/tests only.
- Aggregate metrics across runs; per-stage latency percentiles.

### 2.4 Tooling, documentation and release

- Coverage gate (PVT-007).
- Documents planned in tasks.md: architecture, threat model, testing, limitations, change control, reviewer guide, release-readiness report, automated quickstart test (NFR-DOC-001). The README is still a stub.
- `orch demo reset`, `orch staging bootstrap|status`.
- Per-task TDD Evidence Log and per-task ceremony (HD-CUT-002).

### 2.5 Earlier cuts

- BL-01..BL-13 (plan §14.1) and BL-14..BL-21 (HD-CUT-001, plan §16.5).

---

## 3. Open questions for the human owner

1. **README** (setup, architecture, testing, limitations, trade-offs, AI-governance section; CST-003, CST-009) and the **submission tag** are not built. The final engineering summary is built (§1.2).
2. ~~Expiry and stats placement~~ — resolved by HD-SCN-001: they are baseline features.
3. **Constitution IV (TDD)**: "without per-task ceremony" drops the recorded red phase per task. Scenario change sets do record red then green; the baseline code was not developed red-first. If CON IV requires that record, a Governance §2 exception is needed.
4. ~~Release gate~~ — built: `approve-release` (release-owner) opens only after the policy checks pass.
