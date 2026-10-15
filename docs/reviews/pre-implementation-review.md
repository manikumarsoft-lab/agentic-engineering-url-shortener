&#x20;  # Pre-Implementation Review (2026-10-15)



&#x20;  Agent-performed independent pre-implementation review (2026-10-15). Transcribed by the human owner from screenshots of the original session output; minor wording may differ. Findings dispositioned by the human owner in CR-006 / HD-CUT-001.



Verdict: not captured. The review stated that T003 (task-plan approval) should not be granted against the then-current tasks.md.



Critical Findings

C1. The clarification answer can't change what gets built, so decision lineage breaks in SCN-C. The change set is fixed when the run is submitted (quickstart.md:55, --change-set; change\_set\_ref on the run). T123 says option B plus an approved exception -> "path proceeds", but the only SCN-C change set (aggregate-daily) implements option A, so the run would release code contradicting the recorded decision. gate-decision.schema.json accepts free\_text answers that a deterministic analyst can't interpret; no behavior is defined (= proceeding on a guessed interpretation, SCN-C-AC5).

C2. Impact analysis is computed from the change it is supposed to constrain. ST-05 takes change-set-manifest as input (workflow-graph.v2.yaml:141); CHG-002 checks touched files against components from the same manifest's declared\_components. SCN-B-AC1 and AC5 are proven by circular reasoning.

C3. The late-ambiguity replanning claim contradicts the graph. Plan §11.1 says the answer goes through ST-05 replanning and only ST-11a (+ST-10b) re-run, but G-DESIGN binds impact-analysis, so a new impact-analysis version revokes G-DESIGN and stale closure reruns ST-08 and ST-09 (SC-006 would fail). ST-11a has no input carrying the clarification answer. The injected question is a behavior question that should invalidate the implementation.

C4. The schedule can't be met: 155 tasks, critical path 78 (tasks.md:1289). False dependencies: T110->T109, T119->T118, T075->T068, T084->T082, T063->T062. Change-set authoring (T102, T103, T111, T120) sits on the Day 3 critical path though it only needs the baseline.

C5. A network-dependent, time-varying scanner (SEC-003) sits on every scenario's mandatory path: offline every scenario SAFE\_STOPs (conflicts NFR-RUN-001, PVT-009); online the advisory DB changes over time (breaks NFR-DET-001).



Architectural Weaknesses: asyncio.gather over synchronous agents gives no real concurrency; wait\_for over to\_thread can't kill a thread (fix: subprocesses with process-tree kill, attempt token on writes). Re-promotion and Alembic: release R1 won't recognise revision 0003; staging must not migrate on re-promotion and readiness must not compare heads. orch demo reset rebuilding var/ would delete orchestrator.db, conflicting with FR-OBS-004/AUD-001. Overbuilt: OpenAPI drift normalizer + schemathesis, W3C traceparent + spans table, CI on two OSes.

Orchestration Weaknesses: join/skip semantics not defined in one place; clarify loops unbounded; resume can dead-end after the 3rd attempt (needs approver-granted budget extension); ST-09 300 s timeout too short for full regression incl. PVT-003; NFR-DET-001 only holds with virtual clock and scripted decisions; runtime graph instance v+1 created without approval (FR-GOV-009) - restrict to declared conditional/dynamic nodes; SCN-A-AC4 only via labelled injection.

Governance Weaknesses: decision\_source is client-set (derive server-side); approver keys reachable from the coding-assistant session; changesets/approved.lock.yaml is an editable working-tree file (needs a check only the human can produce, e.g. a signed/annotated tag); agent false negatives can skip G-CLARIFY/G-SECURITY (lexicon needs held-out tests, registry under change control); separation of duties is single-person (disclose); FR-GOV-001 destructive actions not listed.

Testing Weaknesses: no held-out ambiguity corpus; missing negative tests (free-text doesn't proceed; option B + exception yields no contradicting release; timed-out attempt can't write; re-promotion against migrated DB; SC-006 late ambiguity attempt counts unchanged); PVT-006 \~24 full E2E runs on two OSes too costly; 20 "TDD impractical" tasks concentrated on Day 3; traceability --check should run in CI from Phase 1.

Evidence Weaknesses: verification depends on the gitignored DB (export full ordered event log + offline verifier); selection bias (export an index of every run ID incl. failed/aborted); parallelism evidence should be scheduler-level (both nodes READY in same step + join-hold events).



Required Corrections Before Implementation

1\. Bind the change set after the decision (catalog keyed by scenario, option\_id; no approved change set -> FAILED; free\_text reopens clarification or safe-stops; bounded clarify rounds).

2\. Make ST-05 independent of the manifest (requirement + registry + base release import graph; G-DESIGN shows the difference; CHG-002 checks touched files against the analysis).

3\. Fix late-ambiguity routing (answer is input to the raising node, no ST-05 replanning; injected finding affects only threat review; test ST-08/ST-09 not re-run).

4\. Scanner determinism (hash-pinned advisory snapshot; live scan only in orch release check, T136).

5\. Specify: join/skip table; timeout enforcement + attempt fencing; re-promotion without migrating; demo reset never deletes orchestrator.db; decision\_source server-derived; human-only lock files; budget-extension rule for resume.

6\. Re-cut tasks.md: remove false dependencies, run change-set authoring in parallel with Phases 4-6, apply the cut list by recorded human decision.



Q21 cut list (orchestration, governance and all three scenarios preserved)

1\. PVT-006: engine-level interruption at every boundary with stub agents, plus 3 full E2E interruptions (mid-F1, open gate, REL-01).

2\. Drop OpenAPI drift normalizer and schemathesis (T019, drift parts of T035/T099); keep JSON Schema validation and hand-written contract tests.

3\. Drop traceparent and spans (T016, T092); use run\_id correlation and attempt timestamps.

4\. Reduce metrics T093-T095 to per-run counts and a simple MTTR.

5\. CI on one OS.

6\. Merge evidence assembly T138-T145 into one generated evidence index.

7\. Remove G-SECURITY (plan decision PD-007, not a spec requirement).

8\. SCN-C variants: keep A, C (abort) and timeout; show the exception path once (e.g. SEC-003 offline exception), not through option B.

Never cut: transitions + audit, fork/join with sync points, gates (timeout, rework, terminate), policy blocking + exceptions, retry/safe-stop/resume, workspace rollback, staging compensation, stale-closure replanning, and the human's interactive recorded runs of SCN-A, SCN-B and SCN-C.

\--- END ---

