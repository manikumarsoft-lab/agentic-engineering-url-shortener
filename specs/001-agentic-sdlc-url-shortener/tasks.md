---

description: "Task list for feature 001: Agentic Software Engineering System: URL Shortener"
---

# Tasks: Agentic Software Engineering System: URL Shortener

**Input**: Design documents from `specs/001-agentic-sdlc-url-shortener/` (spec.md incl. CR-001..CR-003, plan.md, research.md, data-model.md, contracts/, quickstart.md) and ADR-001..ADR-019 (accepted, Human Gate 4).

**Prerequisites**: plan.md (approved), spec.md (approved), ADRs accepted. **Task-plan approval**: _pending — recorded by T003 (human owner, after `/speckit-analyze`)._

**Tests**: Mandatory. The constitution (Principle IV) requires red-green-refactor TDD, so tests are written first and seen to fail before implementation.

**Status**: Generated 2026-10-15; regenerated 2026-10-15 after `/speckit-analyze` remediation (human decisions on C1–C4, H1–H2, M1–M6, L1–L4). **Nothing is implemented; no task is complete.**

**Stable IDs**: task IDs never change once assigned. Listing order is execution order, so some IDs appear out of numeric order (e.g. T035 before T033; T099 in Phase 4). Tasks added after the first generation start at T152.

## Lifecycle Gate Record

- **Checklist stage exit (C4)**: Checklist stage exit approved by Mani Kumar Vadugu, 2026-10-15. Reviewed: the 19-file checklist set structure and the 8 gaps it surfaced, all closed via CR-003. Item-level checklist verification is performed at the /speckit-implement gate (T001). No checklist item is marked by this record.
- **Constitution exception CEX-001** (Governance §2): for human-decision and checkpoint tasks, verification = a recorded human decision (approver, timestamp, artifact version) in the decision/audit log; compensating control = T127 traceability check confirms each such decision exists. Approved by Mani Kumar Vadugu, 2026-10-15; review condition: re-evaluated at `/speckit-converge`. Recorded in plan.md (Complexity Tracking).
- **Task-plan approval**: pending (T003).

## Format and Field Legend

Each task line is `- [ ] T### [P?] [Story?] Description with file path`, followed by its fields:

- **[P]**: parallelizable — touches no file shared with any concurrent task in its phase and has no unmet dependency (checked mechanically).
- **[Story]**: `US1`–`US5` (spec user stories), `SCN-A`/`SCN-B`/`SCN-C` (required scenarios, P1). Phases 0–2 and 12 carry no story label.
- **Obj** objective · **Req** requirement IDs · **Scn** scenario IDs · **ADR** references · **Paths** exact target paths · **Pre** prerequisites · **Deps** task dependencies · **Artifact** expected artifact · **TDD** obligation · **Validate** command or evidence · **Docs** documentation impact · **Trace** traceability update · **Risk** risk or guardrail · **Done** completion criteria · **Verified by** the test, check or recorded decision that verifies the task (constitution rule; CEX-001 for human decisions) · **Human** approval requirement.
- `HUMAN:` tasks are performed only by the human owner and are never marked complete by an agent.

### TDD-8 (the default TDD obligation)

