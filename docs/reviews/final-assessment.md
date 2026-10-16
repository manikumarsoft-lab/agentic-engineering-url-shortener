# Final Assessment: Agentic Software Engineering System: URL Shortener

**Date**: 2026-10-16 · **Repository state assessed**: commit `f92f672` (plus the Phase 13
Convergence tasks appended to `tasks.md`) · **Scope**: every criterion in
`specs/001-agentic-sdlc-url-shortener/spec.md` and the assignment criteria it cites.

> Independent assessment produced with AI assistance (Claude Code); reviewed by the human owner
> Mani Kumar Vadugu, 2026-10-16.

## 0. Method

- **Assignment**: the assignment text is confidential and not in the repository (CST-004). Its
  criteria are assessed through the spec's `ASMT §n` references (§1 below).
- **Code**: `src/`, `scenarios/`, `policy/`, `tools/`, `.github/workflows/ci.yml` read in full or
  in the relevant parts.
- **Executed checks** (in `.venv`, 2026-10-16):
  - `python -m pytest`: **128 passed, 1 skipped** (`tests/orchestrator/test_process_interruption.py:91`,
    POSIX kill path, runs only in CI).
  - `python tools/trace_check.py`: **PASS, 0 gaps**. It only checks requirement IDs listed in
    `docs/scope/lean-slice.md` §1, so it does not detect the gaps below.
- **Evidence**: all seven runs in `evidence/` were opened. Every audit hash chain is valid; every
  gate decision was made with a human key; the SCN-C exception was requested by the engineer key
  `95b4677fbabf` and approved by the different approver key `63320c4d1c94`.
- **Statuses**: MET (built and evidenced), PARTIAL (built in part, or built but not evidenced),
  MISSING (not built). Statuses describe the repository **before** the documentation changes
  made on 2026-10-16; §6 lists how those changes affect them.
- Constitution findings are reported separately in the converge findings (F1–F6, tasks
  T252–T257) and are not repeated here.

## 1. Assignment criteria (via spec ASMT references)

| ASMT | Criterion | Evidence | Status |
|------|-----------|----------|--------|
| §2 | Working URL shortener: create, redirect, analytics, expiry, validation, health | `src/shortener/`; `tests/shortener/` | MET |
| §3 | Three scenarios (greenfield, brownfield, ambiguous) executed end to end | `evidence/index.md` (7 runs) | PARTIAL: SCN-A-AC4 and SCN-A-AC6 not built |
| §4.1 | Requirement normalization, quality checks, ambiguity handling | `agents/scenario.py` `normalize`, `quality_check`; SCN-C runs | MET |
| §4.2 | Task decomposition with dependencies and acceptance criteria | `decompose`; `task-plan` artifacts | MET |
| §4.3 | Brownfield impact analysis before change | `impact_analysis`; `run_bc533834c7dc4e5e` | MET |
| §4.4 | Explicit graph, parallelism, sync, state, retry, fallback, rollback, compensation, replanning, metrics | `engine.py`, `graph.py`, `metrics.py` | PARTIAL: one fork instead of two; no entry/exit criteria; no aggregate metrics; no late-ambiguity suspension |
| §4.7 | Controlled autonomy, human approval of high-impact actions | `engine._principal`; gate tests | PARTIAL: human-reserved actions enforced; no per-agent permission guard |
| §4.8 | Final engineering summary | `summary.py`; `evidence/*/engineering-summary.json` | MET |
| §5 | Runnable deliverable with setup, architecture, testing, limitations, trade-offs | `README.md` §2–§8 | PARTIAL: `quickstart.md` described commands that do not exist |
| §6 | Reviewer can verify orchestration, auditability, traceability | evidence export, `orch audit verify` | PARTIAL: no bidirectional traceability (FR-OBS-008) |
| §7 | Human ownership and governance of AI work | README §8; human-locked change sets; human gate decisions | MET |

## 2. Spec criteria

