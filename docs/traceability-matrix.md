# Traceability Matrix (EV-008)

**Date**: 2026-10-16 · Built by hand with AI assistance (Claude Code) from what exists in the
repository: module `Satisfies:` lines, test functions and the exported evidence runs. Review by
the human owner Mani Kumar Vadugu: pending. It is **not** generated or checked by a tool (the
bidirectional view and its checker are T268/T269), so it can drift from the code.

"—" means no link exists. Nothing is inferred: a test is listed only if it exercises the
behavior; an evidence run only if its artifacts or audit events show it. Status is from
[docs/reviews/final-assessment.md](reviews/final-assessment.md) §2.

**Evidence runs** (`evidence/<run>/`):

| Alias | Run | Scenario | Outcome |
|-------|-----|----------|---------|
| A | `run_1491b1c537664814` | SCN-A | COMPLETED |
| B | `run_bc533834c7dc4e5e` | SCN-B | COMPLETED |
| BD | `run_77723ef73ccf4ea7` | SCN-B defective (fault injection) | FAILED (rolled back) |
| BC | `run_03a5a6d9a2154bea` | SCN-B compensate (fault injection) | FAILED (compensated) |
| C | `run_fe1eef2844a541f2` | SCN-C option A | COMPLETED |
| CX | `run_5defbd091d494e4c` | SCN-C scanner down (fault injection) | COMPLETED after exception |
| CC | `run_4fae12b6c3f14ca6` | SCN-C option C | ABORTED |

Test paths are relative to `tests/`. Abbreviations: `sh/api` = `shortener/test_api.py`,
`orc/flow` = `orchestrator/test_flow_and_gates.py`, `orc/rel` = `orchestrator/test_reliability.py`,
`orc/akp` = `orchestrator/test_audit_keys_policy.py`, `orc/rpm` =
`orchestrator/test_replan_policy_metrics.py`, `orc/sum` = `orchestrator/test_summary_compensation.py`,
`orc/scan` = `orchestrator/test_security_scan.py`, `e2e` = `e2e/test_scenarios.py`.

## Shortener (FR-SHR)

| Requirement | Code | Test | Evidence | Status |
|-------------|------|------|----------|--------|
| FR-SHR-001 | `src/shortener/app.py` `create_link` | `sh/api::test_create_and_redirect` | — (baseline) | MET |
| FR-SHR-002 | `src/shortener/validation.py` | `shortener/test_validation.py::test_valid_urls_are_normalized`, `::test_invalid_urls_are_rejected_with_a_reason` | — | MET |
| FR-SHR-003 | `validation.py` `ALLOWED_SCHEMES` | `test_validation.py::test_invalid_urls_are_rejected_with_a_reason` | — | MET |
| FR-SHR-004 | `validation.py`; `config.py` `self_hosts` | `test_validation.py::test_invalid_urls_are_rejected_with_a_reason`, `::test_length_limit_is_inclusive` | — | MET |
| FR-SHR-005 | `codes.py`; `store.py` `create` | `sh/api::test_code_collisions_retry_then_give_up_after_five`; `shortener/test_concurrency_serve.py` | — | MET |
| FR-SHR-006 | `codes.py` | `test_validation.py::test_codes_are_random_base62_of_length_7` | — | MET |
| FR-SHR-007 | `app.py` `redirect` | `sh/api::test_create_and_redirect` | — | MET |
| FR-SHR-008 | `app.py` (410) | `sh/api::test_expired_link_returns_410_not_404` | — | MET |
| FR-SHR-009 | `app.py` `create_link` | `sh/api::test_past_naive_or_malformed_expiry_is_rejected` | — | MET |
| FR-SHR-010 | `store.py` `record_click`, `stats` | `sh/api::test_stats_count_clicks_without_personal_data` | — | MET |
| FR-SHR-011 | `app.py` `redirect` | `sh/api::test_analytics_failure_never_blocks_redirect` | — | MET |
| FR-SHR-012 | `store.py` schema (no IP/UA) | `sh/api::test_stats_count_clicks_without_personal_data` | C (PRIV-001 PASS) | MET |
| FR-SHR-013 | `store.py` `create` | `sh/api::test_idempotency_key_replays_or_conflicts` | — | PARTIAL |
| FR-SHR-014 | `store.py` | `shortener/test_concurrency_serve.py::test_orch_serve_handles_200_parallel_creates_with_unique_codes` | — | PARTIAL |
| FR-SHR-015 | `app.py` (`unavailable`) | `sh/api::test_storage_outage_never_redirects_and_ready_reports_it` (redirect only) | — | PARTIAL |
| FR-SHR-016 | `app.py` `live`, `ready` | `sh/api::test_health_live_and_ready` | — | MET |
| FR-SHR-017 | `app.py` `RateLimiter` | `sh/api::test_rate_limit_is_60_creates_per_minute_per_key` | — | MET |
| FR-SHR-018 | `app.py` exception handlers | `sh/api::test_unexpected_errors_do_not_leak_internals`, `::test_malformed_body_does_not_echo_input` | — | MET |
| FR-SHR-019 | `app.py` `require_key`; `src/common/apikeys.py` | `sh/api::test_create_requires_a_valid_key`, `::test_agent_key_cannot_create_links` | — | MET |
| FR-SHR-020 | `scenarios/scn-b/changeset/impl.patch` | `tests/shortener/test_aliases.py` (in `tests.patch`, run in the workspace) | B (`test-results`) | MET |
| FR-SHR-021 | same | same | B | MET |
| FR-SHR-022 | same | same + full `tests/shortener` regression | B | MET |
| FR-SHR-023 | `scenarios/scn-c/changeset/`, `catalog.yaml` | `e2e::test_scn_c_option_a_selects_change_set_from_catalog` | C | MET |

