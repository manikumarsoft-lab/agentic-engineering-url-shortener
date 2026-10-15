<!--
SYNC IMPACT REPORT (SpecKit sync impact report)
====================================================================
Version change: (unversioned template) → 1.0.0
Bump rationale: Initial adoption. Every placeholder replaced with project-specific
governance; no prior ratified version exists, so this is the first MAJOR baseline.

Principles (template placeholder → new title):
  [PRINCIPLE_1_NAME] → I. Specification Before Implementation
  [PRINCIPLE_2_NAME] → II. Explicit Agentic Orchestration
  [PRINCIPLE_3_NAME] → III. Human Governance
  [PRINCIPLE_4_NAME] → IV. Test-Driven Engineering
  [PRINCIPLE_5_NAME] → V. Security and Privacy by Design
  (added)            → VI. Compliance and Change-Control Policy Enforcement
  (added)            → VII. Architecture and Maintainability
  (added)            → VIII. Reliability and Recovery
  (added)            → IX. Observability and Auditability
  (added)            → X. Traceability and Repository Integrity
  (added)            → XI. Evidence-Based Completion

Sections:
  [SECTION_2_NAME] → Authority Hierarchy and Scope Constraints
  [SECTION_3_NAME] → Development Workflow and Quality Gates
  Governance       → fully defined (compliance assessment, exceptions, non-waivable
                     principles, amendments/versioning, conflict resolution,
                     release blocking)
Removed sections: none