### 2.1 Shortener (US-1, FR-SHR)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| FR-SHR-001, FR-SHR-007, US1/AC1 | `src/shortener/app.py`; `tests/shortener/test_api.py::test_create_and_redirect` | MET |
| FR-SHR-002, FR-SHR-003, FR-SHR-004, US1/AC4, NFR-SEC-001 | `src/shortener/validation.py`; `tests/shortener/test_validation.py`; `test_invalid_url_is_rejected_without_storing` | MET |
| FR-SHR-005, FR-SHR-006 | `codes.py`, `store.py` (primary key, ≤ 5 retries); `test_codes_are_random_base62_of_length_7`, `test_code_collisions_retry_then_give_up_after_five` | MET |
| FR-SHR-008, FR-SHR-009, US1/AC2 | `app.py`; `test_expired_link_returns_410_not_404`, `test_past_naive_or_malformed_expiry_is_rejected` | MET |
| FR-SHR-010, FR-SHR-011, FR-SHR-012, US1/AC3 | `store.record_click`; `test_stats_count_clicks_without_personal_data`, `test_analytics_failure_never_blocks_redirect` | MET |
| FR-SHR-013 | `store.create`; `test_idempotency_key_replays_or_conflicts` | PARTIAL: idempotency records never expire (Key Entities "expiry"; T208) |
| FR-SHR-014, A-013 | `test_orch_serve_handles_200_parallel_creates_with_unique_codes` | PARTIAL: concurrent creations only; exact counts under concurrent redirects untested |
| FR-SHR-015 | `app.py` (`sqlite3.Error` → 503); `test_storage_outage_never_redirects_and_ready_reports_it` | PARTIAL: redirect path tested; creation during an outage is implemented but untested |
| FR-SHR-016 | `test_health_live_and_ready` | MET |
| FR-SHR-017, FR-SHR-018, FR-SHR-019, NFR-SEC-004 | `test_rate_limit_is_60_creates_per_minute_per_key`, `test_unexpected_errors_do_not_leak_internals`, `test_create_requires_a_valid_key`, `test_agent_key_cannot_create_links` | MET |
| FR-SHR-020, FR-SHR-021, FR-SHR-022 | `scenarios/scn-b/changeset/`; run `run_bc533834c7dc4e5e` | MET (in the run workspace only, as CST-007 requires) |
| FR-SHR-023 | run `run_fe1eef2844a541f2` (PRIV-001 PASS) | MET |
| US1/AC5 | `test_unknown_or_malformed_codes_are_404` | MET |
| FR-OBS-009 | `tests/shortener/test_logging.py` | MET |