## Orchestration (FR-ORC)

| Requirement | Code | Test | Evidence | Status |
|-------------|------|------|----------|--------|
| FR-ORC-001 | `engine.py` `submit`; `src/cli/main.py` | `cli/test_cli.py::test_submit_status_gate_flow_audit_and_metrics` | all runs | MET |
| FR-ORC-002 | `agents/scenario.py` `normalize` | `e2e::test_scn_a_greenfield_runs_test_first_to_completed` | A, B, C | MET |
| FR-ORC-003 | `scenario.py` `quality_check` | `e2e::test_scn_a_greenfield_runs_test_first_to_completed` | A, B, C (`quality-report`) | MET |
| FR-ORC-004 | `quality_check`; `clarify` node condition | `e2e::test_scn_a_greenfield_runs_test_first_to_completed`, `e2e::test_scn_c_option_a_selects_change_set_from_catalog` | A (skipped), C (raised) | MET |
| FR-ORC-005 | `graph.py` | `orchestrator/test_graph.py` | — | PARTIAL |
| FR-ORC-006 | `engine.py` `_execute_step`, `_resolve` | `orc/flow::test_fork_runs_branches_together_and_join_waits` | A, B, C (`docs` ∥ `threat-review`) | MET |
| FR-ORC-007 | `engine._resolve` conditions | `orc/flow::test_fork_runs_branches_together_and_join_waits`; `e2e::test_scn_a_greenfield_runs_test_first_to_completed` | A | MET |
| FR-ORC-008 | — | — | — | MISSING |
| FR-ORC-009 | `scenario.py` `decompose` | `e2e::test_scn_a_greenfield_runs_test_first_to_completed` | A, B, C (`task-plan`) | MET |
| FR-ORC-010 | `scenario.py` `impact_analysis` | `e2e::test_scn_b_impact_analysis_precedes_change_and_ignores_the_patch` | B | MET |
| FR-ORC-011 | `store.py` | `orchestrator/test_process_interruption.py::test_killed_engine_process_is_safe_stopped_and_resumes` | — | MET |
| FR-ORC-012 | `store.add_artifact` | — | all runs (`artifacts.json`) | PARTIAL |
| FR-ORC-013 | `engine.decide` (`decisions`) | `orc/flow::test_gate_timeout_safe_stops_and_resume_reopens_same_version` | all runs (`decisions.json`) | MET |
| FR-ORC-014 | `engine._fail`, `_classify` | `orc/rel::test_transient_failure_is_retried_with_backoff`, `::test_permanent_failure_is_never_retried` | — | MET |
| FR-ORC-015 | `engine._collect`, `kill_tree` | `orc/rel::test_timeout_kills_the_agent_process` | — | MET |
| FR-ORC-016 | `engine._run_fallback` | `orc/rel::test_fallback_marks_node_degraded` | — | PARTIAL |
| FR-ORC-017 | `engine._rollback`, `_compensate` | `orc/rel::test_rollback_discards_the_isolated_workspace`, `::test_compensation_hook_undoes_committed_effect` | BD, BC | MET |
| FR-ORC-018 | `engine._safe_stop` | `orc/rel::test_retry_budget_is_bounded_then_safe_stop`, `::test_unclassified_failure_safe_stops` | CX | MET |
| FR-ORC-019 | `engine.resume`, `recover` | `orc/rel::test_safe_stop_resume_needs_a_human_approver`, `::test_restart_marks_interrupted_run_safe_stopped_and_resume_completes` | CX | PARTIAL |
| FR-ORC-020 | `engine.new_artifact_version` | `orc/rpm::test_new_artifact_version_reruns_only_stale_nodes_and_revokes_approval` | — | MET |
| FR-ORC-021 | `engine._mark_stale` | same | — | MET |
| FR-ORC-022 | — | — | — | MISSING |
| FR-ORC-023 | `engine._finish`, `_safe_stop` | `orc/rel` | all runs | MET |
| FR-ORC-024 | `src/cli/main.py` | `cli/test_cli.py::test_submit_status_gate_flow_audit_and_metrics` | — | MET |
| FR-ORC-025 | `engine._succeed` | — | — | PARTIAL |
| FR-ORC-026 | `summary.py` | `orc/sum::test_completed_and_aborted_summaries_say_why`, `::test_safe_stopped_and_failed_summaries_say_why` | all runs (`engineering-summary.json`) | MET |
| FR-ORC-027 | `agents/base.py` | — | — | MISSING |
| FR-ORC-028 | `engine.decide` state check (a decided gate refuses further decisions) | — (no dedicated test) | — | MET |
| FR-ORC-029 | `agents/deterministic.py` | — | — | PARTIAL |
| FR-ORC-030 | — | — | — | MISSING |
| FR-ORC-031 | `scenarios/`; `evidence.py` | `e2e` (all scenario tests) | A, B, BD, BC, C, CX, CC | MET |
| FR-ORC-032 | `workspace.py` | `orc/rel::test_rollback_discards_the_isolated_workspace` | all runs (`WORKSPACE_CREATED`) | MET |
| FR-ORC-033 | `scenario.py` `_verify_lock`; `changesets.py` | `e2e::test_unlocked_change_set_is_never_applied`, `::test_tampered_patch_after_lock_is_refused` | — | PARTIAL |
| FR-ORC-034 | `scenario.py` `PROVENANCE` | — | A, B, C (`change-application.provenance`, shortened) | PARTIAL |
| FR-ORC-035 | `engine._rollback` | `e2e::test_scn_b_defective_variant_fails_regression_and_rolls_back` | BD | MET |
| FR-ORC-036 | `scenarios/registry.yaml` | `e2e::test_scn_b_defective_variant_fails_regression_and_rolls_back` | BD | PARTIAL |
| FR-ORC-037 | `scenarios/*/workflow.yaml` | `orc/flow::test_fork_runs_branches_together_and_join_waits` (one fork) | — | PARTIAL |
| FR-ORC-038 | — | — | — | MISSING |
| FR-ORC-039 | `engine._resolve` | `orc/flow::test_fork_runs_branches_together_and_join_waits` | — | PARTIAL |
| FR-ORC-040 | `scenario.py` `promote` | `e2e::test_scn_b_compensate_restores_previous_release_and_corrects_after_approval` | BC | PARTIAL |
| FR-ORC-041 | `scenario.py` `smoke_check` | `orc/sum::test_successful_smoke_takes_the_normal_path` | BC | PARTIAL |
| FR-ORC-042 | `restore_previous_release`, `disable_effects` | `e2e::test_scn_b_compensate_restores_previous_release_and_corrects_after_approval`; `orc/sum::test_compensation_continues_only_along_the_failure_edge` | BC | MET |
| FR-ORC-043 | `workspace.py`; `scenario.py` `_apply_patch` (`GIT_CEILING_DIRECTORIES`) | — | all runs | MET |

