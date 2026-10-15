# Feature Specification: Agentic Software Engineering System: URL Shortener

**Feature Branch**: `main` (no feature branch created, per human instruction; feature directory
`specs/001-agentic-sdlc-url-shortener`)

**Created**: 2026-10-15

**Status**: Draft. AMB-001 to AMB-003 resolved by human decisions HD-001 to HD-003 (2026-10-15).
Pending: `/speckit-clarify`, approval of PVT-001 to PVT-012, and the human specification approval
gate.

**Input**: User description: "Build a production-grade prototype titled 'Agentic Software
Engineering System: URL Shortener'": a governed agentic execution system that turns software
requirements into reviewable engineering outcomes across the SDLC, demonstrated on a URL
shortener service, with three required scenarios (greenfield, brownfield, ambiguous). Full
input retained in the session record of 2026-10-15.

## Source and Classification Conventions

Every requirement, assumption, and target in this document carries a stable identifier and a
**provenance class**:

| Class | Meaning | Change authority |
|-------|---------|------------------|
| **C**: Confirmed | Directly stated by the official assessment (cited as `ASMT §n`) or by the approved feature input (cited as `FI`) | Human owner only, via change control |
| **D**: Derived | Not stated verbatim but necessarily implied by a confirmed requirement or by the ratified constitution (cited as `CON <principle>`) | Human approval at spec gate |
| **A**: Assumption | Reasonable default chosen where sources are silent | Human approval at spec gate; may be revised in Clarify |
| **C (HD)**: Human Decision | A binding decision recorded by the human owner during clarification (cited as `HD-nnn`, with decider and date) | Human owner only, via change control |
| **PVT**: Proposed Validation Target | A numeric or verifiable target proposed where no source supplies one. **Not a confirmed client requirement.** | Requires explicit human approval before being used as a pass/fail criterion |

The official assessment text is confidential and is referenced only by section identifier
(Constitution X).

Identifier scheme: `US-n` user stories · `SCN-A/B/C` required scenarios · `FR-SHR-nnn`
shortener functional · `FR-ORC-nnn` orchestration functional · `FR-GOV-nnn` governance and
policy functional · `FR-OBS-nnn` observability and audit functional · `NFR-<area>-nnn`
non-functional · `PVT-nnn` proposed targets · `A-nnn` assumptions · `CST-nnn` constraints ·
`AMB-nnn` ambiguities · `HD-nnn` human decisions · `EXC-nnn` exclusions · `SC-nnn` success criteria · `EV-nnn`
evidence items.

## System Context *(informative)*

The deliverable consists of two cooperating capabilities:

1. **URL Shortener Service** (demonstration domain): an API-accessible service for creating
   short links, resolving redirects, capturing basic analytics, enforcing expiration and
   validation, and reporting operational health.
2. **Agentic SDLC Orchestration System** (primary capability and the assessment's critical
   differentiator, `ASMT §4.4`): a stateful, governed workflow engine whose stages are
   performed by bounded agents and gated by humans, taking a requirement from ingestion to a
   release-readiness decision and a final engineering summary, with the URL shortener as the
   system under change.

The three required scenarios (SCN-A/B/C) are executions of capability 2 that create or change
capability 1.

### Reference Lifecycle Stages (logical, not an implementation design)

| Stage | Name | Typical owner | Gate type |
|-------|------|---------------|-----------|
| ST-01 | Requirement ingestion | Agent | Entry/exit criteria |
| ST-02 | Requirement normalization | Agent | Entry/exit criteria |
| ST-03 | Ambiguity and requirement-quality detection | Agent | Exit decision: clarify or proceed |
| ST-04 | Human clarification | Human | Conditional mandatory human gate |
| ST-05 | Impact analysis (brownfield and replanning) | Agent | Conditional |
| ST-06 | Task decomposition | Agent | Entry/exit criteria |
| ST-07 | Architecture and design | Agent proposes, human approves | Mandatory human gate |
| ST-08 | Implementation | Agent | Policy gate (change control) |
| ST-09 | Testing | Agent | Exit: executed tests pass |
| ST-10 | Documentation | Agent | Exit: docs current |
| ST-11 | Security and risk validation | Agent | Policy gate (mandatory checks) |
| ST-12 | Release-readiness determination | Agent assesses, human decides | Mandatory human gate |
| ST-13 | Final engineering summary | Agent | Exit: summary complete |

The table lists stages, not execution order; the default graph runs independent stages in parallel and synchronizes them before release readiness (FR-ORC-006, FR-ORC-007).

The required topology properties (sequencing, parallelism, synchronization, conditional
branching) are specified in FR-ORC requirements, not by this table.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - API consumer shortens and resolves links (Priority: P1)

An API consumer submits a long URL, optionally with an expiration, and receives a short link.
Anyone following the short link is redirected to the original destination while the link is
valid; expired, unknown, or invalid links fail clearly and safely. Basic visit analytics are
available for the link.

**Why this priority**: This is the demonstration domain; without it no scenario has a system
under change and no deliverable is "working end-to-end" (`ASMT §5`).

**Independent Test**: Exercise create → resolve → analytics → expire → resolve against a running
service with no orchestration involvement; all outcomes are observable at the service boundary.

**Acceptance Scenarios**:

1. **Given** a well-formed http(s) URL, **When** the consumer requests a short link, **Then**
   a unique short code and full short link are returned, and resolving it redirects to the
   original URL.
2. **Given** a short link created with an expiration in the past relative to resolution time,
   **When** it is resolved, **Then** no redirect occurs and an explicit "expired" outcome,
   distinct from "not found", is returned.
3. **Given** a link that has been resolved N times, **When** the consumer requests its
   analytics, **Then** the visit count equals N and the last-visit time is reported.
4. *(Negative)* **Given** a URL with a disallowed scheme (e.g., `javascript:`, `data:`,
   `file:`), **When** creation is requested, **Then** it is rejected with a validation error
   and no short link is stored.
5. *(Negative)* **Given** an unknown short code, **When** it is resolved, **Then** a "not
   found" outcome is returned and no redirect occurs.

---