### 2.2 Orchestration (US-2, FR-ORC)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| FR-ORC-001, FR-ORC-002, FR-ORC-003, FR-ORC-004, US2/AC1 | `engine.submit`; `agents/scenario.py` `normalize`, `quality_check` | MET |
| FR-ORC-005 | `graph.py` `Node` | PARTIAL: no entry criteria, exit criteria or owner per node |
| FR-ORC-006, FR-ORC-007, US2/AC2 | `test_fork_runs_branches_together_and_join_waits`; conditional `clarify` node | MET |
| US2/AC3 | `test_gate_blocks_downstream_until_approved` | MET |
| FR-ORC-008, US2/AC4 | — | MISSING |
| FR-ORC-009, FR-ORC-010 | `decompose`, `impact_analysis`; `test_scn_b_impact_analysis_precedes_change_and_ignores_the_patch` | MET |
| FR-ORC-011 | `store.py`; `test_killed_engine_process_is_safe_stopped_and_resumes` | MET |
| FR-ORC-012 | `store.add_artifact` | PARTIAL: no input artifact versions or attempt recorded |
| FR-ORC-013 | `decisions` table (bound versions) | MET |
| FR-ORC-014, FR-ORC-015, FR-ORC-018, FR-ORC-023 | `tests/orchestrator/test_reliability.py` | MET |
| FR-ORC-016 | `test_fallback_marks_node_degraded` | PARTIAL: no readiness assessment that shows fallback use |
| FR-ORC-017, FR-ORC-035, FR-ORC-042 | runs `run_77723ef73ccf4ea7` (rollback), `run_03a5a6d9a2154bea` (compensation) | MET |
| FR-ORC-019 | `engine.resume` | PARTIAL: resume silently resets the retry budget; resolution evidence checked only for `policy_fail` |
| FR-ORC-020, FR-ORC-021 | `test_new_artifact_version_reruns_only_stale_nodes_and_revokes_approval` | MET |
| FR-ORC-022 | — | MISSING |
| FR-ORC-024 | `orch run status`, `gate show`, `audit show`, `metrics`, evidence export | MET (CLI allowed by A-011) |
| FR-ORC-025 | `engine._succeed` (`PERMISSION_REFUSED` for undeclared artifacts) | PARTIAL: no declared per-agent permissions |
| FR-ORC-026 | `summary.py`; `test_completed_and_aborted_summaries_say_why`, `test_safe_stopped_and_failed_summaries_say_why` | MET |
| FR-ORC-027, FR-ORC-030 | `agents/base.py` (deterministic only) | MISSING |
| FR-ORC-028 | gate refuses a second decision | MET |
| FR-ORC-029 | `runs` table | PARTIAL: deterministic mode only, but no `agent_mode` recorded per run |
| FR-ORC-031 | `evidence/index.md` | MET |
| FR-ORC-032, FR-ORC-043 | `workspace.py` | MET |
| FR-ORC-033 | `_verify_lock`; `test_tampered_patch_after_lock_is_refused`, `test_unlocked_change_set_is_never_applied` | PARTIAL: mismatch safe-stops but is not recorded as a policy FAIL; lock not tied to a git tag |
| FR-ORC-034 | `agents/scenario.py:35` `PROVENANCE`; all manifests | PARTIAL: label lacks "; applied by the deterministic agent, not generated at run time." (G1) |
| FR-ORC-036 | `scenarios/registry.yaml` | PARTIAL: `--fact` can inject faults without the label (G2) |
| FR-ORC-037 | `scenarios/*/workflow.yaml` | PARTIAL: docs and threat review start only after `test` |
| FR-ORC-038 | — | MISSING |
| FR-ORC-039 | `engine._resolve` join rule | PARTIAL: holds for the single fork; suspension does not exist |
| FR-ORC-040, FR-ORC-041 | `scenarios/scn-b-compensate/workflow.yaml` | PARTIAL: SCN-A, SCN-B, SCN-C complete without staging promotion or smoke check |

### 2.3 Governance (US-3, US-4, FR-GOV)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| FR-GOV-001, FR-GOV-002, FR-GOV-003, FR-GOV-013, FR-GOV-014, FR-GOV-015, FR-GOV-016, US3/AC1, US3/AC2, US3/AC3, US3/AC4, US3/AC5 | `tests/orchestrator/test_flow_and_gates.py`; `test_non_approver_decisions_are_refused_and_audited`; `test_gate_timeout_safe_stops_and_resume_reopens_same_version`; `test_reject_rework_reruns_producer_and_is_bounded` | MET |
| FR-GOV-004 | `engine.decide` (`DECISION_REFUSED`) | MET |
| FR-GOV-005 | `policy/policy-set.yaml` | PARTIAL: PRIV, SEC, REL only; no audit retention, approved dependencies, licensing or change-control checks |
| FR-GOV-006, FR-GOV-007 | `test_policy_outcomes_and_version`, `test_policy_fail_blocks_release_until_exception_is_approved` | MET |
| FR-GOV-008 | `exceptions` table | PARTIAL: no scope, expiry or review condition; no rejection |
| FR-GOV-009 | plan.md / spec.md change logs | PARTIAL: persistence and toolchain deviations had no CR before CR-009 |
| FR-GOV-010, US4/AC1, US4/AC2 | `validate` node and policy facts | PARTIAL: no assessment artifact listing blocking reasons; expiry not modelled |
| FR-GOV-011 | `approve-release` gate (release-owner) | MET |
| FR-GOV-012 | `security_scan.py`; `orch release check`; CI pip-audit | MET |
| FR-GOV-017 | `engine.approve_exception` | MISSING |

