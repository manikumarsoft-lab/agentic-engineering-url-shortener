---

description: "Task list for feature 001: Agentic Software Engineering System: URL Shortener"
---

# Tasks: Agentic Software Engineering System: URL Shortener

**Input**: Design documents from `specs/001-agentic-sdlc-url-shortener/` (spec.md incl. CR-001..CR-005, plan.md incl. §16 CR-006 rulings and HD-CUT-001, research.md, data-model.md, contracts/, quickstart.md) and ADR-001..ADR-019 (accepted, Human Gate 4).

**Prerequisites**: plan.md (approved), spec.md (approved), ADRs accepted. **Task-plan approval**: _pending — recorded by T003 (human owner, after `/speckit-analyze`)._

**Tests**: Mandatory. The constitution (Principle IV) requires red-green-refactor TDD, so tests are written first and seen to fail before implementation.

**Status**: Generated 2026-10-15; regenerated 2026-10-15 after `/speckit-analyze` remediation; **regenerated again 2026-10-15 under CR-006 step 4** (54 tasks, each estimated ≤ 2 h; deadline 2026-10-16 15:30). **Nothing is implemented; no task is complete.**

**Stable IDs**: task IDs never change once assigned and are never reused. T001–T003 are kept. T004–T155 are **retired** by CR-006 step 4 (mapping in §Retired task mapping); new tasks start at T201. Listing order is execution order.

## Lifecycle Gate Record

- **Checklist stage exit (C4)**: Checklist stage exit approved by Mani Kumar Vadugu, 2026-10-15. Reviewed: the 19-file checklist set structure and the 8 gaps it surfaced, all closed via CR-003. Item-level checklist verification is performed at the /speckit-implement gate (T001). No checklist item is marked by this record.
- **Constitution exception CEX-001** (Governance §2): for human-decision and checkpoint tasks, verification = a recorded human decision (approver, timestamp, artifact version) in the decision/audit log; compensating control = T127 traceability check confirms each such decision exists. Approved by Mani Kumar Vadugu, 2026-10-15; review condition: re-evaluated at `/speckit-converge`. Recorded in plan.md (Complexity Tracking). *(CR-006 step 4 note: T127 is retired; its role passes to T203 (structural `--check`) and T249 (`--check --release`).)*
- **Task-plan approval**: pending (T003).
- **CR-006 step 4 regeneration** (2026-10-15): tasks regenerated per plan §16 and HD-CUT-001. `/speckit-analyze` must be re-run on this version before T003.

## Format and Field Legend

Each task line is `- [ ] T### [P?] [Story?] Description`, followed by its fields:

- **[P]**: parallelizable — touches no file shared with any concurrent task and has no unmet dependency.
- **[Story]**: `US1`–`US5` (spec user stories), `SCN-A`/`SCN-B`/`SCN-C` (required scenarios). Phases 0–2 and 12 carry no story label.
- **Req** requirement IDs · **ADR** references · **Paths** target paths · **Deps** task dependencies · **Est** estimate (≤ 2 h) · **Lane** parallel work lane (A shortener, B engine, C change sets, D docs/tooling, H human) · **TDD** obligation · **Done** completion criteria · **Verified by** the test, check or recorded decision that verifies the task (CEX-001 for human decisions) · **Human** approval requirement.
- `HUMAN:` tasks are performed only by the human owner and are never marked complete by an agent.

### TDD-8 (the default TDD obligation)