Dependent artifacts (read the constitution at runtime; NOT modified by this command):
  ⚠ .specify/templates/plan-template.md   — "Constitution Check" gate must be populated
                                            per feature against Principles I–XI.
  ⚠ .specify/templates/spec-template.md   — no change required; FR/NFR separation and
                                            assumptions sections already exist.
  ⚠ .specify/templates/tasks-template.md  — tasks template treats tests as OPTIONAL;
                                            Principle IV makes them mandatory for this
                                            project. /speckit-tasks output MUST include
                                            test-first tasks regardless.
  ✅ .claude/skills/*                      — no agent-specific names requiring change.

Deferred items:
  None. Ratified 2026-10-15 by Mani Kumar Vadugu; Governance §3 and §5 explicitly confirmed by the human owner.
-->

# Agentic Software Engineering System: URL Shortener Constitution

This constitution governs an engineering assessment submission. The URL shortener is the
demonstration domain; the central differentiator is a governed, stateful, non-linear agentic
software engineering orchestration system that transforms requirements into reviewable
engineering outcomes across the software development lifecycle (SDLC).

Normative keywords (MUST, MUST NOT, SHOULD, MAY) follow RFC 2119 meaning.

## Core Principles

### I. Specification Before Implementation

- Production implementation MUST NOT begin without an approved specification.
- Every requirement MUST be testable and traceable to its source (assessment requirement,
  clarification, or recorded assumption).
- Functional requirements (FR) and non-functional requirements (NFR) MUST be identified and
  kept distinguishable.
- Every ambiguity MUST be either resolved through clarification or recorded as an explicit,
  owned assumption.
- A material change to an upstream artifact (requirements, clarifications, plan, contracts,
  ADRs) MUST trigger a recorded downstream impact analysis before dependent work continues.
- Existing code MUST NOT become an undocumented substitute for the specification; where
  implementation and specification diverge, the specification governs until formally changed.

**Rationale**: Reviewers assess requirement understanding and ambiguity management; both are
only demonstrable if the specification, not the code, is the source of truth.

### II. Explicit Agentic Orchestration

- The orchestration system MUST be more than sequential agent chaining.
- It MUST be driven by an explicit dependency graph or an equivalent explicit stateful model.
- It MUST support sequential paths, parallel paths, synchronization (join) points, conditional
  branching, dynamic replanning, interruption, and resumption.
- Every stage MUST define its inputs, outputs, entry criteria, exit criteria, owner (agent or
  human role), and failure behavior.
- Workflow state, cross-stage context, artifact provenance, and decision lineage MUST be
  persisted and recoverable.
- Agent autonomy MUST be bounded by declared permissions and MUST be observable and auditable.

**Rationale**: Non-linear, stateful, governed orchestration is the critical differentiator of
the assessment; a linear sequence of agents is insufficient evidence.

### III. Human Governance

- Humans own requirements, architecture, security-sensitive decisions, material exceptions,
  destructive or irreversible changes, release readiness, and final quality.
- High-impact actions MUST require explicit human approval before execution.
- Approval, rejection, escalation, timeout, and safe-stop behavior MUST be defined for every
  approval gate.
- On approval timeout, the workflow MUST remain blocked or enter safe-stop; it MUST NOT proceed.
- Mandatory approval gates MUST NOT be silently skipped, bypassed, or auto-satisfied.
- Lack of response MUST NOT be interpreted as approval.

**Rationale**: Controlled autonomy means agents execute within boundaries while humans retain
accountable ownership of consequential decisions.

### IV. Test-Driven Engineering

- Red-green-refactor TDD MUST be applied to domain and orchestration behavior wherever
  technically practical; where it is not practical, the reason MUST be recorded.
- A failing test MUST be written before the corresponding implementation, and it MUST be
  observed to fail for the expected reason.
- Implementation MUST be limited to the minimum behavior required to pass the test.
- Refactoring MUST occur only while the test suite remains green.
- The test portfolio MUST include unit, integration, API contract, orchestration state
  transition, reliability (retry/rollback/recovery), security, and end-to-end tests.
- Task completion MUST be backed by executed validation; generated code alone is not evidence.

**Rationale**: Executed tests are the primary objective evidence that requirements are met and
that orchestration control paths (including failure paths) behave as designed.

### V. Security and Privacy by Design

- All external input MUST be validated and normalized at trust boundaries.
- Accepted URL schemes MUST be restricted to an explicit allow-list.
- Malicious redirect and abuse scenarios (e.g., open-redirect misuse, malicious or
  self-referential targets, enumeration, high-volume abuse) MUST be addressed or explicitly
  accepted as documented risk.
- Secrets and sensitive data MUST NOT appear in logs, audit records, error responses, or
  committed files.
- Configuration MUST default to secure values.
- Components MUST operate with least privilege across explicitly documented trust boundaries.
- Authentication assumptions, rate limiting, threat scenarios, and security trade-offs MUST be
  documented.
- Dependency vulnerability scanning and secret scanning MUST be part of release readiness.

**Rationale**: A URL shortener is a known abuse vector; security is a reviewed engineering
principle and cannot be deferred to the end.

### VI. Compliance and Change-Control Policy Enforcement

- Policy guardrails MUST be defined, versioned, and cover: security, compliance, privacy,
  audit retention, approved dependencies, software licensing, and change control.
- Every orchestration run MUST record the policy version it evaluated.
- Every applicable policy check MUST produce exactly one outcome:
  `PASS`, `FAIL`, `EXCEPTION-REQUESTED`, or `NOT-APPLICABLE`.
- A `FAIL` on a mandatory policy check MUST block downstream workflow progression.
- A policy exception MUST require explicit human approval; `EXCEPTION-REQUESTED` MUST block
  progression until approved or rejected.
- Every exception MUST record: applicable policy, reason, scope, approving authority,
  compensating control, approval timestamp, and expiry or review condition.
- Changes to approved requirements, architecture, schemas, workflow states, security controls,
  or release criteria MUST pass formal impact analysis and change approval.
- Release readiness MUST fail while any mandatory compliance or change-control policy is
  violated or covered only by an unapproved or expired exception.
- Policy outcomes and exceptions MUST be included in audit and traceability evidence.

**Rationale**: Governance is demonstrable only when policy evaluation is explicit, versioned,
blocking, and auditable, with exceptions as accountable human decisions.

### VII. Architecture and Maintainability

- Domain logic, API delivery, persistence, orchestration, policy enforcement, telemetry, and
  infrastructure concerns MUST be separated.
- External dependencies SHOULD be accessed through explicit interfaces so they can be replaced
  or substituted in tests.
- Material architectural decisions and their rejected alternatives MUST be recorded as
  Architecture Decision Records (ADRs).
- Complexity MUST be justified by a requirement or by demonstrability; unjustified complexity
  MUST be removed or recorded in the plan's complexity tracking.
- Code MUST be modular, readable, testable, and replaceable.

**Rationale**: Reviewers judge design quality and defensibility; separated concerns and recorded
decisions make both visible.

### VIII. Reliability and Recovery

- Failures MUST be classified as transient or permanent; only transient failures MAY be retried.
- Retries MUST be bounded and MUST define backoff and timeout behavior.
- Repeatable operations MUST be idempotent.
- Fallback behavior MUST be defined where a degraded path is acceptable.
- Rollback (restoring prior state) MUST be distinguished from compensation (applying a
  corrective action after a committed effect).
- Safe-stop conditions MUST be defined, and safe-stop MUST leave state consistent and
  resumable.
- Every execution MUST reach a deterministic terminal outcome.
- Controlled resumption after interruption MUST be supported.
- Evidence of success, failure, retry, rollback, compensation, recovery, and latency MUST be
  captured.

**Rationale**: Bounded retries, fallback, rollback, and safe-stop are explicit assessment
requirements and are the core of trustworthy autonomy.

### IX. Observability and Auditability

- Every orchestration execution MUST carry a unique run identifier, propagated as a
  correlation identifier across stages, agents, and service calls.
- State transitions, decisions, approvals, rejections, retries, failures, rollbacks,
  compensations, replanning events, policy outcomes, and terminal outcomes MUST be recorded.
- Every audit record MUST include: actor type (agent, human, system), actor identity where
  applicable, action, timestamp, affected artifact or state, result, and reason.
- Audit records MUST be append-only.
- Logs, metrics, traces, and workflow history MUST be sufficient to reconstruct an execution.
- Reliability metrics (success rate, retry and rollback frequency, MTTR, end-to-end latency)
  MUST be computed from recorded events.
- Demonstration metrics MUST be clearly labeled and distinguished from production
  measurements.

**Rationale**: Audit-grade observability is what makes governed autonomy verifiable by a
reviewer rather than asserted.

### X. Traceability and Repository Integrity

- Traceability MUST be maintained across requirement → scenario → decision → design → task →
  implementation → test → validation → documentation → evidence.
- Commits MUST be small, logically coherent, and describe engineering intent.
- Approvals, test results, command output, execution logs, metrics, and operational evidence
  MUST NOT be fabricated; illustrative or proposed evidence MUST be labeled as such.
- AI-generated artifacts MUST be reviewed and owned by a human before acceptance.
- Documentation MUST evolve with the implementation in the same change set where practical.
- Assessment source material that is designated confidential MUST NOT be committed; artifacts
  MUST reference it by section identifier instead.

**Rationale**: Change history and traceability are assessed directly; fabricated evidence would
invalidate the submission.

### XI. Evidence-Based Completion

A feature or task is complete only when all of the following hold:

1. Applicable requirements are identified.
2. Decisions and assumptions are recorded.
3. Acceptance criteria are satisfied.
4. Required tests have been executed successfully.
5. Security and reliability checks are complete.
6. Documentation is current.
7. Traceability is complete.
8. Residual risks and limitations are disclosed.
9. Required approval is recorded.
10. Evidence is available for reviewer verification.

**Rationale**: "Done" must be a verifiable state, not a claim.

## Authority Hierarchy and Scope Constraints

When instructions or artifacts conflict, precedence MUST be:

1. Official assessment requirements
2. This constitution (as ratified)
3. Approved feature specification and clarifications
4. Approved technical plan and contracts
5. Approved Architecture Decision Records
6. SpecKit-generated task plan
7. Current implementation
8. Informal conversation

Scope constraints:

- SpecKit is the sole lifecycle and specification framework. Competing planning, task, memory,
  or execution methodologies MUST NOT be introduced.
- Requirements MUST NOT be invented beyond the assessment or approved specification; any
  extension MUST be recorded as an assumption or approved scope addition.
- Material conflicts MUST be stopped and reported, not silently worked around.
- Technology selection is a human decision recorded in the plan and ADRs.

## Development Workflow and Quality Gates

The lifecycle order is: Constitution → Specify → Clarify → Plan → Architecture Decision
Records → Checklist → Tasks → Analyze → Implement → Converge.

- Each stage MUST have an explicit human exit gate before the next stage begins. Mandatory
  gates: constitution ratification, specification approval (post-clarify), plan and ADR
  approval, task-plan approval (post-analyze), and release readiness.
- Upstream SpecKit artifacts MUST NOT be silently modified to accommodate implementation
  convenience; changes follow Governance §2 (exceptions) or §4 (amendments) or the change-control
  rules of Principle VI.
- `/speckit-analyze` findings of CRITICAL severity, or any constitution violation, MUST block
  implementation until resolved or covered by an approved exception.
- Every task MUST reference the requirement(s) it satisfies and the test(s) that verify it.
- Release readiness requires: all Principle XI conditions met; no failing mandatory policy
  check; no unapproved or expired exception; dependency and secret scans executed with results
  recorded; and explicit human sign-off.

## Governance

**§1 Compliance assessment during planning.** Every `plan.md` MUST contain a Constitution Check
that evaluates Principles I–XI individually with outcome `PASS`, `FAIL`,
`EXCEPTION-REQUESTED`, or `NOT-APPLICABLE` and a one-line justification. The check MUST be
performed before design research and re-performed after design. `/speckit-analyze` MUST
re-verify compliance across spec, plan, and tasks before implementation.

**§2 Exceptions.** An exception MUST be proposed in writing (in the plan's complexity tracking
or a dedicated exception record) stating the principle or policy, reason, scope, compensating
control, and expiry or review condition. Only the human owner may approve it; the approval,
approver, and timestamp MUST be recorded. Agents MAY propose but MUST NOT approve exceptions.
Unapproved exceptions have no effect.

**§3 Non-waivable principles.** The following MUST NOT be waived by any exception:

- Principle III (Human Governance) in its entirety.
- Principle IX audit-record requirements (run identifier, recorded transitions/decisions/
  approvals, required audit fields).
- Principle X prohibitions on fabricated evidence and on committing confidential assessment
  material, and the requirement for human ownership of AI-generated artifacts.
- Principle V prohibition on exposing secrets or sensitive data.
- Principle VI rules that a mandatory `FAIL` blocks progression and that exceptions require
  human approval.
- Principle XI conditions 4 (executed tests), 9 (recorded approval), and 10 (verifiable evidence).

All other rules MAY be excepted under §2.

**§4 Amendments and versioning.** Amendments MUST be proposed via `/speckit-constitution`,
include a Sync Impact Report, and be ratified by explicit human approval. Versions follow
semantic versioning: MAJOR for removal or backward-incompatible redefinition of a principle or
governance rule; MINOR for a new principle or section or materially expanded guidance; PATCH for
clarifications and wording fixes. Amendments affecting approved downstream artifacts MUST
trigger impact analysis under Principle I.

**§5 Conflict resolution.** The Authority Hierarchy governs conflicts between artifacts. When
principles conflict with each other, the stricter interpretation that preserves human control,
security, and evidence integrity prevails, in this order: III → V → X → IX → VI → I → VIII →
IV → II → VII. If a conflict cannot be resolved by this order, work MUST stop and the conflict
MUST be escalated to the human owner.

**§6 Non-compliance and release readiness.** Any unresolved constitution violation, failing
mandatory policy check, unapproved or expired exception, or unmet Principle XI condition MUST
mark release readiness as `FAIL`. Release readiness MUST NOT be declared by an agent; it
requires explicit human sign-off recorded with approver and timestamp.

**Version**: 1.0.0 | **Ratified**: 2026-10-15 (ratified by Mani Kumar Vadugu, human owner) | **Last Amended**: 2026-10-15