### 2.4 Observability (US-5, FR-OBS)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| FR-OBS-001, FR-OBS-002, FR-OBS-003, NFR-AUD-001 | `audit.py`; `engine._audit` | MET |
| FR-OBS-004 | triggers in `store.py`; `test_update_and_delete_are_refused` | PARTIAL: refused writes leave no audit event |
| FR-OBS-005 | `orch audit show <run>` | PARTIAL: run filter only |
| FR-OBS-006 | `metrics.py` | PARTIAL: per run only, no aggregate |
| FR-OBS-007, US5/AC3 | `metrics.LABEL` | MET |
| FR-OBS-008, US5/AC2 | — | MISSING |
| FR-OBS-010 | `tools/trace_check.py` | PARTIAL: does not flag untagged tests or modules no task references |
| US5/AC1, NFR-OBS-001, SC-003 | `evidence/<run>/audit.json`, `chain.json` | MET |

### 2.5 Scenarios

| Criterion | Evidence | Status |
|-----------|----------|--------|
| SCN-A-AC1, SCN-A-AC5 | `run_1491b1c537664814` (`clarify` SKIPPED with reason) | MET |
| SCN-A-AC2 | `task-plan`, `design` artifacts | PARTIAL: no data/schema impact field |
| SCN-A-AC3 | artifacts keyed by run; RQ IDs only in the task plan | PARTIAL |
| SCN-A-AC4 | — | MISSING |
| SCN-A-AC6 | — | MISSING |
| SCN-B-AC1, SCN-B-AC2, SCN-B-AC3, SCN-B-AC4 | `run_bc533834c7dc4e5e`, `run_77723ef73ccf4ea7` | MET |
| SCN-B-AC5 | `apply_impl` scope check | PARTIAL: no test, no `undeclared-scope` variant |
| SCN-C-AC1, SCN-C-AC2, SCN-C-AC3, SCN-C-AC4, SCN-C-AC5 | `run_fe1eef2844a541f2`, `run_4fae12b6c3f14ca6`, `run_5defbd091d494e4c`; `test_scn_c_free_text_reopens_then_safe_stops_after_two_rounds` | MET |

### 2.6 Non-functional requirements and validation targets

| Criterion | Evidence | Status |
|-----------|----------|--------|
| NFR-SEC-002, PVT-012 | secret scan, pip-audit snapshot, CI | MET |
| NFR-SEC-003 | per-run `threat-review` artifacts | PARTIAL: no threat-model document |
| NFR-REL-001, NFR-REL-002, NFR-CHG-001, NFR-AUT-001, NFR-RCV-002 | reliability, gate and e2e tests | MET |
| NFR-SCL-001, PVT-003 | 200 parallel creations | PARTIAL: PVT-003 requires 1,000 |
| NFR-SCL-002 | — | MISSING: horizontal scaling not documented |
| NFR-MNT-001 | `docs/adr/` | PARTIAL: ADRs disagree with the code (§4) |
| NFR-PRF-001, NFR-PRF-002, PVT-001, PVT-002 | — | MISSING (non-gating, but SC-009 requires measurement) |
| NFR-RCV-001, PVT-006 | one real interruption test | PARTIAL |
| NFR-TST-001, PVT-007 | all test categories exist | PARTIAL: no coverage measurement |
| NFR-RUN-001 | README §2 | MET |
| PVT-009 | — | MISSING: no timed fresh setup |
| NFR-DOC-001 | `specs/.../quickstart.md` | MISSING: quickstart used `uv sync`, `orch keys init`, `tools/check.py`, `shortener serve`; no quickstart test |
| NFR-DET-001 | ordered commits in the scheduler | PARTIAL: no repeat-run test |
| PVT-004, PVT-005, PVT-008, PVT-010, PVT-011, PVT-013 | graph defaults, config, tests | MET (PVT-008 by construction: state and audit commit in one transaction; no completeness test) |

### 2.7 Success criteria, constraints, evidence

