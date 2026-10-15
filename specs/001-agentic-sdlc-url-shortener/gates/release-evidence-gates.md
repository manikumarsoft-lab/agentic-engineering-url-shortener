# Evidence and Readiness Gates: Agentic Software Engineering System: URL Shortener

**Purpose**: Objectively verifiable checks on artifacts, behavior and evidence that can be
evaluated only after implementation starts. They complement the requirements-quality checklists
in [`../checklists/`](../checklists/), which gate `/speckit-implement`.
**Created**: 2026-10-15
**Feature**: [spec.md](../spec.md) · [plan.md](../plan.md) · [ADRs](../../../docs/adr/README.md)

**Location**: this file is deliberately outside `checklists/` (human decision, 2026-10-15), so
evidence items that cannot pass before implementation do not block `/speckit-implement`. They are
evaluated at `/speckit-converge`, at release readiness and before submission.

**Rules**:
- Mark a gate `[x]` only when its **Evidence** exists from actual execution and its **Pass when**
  criterion holds. Record the evidence path or command output reference inline.
- A gate is never marked from illustrative, scripted-only, AI-backed or hand-edited output (CON X).
- `[Mandatory]` gates block release readiness (Governance §6). `[Optional]` gates are enhancements.
- Phase: **C** = continuous during implementation and converge · **R** = release readiness · **S** = submission.
- Status at creation: **nothing is implemented; every gate is unchecked.**

## Orchestration and State

- [ ] GATE-001 [C] **Non-linear execution.** Evidence: timeline and spans of a recorded scenario run. Pass when: at least two F1 nodes and both F2 nodes have overlapping attempt intervals, and SP-1/SP-2 release only after every predecessor succeeded. Fails when: every attempt in every run is strictly sequential. [D01] [D04] [Mandatory] (FR-ORC-006, FR-ORC-037/038)
- [ ] GATE-002 [C] **Persistent state.** Evidence: interruption test report. Pass when: after killing the orchestrator mid-node and restarting, run, node, gate and artifact state read from the database equals the pre-kill state, and the run is `SAFE_STOPPED (interrupted)`. Fails when: any state exists only in memory. [D02] [Mandatory] (FR-ORC-011, PD-011)
- [ ] GATE-003 [C] **Dependency representation.** Evidence: definition tests. Pass when: the engine executes order solely from `workflow-graph.v2.yaml`, and a fixture with a changed `depends_on` edge changes execution order. Fails when: stage order is hard-coded. [D03] [Mandatory] (FR-ORC-005, ADR-005)
- [ ] GATE-004 [C] **Synchronization under suspension.** Evidence: SCN-A late-ambiguity run timeline. Pass when: SP-1 stays unreleased while ST-11a is `SUSPENDED` and releases only after it succeeds. [D04] [Mandatory] (FR-ORC-039, SCN-A-AC4)
- [ ] GATE-005 [C] **Decision lineage.** Evidence: `GET /trace/requirements/{id}` and decisions for the SCN-C run. Pass when: every decision has bound and affected artifact versions, and the chain from the clarification answer to the re-versioned artifacts is non-empty. [D05] [Mandatory] (FR-ORC-013, SCN-C-AC3/4)
- [ ] GATE-006 [C] **Dynamic replanning.** Evidence: replanning test report and SCN-C timeline. Pass when: unaffected nodes' attempt counts are unchanged, stale nodes re-ran, and bound approvals were revoked and re-requested (SC-006 at 100%). [D21] [Mandatory] (FR-ORC-020/021)

## Governance, Policy and Change Control