### User Story 2 - Software engineer runs a governed orchestration workflow (Priority: P1)

A software engineer submits a requirement to the orchestration system, which creates a
workflow run, normalizes the requirement, checks its quality, plans and executes stages
according to an explicit dependency graph, pauses at human gates, and produces traceable
artifacts and evidence through to a release-readiness outcome.

**Why this priority**: Workflow orchestration is the assessment's critical differentiator
(`ASMT §4.4`).

**Independent Test**: Submit a well-defined requirement; observe that a run is created with a
unique identifier, stages execute in dependency order including at least one parallel
fork/join, the run halts at the design approval gate, and inspection shows full state and
history.

**Acceptance Scenarios**:

1. **Given** a complete, consistent, testable requirement, **When** it is submitted, **Then**
   a workflow run with a unique run identifier is created and its normalized requirement,
   quality-check results, and planned stage graph are inspectable.
2. **Given** a running workflow, **When** two stages have no dependency on each other,
   **Then** they are eligible to run concurrently, and a stage that depends on both starts only
   after both reach a successful exit.
3. **Given** a stage reaches a mandatory human gate, **When** no decision has been recorded,
   **Then** the run remains in an awaiting-approval state and no downstream stage starts.
4. *(Negative)* **Given** a stage whose entry criteria are not satisfied, **When** execution is
   attempted, **Then** the stage does not start and the refusal is recorded with its reason.

---

### User Story 3 - Human reviewer approves, rejects, or clarifies (Priority: P1)

A human reviewer sees pending decisions (clarification questions, design approvals, policy
exceptions, high-impact actions), inspects the evidence behind each, and records approve,
reject, escalate, or a clarification answer. Each decision is attributed and audited and
determines how the workflow proceeds.

**Why this priority**: Controlled autonomy and human ownership are confirmed requirements
(`ASMT §4.7`, `ASMT §7`) and non-waivable constitutional principles (CON III).

**Independent Test**: Drive a run to a gate; record each decision type in separate runs and
verify the resulting state transition and audit record.

**Acceptance Scenarios**:

1. **Given** a pending design approval, **When** the reviewer approves, **Then** the run
   proceeds to dependent stages and the approval (approver, timestamp, artifact version,
   rationale) is recorded.
2. **Given** a pending approval, **When** the reviewer rejects with a reason, **Then** the
   rejected stage returns to rework (or the run terminates, if rework is not possible or the
   reviewer requests termination), and no dependent stage starts.
3. **Given** a pending approval that exceeds its approval timeout, **When** the timeout
   elapses, **Then** the run stays blocked or enters safe-stop and is never treated as
   approved.
4. *(Negative)* **Given** an agent actor, **When** it attempts to record an approval, **Then**
   the attempt is refused and audited.

---

### User Story 4 - Release owner determines release readiness (Priority: P2)

A release owner reviews an automatically assembled release-readiness assessment (requirement
coverage, executed test results, security and policy outcomes, open risks, exceptions,
documentation status, traceability completeness) and records the final go/no-go decision.

**Why this priority**: Release readiness is a confirmed lifecycle stage (`ASMT §4.4`) and a
constitutional gate (CON XI, Governance §6); it depends on US-2 and US-3.

**Independent Test**: Complete a run up to ST-12 once with all checks passing and once with one
mandatory policy check failing; verify a PASS-eligible vs a FAIL assessment and that only a
human decision finalizes the outcome.

**Acceptance Scenarios**:

1. **Given** all mandatory checks pass and no unapproved exceptions exist, **When** the
   assessment is produced, **Then** it is marked "eligible for release", and the release
   becomes "ready" only after the release owner's recorded approval.
2. *(Negative)* **Given** any failing mandatory policy check, unexecuted required test, or
   unapproved or expired exception, **When** the assessment is produced, **Then** it is marked
   FAIL with each blocking reason listed, and the release owner cannot record "ready".

---

### User Story 5 - Assessment reviewer reconstructs and verifies execution (Priority: P2)

An assessment reviewer selects a run (including the three scenario runs) and reconstructs what
happened: the stage graph, every state transition, decisions and approvals, retries,
failures, rollbacks, replanning events, policy outcomes, artifacts with provenance, the
traceability chain, reliability metrics, and the final engineering summary.

**Why this priority**: Reviewers evaluate orchestration effectiveness, auditability, and
defensibility (`ASMT §6`); it depends on runs existing.

**Independent Test**: Given only a run identifier, produce the complete timeline and
traceability chain without access to the agent's conversation history.

**Acceptance Scenarios**:

1. **Given** a completed run identifier, **When** the reviewer inspects it, **Then** an ordered
   timeline of all audited events and the terminal outcome is available.
2. **Given** a requirement identifier, **When** the reviewer traces it, **Then** the linked
   decisions, tasks, artifacts, tests, test results, documentation, and evidence are listed.
3. *(Negative)* **Given** a metric labeled as a demonstration measurement, **When** it is
   displayed, **Then** it is clearly labeled as demonstration data and never as a production
   measurement.

---

### Required Scenario SCN-A - Greenfield capability (Priority: P1)

**Source**: `ASMT §3`, `ASMT §5`, `FI`.

A well-defined new capability moves through Requirement → Decomposition → Design →
Implementation → Testing → Documentation → Validation → Release Readiness.

**Scenario capability (HD-002)**: link expiration plus basic redirect analytics
(FR-SHR-008 to FR-SHR-012), delivered through an orchestrated workflow run (FR-ORC-031).

**Acceptance Criteria**:

1. **SCN-A-AC1**: When the requirement passes all requirement-quality checks (complete,
   internally consistent, testable, within approved policy and architecture boundaries), the
   run proceeds **without** a clarification gate, and records each check performed, its result,
   and the reason clarification was not required.
2. **SCN-A-AC2**: The run records the decomposition (tasks with dependencies and ordering), the
   API and data/schema impacts, and the acceptance criteria derived for the capability.
3. **SCN-A-AC3**: Every produced artifact traces to the originating requirement and to the run.
4. **SCN-A-AC4**: If material ambiguity emerges after decomposition, only the dependent path is
   suspended; unaffected paths continue up to the next synchronization point; governed
   clarification and impact analysis run; after explicit approval the suspended path resumes
   from the correct state (not from the beginning).