| Criterion | Evidence | Status |
|-----------|----------|--------|
| SC-001, SC-004, SC-005, SC-006, SC-011 | test suite | MET |
| SC-002 | `evidence/` | PARTIAL: SCN-A-AC4 and SCN-A-AC6 not met |
| SC-007 | `tools/trace_check.py` | PARTIAL |
| SC-008 | `test_policy_fail_blocks_release_until_exception_is_approved` | PARTIAL: no expired-exception case |
| SC-009 | — | PARTIAL: PVT-001/002 not measured, PVT-003 partial, PVT-009 not recorded |
| SC-010 | README §2; deterministic agents | PARTIAL: no repeat-run determinism test |
| CST-003 | README §2–§8 | PARTIAL: quickstart stale |
| CST-004 | no assessment source committed | MET |
| CST-006, CST-007 | no AI dependency; aliases absent from main `src/` | MET |
| CST-009 | CI, README §8 | PARTIAL: tag `assessment-submission-v1.0` missing |
| EV-001, EV-002, EV-003, EV-004, EV-005, EV-006, EV-007 | `evidence/run_*` | MET |
| EV-008 | — | MISSING |

### 2.8 Edge cases (spec §Edge Cases, in order)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| EC-01 concurrent creations of the same URL, EC-02 code collision | `test_same_url_without_key_creates_distinct_links`, `test_code_collisions_retry_then_give_up_after_five` | MET |
| EC-03 persistence unavailable during creation | `app.py` create → 503 | PARTIAL: untested |
| EC-04 persistence unavailable during redirect, EC-05 analytics failure, EC-06 redirect loop, EC-07 malformed/long/credential/non-printable URLs, EC-08 past or malformed expiry | shortener tests | MET |
| EC-09 interrupted mid-stage, EC-10 stale approval, EC-11 upstream change mid-branch, EC-12 retry budget exhausted, EC-13 permanent failure never retried | orchestrator tests | MET |
| EC-14 integrity mismatch → policy FAIL and safe-stop | `test_tampered_patch_after_lock_is_refused` | PARTIAL: safe-stop, not a policy FAIL |
| EC-15 isolated copy cannot be created → stage fails | `engine.submit` | PARTIAL: workspace is created at submit, not in a stage |
| EC-16 smoke check fails → compensation | `run_03a5a6d9a2154bea` | MET |
| EC-17 compensation fails → SAFE_STOPPED, staging degraded | `test_failed_compensation_safe_stops` | PARTIAL: staging never marked degraded |
| EC-18 duplicate approval or completion applied once | `engine.decide` | MET |
| EC-19 exception expires before release → FAIL | — | MISSING |

### 2.9 Totals

Counted per criterion ID in §2 (each ID in a grouped row carries that row's status; the §1
assignment rows are not counted): **206 criteria: 136 MET, 50 PARTIAL, 20 MISSING.** Of the 11
assignment rows in §1: 6 MET, 5 PARTIAL. (The figures "92 / 52 / 17" in an earlier chat summary
were not computed from this table and are superseded.)

## 3. Gaps and exact fixes

G1–G8 and G10–G11 were found in this assessment; G9 groups the converge tasks.

