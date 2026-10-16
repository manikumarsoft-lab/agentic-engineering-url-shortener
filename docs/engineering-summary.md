# Engineering Summary: Agentic SDLC for a URL Shortener

Feature `001-agentic-sdlc-url-shortener` · lean slice HD-CUT-002 · evidence recorded 2026-10-16 ·
human owner: Mani Kumar Vadugu

## Goals

1. Build a working URL shortener API (create, redirect, expiry, stats, health, validation, keys,
   rate limit) with a generated OpenAPI contract.
2. Build an orchestrator that delivers requirements to that codebase through a dependency graph of
   agent stages and human gates. It must work test-first, under versioned policies, with rollback
   and compensation, and with tamper-evident audit and per-run evidence.
3. Show it on three requirement types: greenfield (SCN-A), brownfield (SCN-B) and ambiguous
   (SCN-C), plus fault-injection runs for rollback, compensation and a policy exception.

## Key design decisions

| Decision | ADR |
|----------|-----|
| Python 3.12, FastAPI, Pydantic v2 | ADR-001 |
| SQLite (WAL), one database per service | ADR-002 (implemented with stdlib `sqlite3`, not SQLAlchemy/Alembic) |
| In-repository engine with a deterministic superstep scheduler (parallel fork, ordered commit, join) | ADR-003 |
| Versioned YAML workflow graph with conditional nodes | ADR-005 |
| Pre-authored change sets (manifest + `tests.patch` + `impl.patch`), human-locked, applied in an isolated workspace | ADR-006 |
| Contract-first OpenAPI with drift tests | ADR-007 |
| Append-only audit with triggers and a per-run hash chain | ADR-008 |
| Versioned YAML policies; FAIL blocks release; exceptions need human approval | ADR-009 |
| Role-mapped API keys stored as SHA-256 hashes; agent keys refused at gates | ADR-010 |
| Metrics and MTTR computed from audit events | ADR-011 |
| Rollback = discard workspace (pre-promotion); compensation = restore previous release + human-approved corrective action (post-promotion) | ADR-012 |
| Failure classification, bounded retry, timeout, fallback, safe-stop, human resume | ADR-013 |
| Version-bound typed gates, timeouts, bounded rework | ADR-016 |
| Replanning re-runs only stale nodes and revokes approvals | ADR-017 |
| Test-first strategy with fault injection | ADR-018 |

## Scenario outcomes (from `evidence/`)

| Scenario | Run | State (reason) | Red → green (tests/failures) | Result |
|----------|-----|----------------|------------------------------|--------|
| SCN-A | run_1491b1c537664814 | COMPLETED | 4/3 → 64/0 | All 5 policies PASS; clarify skipped with reason |
| SCN-B | run_bc533834c7dc4e5e | COMPLETED | 14/13 → 74/0 | Impact analysis reviewed before change; all PASS |
| SCN-B defective | run_77723ef73ccf4ea7 | FAILED (`rolled_back:tests_failed`) | 14/13 → 74/1 | Regression `test_code_collisions_retry_then_give_up_after_five` failed; workspace discarded, nothing promoted |
| SCN-B compensate | run_03a5a6d9a2154bea | FAILED (`compensated:smoke_failed`) | 14/13 → 74/0 | Post-promotion smoke failed; previous release restored and verified; corrective action approved |
| SCN-C option A | run_fe1eef2844a541f2 | COMPLETED | 3/3 → 63/0 | Clarified to daily aggregate counts; PRIV-001 PASS |
| SCN-C scanner down | run_5defbd091d494e4c | COMPLETED | 3/3 → 63/0 | SEC-003 FAIL → exception `exc_925ccbd0c2414f6b` APPROVED → resume → release |
| SCN-C option C | run_4fae12b6c3f14ca6 | ABORTED (`clarification option C: Withdraw the request`) | — | Terminated by a human at clarify |

The audit hash chain verifies as `valid: true` for all 7 runs. Every gate decision was made with a
human role key (engineer `95b4677fbabf`, approver `63320c4d1c94`, release-owner `2788b911e283`).
Repository suite at commit `8efdbf8`: 129 tests. On Windows, 128 passed and 1 skipped (POSIX kill
path).

## Risks

- **Demonstration metrics only.** Single runs on one workstation, with human decision time in MTTR.
  There are no load or latency measurements (PVT-001/002).
- **No run-time code generation.** Deterministic agents apply locked change sets. An AI-backed
  agent is planned, not built.
- **Baseline coupling.** Change sets apply independently to one baseline, so any baseline edit
  invalidates them. There is no baseline tag yet (lean-slice §1.5).
- **Governance gaps.** No separation of duties between key identities, no exception expiry, and
  only five of the planned policy domains (lean-slice §2.2).
- **Coverage gaps.** Interruption is tested at one stage boundary, not all. There is no
  determinism test and no coverage gate. The undeclared-scope check exists but no test exercises it.
- **Snapshot-based SEC-003** in scenario runs. This is mitigated by the live `pip-audit` in CI and
  in `orch release check`.

## Next steps

1. Tag the baseline and locked change sets (e.g. `shortener-baseline-v1`) and the submission commit.
2. Add the determinism test, interruption tests at every stage boundary, and a coverage gate.
3. Add separation of duties between keys, exception expiry, and the remaining policy domains
   (ARCH, AUD, DEP, LIC).
4. Add a test for the undeclared-scope check (CHG-002) and bidirectional requirement ↔ test traceability.
5. Build the orchestrator HTTP API and an AI-backed agent behind the existing gates and locks.
6. Bring ADR-001/ADR-002 in line with the implementation (pip + `requirements.lock`, stdlib
   `sqlite3`), or migrate the implementation to match them.