- [ ] GATE-007 [C] **Approval enforcement.** Evidence: governance test report and audit events. Pass when: approval with an agent key returns 403 with `GATE_DECISION_REFUSED`/`AUTH_REFUSED` audited, the engine-level actor-type check refuses agent actors, and the count of `APPROVED` gates without a human decision record is 0. [D06] [Mandatory] (FR-GOV-003, SC-011)
- [ ] GATE-008 [C] **No approval from silence.** Evidence: timeout tests and scenario timelines. Pass when: every gate deadline produced `GATE_TIMED_OUT` → `SAFE_STOPPED` ("no decision"), and no `TIMED_OUT → APPROVED` transition exists. [D15] [Mandatory] (FR-GOV-002, FR-GOV-014, SC-004)
- [ ] GATE-009 [C] **Policy evaluated and versioned.** Evidence: run records and `POLICY_EVALUATED` events. Pass when: 100% of runs record `policy_set_version`, 100% of evaluations carry it, and every applicable check has exactly one outcome per evaluation. [D07] [D08] [Mandatory] (FR-GOV-005/006)
- [ ] GATE-010 [C] **Compliance failure blocks progression.** Evidence: `test_release_blocked_by_mandatory_fail`. Pass when: after an injected mandatory FAIL, no downstream node starts, the run is `SAFE_STOPPED` with `policy_fail:<check>`, and G-RELEASE never opens. [D09] [Mandatory] (FR-GOV-007, Plan §9.3)
- [ ] GATE-011 [C] **Exceptions are human-approved and complete.** Evidence: exception records. Pass when: 0 `APPROVED` exceptions lack approving authority (approver role), compensating control, approval timestamp, or expiry/review condition; 0 were approved by an agent; and 0 exceptions were approved by the key identity that requested them, with every such attempt refused and audited. [D10] [D11] [Mandatory] (FR-GOV-008, FR-GOV-017, Governance §2)
- [ ] GATE-012 [C] **Expired exception fails readiness.** Evidence: `test_readiness_fail_lists_blocking_reasons`. Pass when: an exception that expires before ST-12 yields REL-003 FAIL and assessment FAIL, and `ready` is refused. [D12] [Mandatory] (SC-008)
- [ ] GATE-013 [C] **Impact analysis precedes change.** Evidence: SCN-B timeline and repository change log. Pass when: in every brownfield run the `impact-analysis` artifact timestamp precedes ST-08 start, and every post-approval change to spec, plan, contracts, ADRs or policy has a CR with impact analysis. [D13] [Mandatory] (FR-GOV-009, SCN-B-AC1)
- [ ] GATE-014 [C] **No unapproved architecture, schema, security or workflow change.** Evidence: `git log` for `specs/**/contracts/`, `docs/adr/`, `policy/`, `src/**/migrations` and security modules. Pass when: every such commit references an approved CR, ADR or G-DESIGN decision ID. [D14] [Mandatory] (CON VI)

## Reliability and Recovery

- [ ] GATE-015 [C] **Bounded retries.** Evidence: audit events across all recorded runs and tests. Pass when: attempts per node ≤ 3 and 0 `RETRY_SCHEDULED` events follow a permanent classification. [D16] [Mandatory] (FR-ORC-014, PVT-004)
- [ ] GATE-016 [C] **Valid rollback claims.** Evidence: SCN-B defective-variant run. Pass when: every `ROLLBACK_COMPLETED` has workspace-disposal evidence, staging still serves R1, and the main working tree hash is unchanged. [D17] [Mandatory] (FR-ORC-035, SCN-B-AC4)
- [ ] GATE-017 [C] **Compensation present.** Evidence: injected smoke-failure run. Pass when: `COMPENSATION_COMPLETED` exists, the previous release passes smoke, non-rollbackable effects are listed, and a G-CORRECTIVE decision is recorded. A compensation-failure test ends `SAFE_STOPPED` with staging marked degraded. [D18] [Mandatory] (FR-ORC-042)
- [ ] GATE-018 [C] **Safe-stop on every trigger.** Evidence: reliability suite. Pass when: each FR-ORC-018 trigger plus rework limit, compensation failure, scheduler stall and startup interruption ends in `SAFE_STOPPED` with a reason code and no node `RUNNING`. [D19] [Mandatory] (FR-ORC-018, Plan §6.1)
- [ ] GATE-019 [C] **Resume behavior.** Evidence: interruption tests (PVT-006). Pass when: one test per stage boundary resumes, by approver action, to the same terminal outcome as an uninterrupted run, with no duplicate side effects. [D20] [Mandatory] (FR-ORC-019, NFR-RCV-001)

## Observability and Evidence Integrity