| # | Gap | Exact fix |
|---|-----|-----------|
| G1 | FR-ORC-034 label shortened | `src/orchestrator/agents/scenario.py:35`: append `"; applied by the deterministic agent, not generated at run time."` to `PROVENANCE`; re-run `tools/author_changesets.py`; the human owner re-locks each change set (`orch changeset lock <path> --key <approver>`). **CR-010 (approved 2026-10-16, accepted deviation)**: the recorded label is kept for this submission; FR-ORC-034 stays PARTIAL; future work T258. |
| G2 | `--fact` injects faults without the label | `src/cli/main.py` `run_submit`: refuse `--fact` keys `fault_injection` and `variant` unless the registry entry sets them; or in `Engine.submit` add `fault-injection` to `labels` when `facts` has `fault_injection` or `variant != "normal"`. Add a CLI test. **Done 2026-10-16 (§8).** |
| G3 | Quickstart described non-existent commands | Rewrite `quickstart.md` from README §2/§5 (done 2026-10-16, §6); add `tests/e2e/test_quickstart.py` running every command against a temporary `ORCH_HOME` (T282). |
| G4 | Release gate vocabulary differs from Human Gate 4 ruling 4 | `engine.py`: gate kind `release` with `ready`, `not_ready`, `escalate`; `not_ready` → FAILED with reasons; `kind: release` on `approve-release` in all four workflows. **CR-009 (approved 2026-10-16)**: accepted deviation for this submission, because changing it now would make the recorded evidence inconsistent with the code; future work. |
| G5 | Submission tag missing (CST-009) | Human owner: `git tag -a assessment-submission-v1.0 -m "…"` and `git push origin assessment-submission-v1.0` after CI is green (T251). |
| G6 | Exact counts under concurrent redirects untested (A-013) | Add a test to `tests/shortener/test_concurrency_serve.py`: 200 parallel GETs to one code, assert `clicks == 200`. **Done 2026-10-16 (§8): the test passed without a code change.** |
| G7 | Idempotency records never expire | `store.create`: ignore and replace rows with `created_at` older than 24 h; test with a fake clock. |
| G8 | Horizontal scaling undocumented (NFR-SCL-002) | README §7 "Horizontal scaling" paragraph (done 2026-10-16, §6). |
| G9 | Constitution, readiness, topology, separation of duties, traceability, metrics, AI mode, PVT and documentation gaps | Phase 13 tasks T252–T289 in `tasks.md`. |
| G10 | Stats readable by any key holder (threat-model TB-5) | **Accepted risk (human owner, 2026-10-16)**: stats contain only aggregate counts and no personal data, and restricting reads to the creating key would change the baseline the locked change sets apply to. Future work T290: owner-scope `GET /api/v1/links/{code}/stats` like SCN-A's TH-1 control. |
| G11 | Creation during a persistence outage untested (FR-SHR-015, EC-03) | Add a test that patches `store.create` to raise `sqlite3.OperationalError` and asserts 503 `persistence_unavailable` and no stored link. |

## 4. ADR disagreements with the implementation

**(amend)**: the code is a legitimate lean-slice choice; the ADR should follow it.
**(fix code)**: the ADR restates a spec requirement or a Human Gate 4 ruling; rewording it would
move the conflict into `spec.md`, so the code should change. The amendments are in ADR-020,
ADR-021 and ADR-022 (all Accepted 2026-10-16, CR-009).

### ADR-001 (amend → ADR-020)

| ADR-001 says | Code does |
|---|---|
| uv with a committed `uv.lock` | pip into `.venv` from `requirements.lock`; no `uv.lock` |
| pytest + Hypothesis + schemathesis | pytest only |
| mypy strict and ruff via `tools/check.py` | none; CI runs pytest, `trace_check.py`, pip-audit |
| `policy/approved-dependencies.yaml`, DEP-001, LIC-001 | absent |
| Prerequisites: Python and uv | Python 3.12 only |

### ADR-002 (amend → ADR-021)

| ADR-002 says | Code does |
|---|---|
| SQLAlchemy Core + Alembic + repository protocols | stdlib `sqlite3`, `CREATE TABLE IF NOT EXISTS`, no repositories or migrations |
| `var/dev`, `var/staging`, `var/work/<run>/<attempt>`, `var/orchestrator` | `var/orchestrator.db`, `var/shortener.db`, `var/staging/{shortener,keys}.db`, `var/work/<run_id>/` (no DB) |
| `synchronous=NORMAL` | not set |
| `orch demo reset` | absent |
| migration tests; PVT-003 with 1,000 creations | none; 200 creations |

### ADR-003 to ADR-019