1. Identify the acceptance criterion (from **Req**/**Done**). 2. Write the failing test. 3. Run it and confirm it fails for the expected reason; paste the failure line into the TDD Evidence Log below. 4. Implement the smallest compliant behavior. 5. Run the test and confirm it passes. 6. Refactor. 7. Run the regression suite (`uv run python tools/check.py`). 8. Update documentation and traceability (**Docs**, **Trace**).

Default **Trace**: Tests carry `@pytest.mark.req(<Req IDs>)`; new modules carry a `Satisfies:` docstring line; task ID in the commit message. Default **Human**: None beyond the human owner's commit review. Default **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4).

### Guardrails (apply to every task)

- Architecture-sensitive work is blocked until its ADR is accepted (all 19 accepted at Human Gate 4); a change to an accepted decision needs a CR and a superseding ADR first.
- Do not modify spec.md, plan.md, contracts or ADRs to suit implementation; use a CR (docs/change-control.md).
- Scenario capabilities (expiration, analytics, aliases, daily counts) are never added to the main working tree's `src/shortener/`; they exist only as change sets (CST-007).
- Evidence comes only from real execution; scripted, AI-backed or hand-edited output is never presented as scenario evidence (CON X).
- Release readiness (Phase 12 HUMAN sign-off) is blocked until T148 shows all mandatory validation executed.

---

## Phase 0: Lifecycle Gates, Timebox and Scope Control

**Purpose**: Close the remaining pre-implementation human gates and set up timebox and scope control for the 2–3 day assessment. No code.

- [ ] T001 HUMAN: Review the 19 requirements-quality checklists in specs/001-agentic-sdlc-url-shortener/checklists/ and record the outcome
  - **Obj**: Satisfy the `/speckit-implement` checklist gate by reviewer decision, not by agent marking · **Req**: CON I, CON III; Spec §CR-003 · **Scn**: — · **ADR**: —
  - **Paths**: `specs/001-agentic-sdlc-url-shortener/checklists/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: none · **Parallel**: no
  - **Artifact**: Reviewed checklists: items marked [x] by the human owner, or new CRs for unsatisfied items · **TDD**: N/A — human decision or action (no code) · **Validate**: `/speckit-implement` checklist table shows each file's status
  - **Docs**: None · **Trace**: default · **Risk**: Agents must not mark checklist items
  - **Done**: Every checklist item is either marked by the human owner or covered by a recorded CR/decision to proceed · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only
- [ ] T002 Run /speckit-analyze (read-only) over all artifacts; the human owner reviews the report and may save it as specs/001-agentic-sdlc-url-shortener/analysis.md
  - **Obj**: Cross-artifact consistency analysis before implementation (CON workflow: CRITICAL findings block) · **Req**: CON Development Workflow; Governance §1 · **Scn**: — · **ADR**: —
  - **Paths**: `specs/001-agentic-sdlc-url-shortener/analysis.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: none · **Parallel**: no
  - **Artifact**: Analysis report with severity-ranked findings (saved to analysis.md at the human owner's request on 2026-10-15) · **TDD**: N/A — analysis, no behavior · **Validate**: Report exists; count of CRITICAL findings stated
  - **Docs**: None · **Trace**: default · **Risk**: Do not fix upstream artifacts silently; changes go through CRs
  - **Done**: Report produced; CRITICAL findings listed for the human owner · **Verified by**: T003 human approval references the reviewed report version (CEX-001 decision record) · **Human**: Human owner decides on each CRITICAL finding
- [ ] T003 HUMAN: Approve the task plan specs/001-agentic-sdlc-url-shortener/tasks.md (task-plan approval gate, post-analyze)
  - **Obj**: Mandatory gate: task-plan approval before implementation · **Req**: CON Development Workflow (mandatory gates) · **Scn**: — · **ADR**: —
  - **Paths**: `specs/001-agentic-sdlc-url-shortener/tasks.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T001, T002 · **Parallel**: no
  - **Artifact**: Approval line (approver, date) in the tasks.md header · **TDD**: N/A — human decision or action (no code) · **Validate**: Approval recorded in tasks.md
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Approval recorded; no unresolved CRITICAL analysis finding · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only
- [ ] T004 Create the scope-control log docs/scope-control.md (must-have scope, deferred scope, day milestones, critical path, checkpoints, stop conditions, decision log)
  - **Obj**: Make the timebox and scope rules operational and auditable · **Req**: CST-005, CST-008, PD-010; Plan §14.1, §14.3, §14.4 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/scope-control.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T003 · **Parallel**: no
  - **Artifact**: docs/scope-control.md with: must-have list (Plan §14.1), backlog BL-01..BL-13, Day 1–3 milestones, critical path (from this file), CP-1..CP-5 decision table, STOP-1..STOP-5 · **TDD**: N/A — documentation · **Validate**: Review: every must-have and backlog ID from Plan §14.1 present
  - **Docs**: New docs/scope-control.md · **Trace**: default · **Risk**: Optional work must not displace mandatory validation (Plan §14.1 scope rule)
  - **Done**: Log committed; checkpoint table has empty decision rows for CP-1..CP-5 · **Verified by**: T127 traceability check (scope-control IDs resolve to Plan §14.1) and each CP decision record · **Human**: default

---

## Phase 1: Setup (Engineering Baseline)

**Purpose**: Project initialization, toolchain, repository hygiene and CI.

- [ ] T005 Create pyproject.toml and uv.lock (Python >=3.12,<3.13; FastAPI, Uvicorn, Pydantic v2, SQLAlchemy Core, Alembic, httpx, Typer, PyYAML, jsonschema; dev: pytest, Hypothesis, schemathesis, pytest-cov, mypy, ruff, pip-audit, detect-secrets, pip-licenses)
  - **Obj**: Pinned, reproducible toolchain · **Req**: NFR-RUN-001, CST-006, DEP-001 · **Scn**: — · **ADR**: ADR-001, ADR-002
  - **Paths**: `pyproject.toml`; `uv.lock`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T004 · **Parallel**: no
  - **Artifact**: pyproject.toml with console scripts `shortener`, `orch`; uv.lock · **TDD**: N/A — configuration · **Validate**: `uv sync --frozen && uv run python -c "import fastapi, sqlalchemy, typer"`
  - **Docs**: None · **Trace**: default · **Risk**: No dependency outside the approved list (T007)
  - **Done**: Fresh `uv sync --frozen` succeeds on the reference workstation · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T006 [P] Create .gitignore (var/, .venv/, caches, coverage) and .gitattributes with eol=lf for src/**, tests/**, changesets/** (incl. *.diff) and specs/**/contracts/**
  - **Obj**: Keep runtime data out of git; make patches immune to core.autocrlf=true · **Req**: CON V, CON X; Plan §14.2 slice 1 (CR-002) · **Scn**: — · **ADR**: ADR-006
  - **Paths**: `.gitignore`; `.gitattributes`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T004 · **Parallel**: yes
  - **Artifact**: .gitignore, .gitattributes · **TDD**: N/A — configuration · **Validate**: `git check-attr eol -- changesets/x/y/patch.diff` prints `eol: lf`; `git check-ignore var/x` matches
  - **Docs**: None · **Trace**: default · **Risk**: CRLF conversion would break `git apply` (ADR-006 risk)
  - **Done**: Both checks pass · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T007 [P] Create policy/approved-dependencies.yaml and policy/license-allowlist.yaml from the locked dependency set
  - **Obj**: Inputs for DEP-001 and LIC-001 · **Req**: DEP-001, LIC-001, FR-GOV-005 · **Scn**: — · **ADR**: ADR-009
  - **Paths**: `policy/approved-dependencies.yaml`; `policy/license-allowlist.yaml`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T005 · **Parallel**: yes
  - **Artifact**: Two YAML policy inputs · **TDD**: N/A — data · **Validate**: `uv run pip-licenses --format=json` licenses ⊆ allow-list (manual check now; automated in T056)
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Every package in uv.lock listed; license allow-list = MIT, BSD-2/3, Apache-2.0, PSF-2.0, ISC · **Verified by**: T056 DEP-001/LIC-001 tests consume these lists · **Human**: default
- [ ] T008 Create package skeleton src/common/, src/shortener/, src/orchestrator/ and the pytest `req` marker plugin in tests/plugins/req_marker.py with tests in tests/tooling/test_req_marker.py
  - **Obj**: Importable packages; requirement IDs recorded on every test and exported to JUnit properties · **Req**: FR-OBS-010, SC-007, CON X · **Scn**: — · **ADR**: ADR-004, ADR-018
  - **Paths**: `src/common/__init__.py`; `src/shortener/__init__.py`; `src/orchestrator/__init__.py`; `tests/conftest.py`; `tests/plugins/req_marker.py`; `tests/tooling/test_req_marker.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T005 · **Parallel**: no
  - **Artifact**: Packages + marker plugin · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/conftest.py tests/plugins/req_marker.py tests/tooling/test_req_marker.py -q`
  - **Docs**: docs/testing.md stub section 'Requirement tags' · **Trace**: default · **Risk**: —
  - **Done**: pytester-based tests prove `req` IDs appear in JUnit XML properties · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T009 Write the import-boundary test tests/architecture/test_import_boundaries.py (common/ imports no domain; shortener and orchestrator never import each other; api→domain→persistence direction)
  - **Obj**: Detect architecture drift automatically (D25) · **Req**: NFR-MNT-001, CON VII · **Scn**: — · **ADR**: ADR-004
  - **Paths**: `tests/architecture/test_import_boundaries.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T008 · **Parallel**: no
  - **Artifact**: AST-based boundary test · **TDD**: TDD-8 (red with a deliberately violating fixture module in tests/architecture/fixtures/) · **Validate**: `uv run pytest tests/architecture/test_import_boundaries.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: Boundary rules must match ADR-004 exactly
  - **Done**: Test fails on the violating fixture, passes on the real tree · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T010 Create tools/check.py (ruff, mypy --strict, pytest with coverage fail_under=85 over shortener.domain, orchestrator.engine, orchestrator.policy, orchestrator.observability)
  - **Obj**: One command for local and CI validation · **Req**: NFR-TST-001, PVT-007 · **Scn**: — · **ADR**: ADR-018
  - **Paths**: `tools/check.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T009 · **Parallel**: no
  - **Artifact**: tools/check.py · **TDD**: N/A — tooling wrapper (exercised by every later task) · **Validate**: `uv run python tools/check.py`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Exits 0 on the skeleton; non-zero on an injected lint error · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T011 [P] Create the detect-secrets baseline .secrets.baseline
  - **Obj**: Secret-scan baseline for SEC-002 and pre-push hygiene · **Req**: NFR-SEC-002, SEC-002 · **Scn**: — · **ADR**: ADR-009
  - **Paths**: `.secrets.baseline`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T005 · **Parallel**: yes
  - **Artifact**: .secrets.baseline · **TDD**: N/A — configuration · **Validate**: `uv run detect-secrets scan --baseline .secrets.baseline` reports no new secrets
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Baseline committed with zero true findings · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T012 Create GitHub Actions workflow .github/workflows/ci.yml running `uv sync --frozen` and `uv run python tools/check.py` on push and pull_request (ubuntu-latest and windows-latest, Python 3.12)
  - **Obj**: CI that runs the test suite (CST-009) · **Req**: CST-009, NFR-TST-001 · **Scn**: — · **ADR**: ADR-018
  - **Paths**: `.github/workflows/ci.yml`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T010, T011 · **Parallel**: no
  - **Artifact**: CI workflow · **TDD**: N/A — CI configuration · **Validate**: Human pushes the branch; the CI run is green (link recorded in the TDD Evidence Log)
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Green CI run on both OS images · **Verified by**: The CI run itself executes tools/check.py; T151 confirms green CI on the tagged commit · **Human**: Human owner pushes to GitHub (outward-facing action)
- [ ] T013 [P] Create README.md skeleton with section headings: Setup, Architecture overview, Testing approach, Limitations, Trade-offs, How AI assistance was used and governed
  - **Obj**: Fix the required deliverable structure early · **Req**: CST-003, CST-009 · **Scn**: — · **ADR**: —
  - **Paths**: `README.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T008 · **Parallel**: yes
  - **Artifact**: README.md with headings and TODO markers · **TDD**: N/A — documentation · **Validate**: Review: all six headings present
  - **Docs**: README.md (filled in T134) · **Trace**: default · **Risk**: —
  - **Done**: Headings present · **Verified by**: T128 quickstart test (setup commands) and T146 docs review · **Human**: default

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure, persistence abstractions, contract tooling and walking skeletons. No user-story work starts before this phase ends.

- [ ] T014 [P] Implement injectable Clock (system, virtual) in src/common/clock.py and prefixed ULID-style IdGenerator in src/common/ids.py; tests in tests/common/test_clock.py and tests/common/test_ids.py
  - **Obj**: Deterministic time and IDs for tests and NFR-DET-001 · **Req**: NFR-DET-001, FR-ORC-001 · **Scn**: — · **ADR**: ADR-015
  - **Paths**: `src/common/clock.py`; `src/common/ids.py`; `tests/common/test_clock.py`; `tests/common/test_ids.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T010 · **Parallel**: yes
  - **Artifact**: Clock and IdGenerator · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/common/test_clock.py tests/common/test_ids.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: IDs match `^(run|nod|gat|art|dec|evt|exc|eps|pev)_[0-9A-HJKMNP-TV-Z]{26}$`; virtual clock advances deterministically · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T015 [P] Implement JSON log formatter and redaction filter in src/common/logging.py; tests in tests/common/test_logging.py
  - **Obj**: Structured logs that never contain secrets · **Req**: NFR-SEC-002, NFR-SEC-004, FR-OBS-009 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `src/common/logging.py`; `tests/common/test_logging.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T010 · **Parallel**: yes
  - **Artifact**: Logging module · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/common/test_logging.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Keys authorization/x-api-key/secret/password/token and pattern `sk_[A-Za-z0-9]+\.[A-Za-z0-9_-]+` are redacted in tests · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T016 [P] Implement W3C traceparent helpers and run-ID→trace-ID mapping in src/common/tracecontext.py; tests in tests/common/test_tracecontext.py
  - **Obj**: Correlation across services · **Req**: FR-OBS-001, FR-OBS-009 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `src/common/tracecontext.py`; `tests/common/test_tracecontext.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T010 · **Parallel**: yes
  - **Artifact**: Trace context module · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/common/test_tracecontext.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Round-trip parse/format; trace ID is the 128-bit run ID in hex · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T017 Implement API key format `sk_<key_id>.<secret>`, SHA-256-at-rest key store reader and constant-time verification in src/common/apikeys.py, plus `orch keys init` in src/orchestrator/cli/keys.py; tests in tests/common/test_apikeys.py
  - **Obj**: Role-mapped keys for both services · **Req**: FR-SHR-019, FR-GOV-003, FR-GOV-013, NFR-SEC-004, HD-003 · **Scn**: — · **ADR**: ADR-010
  - **Paths**: `src/common/apikeys.py`; `src/orchestrator/cli/keys.py`; `tests/common/test_apikeys.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T015 · **Parallel**: no
  - **Artifact**: Key store and CLI writing var/secrets/api-keys.json · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/common/test_apikeys.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: Key file must be under gitignored var/secrets/
  - **Done**: Secrets printed once, stored hashed; roles consumer/engineer/approver/release-owner/agent resolved; wrong secret rejected in constant time · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T018 [P] Write contract-document tests tests/contract/test_contract_documents.py: both OpenAPI files load (schemathesis), all JSON Schemas pass check_schema, all contracts/examples validate
  - **Obj**: Executable validation of the committed contracts (API/schema deliverable) · **Req**: CST-003; Plan §2.2 · **Scn**: — · **ADR**: ADR-007
  - **Paths**: `tests/contract/test_contract_documents.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T010 · **Parallel**: yes
  - **Artifact**: Contract-document test suite · **TDD**: TDD-8 (red with a deliberately invalid example in tests/contract/fixtures/) · **Validate**: `uv run pytest tests/contract/test_contract_documents.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Suite green on the committed contracts (shortener 1.0.0, orchestrator 2.1.0, graph 2.1.0, policy 1.0.0) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T019 Implement the OpenAPI drift normalizer tests/contract_support/openapi_drift.py with unit tests tests/contract_support/test_openapi_drift.py
  - **Obj**: App-generated OpenAPI must equal the committed contract (contract-first) · **Req**: Plan §2.2 · **Scn**: — · **ADR**: ADR-007
  - **Paths**: `tests/contract_support/openapi_drift.py`; `tests/contract_support/test_openapi_drift.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T018 · **Parallel**: no
  - **Artifact**: Normalizer · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/contract_support/openapi_drift.py tests/contract_support/test_openapi_drift.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: If normalization exceeds 2 h, fall back to structural comparison and record the limitation (ADR-007)
  - **Done**: Detects an added field, a removed path and a status-code change; ignores ordering and FastAPI cosmetic fields · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T020 Create meta-schemas src/orchestrator/definitions/schemas/workflow-graph.meta.json and policy-set.meta.json with tests tests/orchestrator/contract/test_definitions.py (schema, cross-references, acyclicity, CON II fields on every node)
  - **Obj**: Graph and policy definitions refuse to load when invalid · **Req**: FR-ORC-005, FR-GOV-005, CON II · **Scn**: — · **ADR**: ADR-005, ADR-009
  - **Paths**: `src/orchestrator/definitions/schemas/workflow-graph.meta.json`; `src/orchestrator/definitions/schemas/policy-set.meta.json`; `tests/orchestrator/contract/test_definitions.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T018 · **Parallel**: no
  - **Artifact**: Meta-schemas + tests · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/contract/test_definitions.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: workflow-graph.v2.yaml 2.1.0 and policy-set.v1.yaml 1.0.0 validate; fixtures with a cycle, unknown check or missing node field are rejected · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T021 Implement shortener persistence abstraction: engine factory (WAL, busy_timeout=5000, BEGIN IMMEDIATE) in src/shortener/persistence/db.py, repository protocols in src/shortener/persistence/repositories.py, Alembic env + revision 0001_baseline (links without expires_at/code_origin; idempotency_records) in src/shortener/persistence/alembic/; tests in tests/shortener/persistence/test_migrations.py
  - **Obj**: Replaceable persistence for the shortener · **Req**: FR-SHR-005, FR-SHR-013, NFR-SCL-002 · **Scn**: — · **ADR**: ADR-002, ADR-007
  - **Paths**: `src/shortener/persistence/db.py`; `src/shortener/persistence/repositories.py`; `src/shortener/persistence/alembic/`; `tests/shortener/persistence/test_migrations.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T014 · **Parallel**: no
  - **Artifact**: Persistence layer + baseline migration · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/persistence/test_migrations.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Upgrade from empty succeeds; `links.code` is PK with pattern-check `^[A-Za-z0-9]{4,10}$`; `destination_url` ≤ 2,048 · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T022 Implement orchestrator persistence: db factory in src/orchestrator/persistence/db.py, Alembic revision 0001_baseline with all data-model §1.2 tables and BEFORE UPDATE/DELETE triggers on audit_events and policy_evaluations (plain DDL, never batch mode); tests in tests/orchestrator/persistence/test_migrations.py
  - **Obj**: Persistent, recoverable workflow state with append-only audit tables · **Req**: FR-ORC-011, FR-OBS-004, FR-ORC-028 · **Scn**: — · **ADR**: ADR-002, ADR-008, ADR-015
  - **Paths**: `src/orchestrator/persistence/db.py`; `src/orchestrator/persistence/alembic/`; `tests/orchestrator/persistence/test_migrations.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T014 · **Parallel**: no
  - **Artifact**: Orchestrator schema · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/persistence/test_migrations.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: CR-002: batch mode prohibited for append-only tables
  - **Done**: UPDATE/DELETE on audit_events raise 'append-only'; triggers present after upgrade; unique (run_id, seq) and unique transition_key · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T023 Walking skeleton (shortener): minimal POST /api/v1/links and GET /{code} → 302 in src/shortener/app.py; integration test with a uvicorn subprocess in tests/shortener/integration/test_walking_skeleton.py
  - **Obj**: Prove the end-to-end slice API → domain → SQLite runs · **Req**: FR-SHR-001, FR-SHR-007 · **Scn**: — · **ADR**: ADR-004
  - **Paths**: `src/shortener/app.py`; `tests/shortener/integration/test_walking_skeleton.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T021, T015 · **Parallel**: no
  - **Artifact**: Running skeleton · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/integration/test_walking_skeleton.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Create then resolve returns 302 to the destination via a real process · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T024 Walking skeleton (orchestrator): POST /api/v1/runs persists a run with a 2-node fixture graph and one RUN_CREATED audit event; `orch run show` prints it; src/orchestrator/app.py, src/orchestrator/cli/main.py; test tests/orchestrator/integration/test_walking_skeleton.py
  - **Obj**: Prove the control-plane slice runs end to end · **Req**: FR-ORC-001, FR-ORC-011 · **Scn**: — · **ADR**: ADR-003, ADR-004
  - **Paths**: `src/orchestrator/app.py`; `src/orchestrator/cli/main.py`; `tests/orchestrator/integration/test_walking_skeleton.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T022, T020, T017 · **Parallel**: no
  - **Artifact**: Running skeleton · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/integration/test_walking_skeleton.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Run row and audit event persisted; process restart shows the same run · **Verified by**: Own tests/command (see Validate) · **Human**: default

---

## Phase 3: User Story 1 — API consumer shortens and resolves links (P1) 🎯 MVP

**Purpose**: Baseline (brownfield) shortener built directly under TDD (CST-007).

**Goal**: Create, validate and resolve short links with idempotency, rate limiting, auth, health and safe failure behavior.

**Independent Test**: Exercise create → resolve → unknown → invalid → persistence-down against a running service with no orchestration (US-1 AC1, AC4, AC5).

- [ ] T035 [US1] Write shortener contract tests: drift vs contracts/shortener-api.openapi.yaml 1.0.0 and schemathesis in tests/shortener/contract/test_openapi_drift.py and tests/shortener/contract/test_schemathesis.py
  - **Obj**: Executable contract conformance (API/schema deliverable) · **Req**: FR-SHR-001..019 (API surface), NFR-TST-001 · **Scn**: — · **ADR**: ADR-007
  - **Paths**: `tests/shortener/contract/test_openapi_drift.py`; `tests/shortener/contract/test_schemathesis.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T023, T019 · **Parallel**: no
  - **Artifact**: Contract suites per operation group (links, redirect, health) · **TDD**: RED first (C3): drift and schemathesis tests per operation group; groups not yet implemented carry `xfail(strict=True, reason='implemented by T033')` so CI stays green while the red state is recorded; T033 removes the markers (green) · **Validate**: `uv run pytest tests/shortener/contract/test_openapi_drift.py tests/shortener/contract/test_schemathesis.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Red run recorded in the TDD Evidence Log; every operation group of contract 1.0.0 has a drift and a schemathesis test · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T025 [P] [US1] Implement URL validation and normalization in src/shortener/domain/validation.py with table + Hypothesis tests in tests/shortener/unit/test_validation.py
  - **Obj**: Reject invalid destinations with machine-readable reasons · **Req**: FR-SHR-002, FR-SHR-003, FR-SHR-004, NFR-SEC-001, PD-001, PVT-010, A-002 · **Scn**: — · **ADR**: ADR-014
  - **Paths**: `src/shortener/domain/validation.py`; `tests/shortener/unit/test_validation.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T023 · **Parallel**: yes
  - **Artifact**: Validation module · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/unit/test_validation.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: DNS names resolving to internal addresses are an accepted residual risk (PD-001); do not resolve DNS
  - **Done**: Codes invalid_request, malformed_url, scheme_not_allowed (only http/https), url_too_long (> 2,048), credentials_in_url, invalid_characters, self_referential_url, private_address_not_allowed (loopback, private, link-local incl. 169.254.169.254, unique-local, unspecified, multicast IP literals and `localhost`) each covered; IDNA lowercase normalization · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T026 [P] [US1] Implement the short-code generator and validator in src/shortener/domain/codes.py with property tests in tests/shortener/unit/test_codes.py
  - **Obj**: Unpredictable, unique-friendly codes · **Req**: FR-SHR-006, A-003 · **Scn**: — · **ADR**: ADR-014
  - **Paths**: `src/shortener/domain/codes.py`; `tests/shortener/unit/test_codes.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T023 · **Parallel**: yes
  - **Artifact**: Generator · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/unit/test_codes.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: CSPRNG base62, length 7; validator `^[A-Za-z0-9]{4,10}$`; consecutive codes show no successor relation in a statistical test; RNG injectable · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T027 [US1] Implement the create-link use case in src/shortener/domain/links.py and repository in src/shortener/persistence/links_repo.py; tests in tests/shortener/unit/test_links.py
  - **Obj**: Create unique links atomically · **Req**: FR-SHR-001, FR-SHR-005, A-004 · **Scn**: — · **ADR**: ADR-002, ADR-014
  - **Paths**: `src/shortener/domain/links.py`; `src/shortener/persistence/links_repo.py`; `tests/shortener/unit/test_links.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T025, T026 · **Parallel**: no
  - **Artifact**: Use case + repository · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/unit/test_links.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Unique via PK; up to 5 regenerations on collision then `code_generation_exhausted` with no partial record; same destination twice yields two links (A-004) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T028 [US1] Implement the resolve use case in src/shortener/domain/resolve.py; tests in tests/shortener/unit/test_resolve.py
  - **Obj**: Resolve outcomes without unsafe redirects · **Req**: FR-SHR-007, FR-SHR-015 · **Scn**: — · **ADR**: ADR-002
  - **Paths**: `src/shortener/domain/resolve.py`; `tests/shortener/unit/test_resolve.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T027 · **Parallel**: no
  - **Artifact**: Resolver · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/unit/test_resolve.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Outcomes redirect / not_found / unavailable; never redirects when persistence state cannot be verified · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T029 [P] [US1] Implement API-key auth dependency in src/shortener/api/auth.py; tests in tests/shortener/security/test_auth.py
  - **Obj**: Protected creation; public redirect · **Req**: FR-SHR-019, NFR-SEC-004, A-001, HD-003 · **Scn**: — · **ADR**: ADR-010
  - **Paths**: `src/shortener/api/auth.py`; `tests/shortener/security/test_auth.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T023 · **Parallel**: yes
  - **Artifact**: Auth dependency · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/security/test_auth.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Missing/invalid key → 401, agent or non-permitted role → 403, no existence hints; key never logged or echoed · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T030 [US1] Implement idempotency handling in src/shortener/api/idempotency.py and src/shortener/persistence/idempotency_repo.py; tests in tests/shortener/unit/test_idempotency.py
  - **Obj**: At-most-once creation per idempotency key · **Req**: FR-SHR-013 · **Scn**: — · **ADR**: ADR-002
  - **Paths**: `src/shortener/api/idempotency.py`; `src/shortener/persistence/idempotency_repo.py`; `tests/shortener/unit/test_idempotency.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T027 · **Parallel**: no
  - **Artifact**: Idempotency layer · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/unit/test_idempotency.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Key `^[A-Za-z0-9_-]{1,128}$`; same key + same payload → 200 with `Idempotent-Replayed: true`; different payload → 409 idempotency_conflict; records expire after 24 h · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T031 [US1] Implement the per-key token bucket in src/shortener/api/ratelimit.py; tests in tests/shortener/unit/test_ratelimit.py
  - **Obj**: Creation abuse control · **Req**: FR-SHR-017, PVT-011, A-015 · **Scn**: — · **ADR**: ADR-010
  - **Paths**: `src/shortener/api/ratelimit.py`; `tests/shortener/unit/test_ratelimit.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T029 · **Parallel**: no
  - **Artifact**: Rate limiter · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/unit/test_ratelimit.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: Single-instance only (NFR-SCL-002); redirect volume is an accepted risk (NFR-SEC-003, BL-13)
  - **Done**: 60 requests/min per key_id; 61st → 429 rate_limited with Retry-After; virtual clock refill · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T032 [P] [US1] Implement problem+json error mapping in src/shortener/api/problems.py; tests in tests/shortener/security/test_error_leakage.py
  - **Obj**: Safe, machine-readable errors · **Req**: FR-SHR-018, FR-SHR-002 · **Scn**: — · **ADR**: ADR-007
  - **Paths**: `src/shortener/api/problems.py`; `tests/shortener/security/test_error_leakage.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T023 · **Parallel**: yes
  - **Artifact**: Error mapper · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/security/test_error_leakage.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Bodies match problem.schema.json; no stack traces, SQL, file paths, secrets or persistence identifiers under injected faults · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T033 [US1] Wire routers src/shortener/api/links.py, src/shortener/api/redirect.py, src/shortener/api/health.py and secure-default config src/shortener/config.py; tests in tests/shortener/integration/test_api.py
  - **Obj**: HTTP surface per contract 1.0.0 · **Req**: FR-SHR-001, FR-SHR-007, FR-SHR-016, SC-001, PD-002 · **Scn**: — · **ADR**: ADR-004, ADR-007
  - **Paths**: `src/shortener/api/links.py`; `src/shortener/api/redirect.py`; `src/shortener/api/health.py`; `src/shortener/config.py`; `src/shortener/app.py`; `tests/shortener/integration/test_api.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T028, T030, T031, T032, T029, T035 · **Parallel**: no
  - **Artifact**: Complete baseline API · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/integration/test_api.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Redirect 302 with `Cache-Control: no-store`, `Referrer-Policy: no-referrer`; /health/live vs /health/ready (DB ping); binds 127.0.0.1; docs UI disabled in staging profile; T035 xfail markers removed and contract suites green · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T034 [US1] Add request logging and correlation middleware in src/shortener/telemetry/middleware.py; tests in tests/shortener/unit/test_telemetry.py
  - **Obj**: Correlated, PII-free operational logs · **Req**: FR-OBS-009, FR-OBS-001 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `src/shortener/telemetry/middleware.py`; `tests/shortener/unit/test_telemetry.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T033, T016 · **Parallel**: no
  - **Artifact**: Middleware · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/unit/test_telemetry.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Logs carry correlation/trace ID from traceparent; no IP, user agent or key secret logged · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T036 [P] [US1] Write persistence-failure integration tests in tests/shortener/integration/test_persistence_failure.py
  - **Obj**: Explicit retriable failure, never a stale redirect · **Req**: FR-SHR-015, FR-SHR-016 · **Scn**: — · **ADR**: ADR-002
  - **Paths**: `tests/shortener/integration/test_persistence_failure.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T033 · **Parallel**: yes
  - **Artifact**: Failure tests · **TDD**: TDD impractical because failure behavior spans the DB driver, repositories and HTTP layer, which only exist together after T033; the units were test-first in T027/T028. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/shortener/integration/test_persistence_failure.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: DB unavailable/locked: create → 503 persistence_unavailable with Retry-After, no partial record; redirect → 503; /health/ready → 503 · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T037 [P] [US1] Write the PVT-003 concurrency test in tests/shortener/concurrency/test_pvt003.py
  - **Obj**: Uniqueness under contention · **Req**: PVT-003, NFR-SCL-001, FR-SHR-014, FR-SHR-005 · **Scn**: — · **ADR**: ADR-002, ADR-014
  - **Paths**: `tests/shortener/concurrency/test_pvt003.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T033 · **Parallel**: yes
  - **Artifact**: Concurrency test · **TDD**: TDD impractical because it needs the full HTTP stack and real SQLite write contention, which cannot exist before T033; uniqueness logic was test-first in T027. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/shortener/concurrency/test_pvt003.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: STOP-2 if SQLite cannot meet PVT-003: report with evidence, do not weaken the test
  - **Done**: 1,000 concurrent creations → 1,000 distinct codes, zero collisions or lost writes · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T038 [US1] Write the shortener security suite in tests/shortener/security/test_security_suite.py (scheme, credentials, self/private host, auth matrix, log scan for secrets)
  - **Obj**: Negative security coverage · **Req**: NFR-SEC-001, NFR-SEC-002, NFR-SEC-004, FR-SHR-003, FR-SHR-004 · **Scn**: — · **ADR**: ADR-010
  - **Paths**: `tests/shortener/security/test_security_suite.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T034 · **Parallel**: no
  - **Artifact**: Security suite · **TDD**: TDD impractical because it is an end-to-end negative matrix over the assembled API; each rule was test-first in T025, T029, T032 and T034. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/shortener/security/test_security_suite.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: 100% of negative cases rejected; captured logs contain no key secret pattern · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T039 [P] [US1] Implement `shortener serve` entry point in src/shortener/__main__.py (port, db path, profile dev|staging|workspace)
  - **Obj**: Launchable instances for dev, staging and isolated copies · **Req**: NFR-RUN-001, FR-ORC-032, FR-ORC-040 · **Scn**: — · **ADR**: ADR-004
  - **Paths**: `src/shortener/__main__.py`; `tests/shortener/integration/test_cli.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T033 · **Parallel**: yes
  - **Artifact**: CLI · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/shortener/integration/test_cli.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Instance starts on a given port with its own DB file; quickstart §3 commands work · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T040 [US1] HUMAN: Review the baseline and create the annotated tag `shortener-baseline-v1` (R0 source; PD-009)
  - **Obj**: Pin the brownfield baseline · **Req**: PD-009, CST-007, HD-002 · **Scn**: — · **ADR**: ADR-006
  - **Paths**: (git tag) shortener-baseline-v1
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T035, T036, T037, T038, T039 · **Parallel**: no
  - **Artifact**: Annotated tag · **TDD**: N/A — human decision or action (no code) · **Validate**: `git tag -n shortener-baseline-v1` shows the annotation; `tools/check.py` green at that commit
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Tag exists on the reviewed commit · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only
- [ ] T041 [US1] HUMAN: Checkpoint CP-1 decision in docs/scope-control.md (continue / apply reductions / stop)
  - **Obj**: Timebox checkpoint · **Req**: CST-005; Plan §14.3 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/scope-control.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T040 · **Parallel**: no
  - **Artifact**: CP-1 row filled · **TDD**: N/A — human decision or action (no code) · **Validate**: Decision row present with date and rationale
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Decision recorded · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only

**Checkpoint**: CP-1: baseline green, contract drift-free, tag `shortener-baseline-v1` created by the human owner.

---

## Phase 4: User Story 2 (part 1) — Orchestration domain and engine core (P1)

**Purpose**: Explicit dependency graph, state machines, transitions, lineage, permissions and the superstep scheduler.

**Goal**: A run is created with a unique ID, its graph instance is inspectable, independent stages run concurrently and joins wait.

**Independent Test**: Submit a fixture requirement with stub agents; observe a fork/join, a conditional skip and full state history (US-2 AC1–AC4).

- [ ] T042 [US2] Implement the append-only audit store and hash chain in src/orchestrator/audit/store.py and src/orchestrator/audit/hashchain.py; tests in tests/orchestrator/observability/test_audit_store.py
  - **Obj**: Tamper-evident audit written in the same transaction as state · **Req**: FR-OBS-001, FR-OBS-002, FR-OBS-003, FR-OBS-004, NFR-AUD-001 · **Scn**: — · **ADR**: ADR-008
  - **Paths**: `src/orchestrator/audit/store.py`; `src/orchestrator/audit/hashchain.py`; `tests/orchestrator/observability/test_audit_store.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T022, T016 · **Parallel**: no
  - **Artifact**: Audit store · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/observability/test_audit_store.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Every appended event validates against audit-event.schema.json; gapless per-run seq; chain verification detects an out-of-band edit · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T043 [P] [US2] Implement run/node/gate state tables in src/orchestrator/engine/state.py with parametrized allowed/prohibited transition tests in tests/orchestrator/state/test_state_tables.py
  - **Obj**: Explicit state machines (data-model §2) · **Req**: FR-ORC-005, FR-ORC-008, FR-ORC-023, CON II · **Scn**: — · **ADR**: ADR-003, ADR-015
  - **Paths**: `src/orchestrator/engine/state.py`; `tests/orchestrator/state/test_state_tables.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T024 · **Parallel**: yes
  - **Artifact**: State tables · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/state/test_state_tables.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Every listed transition allowed; every other pair raises IllegalTransition; terminal states have no exits; G-RELEASE has no REJECTED_REWORK · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T044 [P] [US2] Implement graph loading, predicate registry, instance building, ready-set, downstream closure and dependent-path computation in src/orchestrator/engine/graph.py; tests in tests/orchestrator/state/test_graph.py
  - **Obj**: Execution governed by the versioned graph contract · **Req**: FR-ORC-005, FR-ORC-006, FR-ORC-007, FR-ORC-022, FR-ORC-037, FR-ORC-038 · **Scn**: — · **ADR**: ADR-005, ADR-017
  - **Paths**: `src/orchestrator/engine/graph.py`; `tests/orchestrator/state/test_graph.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T020 · **Parallel**: yes
  - **Artifact**: Graph module · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/state/test_graph.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: workflow-graph.v2.yaml 2.1.0 instantiates 24 nodes; dependent path = all nodes downstream up to and including the next sync point (Spec §Glossary); stale closure = edges ∪ recorded inputs (ADR-017) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T045 [US2] Implement the transition helper (one DB transaction: conditional state update + audit append + unique transition_key) in src/orchestrator/engine/transitions.py; tests in tests/orchestrator/state/test_transitions.py
  - **Obj**: Atomic, idempotent transitions · **Req**: FR-ORC-011, FR-ORC-028, FR-OBS-004 · **Scn**: — · **ADR**: ADR-015, ADR-008
  - **Paths**: `src/orchestrator/engine/transitions.py`; `tests/orchestrator/state/test_transitions.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T043, T042 · **Parallel**: no
  - **Artifact**: Transition helper · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/state/test_transitions.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Duplicate transition_key applied once; competing claim on row_version loses cleanly; a crash between update and append leaves neither · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T046 [US2] Implement versioned artifacts, provenance and decision lineage in src/orchestrator/engine/artifacts.py; tests in tests/orchestrator/unit/test_artifacts.py
  - **Obj**: Context and decision lineage · **Req**: FR-ORC-012, FR-ORC-013, FR-ORC-034 · **Scn**: — · **ADR**: ADR-015
  - **Paths**: `src/orchestrator/engine/artifacts.py`; `tests/orchestrator/unit/test_artifacts.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T045 · **Parallel**: no
  - **Artifact**: Artifact store · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/unit/test_artifacts.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Immutable versions with content hash, producing node/attempt, actor, agent mode, input_versions; status current/stale/superseded/rolled_back; decisions link bound and affected versions · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T047 [US2] Implement the Agent protocol, StageContext capabilities and permission guard in src/orchestrator/agents/base.py, src/orchestrator/agents/capabilities.py, src/orchestrator/security/permissions.py; tests in tests/orchestrator/security/test_permissions.py
  - **Obj**: Controlled autonomy · **Req**: FR-ORC-025, FR-ORC-027, NFR-AUT-001 · **Scn**: — · **ADR**: ADR-010, ADR-003
  - **Paths**: `src/orchestrator/agents/base.py`; `src/orchestrator/agents/capabilities.py`; `src/orchestrator/security/permissions.py`; `tests/orchestrator/security/test_permissions.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T044, T045 · **Parallel**: no
  - **Artifact**: Agent framework · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/security/test_permissions.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Agents receive only declared capabilities; out-of-permission call → PERMISSION_REFUSED audited; loader rejects any role granted gate.decide, exception.approve, run.resume, run.abort, audit.modify, repo.write or keys.issue · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T048 [US2] Implement entry/exit criteria and conditional skip evaluation in src/orchestrator/engine/criteria.py; tests in tests/orchestrator/state/test_criteria.py
  - **Obj**: Stages start only when entry criteria hold; skips are explained · **Req**: FR-ORC-007, FR-ORC-008, SCN-A-AC1 · **Scn**: — · **ADR**: ADR-005
  - **Paths**: `src/orchestrator/engine/criteria.py`; `tests/orchestrator/state/test_criteria.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T044, T045 · **Parallel**: no
  - **Artifact**: Criteria module · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/state/test_criteria.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Unmet entry → BLOCKED with NODE_ENTRY_REFUSED and reason; false condition → SKIPPED with recorded skip reason · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T049 [US2] Implement the deterministic superstep scheduler with timers and stall detection in src/orchestrator/engine/scheduler.py; tests in tests/orchestrator/state/test_scheduler.py
  - **Obj**: Real parallelism with reproducible commit order · **Req**: FR-ORC-006, FR-ORC-037, FR-ORC-038, FR-ORC-039, NFR-DET-001, PD-004 · **Scn**: — · **ADR**: ADR-003
  - **Paths**: `src/orchestrator/engine/scheduler.py`; `tests/orchestrator/state/test_scheduler.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T047, T048, T046 · **Parallel**: no
  - **Artifact**: Scheduler · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/state/test_scheduler.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Fixture graph: F1 branches overlap in time; commit order is node-ID order; sync node releases only when all predecessors succeeded; stall (no READY, no timer, no open gate) → SAFE_STOPPED scheduler_stalled · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T099 [US2] Write orchestrator contract tests: drift vs contracts/orchestrator-api.openapi.yaml 2.1.0, schemathesis, and schema validation of emitted documents in tests/orchestrator/contract/test_openapi_drift.py and tests/orchestrator/contract/test_schemathesis.py
  - **Obj**: Executable orchestrator contract conformance (API/schema deliverable) · **Req**: FR-ORC-024, FR-GOV-003; Plan §2.2 · **Scn**: — · **ADR**: ADR-007
  - **Paths**: `tests/orchestrator/contract/test_openapi_drift.py`; `tests/orchestrator/contract/test_schemathesis.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T024, T019 · **Parallel**: no
  - **Artifact**: Contract suites per operation group (runs, gates, exceptions, resume/abort, audit, trace, metrics, evidence) plus emitted-document schema tests · **TDD**: RED first (C3): one drift + schemathesis test per operation group, each marked `xfail(strict=True)` naming its implementing task (T050, T059, T060, T068, T091, T096, T095, T097); each implementing task removes its marker (green) · **Validate**: `uv run pytest tests/orchestrator/contract/test_openapi_drift.py tests/orchestrator/contract/test_schemathesis.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Red run recorded; every operation of contract 2.1.0 and every JSON Schema has a test; all markers removed by end of Phase 7 · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T050 [US2] Implement the run service and run API (create with Idempotency-Key, get, list, graph, artifacts, timeline) in src/orchestrator/engine/runs.py and src/orchestrator/api/runs.py; tests in tests/orchestrator/api/test_runs_api.py
  - **Obj**: Inspectable runs · **Req**: FR-ORC-001, FR-ORC-024, FR-ORC-029, FR-ORC-031 · **Scn**: — · **ADR**: ADR-015
  - **Paths**: `src/orchestrator/engine/runs.py`; `src/orchestrator/api/runs.py`; `tests/orchestrator/api/test_runs_api.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T049, T099 · **Parallel**: no
  - **Artifact**: Run API · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/api/test_runs_api.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Responses validate against workflow-state.schema.json; run pins graph 2.1.0 and policy-set version; labels always include `demonstration`; agent_mode recorded; removes its T099 xfail marker (contract group green) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T152 [US2] Implement `orch serve` and `orch run submit|show|watch|timeline` in src/orchestrator/cli/main.py and src/orchestrator/cli/runs.py; tests in tests/orchestrator/cli/test_run_cli.py
  - **Obj**: CLI for starting the orchestrator and driving runs (quickstart §4–§6) · **Req**: FR-ORC-001, FR-ORC-024, NFR-DOC-001 · **Scn**: — · **ADR**: ADR-004
  - **Paths**: `src/orchestrator/cli/main.py`; `src/orchestrator/cli/runs.py`; `tests/orchestrator/cli/test_run_cli.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T050 · **Parallel**: no
  - **Artifact**: Run CLI · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/cli/test_run_cli.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: `orch serve --port` starts the API on 127.0.0.1; `run submit --scenario/--change-set/--variant` creates a run with an idempotency key; `run watch` streams node states; `run timeline` prints ordered audit events with terminal outcome · **Verified by**: Own tests/command (see Validate) · **Human**: default

---

## Phase 5: User Story 3 — Human approvals, policy and change control (P1)

**Purpose**: Gates, role authorization, policy model, evaluation, enforcement and exceptions.

**Goal**: Humans approve, reject, escalate or clarify at version-bound gates; policy FAIL blocks; exceptions need a different approver key.

**Independent Test**: Drive a fixture run to each gate type and record each decision type in separate runs; verify transitions and audit (US-3 AC1–AC5).

- [ ] T051 [P] [US3] Implement orchestrator role authorization in src/orchestrator/api/auth.py from `x-required-roles` / `x-required-roles-by-gate-type`; tests in tests/orchestrator/security/test_authz.py
  - **Obj**: Human-only decisions at the API layer · **Req**: FR-GOV-003, FR-GOV-013, SC-011, NFR-AUT-001 · **Scn**: — · **ADR**: ADR-010
  - **Paths**: `src/orchestrator/api/auth.py`; `tests/orchestrator/security/test_authz.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T050 · **Parallel**: yes
  - **Artifact**: Authz dependency · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/security/test_authz.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Agent-role key on any human-reserved endpoint → 403 agent_not_permitted + AUTH_REFUSED audited; wrong role → 403 forbidden; decisions record key_id and role, never the secret · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T052 [P] [US3] Implement the policy model loader with version pinning and implementation-completeness check in src/orchestrator/policy/model.py; tests in tests/orchestrator/policy/test_model.py
  - **Obj**: Versioned policy set · **Req**: FR-GOV-005, FR-GOV-006 · **Scn**: — · **ADR**: ADR-009
  - **Paths**: `src/orchestrator/policy/model.py`; `tests/orchestrator/policy/test_model.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T050 · **Parallel**: yes
  - **Artifact**: Policy loader · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/policy/test_model.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: policy-set.v1.yaml 1.0.0 loads; declared check without implementation → engine refuses to start; run records policy_set_version · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T053 [US3] Implement the evaluator, append-only evaluations and blocking rule (incl. ST-03 routing rule) in src/orchestrator/policy/evaluator.py; tests in tests/orchestrator/policy/test_evaluator.py
  - **Obj**: Compliance evaluation and enforcement · **Req**: FR-GOV-006, FR-GOV-007, SC-008 · **Scn**: — · **ADR**: ADR-009
  - **Paths**: `src/orchestrator/policy/evaluator.py`; `tests/orchestrator/policy/test_evaluator.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T052 · **Parallel**: no
  - **Artifact**: Evaluator · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/policy/test_evaluator.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Exactly one outcome per applicable check per evaluation; evaluations validate against policy-evaluation.schema.json; mandatory FAIL → node exit fails → run SAFE_STOPPED policy_fail:<check>; ST-03 requirement-level FAIL routes to G-CLARIFY until clarified · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T054 [P] [US3] Implement checks PRIV-001 (visitor personal-data lexicon per Spec §Glossary), ARCH-001, CHG-001, CHG-002, CHG-004 in src/orchestrator/policy/checks/privacy.py, architecture.py, change_control.py; tests in tests/orchestrator/policy/test_checks_requirement_change.py
  - **Obj**: Requirement-level and change-control policies · **Req**: FR-SHR-012, FR-SHR-023, FR-ORC-033, SCN-B-AC5, FR-GOV-004 · **Scn**: — · **ADR**: ADR-009, ADR-006
  - **Paths**: `src/orchestrator/policy/checks/privacy.py`; `src/orchestrator/policy/checks/architecture.py`; `src/orchestrator/policy/checks/change_control.py`; `tests/orchestrator/policy/test_checks_requirement_change.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T053 · **Parallel**: yes
  - **Artifact**: Five checks · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/policy/test_checks_requirement_change.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Each check PASS/FAIL/NOT-APPLICABLE tested; creator API key identity is not treated as visitor personal data · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T055 [P] [US3] Implement checks REL-001..REL-005, AUD-001 (retention ≥ 365 days, no automated deletion), AUD-002 in src/orchestrator/policy/checks/release.py and audit.py; tests in tests/orchestrator/policy/test_checks_release_audit.py
  - **Obj**: Release and audit policies · **Req**: FR-GOV-010, FR-ORC-016, PD-002b, A-007 · **Scn**: — · **ADR**: ADR-009, ADR-008
  - **Paths**: `src/orchestrator/policy/checks/release.py`; `src/orchestrator/policy/checks/audit.py`; `tests/orchestrator/policy/test_checks_release_audit.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T053 · **Parallel**: yes
  - **Artifact**: Seven checks · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/policy/test_checks_release_audit.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: REL-003 FAIL on REQUESTED/REJECTED-relied-upon/EXPIRED exceptions; REL-005 advisory never blocks · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T056 [P] [US3] Implement SEC-001..SEC-005, DEP-001, LIC-001/002 and CHG-003 (static Alembic op scan) with scanner adapters (pip-audit, detect-secrets, pip-licenses) behind interfaces in src/orchestrator/policy/checks/security.py, dependencies.py, licensing.py, migrations.py and src/orchestrator/sut/scanners.py; tests in tests/orchestrator/policy/test_checks_security.py
  - **Obj**: Security, dependency, licensing and migration policies · **Req**: FR-GOV-012, NFR-SEC-002, PVT-012, SEC-003, CHG-003 · **Scn**: — · **ADR**: ADR-009, ADR-007
  - **Paths**: `src/orchestrator/policy/checks/security.py`; `src/orchestrator/policy/checks/dependencies.py`; `src/orchestrator/policy/checks/licensing.py`; `src/orchestrator/policy/checks/migrations.py`; `src/orchestrator/sut/scanners.py`; `tests/orchestrator/policy/test_checks_security.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T053, T007 · **Parallel**: yes
  - **Artifact**: Checks + adapters · **TDD**: TDD-8 with fake scanners; one real-tool integration test (TDD impractical for network advisories, Plan §10.4) · **Validate**: `uv run pytest tests/orchestrator/policy/test_checks_security.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Scanner unavailable after retries → SEC-003 FAIL, never PASS (Human Gate 4 ruling 5); drop_*/narrowing alter_column/rename → CHG-003 FAIL · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T057 [US3] Implement gate lifecycle and decisions in src/orchestrator/engine/gates.py; tests in tests/orchestrator/governance/test_gates.py
  - **Obj**: Version-bound human gates · **Req**: FR-GOV-001, FR-GOV-002, FR-GOV-004, FR-GOV-011, FR-GOV-015, FR-GOV-016, FR-ORC-004, FR-ORC-028, SC-004, PVT-013 · **Scn**: — · **ADR**: ADR-016
  - **Paths**: `src/orchestrator/engine/gates.py`; `tests/orchestrator/governance/test_gates.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T049, T051 · **Parallel**: no
  - **Artifact**: Gate engine · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/governance/test_gates.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Stale bound version → 409; engine re-checks actor.type == human; duplicate decision_id applied once; rework ≤ 2 then SAFE_STOPPED 'rework limit exceeded'; reject_terminate → ABORTED; G-RELEASE `not_ready` → FAILED with blocking reasons (CR-002); escalate keeps gate blocking · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T058 [US3] Implement gate deadlines and timeout handling in src/orchestrator/engine/gates.py (timer integration); tests in tests/orchestrator/governance/test_gate_timeout.py
  - **Obj**: No approval from silence · **Req**: FR-GOV-014, FR-GOV-002, PVT-005, SC-004 · **Scn**: — · **ADR**: ADR-016, ADR-013
  - **Paths**: `src/orchestrator/engine/gates.py`; `tests/orchestrator/governance/test_gate_timeout.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T057 · **Parallel**: no
  - **Artifact**: Timeout handling · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/governance/test_gate_timeout.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Deadline (default 24 h; demo profile value recorded on the run) → GATE_TIMED_OUT 'no decision' → SAFE_STOPPED; no TIMED_OUT → APPROVED path exists · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T059 [US3] Implement gate API and CLI (list, show, decide with auto-filled bound versions) in src/orchestrator/api/gates.py and src/orchestrator/cli/gates.py; tests in tests/orchestrator/api/test_gates_api.py
  - **Obj**: Human decision interface · **Req**: FR-GOV-002, FR-GOV-003, FR-ORC-024 · **Scn**: — · **ADR**: ADR-016, ADR-007
  - **Paths**: `src/orchestrator/api/gates.py`; `src/orchestrator/cli/gates.py`; `tests/orchestrator/api/test_gates_api.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T058, T099 · **Parallel**: no
  - **Artifact**: Gate API + CLI · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/api/test_gates_api.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Request bodies validate against gate-decision.schema.json 2.0.0; decision_source recorded interactive/scripted; removes its T099 xfail marker (contract group green) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T060 [US3] Implement the policy exception and compensating-control workflow with FR-GOV-017 separation of duties in src/orchestrator/policy/exceptions.py and src/orchestrator/api/exceptions.py; tests in tests/orchestrator/governance/test_exceptions.py
  - **Obj**: Human-approved, time-bound exceptions · **Req**: FR-GOV-007, FR-GOV-008, FR-GOV-017, SC-008 · **Scn**: — · **ADR**: ADR-009, ADR-016
  - **Paths**: `src/orchestrator/policy/exceptions.py`; `src/orchestrator/api/exceptions.py`; `tests/orchestrator/governance/test_exceptions.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T059, T055, T099 · **Parallel**: no
  - **Artifact**: Exception workflow · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/governance/test_exceptions.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Request on a FAILed eval appends EXCEPTION-REQUESTED and opens G-EXCEPTION-n; approval requires approver role, compensating control, expiry ≤ 30 days or review condition; same key identity as requester → 403 separation_of_duties_violation + audited; non-waivable check → 422; expiry → EXPIRED → REL-003 FAIL; removes its T099 xfail marker (contract group green) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T061 [P] [US3] Write the repository change-control procedure docs/change-control.md (CR template, impact-analysis steps, ADR/contract bump triggers, CR-001..CR-003 as worked examples)
  - **Obj**: Change-request and downstream impact analysis at repository level · **Req**: FR-GOV-009, CON I, CON VI · **Scn**: — · **ADR**: ADR-007
  - **Paths**: `docs/change-control.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T004 · **Parallel**: yes
  - **Artifact**: Procedure document · **TDD**: N/A — documentation · **Validate**: Review: covers requirements, architecture, schemas, workflow, security controls, release criteria
  - **Docs**: New docs/change-control.md · **Trace**: default · **Risk**: —
  - **Done**: Procedure published and linked from README · **Verified by**: T127 traceability check (CR references resolve) and T146 docs review · **Human**: default
- [ ] T062 [US3] HUMAN: Checkpoint CP-2 decision in docs/scope-control.md (engine + gates + policy green?)
  - **Obj**: Timebox checkpoint · **Req**: CST-005; Plan §14.3 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/scope-control.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T060, T054, T056, T152 · **Parallel**: no
  - **Artifact**: CP-2 row filled · **TDD**: N/A — human decision or action (no code) · **Validate**: Decision row present
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Decision recorded; reductions applied if needed · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only

**Checkpoint**: CP-2 (Day 2 midday): engine runs a full fixture graph with gates and policy blocking.

---

## Phase 6: User Story 2 (part 2) — Reliability, system-under-change adapter, agents and replanning (P1)

**Purpose**: Retry, timeout, fallback, rollback, compensation, safe-stop, resume, replanning, isolated workspaces, staging and deterministic agents.

**Goal**: The full graph executes with deterministic agents and every failure path reaches its specified recovery and terminal outcome.

**Independent Test**: Run fixture change sets through the full graph with injected faults (SC-005, SC-006).

- [ ] T063 [US2] Implement the fault injector (test config and labeled runs only) in src/orchestrator/engine/faults.py; tests in tests/orchestrator/reliability/test_faults.py
  - **Obj**: Deterministic failure-path evidence · **Req**: SC-005, FR-ORC-036 · **Scn**: — · **ADR**: ADR-018
  - **Paths**: `src/orchestrator/engine/faults.py`; `tests/orchestrator/reliability/test_faults.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T062 · **Parallel**: no
  - **Artifact**: Injector · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/reliability/test_faults.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Disabled by default; enabling labels the run `fault-injection` (`raise_ambiguity` labels it `finding-injection`, M1) and audits FAULT_INJECTED; faults transient_n, permanent, timeout, kill_after, scanner_unavailable, smoke_fail, compensation_fail, db_locked, raise_ambiguity · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T064 [US2] Implement failure classification, bounded retry and backoff with failure-episode events in src/orchestrator/engine/retry.py; tests in tests/orchestrator/reliability/test_retry.py
  - **Obj**: Retry only what can succeed · **Req**: FR-ORC-014, NFR-REL-001, PVT-004, PD-003 · **Scn**: — · **ADR**: ADR-013
  - **Paths**: `src/orchestrator/engine/retry.py`; `tests/orchestrator/reliability/test_retry.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T063 · **Parallel**: no
  - **Artifact**: Retry module · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/reliability/test_retry.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: ≤ 3 attempts; backoff 1 s ×2 cap 30 s seeded jitter (virtual clock); permanent never retried; unclassified → SAFE_STOPPED; FAILURE_DETECTED/RECOVERY_STARTED/RECOVERY_COMPLETED share episode_id · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T065 [US2] Implement node timeouts as transient failures in src/orchestrator/engine/scheduler.py; tests in tests/orchestrator/reliability/test_node_timeout.py
  - **Obj**: No hung stages · **Req**: FR-ORC-015, PVT-005 · **Scn**: — · **ADR**: ADR-013
  - **Paths**: `src/orchestrator/engine/scheduler.py`; `tests/orchestrator/reliability/test_node_timeout.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T064 · **Parallel**: no
  - **Artifact**: Timeout handling · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/reliability/test_node_timeout.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Default 300 s per node (configurable per graph); timeout → TIMEOUT event → retry within budget · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T066 [P] [US2] Implement declared fallbacks with degraded marking in src/orchestrator/engine/fallback.py; tests in tests/orchestrator/reliability/test_fallback.py
  - **Obj**: Visible degraded paths · **Req**: FR-ORC-016, REL-005 · **Scn**: — · **ADR**: ADR-013
  - **Paths**: `src/orchestrator/engine/fallback.py`; `tests/orchestrator/reliability/test_fallback.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T064 · **Parallel**: yes
  - **Artifact**: Fallback module · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/reliability/test_fallback.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Only graph-declared fallbacks run; FALLBACK_USED audited; artifact degraded=true; REL-005 advisory surfaces it · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T067 [US2] Implement safe-stop entry and safe-stop report in src/orchestrator/engine/recovery.py; tests in tests/orchestrator/reliability/test_safe_stop.py
  - **Obj**: Consistent, resumable stop · **Req**: FR-ORC-018, FR-ORC-023 · **Scn**: — · **ADR**: ADR-013
  - **Paths**: `src/orchestrator/engine/recovery.py`; `tests/orchestrator/reliability/test_safe_stop.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T065 · **Parallel**: no
  - **Artifact**: Safe-stop · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/reliability/test_safe_stop.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Each trigger (policy FAIL, retry exhausted, gate timeout, integrity violation, unclassified, rework limit, compensation failure, scheduler stall, startup interruption) → SAFE_STOPPED with reason code, no node RUNNING, safe-stop-report artifact · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T068 [US2] Implement startup recovery and approver-only resume in src/orchestrator/engine/recovery.py and src/orchestrator/api/runs.py; tests in tests/orchestrator/reliability/test_resume.py
  - **Obj**: Controlled resumption · **Req**: FR-ORC-019, FR-GOV-014, A-016, PD-011, NFR-RCV-001 · **Scn**: — · **ADR**: ADR-013
  - **Paths**: `src/orchestrator/engine/recovery.py`; `src/orchestrator/api/runs.py`; `tests/orchestrator/reliability/test_resume.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T067, T059, T099 · **Parallel**: no
  - **Artifact**: Resume · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/reliability/test_resume.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Interrupted attempts → INTERRUPTED and run SAFE_STOPPED(interrupted); resume needs approver key and resolved/excepted cause (else 409 resume_precondition_failed); timed-out gate reopens on the same version; completed nodes not re-run; removes its T099 xfail marker (contract group green) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T069 [P] [US2] Implement the release store (R0 via `git archive shortener-baseline-v1`, immutable snapshots) in src/orchestrator/sut/releases.py behind a Git interface; tests in tests/orchestrator/sut/test_releases.py
  - **Obj**: Reproducible brownfield baseline and release chain · **Req**: PD-009, FR-ORC-042 · **Scn**: — · **ADR**: ADR-006, ADR-012
  - **Paths**: `src/orchestrator/sut/releases.py`; `tests/orchestrator/sut/test_releases.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T062, T040 · **Parallel**: yes
  - **Artifact**: Release store · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/sut/test_releases.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: R0 snapshot equals the tagged tree for src/shortener, tests/shortener and the shortener contract; snapshots are read-only · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T070 [US2] Implement isolated workspaces with path-traversal guard and discard in src/orchestrator/sut/workspace.py; tests in tests/orchestrator/sut/test_workspace.py
  - **Obj**: Changes only in isolated copies · **Req**: FR-ORC-032, FR-ORC-043 · **Scn**: — · **ADR**: ADR-006
  - **Paths**: `src/orchestrator/sut/workspace.py`; `tests/orchestrator/sut/test_workspace.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T069 · **Parallel**: no
  - **Artifact**: Workspace manager · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/sut/test_workspace.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Workspaces only under var/work/<run>/<attempt>/; `..` and absolute-path escapes refused; main working tree byte-identical before/after (hash test) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T071 [P] [US2] Implement the change-set store, manifest validation, integrity fingerprint and `orch changeset verify` in src/orchestrator/sut/changeset.py and src/orchestrator/cli/changeset.py; tests in tests/orchestrator/sut/test_changeset.py
  - **Obj**: Approved, tamper-evident change sets · **Req**: FR-ORC-033, FR-ORC-034, FR-ORC-036, CHG-001 · **Scn**: — · **ADR**: ADR-006
  - **Paths**: `src/orchestrator/sut/changeset.py`; `src/orchestrator/cli/changeset.py`; `tests/orchestrator/sut/test_changeset.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T069 · **Parallel**: yes
  - **Artifact**: Change-set store + verify CLI (manifest valid, lock match, patch applies to base release) · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/sut/test_changeset.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Manifest fields scenario, variant, base_release, declared_components, contract_version_after, migration_class, reviewer, ai_assistance_disclosure required with the fixed text "Authored with AI assistance (Claude Code) during development; reviewed and locked by the human owner (Mani Kumar Vadugu); applied by the deterministic agent, not generated at run time." (CR-004; missing or different → manifest_invalid); any dependency change → manifest_invalid (ruling 3); lock ≠ bundle → integrity_mismatch · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T072 [US2] Implement the patch applier (`git apply --check`, apply, touched-file extraction) in src/orchestrator/sut/patch.py; tests in tests/orchestrator/sut/test_patch.py
  - **Obj**: Precise application and scope extraction · **Req**: FR-ORC-032, SCN-B-AC5 · **Scn**: — · **ADR**: ADR-006
  - **Paths**: `src/orchestrator/sut/patch.py`; `tests/orchestrator/sut/test_patch.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T070 · **Parallel**: no
  - **Artifact**: Patch applier · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/sut/test_patch.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Non-applying patch → patch_does_not_apply; touched files listed; CRLF fixture applies after .gitattributes normalization (Windows) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T073 [P] [US2] Implement the workspace test runner (pytest subprocess, PYTHONPATH isolation, JUnit parse) in src/orchestrator/sut/testrunner.py; tests in tests/orchestrator/sut/test_testrunner.py
  - **Obj**: Real test execution on the isolated copy · **Req**: FR-ORC-035, SCN-B-AC3 · **Scn**: — · **ADR**: ADR-006, ADR-018
  - **Paths**: `src/orchestrator/sut/testrunner.py`; `tests/orchestrator/sut/test_testrunner.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T070 · **Parallel**: yes
  - **Artifact**: Test runner · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/sut/test_testrunner.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Pass/fail parsed from JUnit; crash without report → transient; tests import the workspace copy, not the installed package · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T074 [P] [US2] Implement the staging manager (start/stop from release dir on :8100, readiness polling, additive-only migration, smoke checks, effects query, process-group cleanup) and `orch staging bootstrap` in src/orchestrator/sut/staging.py and src/orchestrator/cli/staging.py; tests in tests/orchestrator/integration/test_staging.py
  - **Obj**: Local staging promotion target · **Req**: FR-ORC-040, FR-ORC-041, FR-ORC-042, A-012 · **Scn**: — · **ADR**: ADR-012, ADR-004
  - **Paths**: `src/orchestrator/sut/staging.py`; `src/orchestrator/cli/staging.py`; `tests/orchestrator/integration/test_staging.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T069, T039 · **Parallel**: yes
  - **Artifact**: Staging manager · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/integration/test_staging.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Bootstrap (release-owner key) serves R0; promotion idempotent by release_id; destructive migration refused; no orphaned process after stop on Windows · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T153 [US2] Implement `orch staging status` in src/orchestrator/cli/staging.py; tests in tests/orchestrator/cli/test_staging_cli.py
  - **Obj**: Staging visibility (quickstart §4) · **Req**: FR-ORC-040, NFR-DOC-001 · **Scn**: — · **ADR**: ADR-012
  - **Paths**: `src/orchestrator/cli/staging.py`; `tests/orchestrator/cli/test_staging_cli.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T074 · **Parallel**: no
  - **Artifact**: Staging status command · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/cli/test_staging_cli.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Shows active release ID, previous release, last smoke result and degraded flag · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T154 [US2] Implement `orch demo reset` with interactive confirmation, limited to var/, rebuilding R0 from the baseline tag, in src/orchestrator/cli/demo.py; tests in tests/orchestrator/cli/test_demo_reset.py
  - **Obj**: Repeatable demos without touching anything outside var/ · **Req**: NFR-RUN-001, PVT-009, NFR-DOC-001 · **Scn**: — · **ADR**: ADR-004, ADR-006
  - **Paths**: `src/orchestrator/cli/demo.py`; `tests/orchestrator/cli/test_demo_reset.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T153, T069 · **Parallel**: no
  - **Artifact**: Demo reset command · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/cli/test_demo_reset.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: Destructive within var/ only; interactive confirmation every time
  - **Done**: Refuses without an interactive 'yes'; refuses any target path outside var/ (path-traversal and symlink tests); never touches src/, tests/, specs/, docs/, changesets/ or .git; rebuilds R0 and restarts staging · **Verified by**: Own tests/command (see Validate) · **Human**: Interactive confirmation by the operator on every run
- [ ] T075 [US2] Implement deterministic agents ST-01 intake, ST-02 analyst (RQ IDs, change_kind), ST-03 quality (five checks per Spec §Glossary 'fails materially'; ambiguity classification) in src/orchestrator/agents/deterministic/intake.py, analyst.py, quality.py; tests in tests/orchestrator/agents/test_requirement_agents.py
  - **Obj**: Requirement ingestion, normalization and quality checks · **Req**: FR-ORC-002, FR-ORC-003, FR-ORC-004, SCN-A-AC1, SCN-A-AC5, SCN-C-AC1 · **Scn**: — · **ADR**: ADR-003
  - **Paths**: `src/orchestrator/agents/deterministic/intake.py`; `src/orchestrator/agents/deterministic/analyst.py`; `src/orchestrator/agents/deterministic/quality.py`; `tests/orchestrator/agents/test_requirement_agents.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T068, T054 · **Parallel**: no
  - **Artifact**: Three agents · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_requirement_agents.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Well-defined fixture requirement: all checks PASS with rationale, G-CLARIFY SKIPPED with reasons; 'track who clicks links' → missing_information, unclear_term, policy_conflict items · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T076 [US2] Implement ST-05a additive-change check and ST-05 impact analysis with component registry src/orchestrator/definitions/registry/components.yaml (security_sensitive flags) in src/orchestrator/agents/deterministic/additive_check.py and impact.py; tests in tests/orchestrator/agents/test_impact_agents.py
  - **Obj**: Greenfield vs brownfield routing and impact analysis · **Req**: SCN-A-AC6, FR-ORC-010, SCN-B-AC1, FR-ORC-007 · **Scn**: SCN-A, SCN-B · **ADR**: ADR-006, ADR-005
  - **Paths**: `src/orchestrator/agents/deterministic/additive_check.py`; `src/orchestrator/agents/deterministic/impact.py`; `src/orchestrator/definitions/registry/components.yaml`; `tests/orchestrator/agents/test_impact_agents.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T075, T071 · **Parallel**: no
  - **Artifact**: Two agents + registry · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_impact_agents.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Additive PASS skips ST-05; FAIL records reason, reclassifies change_kind=modification and routes to ST-05 (never greenfield); impact analysis lists components, interfaces, data flows, tests, docs, regression risks, rollout/rollback, each linked to RQ IDs; Change Record artifact produced · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T077 [US2] Implement ST-06 planner and ST-07 architect agents in src/orchestrator/agents/deterministic/planner.py and architect.py; tests in tests/orchestrator/agents/test_design_agents.py
  - **Obj**: Decomposition and design · **Req**: FR-ORC-009, SCN-A-AC2 · **Scn**: — · **ADR**: ADR-007
  - **Paths**: `src/orchestrator/agents/deterministic/planner.py`; `src/orchestrator/agents/deterministic/architect.py`; `tests/orchestrator/agents/test_design_agents.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T076 · **Parallel**: no
  - **Artifact**: Two agents · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_design_agents.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Task graph acyclic, every RQ ID covered, every task has AC; design computes contract bump per contracts/README rules; test plan covers each AC · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T078 [US2] Implement ST-08 implementer and ST-09 tester agents with rollback in src/orchestrator/agents/deterministic/implementer.py and tester.py; tests in tests/orchestrator/agents/test_change_agents.py
  - **Obj**: Apply approved change sets and test them in isolation · **Req**: FR-ORC-032, FR-ORC-033, FR-ORC-034, FR-ORC-035, PD-012 · **Scn**: — · **ADR**: ADR-006, ADR-012
  - **Paths**: `src/orchestrator/agents/deterministic/implementer.py`; `src/orchestrator/agents/deterministic/tester.py`; `tests/orchestrator/agents/test_change_agents.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T077, T072, T073, T057 · **Parallel**: no
  - **Artifact**: Two agents · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_change_agents.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: CHG-001/002/004 evaluated at ST-08; integrity or scope FAIL → SAFE_STOPPED; test failure → ROLLBACK_STARTED/COMPLETED, workspace discarded, artifacts rolled_back, run FAILED; provenance label equals the FR-ORC-034 text (CR-004) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T079 [P] [US2] Implement ST-10a/b writer (templates, OpenAPI diff, fallbacks) and ST-11a/b security (STRIDE-lite threat review, may raise ambiguity; scanners via T056) agents in src/orchestrator/agents/deterministic/writer.py and security.py; tests in tests/orchestrator/agents/test_docs_security_agents.py
  - **Obj**: Documentation and security branches of F1/F2 · **Req**: FR-ORC-037, FR-ORC-038, FR-ORC-016, NFR-SEC-003, PD-007 · **Scn**: — · **ADR**: ADR-009, ADR-013
  - **Paths**: `src/orchestrator/agents/deterministic/writer.py`; `src/orchestrator/agents/deterministic/security.py`; `tests/orchestrator/agents/test_docs_security_agents.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T077, T056, T066 · **Parallel**: yes
  - **Artifact**: Two agents · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_docs_security_agents.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: ST-10b falls back to a manual-review section when OpenAPI diff unavailable (degraded); SEC-005 coverage of impacted interfaces; security-sensitive touch → G-SECURITY condition true · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T080 [US2] Implement ST-12 readiness-assessment agent (CON XI conditions via REL/AUD/CHG-004 checks) in src/orchestrator/agents/deterministic/release.py; tests in tests/orchestrator/agents/test_release_agent.py
  - **Obj**: Release-readiness assessment · **Req**: FR-GOV-010, CON XI · **Scn**: — · **ADR**: ADR-009, ADR-016
  - **Paths**: `src/orchestrator/agents/deterministic/release.py`; `tests/orchestrator/agents/test_release_agent.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T078, T079, T055 · **Parallel**: no
  - **Artifact**: Agent · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_release_agent.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Assessment ELIGIBLE or FAIL with each blocking reason; open risks enumerated with severity · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T081 [US2] Implement REL-01 promote+smoke, REL-02 compensation and G-CORRECTIVE corrective actions in src/orchestrator/agents/deterministic/deployer.py; tests in tests/orchestrator/agents/test_deployer.py
  - **Obj**: Promotion and compensation · **Req**: FR-ORC-040, FR-ORC-041, FR-ORC-042, FR-ORC-017 · **Scn**: — · **ADR**: ADR-012
  - **Paths**: `src/orchestrator/agents/deterministic/deployer.py`; `tests/orchestrator/agents/test_deployer.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T080, T074 · **Parallel**: no
  - **Artifact**: Agent · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_deployer.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: No promotion without a recorded `ready`; smoke fail → re-promote previous release, list links/stats created in the failed interval, open G-CORRECTIVE; compensation failure → SAFE_STOPPED staging degraded; audit never altered · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T082 [US2] Implement ST-13 engineering-summary agent in src/orchestrator/agents/deterministic/reporter.py; tests in tests/orchestrator/agents/test_reporter.py
  - **Obj**: Final engineering summary per run · **Req**: FR-ORC-026, FR-ORC-041 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `src/orchestrator/agents/deterministic/reporter.py`; `tests/orchestrator/agents/test_reporter.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T081 · **Parallel**: no
  - **Artifact**: Agent · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_reporter.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Summary contains plan and rationale, artifacts, risks, trade-offs, validation results, assumptions, limitations; produced on COMPLETED, FAILED and ABORTED paths · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T083 [P] [US2] Implement the disabled AI-backed adapter stub in src/orchestrator/agents/ai_backed/stub.py; tests in tests/orchestrator/agents/test_ai_stub.py
  - **Obj**: Interchangeable agent mode without an AI key · **Req**: FR-ORC-027, FR-ORC-030, CST-006, HD-001 · **Scn**: — · **ADR**: ADR-003
  - **Paths**: `src/orchestrator/agents/ai_backed/stub.py`; `tests/orchestrator/agents/test_ai_stub.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T047 · **Parallel**: yes
  - **Artifact**: Stub · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/agents/test_ai_stub.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: agent_mode=ai_backed → 422 agent_mode_unavailable; deterministic mode unaffected with no key present · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T084 [US2] Implement dynamic replanning (triggers, stale closure, gate revocation, graph instance v+1, input-hash memoization, late-ambiguity suspension of the dependent path) in src/orchestrator/engine/replan.py; tests in tests/orchestrator/replan/test_replan.py
  - **Obj**: Re-run only what changed · **Req**: FR-ORC-020, FR-ORC-021, FR-ORC-022, SC-006, SCN-A-AC4, SCN-C-AC4 · **Scn**: — · **ADR**: ADR-017
  - **Paths**: `src/orchestrator/engine/replan.py`; `tests/orchestrator/replan/test_replan.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T082 · **Parallel**: no
  - **Artifact**: Replanner · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/replan/test_replan.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Unaffected nodes' attempt counts unchanged; stale nodes re-run; bound approvals REVOKED and re-requested; REPLAN_*/ARTIFACT_STALE/GATE_REVOKED/GRAPH_VERSION_CREATED audited; suspended node's dependent path holds at the next sync point · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T085 [US2] Write full-graph sequential/parallel/synchronization tests in tests/orchestrator/state/test_full_graph_paths.py using a fixture change set in tests/fixtures/changesets/
  - **Obj**: Prove non-linear execution (D01, D04) · **Req**: FR-ORC-006, FR-ORC-037, FR-ORC-038, FR-ORC-039 · **Scn**: — · **ADR**: ADR-003
  - **Paths**: `tests/orchestrator/state/test_full_graph_paths.py`; `tests/fixtures/changesets/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T084 · **Parallel**: no
  - **Artifact**: Path tests · **TDD**: TDD impractical because whole-graph behavior emerges only when all agents exist; scheduler semantics were test-first in T049 with fixture graphs. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/orchestrator/state/test_full_graph_paths.py tests/fixtures/changesets/ -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Sequential prefix order holds; F1 and F2 attempt intervals overlap; SP-1/SP-2 hold while a branch is SUSPENDED/FAILED/RETRY_WAIT · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T086 [P] [US2] Write rollback tests with a defective fixture change set in tests/orchestrator/reliability/test_rollback.py
  - **Obj**: Valid rollback claims (D17) · **Req**: FR-ORC-017, FR-ORC-035, SCN-B-AC4, NFR-CHG-001 · **Scn**: — · **ADR**: ADR-012
  - **Paths**: `tests/orchestrator/reliability/test_rollback.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T085 · **Parallel**: yes
  - **Artifact**: Rollback tests · **TDD**: TDD impractical because it needs the full graph plus the SUT adapter; rollback mechanics were test-first in T070 and T078. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/orchestrator/reliability/test_rollback.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: ROLLBACK_COMPLETED with workspace disposal evidence; staging release unchanged; main tree hash unchanged; episode mechanism=rollback · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T087 [P] [US2] Write compensation tests (smoke_fail, compensation_fail) in tests/orchestrator/reliability/test_compensation.py
  - **Obj**: Compensation present and distinct (D18) · **Req**: FR-ORC-042, FR-ORC-017 · **Scn**: — · **ADR**: ADR-012
  - **Paths**: `tests/orchestrator/reliability/test_compensation.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T085 · **Parallel**: yes
  - **Artifact**: Compensation tests · **TDD**: TDD impractical because it needs the full graph, staging and deployer; compensation mechanics were test-first in T074 and T081. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/orchestrator/reliability/test_compensation.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Re-promotion verified by previous-release smoke; effects listed; G-CORRECTIVE decision recorded; compensation_fail → SAFE_STOPPED degraded · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T088 [P] [US2] Write interruption tests at every stage boundary in tests/orchestrator/reliability/test_interruption_boundaries.py
  - **Obj**: PVT-006 resume evidence (D20) · **Req**: PVT-006, NFR-RCV-001, FR-ORC-019 · **Scn**: — · **ADR**: ADR-013
  - **Paths**: `tests/orchestrator/reliability/test_interruption_boundaries.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T085 · **Parallel**: yes
  - **Artifact**: Interruption tests · **TDD**: TDD impractical because it requires one test per boundary of the complete graph; resume logic was test-first in T068. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/orchestrator/reliability/test_interruption_boundaries.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: If per-boundary coverage is infeasible, only a recorded human change decision may re-scope PVT-006 (Plan §14.1)
  - **Done**: One kill_after test per node boundary resumes (approver) to the same terminal outcome as an uninterrupted run with no duplicate side effects · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T089 [P] [US2] Write orchestrator security tests in tests/orchestrator/security/test_security_suite.py (agent decisions refused, path traversal, permission refusal audited, no secrets in audit/logs, self-approval refused)
  - **Obj**: Negative governance and security coverage · **Req**: NFR-AUT-001, SC-004, SC-011, FR-GOV-017, NFR-SEC-002 · **Scn**: — · **ADR**: ADR-010, ADR-016
  - **Paths**: `tests/orchestrator/security/test_security_suite.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T085 · **Parallel**: yes
  - **Artifact**: Security suite · **TDD**: TDD impractical because it is a cross-cutting negative suite over the assembled engine; each rule was test-first in T047, T051, T057 and T060. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/orchestrator/security/test_security_suite.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: 100% of agent human-reserved attempts refused and audited; 0 approvals inferred; exported audit contains no key secret pattern · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T090 [US2] HUMAN: Checkpoint CP-3 decision in docs/scope-control.md (reliability, replanning, interruption suites green?)
  - **Obj**: Timebox checkpoint · **Req**: CST-005; Plan §14.3 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/scope-control.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T086, T087, T088, T089, T083, T154 · **Parallel**: no
  - **Artifact**: CP-3 row filled · **TDD**: N/A — human decision or action (no code) · **Validate**: Decision row present
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Decision recorded · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only

**Checkpoint**: CP-3: reliability, replanning and interruption suites green.

---

## Phase 7: User Story 5 — Reviewer reconstructs and verifies execution (P2)

**Purpose**: Audit query, traces, MTTR and reliability metrics, run-level traceability and evidence export.

**Goal**: Given only a run ID, a reviewer reconstructs the timeline, lineage, metrics and evidence.

**Independent Test**: Reconstruct a completed fixture run from its ID alone; trace a requirement both ways; read labeled metrics (US-5 AC1–AC3).

- [ ] T091 [P] [US5] Implement audit query, verify and tamper-refusal endpoints and `orch audit` in src/orchestrator/api/audit.py and src/orchestrator/cli/audit.py; tests in tests/orchestrator/api/test_audit_api.py
  - **Obj**: Queryable, verifiable audit · **Req**: FR-OBS-004, FR-OBS-005 · **Scn**: — · **ADR**: ADR-008
  - **Paths**: `src/orchestrator/api/audit.py`; `src/orchestrator/cli/audit.py`; `tests/orchestrator/api/test_audit_api.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T090, T099 · **Parallel**: yes
  - **Artifact**: Audit API + CLI · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/api/test_audit_api.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Filters run_id, requirement_id (spec IDs and RQ IDs), actor, event_type; PUT/DELETE → 405 + AUDIT_TAMPER_REFUSED; /audit/verify returns head hash; removes its T099 xfail marker (contract group green) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T092 [P] [US5] Implement spans and traceparent propagation to shortener calls in src/orchestrator/observability/spans.py; tests in tests/orchestrator/observability/test_spans.py
  - **Obj**: Traces · **Req**: FR-OBS-001, NFR-OBS-001, PD-005 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `src/orchestrator/observability/spans.py`; `tests/orchestrator/observability/test_spans.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T090 · **Parallel**: yes
  - **Artifact**: Span recorder + GET /runs/{id}/trace · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/observability/test_spans.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Node attempt, subprocess and HTTP spans recorded; shortener log lines carry the same trace ID · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T093 [P] [US5] Implement failure-episode materialization (detected, recovery-start, recovery-complete timestamps; mechanism; recovered/unrecovered/open; includes_human_wait; fault_injected) in src/orchestrator/observability/episodes.py; tests in tests/orchestrator/observability/test_episodes.py
  - **Obj**: MTTR instrumentation from recorded events · **Req**: FR-OBS-006, NFR-RCV-002 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `src/orchestrator/observability/episodes.py`; `tests/orchestrator/observability/test_episodes.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T090 · **Parallel**: yes
  - **Artifact**: Episode builder · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/observability/test_episodes.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Every mechanism (retry, rollback, compensation, human_resume, fallback) emits all three events; episodes recomputable from audit alone · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T094 [US5] Implement reliability metrics and MTTR calculation (population, exclusions, unrecovered/open reported separately, by mechanism, with and without human wait, demonstration label) in src/orchestrator/observability/metrics.py; calculation-validation tests in tests/orchestrator/observability/test_metrics.py
  - **Obj**: MTTR = Σ recovery_duration(recovered) ÷ count(recovered) · **Req**: FR-OBS-006, FR-OBS-007, NFR-RCV-002 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `src/orchestrator/observability/metrics.py`; `tests/orchestrator/observability/test_metrics.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T093 · **Parallel**: no
  - **Artifact**: Metrics module · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/observability/test_metrics.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Hand-built event sequences give exact expected MTTR; unrecovered/open excluded from denominator and counted; success/failure rate, retry, rollback/compensation frequency, latency p50/p95 (active vs human wait); every output has measurement_class=demonstration and disclaimer · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T095 [US5] Implement GET /api/v1/metrics/reliability and `orch metrics` in src/orchestrator/api/metrics.py and src/orchestrator/cli/metrics.py; tests in tests/orchestrator/api/test_metrics_api.py
  - **Obj**: Metrics interface · **Req**: FR-OBS-006, FR-OBS-007 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `src/orchestrator/api/metrics.py`; `src/orchestrator/cli/metrics.py`; `tests/orchestrator/api/test_metrics_api.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T094, T099 · **Parallel**: no
  - **Artifact**: Metrics API + CLI · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/api/test_metrics_api.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Response validates against ReliabilityMetrics schema; include_fault_injection filter works; removes its T099 xfail marker (contract group green) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T096 [P] [US5] Implement run-level bidirectional traceability (GET /trace/requirements/{id}) in src/orchestrator/trace/views.py and src/orchestrator/api/trace.py; tests in tests/orchestrator/api/test_trace_api.py
  - **Obj**: Requirement ↔ decision ↔ task ↔ artifact ↔ test ↔ evidence · **Req**: FR-OBS-008, FR-ORC-013 · **Scn**: — · **ADR**: ADR-015
  - **Paths**: `src/orchestrator/trace/views.py`; `src/orchestrator/api/trace.py`; `tests/orchestrator/api/test_trace_api.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T090, T099 · **Parallel**: yes
  - **Artifact**: Trace API · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/api/test_trace_api.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Forward and reverse views; gaps listed; spec IDs and RQ IDs both resolvable; removes its T099 xfail marker (contract group green) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T097 [US5] Implement evidence export (GET /runs/{id}/evidence, `orch evidence export`) writing docs/evidence/<scenario>/<run-id>/manifest.json in src/orchestrator/observability/evidence.py; tests in tests/orchestrator/observability/test_evidence_export.py
  - **Obj**: Verifiable evidence packs · **Req**: SC-002, SC-003, FR-ORC-029, CON X · **Scn**: — · **ADR**: ADR-008, ADR-011
  - **Paths**: `src/orchestrator/observability/evidence.py`; `tests/orchestrator/observability/test_evidence_export.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T091, T095, T099 · **Parallel**: no
  - **Artifact**: Exporter · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/observability/test_evidence_export.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Manifest lists EV-IDs, file SHA-256 and audit head hash; refuses runs labeled `test` or agent_mode=ai_backed for scenario evidence; removes its T099 xfail marker (contract group green) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T155 [US5] Implement `orch trace <requirement-id>` in src/orchestrator/cli/trace.py; tests in tests/orchestrator/cli/test_trace_cli.py
  - **Obj**: Traceability from the CLI (quickstart §6) · **Req**: FR-OBS-008, NFR-DOC-001 · **Scn**: — · **ADR**: ADR-015
  - **Paths**: `src/orchestrator/cli/trace.py`; `tests/orchestrator/cli/test_trace_cli.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T096 · **Parallel**: no
  - **Artifact**: Trace command · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/orchestrator/cli/test_trace_cli.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Prints forward and reverse links and gaps for spec IDs and RQ IDs · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T098 [US5] Write audit-completeness (PVT-008) and reconstruction (SC-003) tests in tests/orchestrator/observability/test_completeness_reconstruction.py
  - **Obj**: Complete audit evidence (D22) · **Req**: PVT-008, NFR-AUD-001, NFR-OBS-001, SC-003 · **Scn**: — · **ADR**: ADR-008
  - **Paths**: `tests/orchestrator/observability/test_completeness_reconstruction.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T097, T092, T096 · **Parallel**: no
  - **Artifact**: Tests · **TDD**: TDD impractical because completeness is a property of all events emitted by real runs; per-event schema validity was test-first in T042. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/orchestrator/observability/test_completeness_reconstruction.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: 100% of transitions and decisions in fixture runs have schema-valid events; timeline and terminal outcome rebuilt from DB alone; node states rebuilt from audit equal state tables · **Verified by**: Own tests/command (see Validate) · **Human**: default

---

## Phase 8: User Story 4 — Release owner determines release readiness (P2)

**Purpose**: Release gate rules and readiness evidence in the engine.

**Goal**: Readiness is eligible only when all mandatory conditions hold, and only a human release owner can record `ready`.

**Independent Test**: Run to ST-12 once with all checks passing and once with a mandatory FAIL or expired exception (US-4 AC1–AC2, SC-008).

- [ ] T100 [US4] Write release-readiness tests test_release_blocked_by_mandatory_fail and test_readiness_fail_lists_blocking_reasons, plus per-risk acceptance tests, in tests/orchestrator/governance/test_release_readiness.py
  - **Obj**: Failed mandatory policy prevents release (D09, D12) · **Req**: FR-GOV-010, FR-GOV-011, SC-008, US-4 · **Scn**: — · **ADR**: ADR-009, ADR-016
  - **Paths**: `tests/orchestrator/governance/test_release_readiness.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T098, T155 · **Parallel**: no
  - **Artifact**: Release tests · **TDD**: TDD impractical because the blocking chain spans policy, agents and gates; each rule was test-first in T053, T057 and T080. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/orchestrator/governance/test_release_readiness.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Injected SEC-002 finding → SAFE_STOPPED, SP-2 never releases, G-RELEASE never opens; expired exception → REL-003 FAIL, `ready` → 409 assessment_not_eligible; open risk ≥ medium not accepted → decision refused; `not_ready` → FAILED · **Verified by**: Own tests/command (see Validate) · **Human**: default

---

## Phase 9: Required Scenario SCN-A — Greenfield (expiration + basic analytics) (P1)

**Purpose**: Deliver SCN-A only through an orchestrated run (CST-007).

**Goal**: A well-defined requirement proceeds without unnecessary clarification while quality checks, traceability, policy enforcement and late-ambiguity escalation remain active.

**Independent Test**: Run SCN-A with scripted decisions (test) and interactively (evidence); check SCN-A-AC1..AC6.

- [ ] T101 [SCN-A] Author scenarios/scn-a/requirement.md (5 explicit ACs), scenarios/scn-a/expected.yaml and scenarios/scn-a/decisions.scripted.yaml (test-only)
  - **Obj**: SCN-A input and expected outcome · **Req**: SCN-A-AC1, HD-002, FR-SHR-008, FR-SHR-009, FR-SHR-010, FR-SHR-011, FR-SHR-012 · **Scn**: SCN-A · **ADR**: ADR-016
  - **Paths**: `scenarios/scn-a/requirement.md`; `scenarios/scn-a/expected.yaml`; `scenarios/scn-a/decisions.scripted.yaml`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T100 · **Parallel**: no
  - **Artifact**: Scenario pack · **TDD**: N/A — scenario data · **Validate**: T075 quality checks all PASS on requirement.md (unit fixture run)
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Requirement passes all five checks; scripted decisions labeled decision_source=scripted · **Verified by**: T106 end-to-end test consumes this pack · **Human**: default
- [ ] T102 [SCN-A] In authoring workspace var/authoring/scn-a/ (from tag shortener-baseline-v1), TDD the expiration capability: optional `expires_at`, UTC with expired when resolution time ≥ expires_at, `410 link_expired`, `422 invalid_expiration`, migration 0002 (`links.expires_at` nullable)
  - **Obj**: SCN-A change-set content (part 1) · **Req**: FR-SHR-008, FR-SHR-009, A-006, A-014 · **Scn**: SCN-A · **ADR**: ADR-006, ADR-007
  - **Paths**: `var/authoring/scn-a/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T101 · **Parallel**: no
  - **Artifact**: Workspace commits with tests and implementation · **TDD**: TDD-8 inside the authoring workspace (tests written first in tests/shortener/) · **Validate**: `uv run pytest tests/shortener -q` inside var/authoring/scn-a/ (PYTHONPATH=src)
  - **Docs**: None · **Trace**: default · **Risk**: Never modify the main working tree's src/shortener (CST-007)
  - **Done**: Baseline + new tests green in the workspace · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T103 [SCN-A] In var/authoring/scn-a/, TDD analytics: `link_stats` table (migration additive), atomic `redirect_count = redirect_count + 1` in its own transaction after resolution, fallback when the write fails, `analytics_write_failures` metric, `GET /api/v1/links/{code}/analytics`, no personal data
  - **Obj**: SCN-A change-set content (part 2) · **Req**: FR-SHR-010, FR-SHR-011, FR-SHR-012, FR-SHR-014, A-013, NFR-REL-002 · **Scn**: SCN-A · **ADR**: ADR-019
  - **Paths**: `var/authoring/scn-a/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T102 · **Parallel**: no
  - **Artifact**: Workspace commits · **TDD**: TDD-8 inside the authoring workspace · **Validate**: `uv run pytest tests/shortener -q` inside var/authoring/scn-a/
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Concurrent redirects counted exactly; injected analytics failure still redirects (100%) and increments the failure metric · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T104 [SCN-A] Export the SCN-A change set to changesets/scn-a/normal/manifest.yaml, patch.diff and REVIEW.md (contract 1.1.0, migration_class additive, declared_components, ai_assistance_disclosure = the fixed FR-ORC-034 provenance text (CR-004), Change Record)
  - **Obj**: Reviewable SCN-A change set · **Req**: FR-ORC-033, FR-ORC-034, CST-007 · **Scn**: SCN-A · **ADR**: ADR-006, ADR-007
  - **Paths**: `changesets/scn-a/normal/manifest.yaml`; `changesets/scn-a/normal/patch.diff`; `changesets/scn-a/normal/REVIEW.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T103 · **Parallel**: no
  - **Artifact**: Change-set bundle · **TDD**: N/A — packaging (content tested in T102/T103) · **Validate**: `uv run orch changeset verify changesets/scn-a/normal` (manifest valid; patch applies to R0)
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Bundle valid; no dependency changes · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T105 [SCN-A] HUMAN: Review changesets/scn-a/normal/ and record its SHA-256 in changesets/approved.lock.yaml
  - **Obj**: Human-reviewed, locked change set · **Req**: FR-ORC-033 · **Scn**: SCN-A · **ADR**: ADR-006
  - **Paths**: `changesets/approved.lock.yaml`; `changesets/scn-a/normal/REVIEW.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T104 · **Parallel**: no
  - **Artifact**: Lock entry + signed REVIEW.md · **TDD**: N/A — human decision or action (no code) · **Validate**: `orch changeset verify` reports lock match
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Lock committed by the human owner · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only
- [ ] T106 [SCN-A] Write the SCN-A scripted end-to-end test tests/e2e/test_scn_a.py
  - **Obj**: Greenfield proceeds without unnecessary clarification · **Req**: SCN-A-AC1, SCN-A-AC2, SCN-A-AC3, SCN-A-AC5, SCN-A-AC6, SC-002, FR-GOV-006 · **Scn**: SCN-A · **ADR**: ADR-003, ADR-016
  - **Paths**: `tests/e2e/test_scn_a.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T105 · **Parallel**: no
  - **Artifact**: E2E test · **TDD**: TDD impractical because a scenario run requires the locked change set and the complete engine; the behaviors were test-first in Phases 3–8. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_scn_a.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: G-CLARIFY SKIPPED citing each passed check; ST-05a PASS recorded and ST-05 SKIPPED; PRIV-001/ARCH-001 PASS with policy version recorded; decomposition and design artifacts trace to the requirement and run; COMPLETED with staging R1; smoke shows 410 for an expired link · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T107 [P] [SCN-A] Write the SCN-A late-ambiguity (finding-injection) end-to-end test tests/e2e/test_scn_a_late_ambiguity.py
  - **Obj**: Escalation if ambiguity appears after decomposition · **Req**: SCN-A-AC4, FR-ORC-022, FR-ORC-039 · **Scn**: SCN-A · **ADR**: ADR-017
  - **Paths**: `tests/e2e/test_scn_a_late_ambiguity.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T106 · **Parallel**: yes
  - **Artifact**: E2E test · **TDD**: TDD impractical because it requires the complete engine and a locked change set; suspension/replanning were test-first in T084. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_scn_a_late_ambiguity.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: ST-11a SUSPENDED; G-CLARIFY-1 opened; ST-09 and ST-10a finish; SP-1 holds; after the answer only the dependent path re-runs and SP-1 releases; run labeled finding-injection · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T108 [P] [SCN-A] Write the SCN-A-AC6 negative end-to-end test with a behavior-changing fixture change set in tests/e2e/test_scn_a_additive_fail.py
  - **Obj**: Never proceed as greenfield when existing behavior changes · **Req**: SCN-A-AC6, FR-ORC-010 · **Scn**: SCN-A · **ADR**: ADR-005
  - **Paths**: `tests/e2e/test_scn_a_additive_fail.py`; `tests/fixtures/changesets/scn-a-behavior-change/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T106 · **Parallel**: yes
  - **Artifact**: E2E test + fixture · **TDD**: TDD impractical because it requires the complete engine; the additive check was test-first in T076. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_scn_a_additive_fail.py tests/fixtures/changesets/scn-a-behavior-change/ -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: ST-05a FAIL with reason; change_kind reclassified; ST-05 impact analysis executed; no greenfield path taken · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T109 [SCN-A] HUMAN: Execute recorded SCN-A runs interactively (normal and late-ambiguity) and decide every gate with your own keys; then export evidence with `orch evidence export`
  - **Obj**: Real scenario evidence · **Req**: SC-002, FR-ORC-031, PD-006 · **Scn**: SCN-A · **ADR**: ADR-016
  - **Paths**: `docs/evidence/scn-a/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T107, T108 · **Parallel**: no
  - **Artifact**: Evidence manifests for each run · **TDD**: N/A — human decision or action (no code) · **Validate**: Manifest audit head hashes verify (`orch audit verify`)
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: EV-001..EV-004, EV-006, EV-007 present for SCN-A · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner makes all gate decisions

---

## Phase 10: Required Scenario SCN-B — Brownfield (custom aliases) (P1)

**Purpose**: Change the existing shortener through impact analysis, change control, regression and rollback.

**Goal**: Brownfield change applied only after approved impact analysis; failures roll back to R1.

**Independent Test**: Run SCN-B normal, defective and undeclared-scope variants; check SCN-B-AC1..AC5.

- [ ] T110 [SCN-B] Author scenarios/scn-b/requirement.md, scenarios/scn-b/expected.yaml and scenarios/scn-b/decisions.scripted.yaml
  - **Obj**: SCN-B input · **Req**: FR-SHR-020, FR-SHR-021, FR-SHR-022, HD-002 · **Scn**: SCN-B · **ADR**: —
  - **Paths**: `scenarios/scn-b/requirement.md`; `scenarios/scn-b/expected.yaml`; `scenarios/scn-b/decisions.scripted.yaml`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T109 · **Parallel**: no
  - **Artifact**: Scenario pack · **TDD**: N/A — scenario data · **Validate**: T075 classifies change_kind=modification on requirement.md
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Quality checks PASS; change_kind=modification · **Verified by**: T115 end-to-end test consumes this pack · **Human**: default
- [ ] T111 [SCN-B] In var/authoring/scn-b/ (R0 + scn-a patch), TDD custom aliases: optional `alias` matching `^[A-Za-z0-9]{4,10}$`, reserved words (api, health, docs, openapi, redoc, static, admin, case-insensitive), `409 alias_conflict` leaving the mapping unchanged, `422 alias_invalid`/`alias_reserved`, `code_origin` default `generated` (migration 0003), unchanged behavior without alias; export changesets/scn-b/normal/
  - **Obj**: SCN-B change set · **Req**: FR-SHR-020, FR-SHR-021, FR-SHR-022, ADR-014 ruling 1 · **Scn**: SCN-B · **ADR**: ADR-014, ADR-006, ADR-007
  - **Paths**: `var/authoring/scn-b/`; `changesets/scn-b/normal/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T110 · **Parallel**: no
  - **Artifact**: Change-set bundle (contract 1.2.0, additive) · **TDD**: TDD-8 inside the authoring workspace · **Validate**: Workspace tests green; `orch changeset verify changesets/scn-b/normal`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Alias lengths 3 rejected, 4/7/10 accepted, 11 rejected; regression suite unchanged and green; manifest carries the fixed FR-ORC-034 provenance text (CR-004) · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T112 [P] [SCN-B] Create the labeled defective variant changesets/scn-b/defective/ (alias conflict overwrites the existing mapping) for rollback demonstration
  - **Obj**: Fault-injection change set · **Req**: FR-ORC-036, SCN-B-AC4 · **Scn**: SCN-B · **ADR**: ADR-012
  - **Paths**: `changesets/scn-b/defective/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T111 · **Parallel**: yes
  - **Artifact**: Defective bundle · **TDD**: N/A — deliberately defective; failing test is the conflict test from T111 · **Validate**: Applying it in a workspace makes the conflict test fail
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Manifest variant=defective, labeled fault-injection; manifest carries the fixed FR-ORC-034 provenance text (CR-004) · **Verified by**: T116 end-to-end test · **Human**: default
- [ ] T113 [P] [SCN-B] Create the undeclared-scope variant changesets/scn-b/undeclared-scope/ (also touches src/shortener/api/health.py, not declared)
  - **Obj**: Scope-violation fixture · **Req**: SCN-B-AC5, CHG-002 · **Scn**: SCN-B · **ADR**: ADR-006
  - **Paths**: `changesets/scn-b/undeclared-scope/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T111 · **Parallel**: yes
  - **Artifact**: Scope-violation bundle · **TDD**: N/A — fixture · **Validate**: Touched files include api/health.py; declared_components exclude it
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Bundle valid apart from scope; manifest carries the fixed FR-ORC-034 provenance text (CR-004) · **Verified by**: T117 integration test · **Human**: default
- [ ] T114 [SCN-B] HUMAN: Review and lock changesets/scn-b/normal, defective and undeclared-scope in changesets/approved.lock.yaml
  - **Obj**: Human-reviewed, locked change sets · **Req**: FR-ORC-033 · **Scn**: SCN-B · **ADR**: ADR-006
  - **Paths**: `changesets/approved.lock.yaml`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T112, T113 · **Parallel**: no
  - **Artifact**: Lock entries · **TDD**: N/A — human decision or action (no code) · **Validate**: `orch changeset verify` for each variant
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Three lock entries committed by the human owner · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only
- [ ] T115 [SCN-B] Write the SCN-B normal end-to-end test tests/e2e/test_scn_b.py
  - **Obj**: Brownfield change with impact analysis and change control · **Req**: SCN-B-AC1, SCN-B-AC2, SCN-B-AC3, FR-ORC-010, PD-007, SC-002 · **Scn**: SCN-B · **ADR**: ADR-006, ADR-016
  - **Paths**: `tests/e2e/test_scn_b.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T114 · **Parallel**: no
  - **Artifact**: E2E test · **TDD**: TDD impractical because a scenario run requires the locked change set and the complete engine; the behaviors were test-first in Phases 3–8. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_scn_b.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Impact analysis precedes ST-08 and lists components/interfaces/data flows/tests/docs/risks/rollout; G-DESIGN binds the fingerprint; G-SECURITY opens and is escalated once (gate ESCALATED, still blocking) before an approver approves (L3); regression + new tests pass; COMPLETED with staging R2 · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T116 [P] [SCN-B] Write the SCN-B defective-variant end-to-end test tests/e2e/test_scn_b_defective.py
  - **Obj**: Rollback to last known-good · **Req**: SCN-B-AC4, FR-ORC-035, FR-ORC-036, PD-012 · **Scn**: SCN-B · **ADR**: ADR-012
  - **Paths**: `tests/e2e/test_scn_b_defective.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T115 · **Parallel**: yes
  - **Artifact**: E2E test · **TDD**: TDD impractical because it requires the locked defective change set and the complete engine; rollback was test-first in T078/T086. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_scn_b_defective.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: ST-09 fails; ROLLBACK_COMPLETED; staging still R1; main tree unchanged; run FAILED with summary · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T117 [P] [SCN-B] Write scope-violation and integrity-mismatch integration tests in tests/e2e/test_scn_b_scope_integrity.py
  - **Obj**: Block changes outside approved impact analysis · **Req**: SCN-B-AC5, CHG-001, CHG-002, FR-ORC-033 · **Scn**: SCN-B · **ADR**: ADR-006
  - **Paths**: `tests/e2e/test_scn_b_scope_integrity.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T115 · **Parallel**: yes
  - **Artifact**: Integration tests · **TDD**: TDD impractical because it requires locked change sets and the complete engine; CHG-001/002 were test-first in T054. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_scn_b_scope_integrity.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Undeclared scope → CHG-002 FAIL → SAFE_STOPPED 're-analysis required'; tampered patch → CHG-001 FAIL → SAFE_STOPPED · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T118 [SCN-B] HUMAN: Execute recorded SCN-B runs interactively (normal and defective) and export evidence
  - **Obj**: Real scenario evidence · **Req**: SC-002, FR-ORC-031 · **Scn**: SCN-B · **ADR**: ADR-016
  - **Paths**: `docs/evidence/scn-b/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T116, T117 · **Parallel**: no
  - **Artifact**: Evidence manifests · **TDD**: N/A — human decision or action (no code) · **Validate**: Head hashes verify
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: EV-001..EV-007 present for SCN-B (incl. EV-005 impact analysis and rollback evidence) · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner makes all gate decisions

---

## Phase 11: Required Scenario SCN-C — Ambiguous requirement ('track who clicks links') (P1)

**Purpose**: Detect, classify and clarify; never proceed on a guessed interpretation.

**Goal**: Ambiguity is classified and clarified by a human; the run resumes at the earliest affected stage or ends safely.

**Independent Test**: Run SCN-C with option A, option B (with and without exception), option C and timeout; check SCN-C-AC1..AC5.

- [ ] T119 [SCN-C] Author scenarios/scn-c/requirement.md (verbatim 'We need to track who clicks links.'), scenarios/scn-c/expected.yaml and scenarios/scn-c/decisions.scripted.yaml (options A, B, B+exception, C, timeout)
  - **Obj**: SCN-C input · **Req**: HD-002, SCN-C-AC1, SCN-C-AC3 · **Scn**: SCN-C · **ADR**: —
  - **Paths**: `scenarios/scn-c/requirement.md`; `scenarios/scn-c/expected.yaml`; `scenarios/scn-c/decisions.scripted.yaml`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T118 · **Parallel**: no
  - **Artifact**: Scenario pack · **TDD**: N/A — scenario data · **Validate**: T075 produces the classified items for requirement.md
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Questions Q1 (A/B/C, A recommended) and Q2 (retention) defined · **Verified by**: T122 end-to-end test consumes this pack · **Human**: default
- [ ] T120 [SCN-C] In var/authoring/scn-c/ (R0 + scn-a + scn-b), TDD daily aggregate counts: `link_daily_stats(code, day_utc, count)` additive migration 0004, atomic upsert, `daily` buckets in analytics (contract 1.3.0), retention = link lifetime (Q2 default); export changesets/scn-c/aggregate-daily/
  - **Obj**: SCN-C conforming change set · **Req**: FR-SHR-023, FR-SHR-012, PD-008, EXC-005 · **Scn**: SCN-C · **ADR**: ADR-019, ADR-007
  - **Paths**: `var/authoring/scn-c/`; `changesets/scn-c/aggregate-daily/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T119 · **Parallel**: no
  - **Artifact**: Change-set bundle · **TDD**: TDD-8 inside the authoring workspace · **Validate**: Workspace tests green; PRIV-001 PASS on the bundle
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: No visitor personal data stored; manifest carries the fixed FR-ORC-034 provenance text (CR-004) · **Verified by**: Workspace tests (TDD-8) and T122 end-to-end test · **Human**: default
- [ ] T121 [SCN-C] HUMAN: Review and lock changesets/scn-c/aggregate-daily in changesets/approved.lock.yaml
  - **Obj**: Human-reviewed, locked change set · **Req**: FR-ORC-033 · **Scn**: SCN-C · **ADR**: ADR-006
  - **Paths**: `changesets/approved.lock.yaml`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T120 · **Parallel**: no
  - **Artifact**: Lock entry · **TDD**: N/A — human decision or action (no code) · **Validate**: `orch changeset verify`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Lock committed · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only
- [ ] T122 [SCN-C] Write the SCN-C option-A end-to-end test tests/e2e/test_scn_c_option_a.py
  - **Obj**: Clarify, re-version, resume · **Req**: SCN-C-AC1, SCN-C-AC2, SCN-C-AC3, SCN-C-AC4, FR-ORC-020, FR-ORC-013 · **Scn**: SCN-C · **ADR**: ADR-017, ADR-016
  - **Paths**: `tests/e2e/test_scn_c_option_a.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T121 · **Parallel**: no
  - **Artifact**: E2E test · **TDD**: TDD impractical because a scenario run requires the locked change set and the complete engine; clarification and replanning were test-first in T075 and T084. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_scn_c_option_a.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Items classified missing_information/unclear_term/policy_conflict; no ST-06+ READY while G-CLARIFY open; answer recorded with lineage; normalized-requirement v2; replanning events; resume at earliest affected stage; COMPLETED with staging R3 · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T123 [P] [SCN-C] Write SCN-C variant end-to-end tests in tests/e2e/test_scn_c_variants.py
  - **Obj**: Every non-happy outcome is safe · **Req**: SCN-C-AC5, FR-GOV-014, FR-GOV-015, FR-GOV-007, FR-GOV-017 · **Scn**: SCN-C · **ADR**: ADR-016, ADR-009
  - **Paths**: `tests/e2e/test_scn_c_variants.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T122 · **Parallel**: yes
  - **Artifact**: E2E tests · **TDD**: TDD impractical because it requires the complete engine; each variant's rule was test-first in T057, T058, T060 and T054. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_scn_c_variants.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Option B without exception → PRIV-001 FAIL → SAFE_STOPPED; option B exception requested by engineer key and approved by a different approver key → path proceeds; same key approving → 403; option C → ABORTED; timeout → SAFE_STOPPED 'no decision' · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T124 [SCN-C] HUMAN: Execute recorded SCN-C runs interactively (option A, and option B with the real exception path) and export evidence
  - **Obj**: Real scenario evidence incl. approved exception and compensating control · **Req**: SC-002, FR-GOV-008, FR-GOV-017 · **Scn**: SCN-C · **ADR**: ADR-016
  - **Paths**: `docs/evidence/scn-c/`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T123 · **Parallel**: no
  - **Artifact**: Evidence manifests · **TDD**: N/A — human decision or action (no code) · **Validate**: Head hashes verify
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: EV-001..EV-004, EV-006, EV-007 present for SCN-C · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner (engineer key requests, separate approver key decides)
- [ ] T125 [SCN-C] HUMAN: Checkpoint CP-4 decision in docs/scope-control.md (scenario e2e green; feature freeze)
  - **Obj**: Timebox checkpoint and feature freeze · **Req**: CST-005; Plan §14.3 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/scope-control.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T124 · **Parallel**: no
  - **Artifact**: CP-4 row filled · **TDD**: N/A — human decision or action (no code) · **Validate**: Decision row present
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Freeze recorded; backlog work allowed only after this row · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only

**Checkpoint**: CP-4 (Day 3 midday): all scenarios pass scripted e2e; feature freeze.

---

## Phase 12: Polish, Documentation, Traceability, Evidence, Release and Submission

**Purpose**: Cross-cutting validation and the reviewer-facing deliverables. Release readiness is blocked until mandatory validation completes.

- [ ] T126 [P] Write the repeat-run determinism test tests/e2e/test_determinism.py (same stage executions and committed audit order per Spec §Glossary, timestamps/IDs excepted)
  - **Obj**: Reproducible deterministic runs · **Req**: NFR-DET-001, SC-010 · **Scn**: — · **ADR**: ADR-003
  - **Paths**: `tests/e2e/test_determinism.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Determinism test · **TDD**: TDD impractical because repeatability is a property of complete scenario runs; commit ordering was test-first in T049. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_determinism.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Two scripted runs of each scenario compare equal · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T127 [P] Implement the traceability checker tools/trace/build_matrix.py (spec IDs, tasks.md references, pytest req markers, JUnit, docs `satisfies:`, evidence manifests; orphan tests and orphan modules; staleness) with tests in tests/tooling/test_build_matrix.py
  - **Obj**: Requirement → … → evidence matrix with orphan detection · **Req**: FR-OBS-010, SC-007, FR-OBS-008, CON X · **Scn**: — · **ADR**: ADR-018
  - **Paths**: `tools/trace/build_matrix.py`; `tests/tooling/test_build_matrix.py`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Checker producing docs/traceability.md (EV-008) and JSON · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/tooling/test_build_matrix.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: `--check` fails on: C/D requirement without test or doc/evidence; test without requirement tag; src module not referenced by any task; evidence older than its source hash · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T128 [P] Write the automated quickstart test tests/e2e/test_quickstart.py and update specs/001-agentic-sdlc-url-shortener/quickstart.md from 'planned' to 'validated' with recorded outcomes
  - **Obj**: Documentation consistent with behavior · **Req**: NFR-DOC-001, PVT-009 · **Scn**: — · **ADR**: ADR-018
  - **Paths**: `tests/e2e/test_quickstart.py`; `specs/001-agentic-sdlc-url-shortener/quickstart.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Quickstart test · **TDD**: TDD impractical because it verifies documentation against the finished system; each command's behavior was test-first in its implementing task. First run recorded in the TDD Evidence Log (pass or fail); any defect found gets its own red test before the fix (CON IV) · **Validate**: `uv run pytest tests/e2e/test_quickstart.py -q`
  - **Docs**: quickstart.md status updated · **Trace**: default · **Risk**: —
  - **Done**: 100% of quickstart commands executed against a fresh var/; every documented expectation matched · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T129 [P] Measure PVT-001/PVT-002 (non-gating) with tools/perf/measure.py and record docs/evidence/performance.md labeled as demonstration measurements
  - **Obj**: Demonstration performance data · **Req**: PVT-001, PVT-002, NFR-PRF-001, NFR-PRF-002, SC-009, A-009 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `tools/perf/measure.py`; `docs/evidence/performance.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Measurement report · **TDD**: N/A — measurement (non-gating) · **Validate**: `uv run python tools/perf/measure.py`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: p95 for redirect and create at 50 clients recorded with environment description and 'demonstration' label · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T130 [P] Write docs/architecture.md (planes, components, trust boundaries, graph, ADR index links)
  - **Obj**: Architecture overview deliverable · **Req**: CST-003, NFR-MNT-001 · **Scn**: — · **ADR**: ADR-001..ADR-019
  - **Paths**: `docs/architecture.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Architecture doc · **TDD**: N/A — documentation · **Validate**: Review against ADR-004 topology; `satisfies:` front matter present
  - **Docs**: New · **Trace**: default · **Risk**: —
  - **Done**: Matches implemented package layout (T009 green) · **Verified by**: T127 traceability check (satisfies: front matter) and T146 docs review · **Human**: default
- [ ] T131 [P] Write docs/threat-model.md (STRIDE per TB-1..TB-6; controls; accepted risks incl. unauthenticated redirect volume → BL-13)
  - **Obj**: Threat model deliverable · **Req**: NFR-SEC-003, CON V · **Scn**: — · **ADR**: ADR-010, ADR-008
  - **Paths**: `docs/threat-model.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Threat model · **TDD**: N/A — documentation · **Validate**: Review: every NFR-SEC-003 threat has a control or accepted risk
  - **Docs**: New · **Trace**: default · **Risk**: —
  - **Done**: Published · **Verified by**: T127 traceability check and T146 docs review · **Human**: default
- [ ] T132 [P] Write docs/testing.md (portfolio, TDD protocol, fault injection, where TDD was impractical, how to run)
  - **Obj**: Testing approach deliverable · **Req**: CST-003, NFR-TST-001, CON IV · **Scn**: — · **ADR**: ADR-018
  - **Paths**: `docs/testing.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Testing doc · **TDD**: N/A — documentation · **Validate**: Review
  - **Docs**: New · **Trace**: default · **Risk**: —
  - **Done**: Published · **Verified by**: T127 traceability check and T146 docs review · **Human**: default
- [ ] T133 [P] Write docs/limitations.md (BL-01..BL-13, residual risks from ADRs and threat model, demonstration-only metrics, analytics write-failure limitation, key rotation)
  - **Obj**: Limitations and residual risks deliverable · **Req**: CST-003, CST-008, CON XI condition 8 · **Scn**: — · **ADR**: ADR-019, ADR-010
  - **Paths**: `docs/limitations.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Limitations doc · **TDD**: N/A — documentation · **Validate**: Review: every BL item and ADR residual risk listed
  - **Docs**: New · **Trace**: default · **Risk**: —
  - **Done**: Published · **Verified by**: T127 traceability check and T146 docs review · **Human**: default
- [ ] T134 Complete README.md (setup, architecture overview, testing approach, limitations, trade-offs, 'How AI assistance was used and governed')
  - **Obj**: Reviewer-facing entry point · **Req**: CST-003, CST-009 · **Scn**: — · **ADR**: —
  - **Paths**: `README.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T130, T132, T133, T131 · **Parallel**: no
  - **Artifact**: README · **TDD**: N/A — documentation · **Validate**: T128 test covers README setup commands
  - **Docs**: README.md · **Trace**: default · **Risk**: —
  - **Done**: All six sections complete · **Verified by**: T128 quickstart test and T146 docs review · **Human**: default
- [ ] T135 Write the reviewer navigation guide docs/reviewer-guide.md (30-minute path; assessment section → requirement → evidence map by section reference only)
  - **Obj**: Reviewer navigation · **Req**: PVT-009, SC-010, CST-004 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/reviewer-guide.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T134 · **Parallel**: no
  - **Artifact**: Guide · **TDD**: N/A — documentation · **Validate**: Review; no confidential assessment text
  - **Docs**: New · **Trace**: default · **Risk**: —
  - **Done**: Every assessment section reference maps to evidence · **Verified by**: T127 traceability check (every reference resolves) and T146 docs review · **Human**: default
- [ ] T136 Implement `orch release check` in src/orchestrator/cli/release_check.py (scans, traceability --check, coverage, audit verify of evidence runs) writing a draft docs/release-readiness.md with CON XI conditions; tests in tests/release/test_release_check.py
  - **Obj**: Repository-level release-readiness validation · **Req**: FR-GOV-010, FR-GOV-012, PVT-007, PVT-012, CON XI · **Scn**: — · **ADR**: ADR-009
  - **Paths**: `src/orchestrator/cli/release_check.py`; `tests/release/test_release_check.py`; `docs/release-readiness.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T127, T126, T128 · **Parallel**: no
  - **Artifact**: Release check + draft report · **TDD**: TDD-8 · **Validate**: `uv run pytest tests/release/test_release_check.py -q`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Report lists each condition with evidence path or FAIL reason; mandatory FAIL → overall FAIL · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T137 [P] Write docs/engineering-summary.md aggregating the three scenario run summaries (ST-13), plan rationale, trade-offs, validation results, assumptions, limitations
  - **Obj**: Final engineering summary · **Req**: FR-ORC-026 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/engineering-summary.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T133 · **Parallel**: yes
  - **Artifact**: Summary · **TDD**: N/A — documentation · **Validate**: Review: every FR-ORC-026 element present with evidence links
  - **Docs**: New · **Trace**: default · **Risk**: —
  - **Done**: Published · **Verified by**: T127 traceability check (evidence links resolve) and T146 docs review · **Human**: default
- [ ] T138 [P] Create docs/evidence/index.md mapping each evidence type to artifact path and source (run ID or test report)
  - **Obj**: Evidence navigation · **Req**: SC-002, SC-003, CON XI condition 10 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/evidence/index.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T125 · **Parallel**: yes
  - **Artifact**: Evidence index skeleton · **TDD**: N/A — documentation · **Validate**: Review
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Rows for every evidence type in EV-* tasks · **Verified by**: T127 traceability check (evidence manifests and hashes) and T149 gate evaluation · **Human**: default
- [ ] T139 Assemble requirement-to-test traceability evidence (EV-008) and architecture-decision evidence (ADR ↔ code/test links) in docs/evidence/index.md
  - **Obj**: Traceability and ADR evidence · **Req**: SC-007, FR-OBS-010, NFR-MNT-001 · **Scn**: — · **ADR**: ADR-001..ADR-019
  - **Paths**: `docs/evidence/index.md`; `docs/traceability.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T138, T127 · **Parallel**: no
  - **Artifact**: Evidence rows · **TDD**: N/A — evidence assembly · **Validate**: `uv run python tools/trace/build_matrix.py --check` exit 0
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Matrix linked; each ADR row cites implementing modules and validating tests · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T140 Assemble approval evidence (incl. escalation evidence, L4), policy-version evidence and compliance-evaluation evidence from recorded runs and the SCN-B escalation test in docs/evidence/index.md
  - **Obj**: Governance evidence · **Req**: FR-GOV-001, FR-GOV-006, FR-OBS-002 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/evidence/index.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T139 · **Parallel**: no
  - **Artifact**: Evidence rows · **TDD**: N/A — evidence assembly · **Validate**: Each row cites a run ID + event seq range that verifies
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: All three evidence types linked · **Verified by**: T127 traceability check and T149 gate evaluation · **Human**: default
- [ ] T141 Assemble failed-policy blocking, approved-exception and compensating-control evidence (tests + SCN-C option B run) in docs/evidence/index.md
  - **Obj**: Compliance enforcement evidence · **Req**: FR-GOV-007, FR-GOV-008, FR-GOV-017, SC-008 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/evidence/index.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T140 · **Parallel**: no
  - **Artifact**: Evidence rows · **TDD**: N/A — evidence assembly · **Validate**: Rows cite test reports and run events
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: All three evidence types linked · **Verified by**: T127 traceability check and T149 gate evaluation · **Human**: default
- [ ] T142 Assemble change-request and impact-analysis evidence (CR-001..CR-003, contract Change Records, SCN-B impact analysis) in docs/evidence/index.md
  - **Obj**: Change-control evidence · **Req**: FR-GOV-009, SCN-B-AC1 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/evidence/index.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T141 · **Parallel**: no
  - **Artifact**: Evidence rows · **TDD**: N/A — evidence assembly · **Validate**: Review
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Linked · **Verified by**: T127 traceability check and T149 gate evaluation · **Human**: default
- [ ] T143 Assemble state-transition, sequential-path, parallel-path and synchronization evidence (timelines and spans with overlapping intervals) in docs/evidence/index.md
  - **Obj**: Non-linear orchestration evidence · **Req**: FR-ORC-005, FR-ORC-006, FR-ORC-037, FR-ORC-038, FR-ORC-039 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/evidence/index.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T142 · **Parallel**: no
  - **Artifact**: Evidence rows · **TDD**: N/A — evidence assembly · **Validate**: Rows cite span intervals proving overlap
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Linked · **Verified by**: T127 traceability check and T149 gate evaluation · **Human**: default
- [ ] T144 Assemble retry, rollback/compensation, safe-stop, resume and replanning evidence in docs/evidence/index.md
  - **Obj**: Reliability evidence · **Req**: FR-ORC-014, FR-ORC-017, FR-ORC-018, FR-ORC-019, FR-ORC-020, SC-005, SC-006 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/evidence/index.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T143 · **Parallel**: no
  - **Artifact**: Evidence rows · **TDD**: N/A — evidence assembly · **Validate**: Rows cite fault-injection runs and test reports
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Linked · **Verified by**: T127 traceability check and T149 gate evaluation · **Human**: default
- [ ] T145 Record measured demonstration metrics (`orch metrics` incl. MTTR, population, exclusions, unrecovered count) in docs/evidence/metrics.md
  - **Obj**: Measured demonstration metrics · **Req**: FR-OBS-006, FR-OBS-007, NFR-RCV-002 · **Scn**: — · **ADR**: ADR-011
  - **Paths**: `docs/evidence/metrics.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T144 · **Parallel**: no
  - **Artifact**: Metrics evidence · **TDD**: N/A — evidence assembly · **Validate**: Values reproduce from `orch metrics` on the evidence DB
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Labeled 'demonstration'; nothing presented as production statistics · **Verified by**: Own tests/command (see Validate) · **Human**: default
- [ ] T146 Perform and record the release documentation review (docs vs observed behavior) in docs/release-readiness.md
  - **Obj**: Docs-drift release review · **Req**: NFR-DOC-001 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/release-readiness.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T134, T135, T137, T145 · **Parallel**: no
  - **Artifact**: Review record · **TDD**: N/A — review · **Validate**: Discrepancy list with resolution per item
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: 0 unresolved discrepancies or each listed as a FAIL reason · **Verified by**: T150 human decision (CEX-001) and T127 traceability check · **Human**: default
- [ ] T147 HUMAN: Time a fresh clone → setup → tests → three scenarios run following README, and record the result in docs/evidence/fresh-setup.md
  - **Obj**: PVT-009 evidence · **Req**: PVT-009, NFR-RUN-001, SC-010 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/evidence/fresh-setup.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T146 · **Parallel**: no
  - **Artifact**: Timing record · **TDD**: N/A — human decision or action (no code) · **Validate**: Recorded start/end times
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: < 30 minutes, or recorded as a FAIL reason · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner (or a delegated human reviewer)
- [ ] T148 Run `orch release check` and fill CP-5 in docs/scope-control.md
  - **Obj**: Release check executed (blocks readiness until mandatory validation completes) · **Req**: CON XI; Plan §14.5 · **Scn**: — · **ADR**: —
  - **Paths**: `docs/scope-control.md`; `docs/release-readiness.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T136, T147, T129 · **Parallel**: no
  - **Artifact**: Release check output + CP-5 row · **TDD**: N/A — execution · **Validate**: `uv run orch release check`
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Report complete; CP-5 decision recorded by the human owner · **Verified by**: Own tests/command (see Validate) · **Human**: Human owner records the CP-5 decision
- [ ] T149 Prepare evidence references for every gate in specs/001-agentic-sdlc-url-shortener/gates/release-evidence-gates.md (agent adds evidence paths; human marks gates)
  - **Obj**: Evidence gates evaluated · **Req**: Governance §6, CON X · **Scn**: — · **ADR**: —
  - **Paths**: `specs/001-agentic-sdlc-url-shortener/gates/release-evidence-gates.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T148 · **Parallel**: no
  - **Artifact**: Evidence references per gate · **TDD**: N/A — evaluation · **Validate**: Each GATE line has an evidence path or a FAIL note
  - **Docs**: None · **Trace**: default · **Risk**: Agents must not mark gates
  - **Done**: Human owner marks satisfied gates [x] · **Verified by**: T150 human decision (CEX-001) · **Human**: REQUIRED — human owner marks gates
- [ ] T150 HUMAN: Release sign-off in docs/release-readiness.md (approver, timestamp, decision; truthful FAIL is acceptable)
  - **Obj**: Release readiness decided by a human · **Req**: FR-GOV-011, Governance §6, CON III · **Scn**: — · **ADR**: —
  - **Paths**: `docs/release-readiness.md`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T149 · **Parallel**: no
  - **Artifact**: Signed decision · **TDD**: N/A — human decision or action (no code) · **Validate**: Signature line present
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Decision recorded · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only
- [ ] T151 HUMAN: Create and push the annotated tag `assessment-submission-v1.0` on the signed commit; confirm CI is green on it
  - **Obj**: Final submission · **Req**: CST-009, CON III · **Scn**: — · **ADR**: —
  - **Paths**: (git tag) assessment-submission-v1.0; `.github/workflows/ci.yml`
  - **Pre**: Phase entry criteria met; ADR-001..ADR-019 accepted (Human Gate 4) · **Deps**: T150 · **Parallel**: no
  - **Artifact**: Annotated tag on GitHub · **TDD**: N/A — human decision or action (no code) · **Validate**: `git ls-remote --tags origin assessment-submission-v1.0`; CI run link
  - **Docs**: None · **Trace**: default · **Risk**: —
  - **Done**: Tag on remote; CI green · **Verified by**: CEX-001: recorded human decision (approver, timestamp, artifact version) in the decision/audit log; existence confirmed by T127 traceability check · **Human**: REQUIRED — human owner only (outward-facing)

**Checkpoint**: CP-5: release check executed; readiness ready for the human decision.

---

## Timebox and Scope Control

| Day | Phases | Checkpoint task | Exit condition |
|-----|--------|-----------------|----------------|
| Day 1 | 0–3 | T041 (CP-1) | Baseline green, drift-free, tagged `shortener-baseline-v1` |
| Day 2 AM | 4–5 | T062 (CP-2, midday) | Engine runs a full fixture graph with gates and policy blocking |
| Day 2 PM | 6–8 | T090 (CP-3) | Reliability, replanning, interruption suites green |
| Day 3 AM | 9–11 | T125 (CP-4, midday) | All scenarios pass scripted e2e; recorded runs done; feature freeze |
| Day 3 PM | 12 | T148 (CP-5) | Release check executed; readiness ready for the human decision |

**Must-have scope**: Plan §14.1 must-have list (CST-008 must-have + acceptance-criteria variants + G-SECURITY + compensation + traceability check) plus CR-003 additions (FR-GOV-017, FR-OBS-010, NFR-DOC-001, CST-009, SCN-A-AC6).  
**Deferred scope** (disclosed in docs/limitations.md, no tasks here): BL-01..BL-13.  
**Pre-agreed reductions** if CP-2/CP-3 slip (Plan §14.1): SCN-B undeclared-scope by integration test only (already the plan here); minimal doc templates for ST-10a/b; PVT-006 re-scope only by a recorded human change decision.  
**Stop conditions**: STOP-1 constitution violation or CRITICAL analysis finding; STOP-2 a requirement cannot be met as specified (e.g. PVT-003) — report with evidence, never weaken a test; STOP-3 evidence would require fabrication; STOP-4 checkpoint missed by > ½ day after reductions; STOP-5 end of timebox → freeze and report honestly.

### Critical path (computed from task dependencies; longest chain)

T001 → T003 → T004 → T005 → T008 → T009 → T010 → T014 → T022 → T024 → T043 → T045 → T047 → T049 → T050 → T051 → T057 → T058 → T059 → T060 → T062 → T063 → T064 → T065 → T067 → T068 → T075 → T076 → T077 → T078 → T080 → T081 → T082 → T084 → T085 → T086 → T090 → T093 → T094 → T095 → T097 → T098 → T100 → T101 → T102 → T103 → T104 → T105 → T106 → T107 → T109 → T110 → T111 → T112 → T114 → T115 → T116 → T118 → T119 → T120 → T121 → T122 → T123 → T124 → T125 → T138 → T139 → T140 → T141 → T142 → T143 → T144 → T145 → T146 → T147 → T148 → T149 → T150 → T151

## Dependencies and Execution Order

### Phase dependencies

- Phase 0 → Phase 1 → Phase 2 (blocks all stories) → Phase 3 (US1, MVP) → CP-1.
- Phase 4 (US2 core) needs Phase 2; Phase 5 (US3) needs Phase 4; Phase 6 (US2 reliability/agents) needs CP-2 and the baseline tag; Phase 7 (US5) needs CP-3; Phase 8 (US4) needs Phase 7.
- Scenario phases run in order SCN-A → SCN-B → SCN-C because each change set is authored against the previous release (R0 → R1 → R2 → R3).
- Phase 12 needs CP-4; human sign-off and the submission tag are last.

### Synchronization points

- T040 — HUMAN: Review the baseline and create the annotated tag `shortener-baseline-v1` (R0 source; PD-009)
- T041 — HUMAN: Checkpoint CP-1 decision in docs/scope-control.md (continue / apply reductions / stop)
- T062 — HUMAN: Checkpoint CP-2 decision in docs/scope-control.md (engine + gates + policy green?)
- T090 — HUMAN: Checkpoint CP-3 decision in docs/scope-control.md (reliability, replanning, interruption suites green?)
- T125 — HUMAN: Checkpoint CP-4 decision in docs/scope-control.md (scenario e2e green; feature freeze)
- T148 — Run `orch release check` and fill CP-5 in docs/scope-control.md
- T150 — HUMAN: Release sign-off in docs/release-readiness.md (approver, timestamp, decision; truthful FAIL is acceptable)

### Human-only tasks

- T001 — Review the 19 requirements-quality checklists in specs/001-agentic-sdlc-url-shortener/checklists/ and record the outcome
- T003 — Approve the task plan specs/001-agentic-sdlc-url-shortener/tasks.md (task-plan approval gate, post-analyze)
- T040 — Review the baseline and create the annotated tag `shortener-baseline-v1` (R0 source; PD-009)
- T041 — Checkpoint CP-1 decision in docs/scope-control.md (continue / apply reductions / stop)
- T062 — Checkpoint CP-2 decision in docs/scope-control.md (engine + gates + policy green?)
- T090 — Checkpoint CP-3 decision in docs/scope-control.md (reliability, replanning, interruption suites green?)
- T105 — Review changesets/scn-a/normal/ and record its SHA-256 in changesets/approved.lock.yaml
- T109 — Execute recorded SCN-A runs interactively (normal and late-ambiguity) and decide every gate with your own keys; then export evidence with `orch evidence export`
- T114 — Review and lock changesets/scn-b/normal, defective and undeclared-scope in changesets/approved.lock.yaml
- T118 — Execute recorded SCN-B runs interactively (normal and defective) and export evidence
- T121 — Review and lock changesets/scn-c/aggregate-daily in changesets/approved.lock.yaml
- T124 — Execute recorded SCN-C runs interactively (option A, and option B with the real exception path) and export evidence
- T125 — Checkpoint CP-4 decision in docs/scope-control.md (scenario e2e green; feature freeze)
- T147 — Time a fresh clone → setup → tests → three scenarios run following README, and record the result in docs/evidence/fresh-setup.md
- T148 — Run `orch release check` and fill CP-5 in docs/scope-control.md
- T150 — Release sign-off in docs/release-readiness.md (approver, timestamp, decision; truthful FAIL is acceptable)
- T151 — Create and push the annotated tag `assessment-submission-v1.0` on the signed commit; confirm CI is green on it

### Parallel execution examples

- Phase 1: T006, T007, T011, T013
- Phase 2: T014, T015, T016, T018
- Phase 3: T025, T026, T029, T032, T036, T037, T039
- Phase 4: T043, T044
- Phase 5: T051, T052, T054, T055, T056, T061
- Phase 6: T066, T069, T071, T073, T074, T079, T083, T086, T087, T088, T089
- Phase 7: T091, T092, T093, T096
- Phase 9: T107, T108
- Phase 10: T112, T113, T116, T117
- Phase 11: T123
- Phase 12: T126, T127, T128, T129, T130, T131, T132, T133, T137, T138

## Implementation Strategy

1. **MVP = Phase 0–3 (US1)**: a working, tested, contract-conformant shortener and the tagged brownfield baseline.
2. **Engine increment = Phases 4–6**: governed orchestration with fork/join, gates, policy, recovery and replanning (US2, US3).
3. **Verification increment = Phases 7–8**: reconstruction, metrics/MTTR and release readiness (US5, US4).
4. **Scenario increment = Phases 9–11**: SCN-A, SCN-B, SCN-C through the engine, with human-decided recorded runs.
5. **Release increment = Phase 12**: traceability, documentation, evidence, release check, human sign-off, submission tag.

## Requirement Coverage

All 156 requirement IDs found in spec.md (FR, NFR, SC, SCN-x-ACn, CST-003/009, PVT) are referenced by at least one task (checked by the generator).

## TDD Evidence Log

Append one line per red phase: `T### | test id | observed failure (first line) | date`. Required by CON IV; the traceability checker reads it.

| Task | Test | Observed failure | Date |
|------|------|------------------|------|