## Governance (FR-GOV)

| Requirement | Code | Test | Evidence | Status |
|-------------|------|------|----------|--------|
| FR-GOV-001 | gates in `scenarios/*/workflow.yaml`; `engine.resume` | `orc/flow::test_gate_blocks_downstream_until_approved` | all runs | MET |
| FR-GOV-002 | `engine.decide` | `orc/flow::test_escalate_keeps_gate_blocking_and_requires_release_owner`, `::test_reject_terminate_aborts`, `::test_gate_timeout_safe_stops_and_resume_reopens_same_version` | — | MET |
| FR-GOV-003 | `engine._principal`; `common/apikeys.py` | `orc/flow::test_non_approver_decisions_are_refused_and_audited`; `cli/test_cli.py::test_watch_and_resume_with_agent_refusal` | all runs (human keys) | MET |
| FR-GOV-004 | `engine.decide` (bound versions) | `orc/rpm::test_new_artifact_version_reruns_only_stale_nodes_and_revokes_approval` | — | MET |
| FR-GOV-005 | `policy.py`; `policy/policy-set.yaml` | `orc/akp::test_policy_outcomes_and_version` | all runs | PARTIAL |
| FR-GOV-006 | `engine._evaluate_policy` | `orc/akp::test_policy_outcomes_and_version` | A, B, C, CX (`policy_evaluations`) | MET |
| FR-GOV-007 | `engine._evaluate_policy`, `_fail` | `orc/rpm::test_policy_fail_blocks_release_until_exception_is_approved` | CX | MET |
| FR-GOV-008 | `engine.request_exception`, `approve_exception` | `e2e::test_scanner_down_policy_fail_blocks_release_until_exception_approved` | CX | PARTIAL |
| FR-GOV-009 | change logs (`plan.md`, `spec.md`) | — | — | PARTIAL |
| FR-GOV-010 | `scenario.py` `validate_release` | — | A, B, C | PARTIAL |
| FR-GOV-011 | `approve-release` gate | `e2e::test_scn_a_greenfield_runs_test_first_to_completed` | A, B, C, CX | MET |
| FR-GOV-012 | `security_scan.py`; `orch release check`; CI | `orc/scan` (all five tests) | A, B, C (SEC-003, SEC-004 PASS), CX | MET |
| FR-GOV-013 | `decisions` table (`key_id`, `role`) | `orc/flow::test_non_approver_decisions_are_refused_and_audited` | all runs | MET |
| FR-GOV-014 | `engine.step` (timeout), `resume` | `orc/flow::test_gate_timeout_safe_stops_and_resume_reopens_same_version` | — | MET |
| FR-GOV-015 | `engine.decide` | `orc/flow::test_reject_terminate_aborts`; `cli/test_cli.py::test_reject_terminates_or_reworks` | — | MET |
| FR-GOV-016 | `engine.decide` (`rework_limit_exceeded`) | `orc/flow::test_reject_rework_reruns_producer_and_is_bounded` | — | MET |
| FR-GOV-017 | — | — | CX (different keys, not enforced) | MISSING |