| ADR | Disagreement | Proposed change |
|---|---|---|
| 003 | Agents are `fn(ctx) -> dict` run by `agents/runner.py`; IDs from `uuid4().hex`; `Clock`/`FakeClock` in `engine.py`; no AI stub; no determinism test | (amend) agent shape, IDs, clock. (fix code) AI stub (T266), determinism test (T271) |
| 004 | Flat modules plus `src/cli/`; no orchestrator server on 8200; staging is a subprocess smoke check, not a server on 8100 | (amend) layout, processes, paths. (fix code) `orch demo reset` (T287); HTTP API (T284) or a CR removing it |
| 005 | No `sync`/`system` nodes, `optional_inputs` or dynamic gate patterns; conditions `{fact, equals \| not_equals}`; adds `failure_edge`, `compensate` | (amend). (fix code) entry/exit criteria and owner (T252) |
| 006 | Manifest fields differ; lock in `scenarios/changesets.lock.yaml` by approver key, not a tag; R0 from the working tree; one workspace per run; dependency change fails SEC-003 not `manifest_invalid`; label shortened; no `undeclared-scope` variant | (amend) manifest, lock mechanism, R0 source, workspace granularity. (fix code) label (T258; kept by CR-010, accepted deviation), variant (T276), tag anchoring (T279), `git archive` (T288) |
| 007 | Contract generated from the app (CR-007); no Alembic | (amend) code-first contract with drift test. (fix code) CHG-003 as a policy check (T253) |
| 008 | No schema validation of events, no 405 / `AUDIT_TAMPER_REFUSED`, no `orch audit export`; evidence export writes `chain.json` with `head_hash` | (amend) export mechanism. (fix code) audit refused tamper attempts (T277) |
| 009 | Regex secret scan (SEC-004), not detect-secrets as "SEC-002"; SEC-002 is "no open high threat"; no pip-licenses, expiry, non-waivable list or G-EXCEPTION gate | (amend) scanners, check IDs, CLI exception flow. (fix code) expiry and non-waivable checks (T254), licensing (T253), separation of duties (T262) |
| 010 | No `x-required-roles` API; roles from `gate.roles`; engineer or approver may request exceptions; agents limited only by `produces` | (amend) role sources. (fix code) agent capability guard (T275) |
| 011 | `label: "demonstration data"` not `measurement_class`; no per-mechanism MTTR, `includes_human_wait` or `fault_injected` | (amend). (fix code) aggregate metrics (T270) |
| 012 | Failed compensation does not mark staging degraded; promotion not idempotent by `release_id` | (fix code) only |
| 013 | Resume resets the retry budget; no REL-005 | (amend) remove REL-005. (fix code) approver-granted extension (T274) |
| 014 | Matches the code | none (1,000-creation test: T273) |
| 015 | IDs not ULIDs (`run_`, `dec_`, `exc_`, `ep_`); artifact content inline in DB; no rebuild-from-audit test | (amend) ID format and storage. (fix code) consistency test (T241 scope) |
| 016 | Release gate offers approve / reject_rework / reject_terminate / escalate (reject_terminate → ABORTED) instead of ruling 4's ready / not_ready / escalate (not_ready → FAILED); no `decision_source` | (amend) drop `decision_source`. Ruling 4 not amended: G4 accepted as a deviation in CR-009 (2026-10-16), future work |
| 017 | `NODE_STALE` not `ARTIFACT_STALE`; no `GRAPH_VERSION_CREATED` or memoization; no late ambiguity | (amend) event names. (fix code) late ambiguity (T264) |
| 018 | No `tools/check.py`, coverage, `req` markers, TDD log or `FAULT_INJECTED`; fault injection via facts plus registry labels | (amend) test-first recorded per scenario run. (fix code) G2, T281; Constitution IV decision T256 (human) |
| 019 | Analytics and `analytics_write_failures` are baseline (HD-SCN-001), reported by `/health/ready` | (amend). (fix code) concurrency exactness test (G6) |

Consequential edits of CR-009: `plan.md` (Technical Context, §2.1, §12 R-01/R-02,
§14.2 slice 1) and `research.md` (R-01, R-02) carry "As built (CR-009, approved)" notes; CR-009
was approved by the human owner on 2026-10-16.

## 5. Recommended order

1. Fix code where the ADR is right and no deviation is proposed: G2, G6, G7, G11. G2 and G6 done 2026-10-16 (§8).
2. Human owner decides CR-009 (ADR-020/021/022, G4 deviation) and CR-010 (G1 deviation), and G10. Done 2026-10-16 (§7).
3. Work through Phase 13 (T252–T289), constitution items first.
4. Human owner records PVT-009 timing and creates the submission tag (G5, T251).