5. **SCN-A-AC5** *(Negative)*: A clarification gate MUST NOT be raised artificially for a
   requirement that passed all quality checks; any raised gate must cite the failed check.

**Required evidence**: EV-001, EV-002, EV-003, EV-004, EV-006, EV-007.

---

### Required Scenario SCN-B - Brownfield change (Priority: P1)

**Source**: `ASMT §3`, `ASMT §4.3`, `FI`.

An enhancement, refactor, or defect correction is applied to the existing URL shortener.

**Scenario capability (HD-002)**: custom aliases (FR-SHR-020 to FR-SHR-022) added to the
creation flow of the baseline shortener, delivered through an orchestrated workflow run
(FR-ORC-031).

**Acceptance Criteria**:

1. **SCN-B-AC1**: Before any change is made, the run produces an impact analysis listing
   impacted components, interfaces, data flows, tests, documentation, regression risks, and
   rollout/rollback considerations, and links each to the requirement.
2. **SCN-B-AC2**: Implementation does not start until the impact analysis is complete and the
   change is approved under change control.
3. **SCN-B-AC3**: Pre-existing tests relevant to the impacted areas are executed and pass after
   the change (regression evidence), alongside new tests for the change.
4. **SCN-B-AC4**: If validation fails after the change, the change is rolled back (or
   compensated), and the system returns to its last known-good state with evidence recorded.
5. **SCN-B-AC5** *(Negative)*: A change touching components not listed in the approved impact
   analysis is detected and blocked pending re-analysis and approval.

**Required evidence**: EV-001, EV-002, EV-003, EV-004, EV-005, EV-006, EV-007.

---

### Required Scenario SCN-C - Ambiguous requirement (Priority: P1)

**Source**: `ASMT §3`, `ASMT §4.1`, `FI`.

Incomplete, unclear, or conflicting input is submitted.

**Scenario input (HD-002)**: the request "track who clicks links", which is underspecified
(what "who" means) and conflicts with the no-personal-data constraint (FR-SHR-012, A-005).
Executed through an orchestrated workflow run (FR-ORC-031); the outcome is governed by the
recorded clarification and any policy decision (FR-SHR-023).

**Acceptance Criteria**:

1. **SCN-C-AC1**: The ambiguity is detected and each item is classified (missing information,
   unclear term, internal conflict, or policy conflict) with the affected requirement text.
2. **SCN-C-AC2**: No implementation, design approval, or release stage starts on the affected
   path while the ambiguity is unresolved.
3. **SCN-C-AC3**: A clarification request with specific questions (and suggested options where
   possible) is presented to a human; the answer is recorded as a decision with lineage.
4. **SCN-C-AC4**: After the decision, downstream impact is identified, the affected artifacts are
   re-versioned, and the run resumes at the earliest affected stage.
5. **SCN-C-AC5** *(Negative)*: If clarification is rejected, unanswered beyond timeout, or
   contradicts policy, the run enters safe-stop or terminates with a recorded reason, and never
   proceeds on a guessed interpretation.

**Required evidence**: EV-001, EV-002, EV-003, EV-004, EV-006, EV-007.

---

### Edge Cases

- Two creation requests for the same URL arrive concurrently: both succeed with distinct codes
  unless they share an idempotency key (A-004); no code is ever assigned to two destinations.
- Short-code collision during generation: generation retries within a bound; on exhaustion an
  explicit failure is returned and no partial record exists.
- Persistence is unavailable during creation: an explicit retriable failure is returned; no
  short link is reported as created.
- Persistence is unavailable during redirect: the service reports unavailability rather than
  redirecting to a wrong or stale destination.
- Analytics recording fails during a redirect: the redirect still succeeds (fallback); the
  analytics failure is recorded.
- A destination URL points back to the shortener itself (redirect loop): rejected.
- Extremely long URL, malformed URL, URL with embedded credentials, or non-printable characters:
  rejected with a specific validation reason.
- Expiration supplied in the past, or malformed: rejected at creation.
- The orchestration process is interrupted mid-stage: on restart, the run resumes from
  persisted state; completed idempotent stages are not re-executed; the interrupted stage is
  retried or marked failed according to its failure classification.
- An approval arrives for a stale artifact version (superseded by replanning): it is refused
  and the reviewer is shown the current version.
- An upstream artifact changes while a downstream parallel branch is mid-execution: the
  dependent branch is invalidated or suspended; unaffected branches continue.
- Retry budget exhausted on a mandatory stage: safe-stop with recorded reason.
- A permanent (non-transient) failure is never retried.
- A duplicate approval or duplicate stage-completion event is applied at most once.
- A human approves a policy exception that later expires before release: release readiness
  reverts to FAIL.

## Requirements *(mandatory)*

### Functional Requirements: URL Shortener Service (FR-SHR)