- [ ] GATE-020 [C] **Complete audit evidence.** Evidence: audit completeness test and `orch audit verify`. Pass when: 100% of transitions and decisions in scenario runs have schema-valid events with all required fields (PVT-008), and every evidence run's hash chain verifies. [D22] [Mandatory] (FR-OBS-002/003/004)
- [ ] GATE-021 [R] **No fabricated results.** Evidence: `docs/evidence/**/manifest.json`, audit head hashes, metric outputs. Pass when: every evidence file's hash matches its exported source, every manifest's audit head hash verifies against the database, 0 evidence items come from `test`-labeled or `ai_backed` runs, and every metric output carries `measurement_class: demonstration`. [D23] [Mandatory] (CON X, FR-ORC-029, FR-OBS-007)
- [ ] GATE-022 [C] **Specification and tests precede implementation.** Evidence: git history and the red-phase entries in the task log. Pass when: no `src/` file is committed before the plan approval commit, and for each task the recorded red-phase failure output predates its implementing commit. [D24] [Mandatory] (CON I, CON IV)
- [ ] GATE-023 [R] **No undocumented architecture drift.** Evidence: contract drift tests, import-boundary lint, ADR index. Pass when: drift tests and boundary lint are green, and every structural divergence from ADR-001 to ADR-019 is covered by a superseding ADR. [D25] [Mandatory] (CON VII)

## Traceability

- [ ] GATE-024 [R] **No orphan requirements.** Evidence: `tools/trace/build_matrix.py --check`. Pass when: 0 C/D requirements lack a test or a doc/evidence link (SC-007). [D26] [Mandatory]
- [ ] GATE-025 [R] **No orphan tasks.** Evidence: the same tool run over `tasks.md`. Pass when: 0 tasks lack requirement and test references. [D27] [Mandatory]
- [ ] GATE-026 [R] **No orphan implementation.** Evidence: the same tool run. Pass when: 0 modules in `shortener.domain`, `orchestrator.engine`, `orchestrator.policy` or `orchestrator.observability` are not referenced by any task, and the finding is included in EV-008. [D28] [Mandatory] (FR-OBS-010)
- [ ] GATE-027 [R] **No orphan tests.** Evidence: the same tool run (pytest collection). Pass when: 0 collected tests lack a requirement ID tag, and the finding is included in EV-008. [D29] [Mandatory] (FR-OBS-010)
- [ ] GATE-028 [R] **Documentation consistent with behavior.** Evidence: drift tests, doc source-hash check, automated quickstart test report, release-review record. Pass when: contract drift tests are green, 0 docs reference an outdated source hash, the automated quickstart test executed 100% of quickstart commands successfully, and the release review comparing docs to observed behavior records 0 unresolved discrepancies. [D30] [Mandatory] (NFR-DOC-001)
- [ ] GATE-029 [R] **No unsupported completion claims.** Evidence: `tasks.md`, `docs/release-readiness.md`, engineering summaries. Pass when: every "done", "passed" or "complete" claim links an executed test report, a run evidence file or a recorded approval. Claims without evidence: 0. [D31] [Mandatory] (CON XI)

## Release Readiness and Submission

- [ ] GATE-030 [R] **Release checks executed.** Evidence: `orch release check` report. Pass when: dependency and secret scans executed with recorded outputs and 0 high/critical findings or an approved exception (PVT-012); coverage ≥ 85% on the declared scope (PVT-007); all mandatory tests pass; and human sign-off is recorded with approver and timestamp. [Mandatory] (FR-GOV-010/012, Governance §6)
- [ ] GATE-031 [S] **Submission integrity.** Evidence: final commit. Pass when: the secret scan is clean, no assessment source text is committed (CST-004), a fresh-setup run under 30 minutes is recorded (PVT-009), the limitations list includes BL-01 to BL-13, and the README contains the section "How AI assistance was used and governed". [Mandatory] (CST-009)
- [ ] GATE-032 [S] **GitHub evidence present.** Evidence: GitHub repository at the annotated tag `assessment-submission-v1.0`. Pass when: the annotated tag exists on the remote and marks the submission commit, the evidence manifests and docs exist at that commit, and the working tree was clean when it was made. [Mandatory] (CST-009)
- [ ] GATE-033 [S] **Human submission sign-off.** Evidence: signed entry in `docs/release-readiness.md`. Pass when: the final submission decision is recorded by the human owner with a timestamp, and no agent recorded it. [D31] [Mandatory] (CON III)
- [ ] GATE-034 [S] **CI evidence.** Evidence: GitHub Actions run for the tagged submission commit. Pass when: the CI workflow ran the test suite and passed. [Mandatory] (CST-009)

## Detection Coverage Map