## 6. Documentation changes made after this assessment (2026-10-16)

These docs-only changes were made after the statuses above were assessed. They do not change
code, change sets or evidence.

| Item | Change | Effect on status |
|------|--------|------------------|
| NFR-SEC-003 | `docs/security/threat-model.md` created (TH-0..TH-2, AR-1, TB-1..TB-13) | Documentation now exists; stays PARTIAL until the human owner reviews it and decides TB-5 (G10) |
| NFR-DOC-001, CST-003 | `quickstart.md` rewritten with existing commands (shortener commands checked against the code) | NFR-DOC-001 MISSING → PARTIAL (commands now exist, but no automated quickstart test, T282); CST-003 stays PARTIAL (submission tag, T251) |
| NFR-SCL-002 | README §7 "Horizontal scaling" | Documented; MET as "documented, not demonstrated" |
| EV-008 | `docs/traceability-matrix.md` created from existing links | PARTIAL: hand-built, not generated or checked (FR-OBS-008, T268/T269 remain) |
| FR-GOV-009, NFR-MNT-001 | CR-009, CR-010, ADR-020/021/022 (all Proposed) | No change until the human owner approves |
| F7, F8 | `docs/scope/lean-slice.md` corrected | Claims now match the code; FR-ORC-034/037/038 statuses unchanged |

## 7. Human owner decisions (2026-10-16)

Recorded for the human owner Mani Kumar Vadugu, 2026-10-16. Docs only: no code, change set,
policy or evidence changes. The statuses in §1–§2 are not re-assessed by these decisions.

| Item | Decision | Effect |
|------|----------|--------|
| CR-009 | Approved. ADR-020, ADR-021 and ADR-022 are Accepted. The G4 release-gate deviation is accepted for this submission; aligning `approve-release` with Human Gate 4 ruling 4 is future work | ADR-001/002 status notes, ADR index, "As built" notes in plan.md and research.md set to approved; T285 done |
| CR-010 | Approved as an accepted deviation: the recorded provenance label is kept for this submission | FR-ORC-034 stays PARTIAL; full label is future work T258 |
| G10 | Accepted risk for this submission: stats contain only aggregate counts and no personal data; restricting reads to the creating key would change the baseline the locked change sets apply to | Threat model TB-5 "accepted risk (human owner, 2026-10-16)"; owner-scoping is T290 |
| Review | This assessment was reviewed by the human owner | Header updated |

## 8. Code changes made after this assessment (2026-10-16)

Each change was made test-first: the new test was run and failed before the fix, then passed after
it. No change to `scenarios/`, `policy/`, `evidence/` or the change-set lock. Statuses in §1–§2
describe the repository before these changes; this table gives the effect.

| Item | Change | Red → green | Effect on status |
|------|--------|-------------|------------------|
| FR-GOV-017 (T262) | `Engine.approve_exception` refuses approval by the key that requested the exception: `AuthError` ("separation of duties: …"), audited as `AUTH_REFUSED` with `violation: separation_of_duties_violation`; the exception stays `REQUESTED` | `test_requesting_key_cannot_approve_its_own_exception`: failed with "DID NOT RAISE AuthError", then passed | MISSING → MET |
| FR-ORC-036 (G2) | `orch run submit` refuses `--fact fault_injection=…` or `--fact variant=…` unless the value equals the one the scenario's registry entry sets; no run is created | `test_fault_facts_come_only_from_the_registry` (4 cases: scn-a, scn-c, scn-b `variant=defective`, scn-b-defective `variant=normal`): all 4 created a run before the fix, then were refused | Stays PARTIAL: the `undeclared-scope` variant is still missing (T276) |
| FR-SHR-014, A-013 (G6) | Test only: 200 parallel redirects to one code through `orch serve`, then `clicks == 200` | `test_orch_serve_counts_200_parallel_redirects_exactly` passed on its first run; no code change | PARTIAL → MET |

Checks after the changes: `python -m pytest` 134 passed, 1 skipped (the POSIX kill path, CI only);
`python tools/trace_check.py` PASS, 0 gaps.