| ID | Class | Requirement | Source |
|----|-------|-------------|--------|
| FR-SHR-001 | C | The service MUST create a short link for a valid destination URL and return the short code and the full short link. | ASMT §2, FI |
| FR-SHR-002 | C | The service MUST validate and normalize destination URLs and reject invalid ones with a specific, machine-readable reason. | FI, CON V |
| FR-SHR-003 | D | Accepted destination schemes MUST be restricted to an allow-list; default `http` and `https` only (A-002). | CON V |
| FR-SHR-004 | D | The service MUST reject destinations that are malformed, exceed the maximum length (PVT-010), contain embedded credentials, or resolve to the shortener's own short-link domain. | CON V |
| FR-SHR-005 | C | Every short code MUST be unique: a code MUST never map to more than one destination, including under concurrent creation. | FI |
| FR-SHR-006 | D | Short codes MUST NOT be sequentially predictable; consecutive creations MUST NOT yield guessable successors. | CON V |
| FR-SHR-007 | C | Resolving an active short code MUST redirect to its destination. | ASMT §2, FI |
| FR-SHR-008 | C | A creator MAY specify an expiration; resolving an expired link MUST NOT redirect and MUST return an outcome distinguishable from "not found". | FI |
| FR-SHR-009 | D | An expiration in the past or a malformed expiration MUST be rejected at creation. | FI |
| FR-SHR-010 | C | The service MUST capture basic analytics per link: total successful redirects and last redirect time, retrievable per short code. | ASMT §2, FI |
| FR-SHR-011 | D | Analytics capture MUST NOT block or fail a redirect; analytics failures MUST be recorded (fallback). | FI, CON VIII |
| FR-SHR-012 | D | Analytics MUST NOT store raw client IP addresses or other personal data (A-005). | CON V |
| FR-SHR-013 | C | Creation requests carrying the same idempotency key and same payload MUST return the original result without creating a second link; the same key with a different payload MUST be rejected as a conflict. | FI, CON VIII |
| FR-SHR-014 | C | Concurrent creation and resolution requests MUST yield correct, non-corrupted results. | FI |
| FR-SHR-015 | C | When persistence is unavailable, creation MUST fail with an explicit retriable error and leave no partial record; resolution MUST report unavailability and MUST NOT redirect to an unverified destination. | FI |
| FR-SHR-016 | C | The service MUST expose operational health distinguishing liveness (process running) from readiness (able to serve, including persistence reachability). | FI |
| FR-SHR-017 | D | Link creation MUST be rate-limited per client (PVT-011); exceeding the limit MUST return an explicit rate-limit outcome. | CON V |
| FR-SHR-018 | D | Error responses MUST NOT expose internal details, stack traces, secrets, or persistence identifiers. | CON V |
| FR-SHR-019 | C | Link creation and analytics retrieval MUST require a valid role-mapped API key (`consumer` or higher-privileged human role); redirect resolution MUST be public. Missing or invalid keys MUST be rejected without revealing whether a link exists. | HD-003, CON V |
| FR-SHR-020 | C | *(SCN-B)* A creator MAY request a custom alias as the short code; if the alias is already in use, creation MUST be rejected as a conflict and the existing mapping MUST remain unchanged. | HD-002 |
| FR-SHR-021 | D | *(SCN-B)* Custom aliases MUST satisfy the same character-set and length rules as generated codes (A-003) and MUST NOT match a reserved word list (e.g., names used by the service's own operational endpoints). | HD-002, CON V |
| FR-SHR-022 | D | *(SCN-B)* Adding custom aliases MUST NOT change the behavior of creation requests that do not specify an alias (regression safety). | HD-002, CON VI |
| FR-SHR-023 | D | *(SCN-C)* Any analytics enhancement arising from SCN-C MUST conform to the outcome of the governed clarification and MUST NOT capture personal data unless a human-approved policy exception exists (CON VI). | HD-002, CON V |

### Functional Requirements: Orchestration (FR-ORC)

| ID | Class | Requirement | Source |
|----|-------|-------------|--------|
| FR-ORC-001 | C | Users MUST be able to create a workflow run from a requirement input; each run MUST receive a unique, immutable run identifier. | ASMT §4.4, FI, CON IX |
| FR-ORC-002 | C | The system MUST normalize the requirement into a structured form (intent, actors, functional and non-functional statements, constraints, acceptance criteria candidates) with stable requirement identifiers. | ASMT §4.1 |
| FR-ORC-003 | C | The system MUST run requirement-quality checks (completeness, consistency, testability, policy conformance, architecture-boundary conformance) and record each check's result and rationale. | ASMT §4.1, FI |
| FR-ORC-004 | C | When any requirement-quality check fails materially, the system MUST raise a human clarification gate listing specific questions; when all pass, it MUST NOT raise one (SCN-A-AC1, SCN-A-AC5). | FI |
| FR-ORC-005 | C | Execution MUST be governed by an explicit dependency graph in which each stage declares inputs, outputs, entry criteria, exit criteria, owner, and failure behavior. | ASMT §4.4, CON II |
| FR-ORC-006 | C | The default lifecycle graph MUST contain at least one parallel fork of independent stages and a synchronization point that waits for all required predecessors. | ASMT §4.4 |
| FR-ORC-007 | C | The graph MUST support conditional branches (e.g., clarification only when needed; impact analysis for brownfield changes). | ASMT §4.4, FI |
| FR-ORC-008 | C | A stage MUST NOT start until its entry criteria are met, and MUST NOT be marked complete until its exit criteria are verified; refusals MUST be recorded. | ASMT §4.4 |
| FR-ORC-009 | C | Task decomposition MUST produce tasks with identifiers, dependencies, ordering, linked requirement identifiers, and acceptance criteria. | ASMT §4.2 |
| FR-ORC-010 | C | For brownfield changes, the system MUST produce an impact analysis (SCN-B-AC1) before decomposition is approved. | ASMT §4.3 |
| FR-ORC-011 | C | Workflow state, stage outputs, cross-stage context, and artifact versions MUST be persisted such that a run survives process interruption. | ASMT §4.4 |
| FR-ORC-012 | C | Every artifact MUST record provenance: producing stage, actor, run identifier, input artifact versions, and timestamp. | ASMT §4.4, CON II |
| FR-ORC-013 | C | Every decision (agent or human) MUST be recorded with its rationale and linked to the artifacts it affects (decision lineage). | ASMT §4.4 |
| FR-ORC-014 | C | Transient stage failures MUST be retried with a bounded retry budget and backoff (PVT-004); permanent failures MUST NOT be retried. | ASMT §4.4, CON VIII |
| FR-ORC-015 | C | Each stage MUST have a timeout (PVT-005); a timeout counts as a transient failure unless classified otherwise. | ASMT §4.4, CON VIII |
| FR-ORC-016 | C | Stages MAY declare a fallback path (e.g., degraded analysis); use of a fallback MUST be recorded and visible in the release-readiness assessment. | ASMT §4.4 |
| FR-ORC-017 | C | The system MUST support rollback (restoring artifacts or system-under-change to the last approved version) and compensation (corrective action for an effect already committed), and MUST record which one was applied. | ASMT §4.4, CON VIII |
| FR-ORC-018 | C | The system MUST enter safe-stop when continuation is unsafe: mandatory policy FAIL, retry budget exhausted on a mandatory stage, approval timeout, integrity violation, or unclassified failure. Safe-stop MUST leave state consistent and resumable. | ASMT §4.4, CON III, CON VIII |
| FR-ORC-019 | C | An interrupted or safe-stopped run MUST be resumable by an authorized human action, continuing from persisted state without re-executing completed stages whose inputs are unchanged. | ASMT §4.4, FI |
| FR-ORC-020 | C | When an upstream artifact receives a new version, the system MUST identify dependent downstream stages and artifacts, mark them stale, re-plan the affected subgraph, and re-run only the affected stages. | ASMT §4.4, CON I |
| FR-ORC-021 | C | Replanning MUST preserve governance: approvals of invalidated artifacts MUST be revoked and re-requested; replanning events MUST be audited. | ASMT §4.4, FI |
| FR-ORC-022 | C | When ambiguity emerges mid-run, only the dependent path MUST be suspended; independent paths MAY continue to their next synchronization point (SCN-A-AC4). | FI |
| FR-ORC-023 | C | Every run MUST end in exactly one deterministic terminal outcome: `COMPLETED`, `FAILED`, `ABORTED` (human-terminated), or `SAFE_STOPPED` (resumable). | CON VIII |
| FR-ORC-024 | C | Users MUST be able to inspect a run: graph, current and historical stage states, pending gates, artifacts, decisions, policy outcomes, and metrics. | FI, ASMT §5 |
| FR-ORC-025 | C | Stages MUST be performed by agents with declared roles and declared permissions; an agent action outside its declared permissions MUST be refused and audited. | ASMT §4.7, CON II |
| FR-ORC-026 | C | At the end of a run the system MUST produce a final engineering summary containing plan and rationale, artifacts, risks, trade-offs, validation results, assumptions, and limitations. | ASMT §4.8 |
| FR-ORC-027 | C | Agents MUST be executable in two interchangeable modes behind one agent interface: deterministic (default) and AI-backed (optional, disabled by default). | HD-001 |
| FR-ORC-028 | C | Duplicate submission of the same stage-completion or decision event MUST be applied at most once (idempotent state transitions). | CON VIII |
| FR-ORC-029 | C | Automated tests and recorded scenario evidence MUST use deterministic mode only; each run MUST record the agent mode used, and evidence from AI-backed runs MUST NOT be presented as scenario evidence. | HD-001, CON X |
| FR-ORC-030 | C | AI-backed mode MUST be subject to identical stage gates, policy checks, permission checks, and audit recording as deterministic mode; enabling it MUST be an explicit configuration choice, and its absence (including a missing API key) MUST NOT prevent any other capability from working. | HD-001 |
| FR-ORC-031 | C | Each required scenario (SCN-A, SCN-B, SCN-C) MUST be executed as a workflow run of the orchestration system and produce recorded state transitions, gate events, approvals, and audit records. | HD-002 |

### Functional Requirements: Governance and Policy (FR-GOV)

| ID | Class | Requirement | Source |
|----|-------|-------------|--------|
| FR-GOV-001 | C | High-impact actions MUST require explicit human approval: design approval, applying changes to the system under change, destructive or irreversible actions, policy exceptions, resuming from safe-stop, and release readiness. | ASMT §4.4, ASMT §4.7, CON III |
| FR-GOV-002 | C | Approval gates MUST support decisions approve, reject (with reason), and escalate, plus a defined timeout outcome; lack of response MUST NOT be treated as approval. | CON III |
| FR-GOV-003 | C | Only human actors MAY record approvals, rejections, clarification answers, exception approvals, and release decisions. These actions MUST require a human-role API key holding the corresponding role (`approver` for approvals, rejections, and exception approvals; `release-owner` for release decisions; `engineer` or `approver` for clarification answers); requests with agent-role credentials MUST be refused and the refusal audited. | CON III, HD-003 |
| FR-GOV-004 | C | An approval MUST be bound to a specific artifact version; approvals for superseded versions MUST be refused. | CON III, CON VI |
| FR-GOV-005 | C | The system MUST evaluate a versioned policy set covering security, compliance, privacy, audit retention, approved dependencies, software licensing, and change control. | ASMT §4.4, CON VI |
| FR-GOV-006 | C | Each run MUST record the policy-set version evaluated; each applicable check MUST yield exactly one of `PASS`, `FAIL`, `EXCEPTION-REQUESTED`, `NOT-APPLICABLE`. | CON VI |
| FR-GOV-007 | C | A mandatory `FAIL` MUST block downstream progression; `EXCEPTION-REQUESTED` MUST block until a human decides. | CON VI |
| FR-GOV-008 | C | Each exception MUST record: policy, reason, scope, approving authority, compensating control, approval timestamp, and expiry or review condition. | CON VI |
| FR-GOV-009 | C | Changes to approved requirements, architecture, schemas, workflow definitions, security controls, or release criteria MUST pass impact analysis and change approval before taking effect. | CON VI |
| FR-GOV-010 | C | The release-readiness assessment MUST evaluate all Principle XI conditions and report `FAIL` with each blocking reason if any mandatory condition is unmet, including any unapproved or expired exception. | CON XI, Governance §6 |
| FR-GOV-011 | C | Release readiness MUST become "ready" only through a recorded human release decision on a non-FAIL assessment. | CON III, Governance §6 |
| FR-GOV-012 | C | Release-readiness checks MUST include executed dependency-vulnerability and secret scans with recorded results. | CON V |
| FR-GOV-013 | C | Every audited human decision MUST record the authenticated role and key identity (never the key secret) under which it was made. | HD-003, CON IX |

### Functional Requirements: Observability and Audit (FR-OBS)

| ID | Class | Requirement | Source |
|----|-------|-------------|--------|
| FR-OBS-001 | C | Every audited event MUST carry the run identifier as a correlation identifier across stages, agents, and service calls. | ASMT §4.4, CON IX |
| FR-OBS-002 | C | The system MUST record state transitions, decisions, approvals, rejections, retries, failures, rollbacks, compensations, fallbacks, replanning events, policy outcomes, and terminal outcomes. | ASMT §4.4, CON IX |
| FR-OBS-003 | C | Each audit record MUST include actor type, actor identity where applicable, action, timestamp, affected artifact or state, result, and reason. | CON IX |
| FR-OBS-004 | C | Audit records MUST be append-only; any attempted modification or deletion MUST be refused and itself audited. | CON IX |
| FR-OBS-005 | C | Users MUST be able to query audit records by run identifier, requirement identifier, actor, and event type. | FI |
| FR-OBS-006 | C | The system MUST compute and expose per-run and aggregate reliability metrics: success rate, retry frequency, rollback/compensation frequency, MTTR, and end-to-end and per-stage latency. | ASMT §4.4 |
| FR-OBS-007 | C | Metrics derived from demonstration runs MUST be labeled as demonstration measurements. | CON IX |
| FR-OBS-008 | C | Users MUST be able to retrieve a bidirectional traceability view: requirement → scenario → decision → task → artifact → test → result → documentation → evidence, and the reverse. | CON X, ASMT §6 |
| FR-OBS-009 | D | The URL shortener MUST emit structured operational logs and request-level correlation identifiers without secrets or personal data. | CON V, CON IX |

### Non-Functional Requirements

Targets marked PVT are proposals requiring approval (see Proposed Validation Targets).

| ID | Area | Requirement | Verification | Target |
|----|------|-------------|--------------|--------|
| NFR-SEC-001 | Security | All external input is validated at trust boundaries; URL scheme allow-list enforced. | Security test suite incl. negative cases | 100% of negative security cases rejected |
| NFR-SEC-002 | Security | No secrets or personal data in logs, audit, errors, or repository. | Secret scan + log inspection tests | Zero findings (PVT-012) |
| NFR-SEC-003 | Security | Threat scenarios (open-redirect abuse, enumeration, injection, abuse volume, approval spoofing) documented with controls or accepted risk. | Threat model review | All listed threats addressed |
| NFR-SEC-004 | Security | API keys are never logged, echoed, or stored in plain text in audit records; protected operations reject missing, invalid, or wrong-role keys. | Authorization and log-inspection tests | 100% of negative authorization cases rejected |
| NFR-REL-001 | Reliability | Retries bounded; permanent failures never retried; deterministic terminal outcomes. | Orchestration reliability tests with injected faults | PVT-004 |
| NFR-REL-002 | Reliability | Redirect continues when analytics capture fails. | Fault-injection test | 100% redirects succeed under analytics failure |
| NFR-SCL-001 | Scalability | Short-code uniqueness and correctness hold under concurrent load. | Concurrency test | PVT-003 |
| NFR-SCL-002 | Scalability | Design permits horizontal scaling of the shortener (no single-instance-only state other than persistence), documented as a trade-off if not demonstrated. | Architecture review | Documented |
| NFR-MNT-001 | Maintainability | Concerns separated per CON VII; material decisions recorded as ADRs. | Architecture review, ADR presence | 100% material decisions have ADRs |
| NFR-OBS-001 | Observability | Any run can be reconstructed from recorded data alone. | Reconstruction test (US-5) | 100% of scenario runs reconstructable |
| NFR-AUD-001 | Auditability | Every state transition and decision has a complete audit record. | Audit completeness test | 100% (PVT-008) |
| NFR-PRF-001 | Performance | Redirect resolution latency. | Load test in reference environment | PVT-001 |
| NFR-PRF-002 | Performance | Short-link creation latency. | Load test in reference environment | PVT-002 |
| NFR-RCV-001 | Recoverability | Interrupted runs resume to the same terminal outcome as uninterrupted runs. | Interruption tests at each stage boundary | PVT-006 |
| NFR-RCV-002 | Recoverability | MTTR is measured from failure detection to successful recovery for demonstration runs. | Metrics output | Reported (not targeted) |
| NFR-TST-001 | Testability | Unit, integration, API contract, orchestration transition, reliability, security, and end-to-end tests exist and are executed. | Test reports | PVT-007 |
| NFR-CHG-001 | Change safety | No change to the system under change is applied without approved impact analysis and passing regression tests; failed validation triggers rollback. | SCN-B evidence | 100% of SCN-B changes |
| NFR-AUT-001 | Controlled autonomy | Agents cannot perform human-reserved actions; out-of-permission actions are refused. | Authorization tests | 100% refused and audited |
| NFR-RUN-001 | Operability | The full system runs end-to-end on a single developer workstation from documented setup steps, with no AI API key and AI-backed mode disabled. | Fresh-environment setup run | PVT-009 |
| NFR-DET-001 | Reproducibility | Deterministic-mode scenario runs produce the same stage sequence, gate events, and terminal outcome on repeated execution with the same inputs and decisions (timestamps and identifiers excepted). | Repeat-run comparison test | 100% of scenario runs |

### Proposed Validation Targets (require human approval)

| ID | Target | Rationale |
|----|--------|-----------|
| PVT-001 | 95% of redirect resolutions complete in under 100 ms at the service boundary, at 50 concurrent clients, in the local reference environment | Redirects are latency-sensitive; modest local target suitable for a prototype |
| PVT-002 | 95% of creations complete in under 250 ms under the same conditions | Creation is less latency-critical than redirect |
| PVT-003 | 1,000 concurrent creations produce 1,000 distinct codes with zero collisions or lost writes | Verifies uniqueness under contention |
| PVT-004 | Default retry budget of 3 attempts per stage with exponential backoff; zero retries for permanent failures | Common bounded-retry default |
| PVT-005 | Each stage declares a timeout; default 5 minutes for agent stages, configurable; approval-gate timeout configurable (default 24 hours, shortened in demos) | Prevents indefinite hangs while allowing human response time |
| PVT-006 | 100% of interruption tests (one per stage boundary) resume to the same terminal outcome without duplicate side effects | Recoverability proof |
| PVT-007 | All test categories in NFR-TST-001 present; ≥ 85% line coverage of domain, orchestration, and policy logic; 100% of mandatory tests passing at release | Evidence-based completion (CON XI) |
| PVT-008 | 100% of state transitions and decisions in scenario runs have complete audit records | Audit-grade evidence |
| PVT-009 | A reviewer completes setup and runs all three scenarios in under 30 minutes following the documentation | Reviewability of the deliverable |
| PVT-010 | Maximum destination URL length 2,048 characters | Widely used practical limit |
| PVT-011 | Default creation rate limit 60 requests per minute per client | Abuse control without hindering demo use |
| PVT-012 | Zero high or critical findings from dependency and secret scans at release, or an approved exception per CON VI | Release-readiness gate |

### Key Entities

- **Short Link**: short code (generated or custom alias), code origin (generated/alias),
  destination URL (normalized), creation time, optional expiration, status (active/expired),
  creator key identity (HD-003).
- **Link Analytics**: per short link: total successful redirects, last redirect time; no
  personal data.
- **Idempotency Record**: idempotency key, request fingerprint, original result, expiry.
- **Requirement**: stable identifier, provenance class, source reference, normalized text,
  type (FR/NFR/constraint), acceptance criteria, version.
- **Workflow Run**: run identifier, originating requirement set, scenario type, policy-set
  version, graph version, current state, terminal outcome, timestamps.
- **Stage / Stage Execution**: stage identifier, declared inputs/outputs, entry/exit criteria,
  owner role, failure behavior; executions carry attempt number, status, timing, failure
  classification.
- **Dependency Graph (Plan)**: versioned set of stages and dependency edges for a run; new
  version on replanning.
- **Agent**: role, declared permissions, execution mode (deterministic or AI-backed, HD-001).
- **API Key / Role Binding**: key identity (non-secret), role (`consumer`, `engineer`,
  `approver`, `release-owner`, `agent`), actor type (human or agent), status (HD-003).
- **Artifact**: type (normalized requirement, task plan, design, code change, test result,
  document, assessment, summary), version, provenance, status (current/stale/rolled back).
- **Decision**: identifier, actor, type (clarification, approval, rejection, escalation,
  exception, release), rationale, bound artifact versions, timestamp.
- **Approval Gate**: gate identifier, required approver role, timeout, status, bound artifact
  version.
- **Policy Set / Policy Check / Exception**: versioned rules; per-run check outcomes; exception
  records with the fields in FR-GOV-008.
- **Audit Event**: append-only record with the fields in FR-OBS-003.
- **Impact Analysis**: change reference, impacted components, interfaces, data flows, tests,
  docs, regression risks, rollout/rollback considerations.
- **Release-Readiness Assessment**: per-condition results, blocking reasons, human decision.
- **Engineering Summary**: final report per FR-ORC-026.

### Required Evidence

| ID | Evidence | Produced for |
|----|----------|--------------|
| EV-001 | Run timeline (ordered audit events with terminal outcome) | All scenarios |
| EV-002 | Requirement-quality check results with rationale | SCN-A, SCN-B, SCN-C |
| EV-003 | Decomposition (tasks, dependencies, requirement links, acceptance criteria) | SCN-A, SCN-C |
| EV-004 | Decision lineage including clarifications and approvals | SCN-A (if triggered), SCN-C |
| EV-005 | Impact analysis document | SCN-B |
| EV-006 | Test execution results (new and regression); rollback evidence if triggered | SCN-A, SCN-B, SCN-C |
| EV-007 | Release-readiness assessment, policy outcomes, final engineering summary, metrics (labeled) | All scenarios |
| EV-008 | Traceability matrix requirement ↔ test ↔ evidence | Submission |

All evidence MUST be produced by actual execution; illustrative examples MUST be labeled
(CON X).

### Constraints

- **CST-001**: SpecKit is the sole lifecycle framework; the lifecycle order and human gates of
  the constitution apply (CON, Authority Hierarchy).
- **CST-002**: Technology choices (language, framework, persistence, agent framework,
  deployment platform) are deferred to `/speckit-plan` and ADRs and require human approval.
- **CST-003**: The prototype MUST be runnable end-to-end and include setup instructions,
  architecture overview, testing approach, limitations, and trade-offs (`ASMT §5`).
- **CST-004**: The assessment source document MUST NOT be committed; reference by section
  only.
- **CST-005**: Work is time-boxed to the assessment window of 2–3 days (`ASMT §2`); scope is
  prioritized accordingly.
- **CST-006**: No AI API key or external AI service may be required to build, run, test, or
  demonstrate the project (HD-001).
- **CST-007**: The baseline shortener is built directly through the SpecKit lifecycle under TDD
  and traceability; scenario capabilities (expiration plus analytics, custom aliases, the
  ambiguous click-tracking request) are delivered only through orchestrated workflow runs
  (HD-002).

### Exclusions (out of scope for this feature)

- **EXC-001**: End-user web UI for link management (API and command-line/inspection interfaces
  are sufficient). A read-only reviewer view is optional, not required.
- **EXC-002**: User account registration, multi-tenant management, and billing.
- **EXC-003**: Custom domains, QR codes, link editing, and bulk import.
- **EXC-004**: Production cloud deployment and multi-region operation (design considerations
  documented only).
- **EXC-005**: Advanced analytics (geolocation, device, referrer breakdowns, unique-visitor
  tracking).
- **EXC-006**: Automated malware or phishing reputation lookups of destination URLs (documented
  as a limitation with a recommended future control).

### Resolved Ambiguities: Human Decisions

Each ambiguity below was resolved by the human owner. Decisions are binding (class **C**,
source `HD-nnn`) and change only through change control (CON VI).

#### HD-001: Agent execution model (resolves AMB-001)

- **Decider**: Mani Kumar Vadugu (human owner) · **Date**: 2026-10-15 · **Option chosen**: C
- **Decision**: Pluggable agent execution behind a single agent interface, with two modes:
  1. **Deterministic mode**: the default, and the **only** mode used for automated tests and
     for recorded scenario evidence.
  2. **AI-backed mode**: optional, **disabled by default**; the project MUST build, run, test,
     and execute all scenarios with no AI API key present.
  Both modes are subject to **identical** stage gates, policy checks, permission checks, and
  audit recording.
- **Rejected alternatives**: A (AI-only: non-reproducible evidence, requires key and cost);
  B (deterministic-only: agent behavior may read as simulated with no extension path).
- **Affected requirements**: FR-ORC-025, FR-ORC-027, FR-ORC-029, FR-ORC-030, NFR-AUT-001,
  NFR-RUN-001, CST-006.

#### HD-002: Scenario content (resolves AMB-002)

- **Decider**: Mani Kumar Vadugu (human owner) · **Date**: 2026-10-15 · **Option chosen**: A
- **Decision**:
  - **Baseline**: the core shortener (link creation, validation, short-code generation,
    redirect resolution, operational health, idempotency, rate limiting, persistence-failure
    handling) is built directly via the SpecKit lifecycle and MUST follow TDD and
    traceability. It is the **brownfield baseline** for the scenarios.
  - **SCN-A (greenfield)**: link expiration plus basic redirect analytics (FR-SHR-008 to
    FR-SHR-012).
  - **SCN-B (brownfield)**: custom aliases (creator-chosen short codes) added to the existing
    creation flow.
  - **SCN-C (ambiguous)**: the request "track who clicks links", which conflicts with the
    no-personal-data constraint (FR-SHR-012, A-005) and therefore cannot be implemented as
    stated without a governed decision.
  - All three scenarios MUST be executed **through the orchestration system** and produce
    recorded workflow evidence (state transitions, gates, approvals, audit).
- **Rejected alternatives**: B (orchestrator builds the whole shortener: highest schedule
  risk, shortener viability coupled to orchestrator); C (defect fix as brownfield: weaker
  impact-analysis evidence).
- **Affected requirements**: SCN-A, SCN-B, SCN-C, FR-SHR-020 to FR-SHR-023, FR-ORC-031,
  A-010, CST-007.

#### HD-003: Access control (resolves AMB-003)

- **Decider**: Mani Kumar Vadugu (human owner) · **Date**: 2026-10-15 · **Option chosen**: A
- **Decision**: Static API keys mapped to roles: `consumer`, `engineer`, `approver`,
  `release-owner` (human roles) and `agent` (agent role). Redirect resolution is public.
  Approval, rejection, exception approval, and release-readiness decisions require a
  **human-role key** with the corresponding role; requests made with agent-role credentials
  MUST be refused and the refusal audited.
- **Rejected alternatives**: B (no authentication: cannot credibly enforce non-waivable
  CON III); C (external identity provider: scope and dependency exceed the assessment window).
- **Accepted limitation**: key issuance, rotation, and revocation are documented
  limitations, not production identity management.
- **Affected requirements**: FR-SHR-019, FR-GOV-003, FR-GOV-013, NFR-AUT-001, NFR-SEC-004.

## Assumptions

- **A-001**: Redirect resolution is anonymous and public; short links are shareable.
- **A-002**: Only `http` and `https` destinations are accepted.
- **A-003**: Short codes are case-sensitive, URL-safe, and at most 10 characters.
- **A-004**: Creating the same destination twice without an idempotency key yields two distinct
  short links (no implicit deduplication); idempotency is opt-in via key.
- **A-005**: Analytics are aggregate counts and timestamps only; no IP addresses, user agents, or
  personal data are stored.
- **A-006**: Expiration is optional; links without expiration do not expire. Expired links are
  retained (not deleted) so the "expired" outcome remains distinguishable.
- **A-007**: Audit records are retained for at least the assessment review period; production
  retention policy is defined in the policy set and documented, not enforced by deletion.
- **A-008**: A single human may hold multiple roles (engineer, approver, release owner) in the
  prototype, but every decision records the role under which it was made.
- **A-009**: "Reference environment" for performance targets is a single developer workstation;
  results are demonstration measurements, not production capacity claims.
- **A-010**: *(Superseded by HD-002 for scenario content.)* The system under change for SCN-B is
  the baseline shortener built directly via SpecKit (true brownfield relative to the scenario
  run).
- **A-011**: Inspection interfaces (run, audit, traceability, metrics) may be API- or
  command-line-based; a graphical interface is not required (EXC-001).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An API consumer can create a short link and be redirected through it on the first
  attempt, with expired, unknown, and invalid links each producing their distinct outcome in
  100% of acceptance tests.
- **SC-002**: All three required scenarios (SCN-A, SCN-B, SCN-C) complete with their acceptance
  criteria met and evidence items EV-001 to EV-007 produced by actual execution.
- **SC-003**: For every scenario run, an assessment reviewer can reconstruct the complete
  timeline and terminal outcome from recorded data alone, without consulting the authoring
  conversation.
- **SC-004**: 100% of human-reserved actions attempted by agents are refused and audited; 0
  approvals are inferred from silence or timeout.
- **SC-005**: 100% of injected-fault tests (transient failure, permanent failure, timeout,
  interruption, policy FAIL) reach the specified recovery path (retry, fallback, rollback or
  compensation, safe-stop, or resume) and a deterministic terminal outcome.
- **SC-006**: A change to an upstream artifact causes re-execution of only the affected stages
  (unaffected completed stages are not re-run) and re-requests every invalidated approval, in
  100% of replanning tests.
- **SC-007**: Every confirmed and derived requirement traces to at least one test and one
  evidence or documentation item (bidirectional traceability completeness 100%).
- **SC-008**: Release readiness is reported FAIL in 100% of test cases containing a mandatory
  policy failure or an unapproved or expired exception.
- **SC-009**: Performance, concurrency, and setup targets PVT-001, PVT-002, PVT-003, and
  PVT-009 are met once approved; until approved, results are reported as demonstration
  measurements only.
- **SC-010**: A reviewer with no AI API key can set up the project, run all automated tests, and
  execute all three scenarios in deterministic mode; repeated deterministic runs yield the same
  stage sequence, gate events, and terminal outcomes (HD-001, NFR-DET-001).
- **SC-011**: 100% of approval, rejection, exception-approval, and release-decision attempts made
  with agent-role credentials are refused and produce an audit record (HD-003).