| ID | Detection | Requirements-quality items (`checklists/`) | Evidence gates |
|----|-----------|------|------|
| D01 | linear chaining disguised as orchestration | orchestration CHK002, orchestration CHK008 | GATE-001 |
| D02 | missing persistent state | orchestration CHK003 | GATE-002 |
| D03 | missing dependency representation | orchestration CHK001 | GATE-003 |
| D04 | missing synchronization | orchestration CHK002, orchestration CHK009 | GATE-001, GATE-004 |
| D05 | missing decision lineage | orchestration CHK005, scenario-ambiguous CHK004 | GATE-005 |
| D06 | missing approval enforcement | controlled-autonomy CHK002, controlled-autonomy CHK004, human-approvals CHK001 | GATE-007 |
| D07 | missing compliance policy evaluation | compliance-change-control CHK001, compliance-change-control CHK008 | GATE-009 |
| D08 | policy execution without a recorded policy version | compliance-change-control CHK002 | GATE-009 |
| D09 | compliance failure that does not block progression | compliance-change-control CHK009, compliance-change-control CHK014, release-readiness CHK002, scenario-ambiguous CHK009, security CHK016 | GATE-010 |
| D10 | unapproved policy exception | compliance-change-control CHK010, controlled-autonomy CHK011, scenario-ambiguous CHK010 | GATE-011 |
| D11 | missing compensating control | compliance-change-control CHK004 | GATE-011 |
| D12 | expired policy exception | compliance-change-control CHK016, release-readiness CHK002 | GATE-012 |
| D13 | material change implemented without impact analysis | compliance-change-control CHK005, compliance-change-control CHK017, scenario-brownfield CHK002, scenario-brownfield CHK005 | GATE-013 |
| D14 | architecture, schema, security, or workflow change without formal approval | architecture CHK005, compliance-change-control CHK012, scenario-brownfield CHK003, scenario-brownfield CHK005 | GATE-014 |
| D15 | approval inferred from silence | human-approvals CHK007, release-readiness CHK006, scenario-ambiguous CHK009 | GATE-008 |
| D16 | unlimited retries | reliability-recovery CHK007, reliability-recovery CHK008 | GATE-015 |
| D17 | invalid rollback claims | reliability-recovery CHK010, reliability-recovery CHK011, scenario-brownfield CHK004 | GATE-016 |
| D18 | missing compensation | reliability-recovery CHK003, reliability-recovery CHK010, reliability-recovery CHK014 | GATE-017 |
| D19 | missing safe-stop | orchestration CHK011, reliability-recovery CHK004, reliability-recovery CHK012, reliability-recovery CHK014 | GATE-018 |
| D20 | missing resume behavior | human-approvals CHK005, orchestration CHK017, reliability-recovery CHK005, reliability-recovery CHK013 | GATE-019 |
| D21 | missing dynamic replanning | human-approvals CHK004, orchestration CHK006, orchestration CHK010, scenario-ambiguous CHK007, scenario-greenfield CHK008 | GATE-006 |
| D22 | incomplete audit evidence | observability-audit CHK002, observability-audit CHK003, observability-audit CHK010, observability-audit CHK011 | GATE-020 |
| D23 | fabricated results | controlled-autonomy CHK006, controlled-autonomy CHK010, documentation CHK008, documentation CHK009, github-evidence CHK003, human-approvals CHK012, observability-audit CHK006, observability-audit CHK015, orchestration CHK012 | GATE-021 |
| D24 | implementation preceding specification or tests | github-evidence CHK009, testing-tdd CHK001, testing-tdd CHK015 | GATE-022 |
| D25 | undocumented architecture drift | adr CHK007, architecture CHK012, documentation CHK012 | GATE-023 |
| D26 | orphan requirements | requirements-quality CHK006, traceability CHK006 | GATE-024 |
| D27 | orphan tasks | traceability CHK003 | GATE-025 |
| D28 | orphan implementation | traceability CHK007 | GATE-026 |
| D29 | orphan tests | testing-tdd CHK014, traceability CHK008 | GATE-027 |
| D30 | documentation inconsistent with behavior | documentation CHK006, documentation CHK007, release-readiness CHK010, traceability CHK009 | GATE-028 |
| D31 | unsupported completion claims | assessment-submission CHK008, human-approvals CHK006, release-readiness CHK001, release-readiness CHK008, testing-tdd CHK011 | GATE-029, GATE-033 |

Generated from the `[Dnn]` tags in the files on 2026-10-15. Detections with no checklist item or no gate: none.