## Observability (FR-OBS)

| Requirement | Code | Test | Evidence | Status |
|-------------|------|------|----------|--------|
| FR-OBS-001 | `audit.py` (`run_id` per event) | `orc/akp::test_hash_chain_verifies` | all runs | MET |
| FR-OBS-002 | `engine._audit` calls | `cli/test_cli.py::test_submit_status_gate_flow_audit_and_metrics` | all runs (`audit.json`) | MET |
| FR-OBS-003 | `audit.append` fields | `orc/akp::test_hash_chain_verifies` | all runs | MET |
| FR-OBS-004 | `store.py` triggers; hash chain | `orc/akp::test_update_and_delete_are_refused`, `::test_out_of_band_tampering_is_detected` | all runs (`chain.json` valid) | PARTIAL |
| FR-OBS-005 | `orch audit show` | `cli/test_cli.py::test_submit_status_gate_flow_audit_and_metrics` | — | PARTIAL |
| FR-OBS-006 | `metrics.py` | `orc/rpm::test_mttr_counts_recovered_episodes_only`, `::test_run_metrics_are_labelled_and_complete` | all runs (`metrics.json`) | PARTIAL |
| FR-OBS-007 | `metrics.LABEL` | `orc/rpm::test_run_metrics_are_labelled_and_complete` | all runs | MET |
| FR-OBS-008 | — (this document is a manual substitute) | — | — | MISSING |
| FR-OBS-009 | `app.py` `JsonFormatter`, `request_log` | `shortener/test_logging.py` | — | MET |
| FR-OBS-010 | `tools/trace_check.py` | `test_traceability.py::test_traceability_check_has_no_gaps` | CI | PARTIAL |