1. Identify the acceptance criterion (from **Req**/**Done**). 2. Write the failing test. 3. Run it and confirm it fails for the expected reason; paste the failure line into the TDD Evidence Log below. 4. Implement the smallest compliant behavior. 5. Run the test and confirm it passes. 6. Refactor. 7. Run the regression suite (`uv run python tools/check.py`). 8. Update documentation and traceability.

Default trace: tests carry `@pytest.mark.req(<Req IDs>)`; new modules carry a `Satisfies:` docstring line; task ID in the commit message. Default **Human**: none beyond the human owner's commit review. Default prerequisite: T003 approved.

### Guardrails (apply to every task)

- Architecture-sensitive work is blocked until its ADR is accepted; a change to an accepted decision needs a CR and a superseding ADR first.
- Do not modify spec.md, plan.md, contracts or ADRs to suit implementation; use a CR (docs/change-control.md). T201 is the CR-006 alignment step and needs human approval.
- Scenario capabilities (expiration, analytics, aliases, daily counts) are never added to the main working tree's `src/shortener/`; they exist only as change sets (CST-007).
- Evidence comes only from real execution; scripted, AI-backed or hand-edited output is never presented as scenario evidence (CON X).
- Human-role API keys are created by the human in their own terminal, outside the coding-assistant session, and never stored in the repository (plan §16.3). Agents never run `orch keys init` or `orch gate decide`.
- HD-CUT-001 cut items (BL-14..BL-21) have no tasks and are disclosed as *planned, not implemented*.
- Release readiness (T251) is blocked until T249 shows all mandatory validation executed.

---

## Phase 0: Lifecycle Gates and CR-006 Alignment

- [ ] T001 HUMAN: Review the 19 requirements-quality checklists in specs/001-agentic-sdlc-url-shortener/checklists/ and record the outcome
  - **Obj**: Satisfy the `/speckit-implement` checklist gate by reviewer decision, not by agent marking · **Req**: CON I, CON III; Spec §CR-003 · **Scn**: — · **ADR**: —
  - **Paths**: `specs/001-agentic-sdlc-url-shortener/checklists/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: none · **Parallel**: no
  - **Artifact**: Reviewed checklists: items marked [x] by the human owner, or new CRs for unsatisfied items · **TDD**: N/A — human decision or action (no code) · **Validate**: `/speckit-implement` checklist table shows each file's status
  - **Docs**: None · **Trace**: default · **Risk**: Agents must not mark checklist items
  - **Done**: Every checklist item is either marked by the human owner or covered by a recorded CR/decision to proceed · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only
  - **Decision record**: T001 decision (Mani Kumar Vadugu, 2026-10-15): I reviewed the per-file summary of all 19 checklists and read orchestration.md, human-approvals.md and scenario-ambiguous.md in full. I accept the checklist set as the requirements-quality gate for /speckit-implement. Items remain unchecked until verified against evidence.
- [ ] T002 Run /speckit-analyze (read-only) over all artifacts; the human owner reviews the report and may save it as specs/001-agentic-sdlc-url-shortener/analysis.md
  - **Obj**: Cross-artifact consistency analysis before implementation (CON workflow: CRITICAL findings block) · **Req**: CON Development Workflow; Governance §1 · **Scn**: — · **ADR**: —
  - **Paths**: `specs/001-agentic-sdlc-url-shortener/analysis.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: none · **Parallel**: no
  - **Artifact**: Analysis report with severity-ranked findings (saved to analysis.md at the human owner's request on 2026-10-15) · **TDD**: N/A — analysis, no behavior · **Validate**: Report exists; count of CRITICAL findings stated
  - **Docs**: None · **Trace**: default · **Risk**: Do not fix upstream artifacts silently; changes go through CRs
  - **Done**: Report produced; CRITICAL findings listed for the human owner · **Verified by**: T003 human approval references the reviewed report version (CEX-001 decision record) · **Human**: Human owner decides on each CRITICAL finding
- [ ] T201 Align contracts, ADRs and quickstart with plan §16 and HD-CUT-001 (CR-006 step 7); create docs/scope-control.md
  - **Req**: FR-GOV-009, CON VI; Plan §16.1–§16.5 · **ADR**: ADR-003, ADR-006, ADR-010, ADR-012, ADR-013, ADR-016, ADR-017 · **Deps**: none · **Est**: 2.0 h · **Lane**: D
  - **Paths**: `contracts/workflow-graph.v2.yaml` (→ 2.2.0); `contracts/schemas/gate-decision.schema.json` (→ 2.1.0); `contracts/orchestrator-api.openapi.yaml` (→ 2.2.0); `contracts/policy-set.v1.yaml` (→ 1.1.0); `contracts/README.md` (Change Records); `docs/adr/` (amendment notes); `quickstart.md`; `docs/scope-control.md`
  - **Content**: graph — remove G-SECURITY (SP-2 joins ST-10b and ST-11b); ST-05 inputs without the change-set manifest; REL-01 `smoke_failed` failure edge to REL-02 and ST-13 terminal hook per §16.2; G-CLARIFY rounds ≤ 2, `free_text` reopens, change set selected from the catalog after ST-03 passes on the clarified requirement; G-CLARIFY-n answer as optional input of the raising node only; ST-09 timeout override (value proposed in the Change Record). Gate-decision — `decision_source` removed from the body (server-derived). API — resume accepts an audited retry-budget extension; `change_set_ref` optional for clarify scenarios. Policy — SEC-004 retired with G-SECURITY; SEC-003 input is the hash-pinned advisory snapshot. Scope-control — timebox, CP-1..CP-5 rows, BL-01..BL-21, STOP-1..STOP-5
  - **TDD**: N/A — contract and documentation change · **Done**: Every §16 ruling reflected; each contract bump has a Change Record · **Verified by**: T219 contract-document and meta-schema tests; CEX-001 approval record · **Human**: REQUIRED — human owner approves the alignment
- [ ] T003 HUMAN: Approve the task plan specs/001-agentic-sdlc-url-shortener/tasks.md (task-plan approval gate, post-analyze)
  - **Obj**: Mandatory gate: task-plan approval before implementation · **Req**: CON Development Workflow (mandatory gates) · **Scn**: — · **ADR**: —
  - **Paths**: `specs/001-agentic-sdlc-url-shortener/tasks.md`
  - **Pre**: `/speckit-analyze` re-run on this version (CR-006 step 4) · **Deps**: T001, T002, T201 · **Parallel**: no
  - **Artifact**: Approval line (approver, date) in the tasks.md header · **TDD**: N/A — human decision or action (no code) · **Validate**: Approval recorded in tasks.md
  - **Done**: Approval recorded; no unresolved CRITICAL analysis finding · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T203 traceability check · **Human**: REQUIRED — human owner only

---

## Phase 1: Setup (Engineering Baseline)

- [ ] T202 Create toolchain and skeleton: pyproject.toml + uv.lock, .gitignore/.gitattributes (eol=lf), policy/approved-dependencies.yaml, policy/license-allowlist.yaml, .secrets.baseline, src/common|shortener|orchestrator packages, pytest `req` marker plugin, import-boundary test, tools/check.py
  - **Req**: NFR-RUN-001, CST-006, DEP-001, LIC-001, NFR-MNT-001, NFR-TST-001, PVT-007, FR-OBS-010 · **ADR**: ADR-001, ADR-002, ADR-004, ADR-018 · **Deps**: T003 · **Est**: 2.0 h · **Lane**: D
  - **Paths**: `pyproject.toml`; `uv.lock`; `.gitignore`; `.gitattributes`; `policy/`; `.secrets.baseline`; `src/*/__init__.py`; `tests/plugins/req_marker.py`; `tests/tooling/test_req_marker.py`; `tests/architecture/test_import_boundaries.py`; `tools/check.py`
  - **TDD**: TDD-8 for the marker plugin and boundary test (red with a violating fixture) · **Done**: `uv sync --frozen` succeeds; `req` IDs appear in JUnit properties; boundary test fails on the fixture and passes on the tree; `tools/check.py` runs ruff, mypy --strict and pytest with coverage fail_under=85 · **Verified by**: tests/tooling/test_req_marker.py; tests/architecture/test_import_boundaries.py; `uv run python tools/check.py`
- [ ] T203 Implement the traceability checker tools/trace/build_matrix.py (structural `--check` from Phase 1; `--release` mode for full coverage) and the CI workflow .github/workflows/ci.yml (ubuntu-latest) running tools/check.py and `build_matrix.py --check`; README.md skeleton
  - **Req**: FR-OBS-010, SC-007, FR-OBS-008, CST-009, CON X, CST-003 · **ADR**: ADR-018 · **Deps**: T202 · **Est**: 1.5 h · **Lane**: D
  - **Paths**: `tools/trace/build_matrix.py`; `tests/tooling/test_build_matrix.py`; `.github/workflows/ci.yml`; `README.md`
  - **TDD**: TDD-8 · **Done**: `--check` fails on a test without a `req` tag, a tag naming an unknown spec ID, or a `src/` module no task references; `--release` additionally fails on a C/D requirement without a test and a doc/evidence item, or stale evidence; README has the six required headings · **Verified by**: tests/tooling/test_build_matrix.py; green CI run (link in TDD Evidence Log) · **Human**: Human owner pushes to GitHub

---

## Phase 2: Foundational

- [ ] T204 [P] Implement src/common: injectable Clock (system, virtual), prefixed ULID IdGenerator, JSON logging with redaction, API key store (`sk_<key_id>.<secret>`, SHA-256 at rest, constant-time compare, roles) and `orch keys init`
  - **Req**: NFR-DET-001, FR-ORC-001, NFR-SEC-002, NFR-SEC-004, FR-OBS-009, FR-SHR-019, FR-GOV-003, FR-GOV-013, HD-003 · **ADR**: ADR-010, ADR-011, ADR-015 · **Deps**: T202 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/common/clock.py`; `src/common/ids.py`; `src/common/logging.py`; `src/common/apikeys.py`; `src/orchestrator/cli/keys.py`; `tests/common/`
  - **TDD**: TDD-8 · **Done**: IDs match the prefixed pattern; virtual clock deterministic; secrets and key patterns redacted; roles consumer/engineer/approver/release-owner/agent resolved; wrong secret rejected; `keys init` writes only under gitignored `var/secrets/` and prints secrets once · **Verified by**: tests/common/ · **Human**: Human runs `orch keys init` in their own terminal (plan §16.3)
- [ ] T205 [P] Implement shortener persistence: engine factory (WAL, busy_timeout, BEGIN IMMEDIATE), repository protocols, Alembic 0001_baseline
  - **Req**: FR-SHR-005, FR-SHR-013, NFR-SCL-002 · **ADR**: ADR-002, ADR-007 · **Deps**: T202 · **Est**: 1.0 h · **Lane**: A
  - **Paths**: `src/shortener/persistence/`; `tests/shortener/persistence/test_migrations.py`
  - **TDD**: TDD-8 · **Done**: Upgrade from empty; `links.code` PK with pattern check; `destination_url` ≤ 2,048 · **Verified by**: tests/shortener/persistence/test_migrations.py
- [ ] T206 Implement orchestrator persistence (Alembic 0001 with all data-model §1.2 tables, append-only triggers, plain DDL) and the audit store with per-run seq and hash chain
  - **Req**: FR-ORC-011, FR-ORC-028, FR-OBS-001..004, NFR-AUD-001 · **ADR**: ADR-002, ADR-008, ADR-015 · **Deps**: T204 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/persistence/`; `src/orchestrator/audit/store.py`; `src/orchestrator/audit/hashchain.py`; `tests/orchestrator/persistence/`; `tests/orchestrator/observability/test_audit_store.py`
  - **TDD**: TDD-8 · **Done**: UPDATE/DELETE on audit_events raise 'append-only'; unique (run_id, seq) and transition_key; every event validates against audit-event.schema.json; chain verification detects an out-of-band edit · **Verified by**: tests/orchestrator/persistence/; tests/orchestrator/observability/test_audit_store.py

---

## Phase 3: User Story 1 — Shortener baseline (P1) 🎯 MVP (Lane A)

- [ ] T207 [P] [US1] Implement URL validation/normalization and the short-code generator with table and Hypothesis tests
  - **Req**: FR-SHR-002, FR-SHR-003, FR-SHR-004, FR-SHR-006, NFR-SEC-001, PD-001, PVT-010, A-002, A-003 · **ADR**: ADR-014 · **Deps**: T202 · **Est**: 1.5 h · **Lane**: A
  - **Paths**: `src/shortener/domain/validation.py`; `src/shortener/domain/codes.py`; `tests/shortener/unit/test_validation.py`; `tests/shortener/unit/test_codes.py`
  - **TDD**: TDD-8 · **Done**: Every data-model §4 validation code covered (incl. private/loopback/link-local literals and `localhost`); CSPRNG base62 length 7; validator `^[A-Za-z0-9]{4,10}$`; no successor relation in a statistical test · **Verified by**: tests/shortener/unit/test_validation.py; tests/shortener/unit/test_codes.py
- [ ] T208 [US1] Implement create, resolve and idempotency use cases with repositories
  - **Req**: FR-SHR-001, FR-SHR-005, FR-SHR-007, FR-SHR-013, FR-SHR-015, A-004 · **ADR**: ADR-002, ADR-014 · **Deps**: T205, T207 · **Est**: 1.5 h · **Lane**: A
  - **Paths**: `src/shortener/domain/links.py`; `src/shortener/domain/resolve.py`; `src/shortener/persistence/links_repo.py`; `src/shortener/persistence/idempotency_repo.py`; `tests/shortener/unit/`
  - **TDD**: TDD-8 · **Done**: ≤ 5 regenerations then `code_generation_exhausted` with no partial record; outcomes redirect/not_found/unavailable, never redirects unverified; same key + payload → original result, different payload → conflict, 24 h expiry · **Verified by**: tests/shortener/unit/test_links.py, test_resolve.py, test_idempotency.py
- [ ] T209 [US1] Wire the shortener API (links, redirect, health, problem+json, config, `shortener serve`) with hand-written contract tests against shortener-api 1.0.0
  - **Req**: FR-SHR-001, FR-SHR-007, FR-SHR-016, FR-SHR-018, SC-001, PD-002, NFR-RUN-001 · **ADR**: ADR-004, ADR-007 · **Deps**: T208, T204 · **Est**: 2.0 h · **Lane**: A
  - **Paths**: `src/shortener/api/`; `src/shortener/config.py`; `src/shortener/app.py`; `src/shortener/__main__.py`; `tests/shortener/contract/`; `tests/shortener/integration/test_api.py`
  - **TDD**: TDD-8 (contract tests first) · **Done**: Responses validate against the contract's schemas and documented status codes; redirect 302 with `Cache-Control: no-store` and `Referrer-Policy: no-referrer`; live vs ready; binds 127.0.0.1; error bodies leak nothing · **Verified by**: tests/shortener/contract/; tests/shortener/integration/test_api.py
- [ ] T210 [US1] Add API-key auth, per-key rate limit, request-correlation logging middleware and the shortener security suite
  - **Req**: FR-SHR-017, FR-SHR-019, FR-OBS-009, FR-OBS-001, NFR-SEC-001, NFR-SEC-002, NFR-SEC-004, PVT-011, A-015 · **ADR**: ADR-010, ADR-011 · **Deps**: T209 · **Est**: 2.0 h · **Lane**: A
  - **Paths**: `src/shortener/api/auth.py`; `src/shortener/api/ratelimit.py`; `src/shortener/telemetry/middleware.py`; `tests/shortener/security/`; `tests/shortener/unit/test_ratelimit.py`
  - **TDD**: TDD-8 · **Done**: Missing/invalid key → 401, wrong or agent role → 403 with no existence hints; 61st request/min → 429 with Retry-After; logs carry correlation ID and no IP, user agent or key secret; 100% of negative security cases rejected · **Verified by**: tests/shortener/security/; tests/shortener/unit/test_ratelimit.py
- [ ] T211 [P] [US1] Write integration tests: uvicorn subprocess round trip, persistence failure, PVT-003 concurrency
  - **Req**: FR-SHR-014, FR-SHR-015, FR-SHR-016, PVT-003, NFR-SCL-001 · **ADR**: ADR-002, ADR-014 · **Deps**: T210 · **Est**: 1.5 h · **Lane**: A
  - **Paths**: `tests/shortener/integration/test_persistence_failure.py`; `tests/shortener/concurrency/test_pvt003.py`; `tests/shortener/integration/test_walking_skeleton.py`
  - **TDD**: TDD impractical: these need the assembled HTTP stack and real SQLite contention; the units were test-first in T207/T208. First run recorded; any defect gets its own red test first (CON IV) · **Done**: DB unavailable → 503 and no partial record, redirect → 503; 1,000 concurrent creations → 1,000 distinct codes (STOP-2 if not met) · **Verified by**: the listed tests
- [ ] T212 [US1] HUMAN: Review the baseline, create the annotated tag `shortener-baseline-v1` and record CP-1 in docs/scope-control.md
  - **Req**: PD-009, CST-007, HD-002, CST-005 · **ADR**: ADR-006 · **Deps**: T211 · **Est**: 0.5 h · **Lane**: H
  - **TDD**: N/A — human decision · **Done**: Tag on the reviewed commit; CP-1 row (continue / reduce / stop) recorded · **Verified by**: CEX-001 decision record; T203 traceability check · **Human**: REQUIRED — human owner only

---

## Phase 4: Change Sets (Lane C, in parallel with the engine)

- [ ] T213 [P] Implement the change-set store: manifest validation, fingerprint, catalog `changesets/catalog.yaml` keyed by (scenario, option_id), lock verification against a human-created annotated git tag, `orch changeset verify`
  - **Req**: FR-ORC-033, FR-ORC-034, FR-ORC-036, CHG-001; Plan §16.1 (C1), §16.3 · **ADR**: ADR-006 · **Deps**: T204, T201 · **Est**: 1.5 h · **Lane**: C
  - **Paths**: `src/orchestrator/sut/changeset.py`; `src/orchestrator/cli/changeset.py`; `tests/orchestrator/sut/test_changeset.py`
  - **TDD**: TDD-8 · **Done**: Required manifest fields incl. the fixed FR-ORC-034 text; dependency change → manifest_invalid; lock ≠ bundle, lock ≠ tagged content, or missing/lightweight tag → integrity_mismatch; catalog lookup miss → `no_approved_change_set` · **Verified by**: tests/orchestrator/sut/test_changeset.py
- [ ] T214 [SCN-A] Author the SCN-A scenario pack and change set in var/authoring/scn-a/ (from R0): expiration (`expires_at`, 410, 422, migration 0002) and analytics (`link_stats`, atomic counter, fallback, analytics endpoint); export changesets/scn-a/normal/ and the behavior-change fixture
  - **Req**: FR-SHR-008..012, FR-SHR-014, A-006, A-013, A-014, NFR-REL-002, SCN-A-AC1, SCN-A-AC6 · **ADR**: ADR-006, ADR-007, ADR-019 · **Deps**: T212, T213 · **Est**: 2.0 h · **Lane**: C
  - **Paths**: `scenarios/scn-a/`; `var/authoring/scn-a/`; `changesets/scn-a/normal/`; `tests/fixtures/changesets/scn-a-behavior-change/`
  - **TDD**: TDD-8 inside the authoring workspace · **Done**: Baseline + new tests green in the workspace; contract 1.1.0, migration additive; `orch changeset verify` passes · **Verified by**: workspace `uv run pytest tests/shortener -q`; `orch changeset verify`
- [ ] T215 [SCN-B] Author the SCN-B scenario pack and change sets (R0 + scn-a): custom aliases (409, 422, reserved words, `code_origin` migration 0003), plus the labeled `defective` and `undeclared-scope` variants
  - **Req**: FR-SHR-020..022, FR-ORC-036, SCN-B-AC4, SCN-B-AC5 · **ADR**: ADR-014, ADR-006, ADR-012 · **Deps**: T214 · **Est**: 2.0 h · **Lane**: C
  - **Paths**: `scenarios/scn-b/`; `var/authoring/scn-b/`; `changesets/scn-b/{normal,defective,undeclared-scope}/`
  - **TDD**: TDD-8 inside the authoring workspace (the defective variant is verified by making the conflict test fail) · **Done**: Alias lengths 3/11 rejected, 4/7/10 accepted; regression unchanged; variants labeled · **Verified by**: workspace tests; `orch changeset verify` per variant
- [ ] T216 [SCN-C] Author the SCN-C scenario pack (verbatim "We need to track who clicks links.", Q1 A/B/C, Q2 retention) and the aggregate-daily change set (R0 + A + B, migration 0004); add catalog entries
  - **Req**: FR-SHR-023, FR-SHR-012, PD-008, SCN-C-AC1, SCN-C-AC3; Plan §16.1 (C1) · **ADR**: ADR-019, ADR-007 · **Deps**: T215 · **Est**: 1.5 h · **Lane**: C
  - **Paths**: `scenarios/scn-c/`; `var/authoring/scn-c/`; `changesets/scn-c/aggregate-daily/`; `changesets/catalog.yaml`
  - **TDD**: TDD-8 inside the authoring workspace · **Done**: No visitor personal data stored; catalog maps (scn-a, default), (scn-b, default), (scn-c, A) → bundles; (scn-c, B) has no entry · **Verified by**: workspace tests; `orch changeset verify`
- [ ] T217 HUMAN: Review and lock all change sets in changesets/approved.lock.yaml, create the annotated tag over the lock, and record CP-2
  - **Req**: FR-ORC-033, CHG-001; Plan §16.3 · **ADR**: ADR-006 · **Deps**: T216 · **Est**: 0.5 h · **Lane**: H
  - **TDD**: N/A — human decision · **Done**: Lock and tag created by the human; `orch changeset verify` reports a match for every bundle; CP-2 row recorded · **Verified by**: CEX-001 decision record; `orch changeset verify` · **Human**: REQUIRED — human owner only

---

## Phase 5: User Story 2 — Engine core (P1) (Lane B)

- [ ] T218 [US2] Implement run/node/gate state tables and the transition helper (conditional update on row_version + audit append + unique transition_key in one transaction)
  - **Req**: FR-ORC-005, FR-ORC-008, FR-ORC-011, FR-ORC-023, FR-ORC-028, CON II · **ADR**: ADR-003, ADR-015 · **Deps**: T206 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/state.py`; `src/orchestrator/engine/transitions.py`; `tests/orchestrator/state/test_state_tables.py`; `tests/orchestrator/state/test_transitions.py`
  - **TDD**: TDD-8 · **Done**: Every listed transition allowed, every other pair → IllegalTransition (audited); terminal states have no exits; duplicate transition_key applied once; competing claim loses cleanly; crash between update and append leaves neither · **Verified by**: the listed tests
- [ ] T219 [P] [US2] Implement graph loading (meta-schemas for graph and policy; contract-document and example validation), instance building, conditions, entry/exit criteria, ready set per the plan §16.2 join/skip table, downstream closure and dependent path
  - **Req**: FR-ORC-005..008, FR-ORC-022, FR-ORC-037, FR-ORC-038, FR-ORC-039, CON II · **ADR**: ADR-005, ADR-017, ADR-007 · **Deps**: T202, T201 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/graph.py`; `src/orchestrator/engine/criteria.py`; `src/orchestrator/definitions/schemas/`; `tests/orchestrator/state/test_graph.py`; `tests/contract/test_contract_documents.py`
  - **TDD**: TDD-8 · **Done**: Graph 2.2.0 instantiates; cycle/unknown-check/missing-field fixtures rejected; each §16.2 row has a test (incl. REL-01 failure edge, ST-13 hook); unmet entry → BLOCKED with reason; false condition → SKIPPED with reason · **Verified by**: the listed tests
- [ ] T220 [US2] Implement versioned artifacts, provenance and decision lineage
  - **Req**: FR-ORC-012, FR-ORC-013, FR-ORC-034 · **ADR**: ADR-015 · **Deps**: T218 · **Est**: 1.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/artifacts.py`; `tests/orchestrator/unit/test_artifacts.py`
  - **TDD**: TDD-8 · **Done**: Immutable versions with content hash, producing node/attempt, actor, agent mode, input_versions; status current/stale/superseded/rolled_back; decisions link bound and affected versions · **Verified by**: tests/orchestrator/unit/test_artifacts.py
- [ ] T221 [P] [US2] Implement the Agent protocol, StageContext capabilities, permission guard and the disabled AI-backed stub
  - **Req**: FR-ORC-025, FR-ORC-027, FR-ORC-030, NFR-AUT-001, CST-006, HD-001 · **ADR**: ADR-003, ADR-010 · **Deps**: T204 · **Est**: 1.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/agents/base.py`; `src/orchestrator/agents/capabilities.py`; `src/orchestrator/security/permissions.py`; `src/orchestrator/agents/ai_backed/stub.py`; `tests/orchestrator/security/test_permissions.py`; `tests/orchestrator/agents/test_ai_stub.py`
  - **TDD**: TDD-8 · **Done**: Out-of-permission call → PERMISSION_REFUSED audited; loader rejects any role granted gate.decide, exception.approve, run.resume, run.abort, audit.modify, repo.write or keys.issue; ai_backed → 422 agent_mode_unavailable · **Verified by**: the listed tests
- [ ] T222 [US2] Implement the subprocess agent runner: one child process per attempt, per-node timeout with process-tree kill (Windows process group), fencing tokens on artifact writes and transitions
  - **Req**: FR-ORC-015, FR-ORC-028, PVT-005; Plan §16.3 · **ADR**: ADR-003, ADR-013, ADR-004 · **Deps**: T221, T218 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/runner.py`; `tests/orchestrator/reliability/test_runner_timeout.py`
  - **TDD**: TDD-8 · **Done**: Timeout → tree killed, TIMEOUT audited, attempt FAILED_TRANSIENT; a write carrying a superseded token is refused and audited; no orphaned process after kill on Windows · **Verified by**: tests/orchestrator/reliability/test_runner_timeout.py
- [ ] T223 [US2] Implement the deterministic superstep scheduler: concurrent step, node-ID commit order, step events (ready set per step, sync held), timers, stall detection
  - **Req**: FR-ORC-006, FR-ORC-037, FR-ORC-038, FR-ORC-039, NFR-DET-001, PD-004 · **ADR**: ADR-003 · **Deps**: T219, T220, T222 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/scheduler.py`; `tests/orchestrator/state/test_scheduler.py`
  - **TDD**: TDD-8 · **Done**: Fixture graph: F1 branches READY in the same step and attempt intervals overlap; commit order is node-ID order; sync releases only per §16.2; stall → SAFE_STOPPED scheduler_stalled · **Verified by**: tests/orchestrator/state/test_scheduler.py
- [ ] T224 [US2] Implement the run service, run API, orchestrator role authorization (server-derived `decision_source`) and CLI (`orch serve`, `run submit|show|watch|timeline`)
  - **Req**: FR-ORC-001, FR-ORC-024, FR-ORC-029, FR-ORC-031, FR-GOV-003, FR-GOV-013, SC-011, NFR-AUT-001, NFR-DOC-001 · **ADR**: ADR-015, ADR-010, ADR-004 · **Deps**: T223 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/runs.py`; `src/orchestrator/api/`; `src/orchestrator/cli/main.py`; `src/orchestrator/cli/runs.py`; `tests/orchestrator/api/test_runs_api.py`; `tests/orchestrator/security/test_authz.py`
  - **TDD**: TDD-8 · **Done**: Responses validate against workflow-state.schema.json; runs pin graph and policy versions, record agent_mode, labels include `demonstration`; agent key on human-reserved endpoints → 403 + AUTH_REFUSED; decisions record key_id and role; `decision_source` derived from key class, client value ignored · **Verified by**: the listed tests

---

## Phase 6: User Story 3 — Gates, policy and exceptions (P1)

- [ ] T225 [US3] Implement the gate lifecycle with decisions (approve, reject_rework ≤ 2, reject_terminate, escalate, answer), version binding, timeout → SAFE_STOPPED, clarification rounds ≤ 2 with `free_text` reopening, G-RELEASE `not_ready` → FAILED; gate API and CLI
  - **Req**: FR-GOV-001, FR-GOV-002, FR-GOV-004, FR-GOV-011, FR-GOV-014..016, FR-ORC-004, FR-ORC-028, SC-004, PVT-013; Plan §16.1 (C1) · **ADR**: ADR-016, ADR-013 · **Deps**: T223, T224 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/gates.py`; `src/orchestrator/api/gates.py`; `src/orchestrator/cli/gates.py`; `tests/orchestrator/governance/`
  - **TDD**: TDD-8 · **Done**: Stale bound version → 409; engine re-checks actor.type == human; duplicate decision_id applied once; third rework → SAFE_STOPPED 'rework limit exceeded'; third clarify round → SAFE_STOPPED 'clarification limit exceeded'; free_text never interpreted; escalate keeps the gate blocking; no TIMED_OUT → APPROVED path · **Verified by**: tests/orchestrator/governance/
- [ ] T226 [P] [US3] Implement policy loader (version pinning, completeness), evaluator, blocking rule and ST-03 routing, with checks PRIV-001, ARCH-001, CHG-001, CHG-002, CHG-003, CHG-004
  - **Req**: FR-GOV-005, FR-GOV-006, FR-GOV-007, FR-SHR-012, FR-SHR-023, FR-ORC-033, SCN-B-AC5, SC-008 · **ADR**: ADR-009, ADR-006 · **Deps**: T220 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/policy/model.py`; `src/orchestrator/policy/evaluator.py`; `src/orchestrator/policy/checks/`; `tests/orchestrator/policy/`
  - **TDD**: TDD-8 · **Done**: One outcome per applicable check; evaluations append-only and schema-valid; mandatory FAIL → SAFE_STOPPED policy_fail:<check>; unclarified requirement-level FAIL routes to G-CLARIFY; CHG-002 compares touched files with the impact analysis; drop/narrowing/rename → CHG-003 FAIL · **Verified by**: tests/orchestrator/policy/
- [ ] T227 [P] [US3] Implement checks REL-001..005, AUD-001/002, SEC-001/002/003/005, DEP-001, LIC-001/002 with scanner adapters behind interfaces; SEC-003 against the hash-pinned advisory snapshot
  - **Req**: FR-GOV-010, FR-GOV-012, FR-ORC-016, NFR-SEC-002, PVT-012, PD-002b; Plan §16.1 (C5) · **ADR**: ADR-009, ADR-008 · **Deps**: T226 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/policy/checks/`; `src/orchestrator/sut/scanners.py`; `policy/advisory-snapshot/`; `tests/orchestrator/policy/test_checks_release_security.py`
  - **TDD**: TDD-8 with fake scanners; one real-tool integration test · **Done**: Snapshot missing or hash mismatch → SEC-003 FAIL, never PASS; no network access in runs; REL-003 FAIL on requested/rejected/expired exceptions; REL-005 advisory never blocks · **Verified by**: tests/orchestrator/policy/test_checks_release_security.py
- [ ] T228 [US3] Implement the policy exception workflow with FR-GOV-017 separation of duties and expiry
  - **Req**: FR-GOV-007, FR-GOV-008, FR-GOV-017, SC-008 · **ADR**: ADR-009, ADR-016 · **Deps**: T225, T227 · **Est**: 1.5 h · **Lane**: B
  - **Paths**: `src/orchestrator/policy/exceptions.py`; `src/orchestrator/api/exceptions.py`; `tests/orchestrator/governance/test_exceptions.py`
  - **TDD**: TDD-8 · **Done**: Request → EXCEPTION-REQUESTED + G-EXCEPTION-n; approval needs approver role, compensating control and expiry ≤ 30 days or a review condition; same key identity → 403 separation_of_duties_violation, audited; non-waivable → 422; expiry → EXPIRED → REL-003 FAIL · **Verified by**: tests/orchestrator/governance/test_exceptions.py

---

## Phase 7: User Story 2 — Reliability, system-under-change adapter, replanning (P1)

- [ ] T229 [US2] Implement failure classification, bounded retry with seeded backoff, declared fallbacks, safe-stop entry with report, and the fault injector
  - **Req**: FR-ORC-014, FR-ORC-016, FR-ORC-018, FR-ORC-023, NFR-REL-001, PVT-004, PD-003, SC-005, FR-ORC-036 · **ADR**: ADR-013, ADR-018 · **Deps**: T223 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/retry.py`; `src/orchestrator/engine/fallback.py`; `src/orchestrator/engine/recovery.py`; `src/orchestrator/engine/faults.py`; `tests/orchestrator/reliability/`
  - **TDD**: TDD-8 · **Done**: ≤ 3 attempts; permanent never retried; unclassified → SAFE_STOPPED; FALLBACK_USED and degraded=true; each safe-stop trigger → SAFE_STOPPED with reason, no node RUNNING, report artifact; injector disabled by default, labels runs `fault-injection` / `finding-injection`, audits FAULT_INJECTED · **Verified by**: tests/orchestrator/reliability/
- [ ] T230 [US2] Implement startup recovery and approver-only resume with an audited retry-budget extension
  - **Req**: FR-ORC-019, FR-GOV-014, A-016, PD-011, NFR-RCV-001; Plan §16.3 · **ADR**: ADR-013 · **Deps**: T229, T225 · **Est**: 1.5 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/recovery.py`; `src/orchestrator/api/runs.py`; `tests/orchestrator/reliability/test_resume.py`
  - **TDD**: TDD-8 · **Done**: Interrupted attempts → INTERRUPTED and run SAFE_STOPPED(interrupted); resume needs approver key and resolved/excepted cause (else 409); timed-out gate reopens on the same version; completed nodes not re-run; an exhausted node resumes only with an audited extension (approver, key ID, nodes, attempts, reason) · **Verified by**: tests/orchestrator/reliability/test_resume.py
- [ ] T231 [P] [US2] Implement the release store (R0 via `git archive`), isolated workspaces (traversal guard, discard), patch applier and workspace test runner (pytest subprocess, JUnit)
  - **Req**: FR-ORC-032, FR-ORC-035, FR-ORC-043, PD-009, SCN-B-AC3, SCN-B-AC5 · **ADR**: ADR-006, ADR-012, ADR-018 · **Deps**: T212, T213 · **Est**: 2.0 h · **Lane**: C
  - **Paths**: `src/orchestrator/sut/releases.py`; `src/orchestrator/sut/workspace.py`; `src/orchestrator/sut/patch.py`; `src/orchestrator/sut/testrunner.py`; `tests/orchestrator/sut/`
  - **TDD**: TDD-8 · **Done**: R0 equals the tagged tree; workspaces only under var/work/<run>/<attempt>/; escapes refused; main tree hash unchanged; non-applying patch → patch_does_not_apply; touched files listed; CRLF fixture applies; JUnit parsed; crash without report → transient · **Verified by**: tests/orchestrator/sut/
- [ ] T232 [US2] Implement the staging manager (forward promotion with additive migration; re-promotion without migration; smoke; effects query; process cleanup), `orch staging bootstrap|status` and `orch demo reset`
  - **Req**: FR-ORC-040, FR-ORC-041, FR-ORC-042, A-012, NFR-RUN-001, PVT-009; Plan §16.3 · **ADR**: ADR-012, ADR-004 · **Deps**: T231 · **Est**: 2.0 h · **Lane**: C
  - **Paths**: `src/orchestrator/sut/staging.py`; `src/orchestrator/cli/staging.py`; `src/orchestrator/cli/demo.py`; `tests/orchestrator/integration/test_staging.py`; `tests/orchestrator/cli/`
  - **TDD**: TDD-8 · **Done**: Promotion idempotent by release_id; destructive migration refused; previous release starts on the migrated DB without migrating and passes smoke; readiness never compares migration heads; no orphaned process on Windows; demo reset needs interactive 'yes', stays inside var/ and never deletes `var/orchestrator/orchestrator.db` · **Verified by**: tests/orchestrator/integration/test_staging.py; tests/orchestrator/cli/
- [ ] T233 [US2] Implement dynamic replanning (stale closure, gate revocation, graph instance version, input-hash memoization) and late-ambiguity suspension with the answer routed only to the raising node
  - **Req**: FR-ORC-020, FR-ORC-021, FR-ORC-022, SC-006, SCN-A-AC4, SCN-C-AC4; Plan §16.1 (C3) · **ADR**: ADR-017 · **Deps**: T225, T220 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/engine/replan.py`; `tests/orchestrator/replan/test_replan.py`
  - **TDD**: TDD-8 · **Done**: Only closure nodes re-run; unaffected attempt counts unchanged; bound approvals REVOKED and re-requested; REPLAN_*, ARTIFACT_STALE, GATE_REVOKED, GRAPH_VERSION_CREATED audited; G-CLARIFY-n answer feeds only the raising node; G-DESIGN not revoked; ST-08/ST-09 attempt counts unchanged · **Verified by**: tests/orchestrator/replan/test_replan.py

---

## Phase 8: User Story 2 — Deterministic agents (P1)

- [ ] T234 [US2] Implement ST-01 intake, ST-02 analyst and ST-03 quality agents (five checks, ambiguity classification) with a held-out ambiguity corpus; change-set selection from the catalog after ST-03 passes on the clarified requirement
  - **Req**: FR-ORC-002..004, SCN-A-AC1, SCN-A-AC5, SCN-C-AC1, SCN-C-AC5; Plan §16.1 (C1) · **ADR**: ADR-003 · **Deps**: T226, T223, T213 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/agents/deterministic/intake.py`, `analyst.py`, `quality.py`; `tests/orchestrator/agents/test_requirement_agents.py`; `tests/orchestrator/agents/corpus/`
  - **TDD**: TDD-8 · **Done**: Well-defined requirement → all PASS, G-CLARIFY SKIPPED with reasons; 'track who clicks links' → missing_information, unclear_term, policy_conflict; held-out corpus detection rates recorded; catalog miss → run FAILED with reason · **Verified by**: tests/orchestrator/agents/test_requirement_agents.py
- [ ] T235 [US2] Implement ST-05a additive-change check, ST-05 impact analysis (requirement + component registry + baseline import graph, never the manifest), ST-06 planner and ST-07 architect
  - **Req**: SCN-A-AC2, SCN-A-AC6, FR-ORC-007, FR-ORC-009, FR-ORC-010, SCN-B-AC1; Plan §16.1 (C2) · **ADR**: ADR-005, ADR-006, ADR-007 · **Deps**: T234, T231 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/agents/deterministic/additive_check.py`, `impact.py`, `planner.py`, `architect.py`; `src/orchestrator/definitions/registry/components.yaml`; `tests/orchestrator/agents/test_impact_design_agents.py`
  - **TDD**: TDD-8 · **Done**: Additive PASS skips ST-05; FAIL reclassifies and routes to ST-05; ST-05 never reads the manifest (test asserts it); impact lists components, interfaces, data flows, tests, docs, risks, rollout/rollback linked to RQ IDs; task graph acyclic with AC per task; design computes the contract bump · **Verified by**: tests/orchestrator/agents/test_impact_design_agents.py
- [ ] T236 [US2] Implement ST-08 implementer (CHG-001/002/004, scope check) and ST-09 tester with rollback
  - **Req**: FR-ORC-032..035, PD-012, SCN-B-AC4, SCN-B-AC5 · **ADR**: ADR-006, ADR-012 · **Deps**: T235, T229, T226 · **Est**: 1.5 h · **Lane**: B
  - **Paths**: `src/orchestrator/agents/deterministic/implementer.py`, `tester.py`; `tests/orchestrator/agents/test_change_agents.py`
  - **TDD**: TDD-8 · **Done**: Integrity or scope FAIL → SAFE_STOPPED; test failure → ROLLBACK_STARTED/COMPLETED, workspace discarded, artifacts rolled_back, run FAILED; provenance label equals the FR-ORC-034 text · **Verified by**: tests/orchestrator/agents/test_change_agents.py
- [ ] T237 [US2] Implement ST-10a/b writer (templates, fallbacks), ST-11a/b security (STRIDE-lite threat review that may raise ambiguity; scanners via T227) and ST-12 readiness assessment
  - **Req**: FR-ORC-016, FR-ORC-037, FR-ORC-038, FR-GOV-010, NFR-SEC-003, CON XI · **ADR**: ADR-009, ADR-013, ADR-016 · **Deps**: T236, T227 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/agents/deterministic/writer.py`, `security.py`, `release.py`; `tests/orchestrator/agents/test_docs_security_release_agents.py`
  - **TDD**: TDD-8 · **Done**: ST-10b falls back to a manual-review section (degraded); SEC-005 covers impacted interfaces; ST-11a can return needs_clarification; assessment ELIGIBLE or FAIL with each blocking reason and open risks with severity · **Verified by**: tests/orchestrator/agents/test_docs_security_release_agents.py
- [ ] T238 [US2] Implement REL-01 promote + smoke, REL-02 compensation, G-CORRECTIVE corrective actions and the ST-13 engineering-summary agent
  - **Req**: FR-ORC-017, FR-ORC-026, FR-ORC-040..042 · **ADR**: ADR-012, ADR-011 · **Deps**: T237, T232, T225 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `src/orchestrator/agents/deterministic/deployer.py`, `reporter.py`; `tests/orchestrator/agents/test_deployer_reporter.py`
  - **TDD**: TDD-8 · **Done**: No promotion without a recorded `ready`; smoke fail → REL-02 via the §16.2 failure edge, previous release re-promoted without migration, failed-interval links/stats listed, G-CORRECTIVE opened; compensation failure → SAFE_STOPPED degraded; summary has plan and rationale, artifacts, risks, trade-offs, validation results, assumptions, limitations on COMPLETED, FAILED and ABORTED paths · **Verified by**: tests/orchestrator/agents/test_deployer_reporter.py

---

## Phase 9: User Story 5 — Reconstruction, metrics and evidence (P2)

- [ ] T239 [P] [US5] Implement audit query/verify endpoints and `orch audit`, failure episodes, and reliability metrics (success/failure rate, retry, rollback and compensation frequency, MTTR, end-to-end and per-stage latency split active vs human wait, demonstration labels) with `orch metrics`
  - **Req**: FR-OBS-004..007, NFR-RCV-002 · **ADR**: ADR-008, ADR-011 · **Deps**: T224 · **Est**: 2.0 h · **Lane**: D
  - **Paths**: `src/orchestrator/api/audit.py`; `src/orchestrator/cli/audit.py`; `src/orchestrator/observability/episodes.py`; `src/orchestrator/observability/metrics.py`; `src/orchestrator/api/metrics.py`; `src/orchestrator/cli/metrics.py`; `tests/orchestrator/observability/`
  - **TDD**: TDD-8 · **Done**: Filters run_id, requirement_id, actor, event_type; PUT/DELETE → 405 + AUDIT_TAMPER_REFUSED; hand-built event sequences give exact MTTR; unrecovered/open excluded from the denominator and counted; p50/p95 latency; every output has measurement_class=demonstration · **Verified by**: tests/orchestrator/observability/
- [ ] T240 [US5] Implement run-level bidirectional traceability with `orch trace`, and evidence export (full ordered event log, manifest with hashes, offline verifier, index of every run ID incl. failed/aborted/safe-stopped)
  - **Req**: FR-OBS-008, FR-ORC-013, SC-002, SC-003, FR-ORC-029, CON X · **ADR**: ADR-015, ADR-008 · **Deps**: T239 · **Est**: 2.0 h · **Lane**: D
  - **Paths**: `src/orchestrator/trace/`; `src/orchestrator/api/trace.py`; `src/orchestrator/cli/trace.py`; `src/orchestrator/observability/evidence.py`; `tools/verify_evidence.py`; `tests/orchestrator/observability/test_evidence_export.py`; `tests/orchestrator/api/test_trace_api.py`
  - **TDD**: TDD-8 · **Done**: Forward and reverse views with gaps; the verifier re-checks the hash chain without the DB; export refuses runs labeled `test` or agent_mode=ai_backed for scenario evidence; run index lists every run with its outcome · **Verified by**: the listed tests

---

## Phase 10: Engine Integration Suites

- [ ] T241 [US2] Write full-graph path, governance-negative and release-readiness tests with stub agents and fixture change sets
  - **Req**: FR-ORC-006, FR-ORC-037..039, NFR-AUT-001, SC-004, SC-008, SC-011, FR-GOV-010, FR-GOV-011, FR-GOV-017, NFR-OBS-001, PVT-008, US-4 · **ADR**: ADR-003, ADR-016, ADR-015 · **Deps**: T228, T240, T237 · **Est**: 2.0 h · **Lane**: D
  - **Paths**: `tests/orchestrator/state/test_full_graph_paths.py`; `tests/orchestrator/security/test_security_suite.py`; `tests/orchestrator/governance/test_release_readiness.py`; `tests/orchestrator/observability/test_completeness_reconstruction.py`
  - **TDD**: TDD impractical: whole-graph behavior emerges only once all modules exist; each rule was test-first in Phases 5–8. First run recorded; defects get a red test first (CON IV) · **Done**: Same-step READY and join-hold events for F1/F2; sync holds on SUSPENDED/FAILED/RETRY_WAIT; mandatory FAIL → SP-2 never releases; expired exception → `ready` refused 409; 100% of agent human-reserved attempts refused and audited; node states rebuilt from audit equal state tables · **Verified by**: the listed tests
- [ ] T242 [US2] Write the reliability suite: rollback, compensation (smoke_fail, compensation_fail), interruption at every boundary with stub agents plus 3 full E2E interruptions (mid-F1, open gate, REL-01), retry-budget extension, late-ambiguity attempt counts
  - **Req**: FR-ORC-017, FR-ORC-019, FR-ORC-035, FR-ORC-042, PVT-006, NFR-RCV-001, SC-005, SC-006, SCN-B-AC4, NFR-CHG-001; HD-CUT-001 #1 · **ADR**: ADR-012, ADR-013, ADR-017 · **Deps**: T238, T230, T233 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `tests/orchestrator/reliability/test_rollback.py`; `test_compensation.py`; `test_interruption_boundaries.py`
  - **TDD**: TDD impractical: needs the full graph, SUT adapter and staging; mechanics were test-first in T229–T233, T236, T238. First run recorded; defects get a red test first (CON IV) · **Done**: Rollback evidence with workspace disposal, staging unchanged; re-promotion verified by previous-release smoke; every boundary resumes to the same terminal outcome with no duplicate side effects · **Verified by**: the listed tests

---

## Phase 11: Required Scenarios (P1)

- [ ] T243 [SCN-A] [SCN-B] Write scripted end-to-end tests for SCN-A (normal, late-ambiguity finding-injection, additive-fail) and SCN-B (normal with G-DESIGN escalation, defective, undeclared scope, integrity tamper)
  - **Req**: SCN-A-AC1..AC6, SCN-B-AC1..AC5, SC-002, FR-ORC-022, FR-ORC-031 · **ADR**: ADR-003, ADR-006, ADR-016, ADR-017 · **Deps**: T238, T217 · **Est**: 2.0 h · **Lane**: B
  - **Paths**: `tests/e2e/test_scn_a.py`; `tests/e2e/test_scn_b.py`
  - **TDD**: TDD impractical: needs locked change sets and the complete engine; behaviors were test-first in Phases 5–8. First run recorded; defects get a red test first (CON IV) · **Done**: SCN-A: G-CLARIFY SKIPPED citing each check, ST-05a PASS, COMPLETED with R1, 410 on staging; late ambiguity: ST-11a SUSPENDED, SP-1 holds, answer to ST-11a only; additive-fail reroutes to ST-05. SCN-B: impact before ST-08, escalate then approve, regression + new tests pass, R2; defective → rollback, staging R1, FAILED; scope → CHG-002 SAFE_STOPPED; tamper → CHG-001 SAFE_STOPPED · **Verified by**: the listed tests
- [ ] T244 [P] [SCN-C] Write scripted SCN-C end-to-end tests (option A, option C → ABORTED, timeout, option B without exception, free_text reopen, clarification limit, one approved exception via injected SEC-003 failure) and the repeat-run determinism test
  - **Req**: SCN-C-AC1..AC5, FR-GOV-007, FR-GOV-008, FR-GOV-014, FR-GOV-015, FR-GOV-017, NFR-DET-001, SC-010; HD-CUT-001 #8 · **ADR**: ADR-016, ADR-009, ADR-017 · **Deps**: T238, T217 · **Est**: 2.0 h · **Lane**: D
  - **Paths**: `tests/e2e/test_scn_c.py`; `tests/e2e/test_determinism.py`
  - **TDD**: TDD impractical: needs the complete engine; each rule was test-first in T225–T228, T233, T234. First run recorded; defects get a red test first (CON IV) · **Done**: No ST-05+ READY while G-CLARIFY open; option A → v2, aggregate-daily selected, COMPLETED R3; B → PRIV-001 FAIL → SAFE_STOPPED; C → ABORTED; timeout → SAFE_STOPPED 'no decision'; exception requested by engineer key, approved by a different approver key, same key → 403; two scripted runs per scenario compare equal · **Verified by**: the listed tests
- [ ] T245 [SCN-A] HUMAN: Execute recorded SCN-A runs (normal and late-ambiguity) with your own keys, export evidence, record CP-3
  - **Req**: SC-002, FR-ORC-031, PD-006 · **ADR**: ADR-016 · **Deps**: T243 · **Est**: 1.0 h · **Lane**: H
  - **TDD**: N/A — human decision · **Done**: EV-001..EV-004, EV-006, EV-007 for SCN-A; offline verifier passes · **Verified by**: CEX-001 decision record; `tools/verify_evidence.py` · **Human**: REQUIRED — human owner makes all gate decisions
- [ ] T246 [SCN-B] HUMAN: Execute recorded SCN-B runs (normal with one G-DESIGN escalation, and defective) and export evidence
  - **Req**: SC-002, FR-ORC-031, FR-GOV-002 · **ADR**: ADR-016 · **Deps**: T245 (staging must serve R1), T243 · **Est**: 1.0 h · **Lane**: H
  - **TDD**: N/A — human decision · **Done**: EV-001..EV-007 for SCN-B incl. EV-005 and rollback evidence; escalation recorded · **Verified by**: CEX-001 decision record; `tools/verify_evidence.py` · **Human**: REQUIRED — human owner makes all gate decisions
- [ ] T247 [SCN-C] HUMAN: Execute recorded SCN-C runs (option A, and one exception run with an engineer key requesting and a separate approver key deciding), export evidence, record CP-4 (feature freeze)
  - **Req**: SC-002, FR-GOV-008, FR-GOV-017 · **ADR**: ADR-016 · **Deps**: T246 (staging must serve R2), T244 · **Est**: 1.0 h · **Lane**: H
  - **TDD**: N/A — human decision · **Done**: EV-001..EV-004, EV-006, EV-007 for SCN-C; CP-4 recorded · **Verified by**: CEX-001 decision record; `tools/verify_evidence.py` · **Human**: REQUIRED — human owner (engineer key requests, separate approver key decides)

---

## Phase 12: Documentation, Release and Submission

- [ ] T248 [P] Write README.md (setup, architecture overview, testing approach, limitations, trade-offs, "How AI assistance was used and governed" incl. key custody), docs/architecture.md, docs/threat-model.md, docs/testing.md, docs/limitations.md (BL-01..BL-21, plan §16.4) and docs/change-control.md
  - **Req**: CST-003, CST-009, NFR-MNT-001, NFR-SEC-003, NFR-TST-001, CON IV, CST-008, FR-GOV-009 · **ADR**: ADR-001..ADR-019 · **Deps**: T241 · **Est**: 2.0 h · **Lane**: D
  - **TDD**: N/A — documentation · **Done**: Six README sections complete; every BL item and §16.4 limitation listed; every NFR-SEC-003 threat has a control or accepted risk; `satisfies:` front matter present · **Verified by**: T249 quickstart test and docs review; T203 `--check`
- [ ] T249 Implement the automated quickstart test, `orch release check` (live dependency scan, `build_matrix.py --check --release`, coverage, audit verify of evidence runs) and the PVT-001/002 demonstration measurement
  - **Req**: NFR-DOC-001, PVT-009, FR-GOV-010, FR-GOV-012, PVT-007, PVT-012, PVT-001, PVT-002, SC-009, CON XI; Plan §16.1 (C5) · **ADR**: ADR-009, ADR-018, ADR-011 · **Deps**: T247, T248 · **Est**: 2.0 h · **Lane**: D
  - **Paths**: `tests/e2e/test_quickstart.py`; `src/orchestrator/cli/release_check.py`; `tests/release/test_release_check.py`; `tools/perf/measure.py`; `docs/evidence/performance.md`; `docs/release-readiness.md`
  - **TDD**: TDD-8 for the release check; quickstart test is TDD-impractical (verifies docs against the finished system; first run recorded) · **Done**: 100% of quickstart commands executed against a fresh var/; report lists each CON XI condition with evidence or FAIL reason; p95 recorded as demonstration data · **Verified by**: tests/e2e/test_quickstart.py; tests/release/test_release_check.py
- [ ] T250 Generate docs/evidence/index.md from the export manifests and run index; write docs/engineering-summary.md and docs/evidence/metrics.md; record the docs-vs-behavior review in docs/release-readiness.md
  - **Req**: FR-ORC-026, SC-002, SC-003, SC-007, FR-OBS-006, FR-OBS-007, NFR-DOC-001, CON X; HD-CUT-001 #6 · **ADR**: ADR-011 · **Deps**: T249 · **Est**: 1.5 h · **Lane**: D
  - **TDD**: N/A — evidence assembly · **Done**: Every EV item per scenario linked with run ID and hashes; ADR rows cite modules and tests; metrics labeled 'demonstration'; 0 unresolved doc discrepancies or each listed as a FAIL reason · **Verified by**: T203 `--check --release`; T251 human decision
- [ ] T251 HUMAN: Time a fresh clone → setup → tests → three scenarios (PVT-009), record CP-5, mark the release evidence gates, sign docs/release-readiness.md, create and push `assessment-submission-v1.0`, confirm CI green
  - **Req**: PVT-009, NFR-RUN-001, SC-010, FR-GOV-011, Governance §6, CST-009, CON III · **ADR**: — · **Deps**: T250 · **Est**: 1.5 h · **Lane**: H
  - **TDD**: N/A — human decision · **Done**: Timing < 30 min or recorded as a FAIL reason; gates marked by the human; signed decision (truthful FAIL is acceptable); tag on remote with green CI · **Verified by**: CEX-001 decision record; `git ls-remote --tags origin assessment-submission-v1.0` · **Human**: REQUIRED — human owner only (outward-facing)

---

## Timebox and Scope Control

**Deadline**: 2026-10-16 15:30. **Total estimate**: ≈ 88 task-hours across 54 tasks (46 agent/tooling tasks incl. T002 and T201, and 8 human tasks; the T001 decision is already recorded).

### Critical path (longest dependency chain, estimated hours)

T201 (2.0) → T003 (0.5) → T202 (2.0) → T204 (2.0) → T206 (2.0) → T218 (2.0) → T222 (2.0) → T223 (2.0) → T234 (2.0) → T235 (2.0) → T236 (1.5) → T237 (2.0) → T238 (2.0) → T243 (2.0) → T245 (1.0) → T246 (1.0) → T247 (1.0) → T249 (2.0) → T250 (1.5) → T251 (1.5) = **≈ 34 h**

### Schedule feasibility (must be decided by the human owner)

**The critical path alone (≈ 34 h of sequential work) exceeds the wall-clock time left before 2026-10-16 15:30.** That holds even with perfect parallelism on every other lane. Lanes A (shortener), C (change sets) and D (tooling/docs) fit beside lane B only if they run as separate concurrent sessions, and the human must be available for T212, T217 and T245–T247. Per STOP-4/STOP-5, the human owner decides at CP-1 at the latest whether to move the deadline, accept a truthful partial FAIL at release, or approve further cuts (each further cut would remove an assessed capability).

| Checkpoint | Recorded in | Planned at (hours after T003) | Exit condition |
|------------|-------------|-------------------------------|----------------|
| CP-1 | T212 | ≈ H+11 | Baseline green and tagged |
| CP-2 | T217 | ≈ H+17 | All change sets locked and tagged |
| CP-3 | T245 | ≈ H+24.5 | Engine suites green; SCN-A recorded |
| CP-4 | T247 | ≈ H+26.5 | All scenarios recorded; feature freeze |
| CP-5 | T251 | ≈ H+31.5 | Release check executed; human decision |

**Stop conditions**: STOP-1 constitution violation or CRITICAL analysis finding; STOP-2 a requirement cannot be met as specified (e.g. PVT-003) — report with evidence, never weaken a test; STOP-3 evidence would require fabrication; STOP-4 checkpoint missed by > ½ day after reductions; STOP-5 end of timebox → freeze and report honestly.

### Removed false dependencies (CR-006 step 4)

| Old dependency | Now |
|----------------|-----|
| T110 → T109 (SCN-B authoring waited for the human SCN-A run) | T215 depends only on T214 (authoring chain) |
| T119 → T118 (SCN-C authoring waited for the human SCN-B run) | T216 depends only on T215 |
| T075 → T068 (requirement agents waited for resume) | T234 depends on T226, T223, T213 |
| T084 → T082 (replanning waited for the reporter agent) | T233 depends on T225, T220 |
| T063 → T062 (fault injector waited for CP-2) | T229 depends on T223 |

Remaining scenario-order dependencies are real: T246 needs staging at R1 (from T245) and T247 needs R2 (from T246).

### Parallel lanes

- **Lane A (shortener)**: T205, T207–T212.
- **Lane B (engine)**: T204, T206, T218–T230, T233–T238, T242, T243.
- **Lane C (change sets and SUT)**: T213–T216, T231, T232 — runs alongside lane B from T204 onward.
- **Lane D (tooling, observability, docs)**: T201–T203, T239–T241, T244, T248–T250.
- **Lane H (human)**: T001–T003, T212, T217, T245–T247, T251.

## Retired task mapping (CR-006 step 4)

| Retired IDs | Now in |
|-------------|--------|
| T004 | T201 |
| T005–T011, T013 | T202, T203 |
| T012, T127 | T203 (release mode in T249) |
| T014, T015, T017 | T204 |
| T018, T020, T044, T048 | T219 |
| T021 | T205 |
| T022, T042 | T206 |
| T023, T033, T035, T039 | T209 |
| T025, T026 | T207 |
| T027, T028, T030 | T208 |
| T029, T031, T032, T034, T038 | T210 |
| T036, T037 | T211 |
| T040, T041 | T212 |
| T043, T045 | T218 |
| T046 | T220 |
| T047, T083 | T221 |
| T065 | T222 |
| T049 | T223 |
| T024, T050, T051, T099, T152 | T224 |
| T057, T058, T059 | T225 |
| T052, T053, T054 | T226 |
| T055, T056 | T227 |
| T060 | T228 |
| T063, T064, T066, T067 | T229 |
| T068 | T230 |
| T069, T070, T072, T073 | T231 |
| T074, T153, T154 | T232 |
| T084 | T233 |
| T071 | T213 |
| T075 | T234 |
| T076, T077 | T235 |
| T078 | T236 |
| T079, T080 | T237 |
| T081, T082 | T238 |
| T091, T093, T094, T095 | T239 |
| T096, T097, T155 | T240 |
| T085, T089, T098, T100 | T241 |
| T086, T087, T088 | T242 |
| T101–T105 | T214 (lock in T217) |
| T110–T113 | T215 |
| T119, T120 | T216 |
| T114, T121 | T217 |
| T106–T108, T115–T117 | T243 |
| T122, T123, T126 | T244 |
| T109, T118, T124 | T245, T246, T247 |
| T061, T130–T135 | T248 |
| T128, T129, T136 | T249 |
| T137–T146 | T250 |
| T062, T090, T125 | CP rows in T217, T245, T247 |
| T147–T151 | T251 |
| T016, T019, T092 | Cut (HD-CUT-001; BL-15, BL-16) |

## Requirement Coverage

Not yet verified for this version. T203's `--check` and a re-run of `/speckit-analyze` (before T003) must confirm that every requirement ID in spec.md is referenced by at least one task.

## TDD Evidence Log

Append one line per red phase: `T### | test id | observed failure (first line) | date`. Required by CON IV; the traceability checker reads it.

| Task | Test | Observed failure | Date |
|------|------|------------------|------|