## Scenario acceptance criteria

| Criterion | Code | Test | Evidence | Status |
|-----------|------|------|----------|--------|
| SCN-A-AC1, AC5 | `quality_check`; `clarify` skip reason | `e2e::test_scn_a_greenfield_runs_test_first_to_completed` | A | MET |
| SCN-A-AC2 | `decompose`, `design` | same | A | PARTIAL |
| SCN-A-AC3 | `store.add_artifact` | — | A | PARTIAL |
| SCN-A-AC4 | — | — | — | MISSING |
| SCN-A-AC6 | — | — | — | MISSING |
| SCN-B-AC1, AC2 | `impact_analysis`; `approve-design` | `e2e::test_scn_b_impact_analysis_precedes_change_and_ignores_the_patch` | B | MET |
| SCN-B-AC3 | `run_tests` (full regression) | same | B | MET |
| SCN-B-AC4 | `engine._rollback` | `e2e::test_scn_b_defective_variant_fails_regression_and_rolls_back` | BD | MET |
| SCN-B-AC5 | `apply_impl` scope check | — | — | PARTIAL |
| SCN-C-AC1, AC3 | `quality_check`; `clarify` gate | `e2e::test_scn_c_option_a_selects_change_set_from_catalog` | C | MET |
| SCN-C-AC2 | `clarify` blocks downstream | same | C, CC | MET |
| SCN-C-AC4 | `select_change_set`, `requality` | same | C | MET |
| SCN-C-AC5 | timeout, abort, free text, policy FAIL | `e2e::test_scn_c_option_c_aborts`, `::test_scn_c_free_text_reopens_then_safe_stops_after_two_rounds`, `orc/flow::test_gate_timeout_safe_stops_and_resume_reopens_same_version`, `e2e::test_scanner_down_policy_fail_blocks_release_until_exception_approved` | CC, CX | MET |

## Selected non-functional requirements

| Requirement | Code | Test | Evidence | Status |
|-------------|------|------|----------|--------|
| NFR-SEC-001 | `validation.py` | `shortener/test_validation.py` | — | MET |
| NFR-SEC-002 | `security_scan.py`; logging | `orc/scan::test_secret_scan_finds_keys_without_recording_them`; `shortener/test_logging.py` | all runs (SEC-004) | MET |
| NFR-SEC-003 | `scenario.py` `threat_review` | — | A, B, C (`threat-review`); `docs/security/threat-model.md` | PARTIAL |
| NFR-SEC-004 | `common/apikeys.py` | `cli/test_cli.py::test_keys_create_prints_once_and_stores_only_a_hash`; `orc/akp::test_keys_are_hashed_and_role_mapped` | — | MET |
| NFR-REL-001 | `engine.py` | `orc/rel` | — | MET |
| NFR-REL-002 | `app.py` `redirect` | `sh/api::test_analytics_failure_never_blocks_redirect` | — | MET |
| NFR-AUD-001 | `audit.py`; `Store.tx` | `orc/akp::test_append_outside_a_transaction_is_refused` | all runs | MET |
| NFR-AUT-001 | `engine._principal` | `orc/flow::test_non_approver_decisions_are_refused_and_audited` | — | MET |
| NFR-RCV-001 | `engine.recover`, `resume` | `orchestrator/test_process_interruption.py::test_killed_engine_process_is_safe_stopped_and_resumes` | — | PARTIAL |
| NFR-DET-001 | `engine._execute_step` (node-ID commit order) | — | — | PARTIAL |
| NFR-CHG-001 | `approve-design`; `run_tests`; rollback | `e2e::test_scn_b_impact_analysis_precedes_change_and_ignores_the_patch` | B, BD | MET |
| NFR-DOC-001 | `specs/.../quickstart.md` | — | — | PARTIAL (quickstart rewritten 2026-10-16; no automated test, T282) |
