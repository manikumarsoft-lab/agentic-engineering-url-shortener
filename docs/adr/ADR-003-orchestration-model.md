# ADR-003: Orchestration Model — In-Repository Engine with Deterministic Superstep Scheduling

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Engine-from-scratch selected by the human owner (research R-03,
DQ-008); superstep scheduling approved at plan gate as PD-004 (Mani Kumar Vadugu, 2026-10-15).

## Context

The orchestration system is the assessment's critical differentiator (ASMT §4.4). It must be
executable code in this repository (human-owner addition, 2026-10-15) and support sequential,
parallel, synchronized, conditional, interruptible, resumable and replannable execution
(CON II, FR-ORC-005..008, -037..039). Scenario evidence must be reproducible (NFR-DET-001), and
the same governance must apply to deterministic and AI-backed agents (HD-001, FR-ORC-030).

## Decision Drivers

- Visibility and testability of every governed semantic (gates, retries, policy, audit).
- Determinism of committed event order for repeat-run comparison.
- No AI-framework coupling in the default path.
- Bounded implementation size within the timebox.

## Options Considered

### Option A — Engine from scratch; explicit DAG; superstep scheduler
- **Approach**: own modules for graph loading, state machines (tables as data), transitions, gates, retry, replanning, recovery; scheduler executes all READY nodes of a step concurrently (`asyncio.gather`, per-node timeout), then commits results in lexicographic node-ID order.
- **Advantages**: every semantic is first-class code under test; real parallelism with reproducible commit order; no external runtime.
- **Disadvantages**: most code to write; a fast branch may wait up to one sibling's step duration.
- **Risks**: scope; subtle scheduler bugs.
- **Implementation impact**: small core, transition-table tests, virtual clock; checkpoint CP-2.
- **Assessment implications**: strongest evidence of non-linear, governed orchestration.

### Option B — Own DAG + `transitions` library for state machines
- **Approach**: library-managed per-node state machine.
- **Advantages**: less state-machine boilerplate.
- **Disadvantages**: library state must be mirrored to the DB for persistence/replay; extra dependency.
- **Risks**: divergence between library and persisted state.
- **Implementation impact**: adapter layer.
- **Assessment implications**: marginal benefit.

### Option C — LangGraph (graph execution + checkpointing)
- **Approach**: build nodes as LangGraph nodes; use interrupts for gates.
- **Advantages**: execution and checkpoints out of the box.
- **Disadvantages**: library owns semantics being assessed; AI-framework coupling conflicts with deterministic default; policy/audit layered on top.
- **Risks**: reviewers attribute orchestration to the library; version churn.
- **Implementation impact**: integration plus custom governance anyway.
- **Assessment implications**: weakens "engine in this repository".

### Option D (scheduling alternative) — free-running asyncio tasks committing on completion
- **Approach**: each node commits whenever it finishes.
- **Advantages**: minimal latency.
- **Disadvantages**: nondeterministic audit order; breaks NFR-DET-001 comparison.
- **Risks**: flaky e2e assertions.
- **Implementation impact**: would require partial-order comparison tooling.
- **Assessment implications**: weaker reproducibility evidence.

## Decision

Option A with superstep scheduling. Timers (retry backoff, gate deadlines) advance independently
of steps. `Clock` and `IdGenerator` are injected; tests use a virtual clock. Agents implement one
`Agent.execute(StageContext) -> StageResult` protocol; deterministic agents are the default and
the only mode for tests/evidence; the AI-backed adapter is a disabled stub (CST-008 #1).

## Rationale

Maximal demonstrability and determinism; scheduling choice trades negligible demo latency for
reproducible evidence.

## Consequences

- **Positive**: complete control over governance semantics; reproducible runs.
- **Negative**: more code; join latency.
- **Operational**: single orchestrator process; no external workflow server.
- **Testing**: parametrized allowed/prohibited transition tests; fork/join tests with virtual clock; repeat-run determinism test.
- **Governance**: gates, policy and audit are engine primitives, identical for both agent modes.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Engine not ready by CP-2 | Pre-agreed simplified reductions (plan §14.1); STOP-4 |
| Scheduler deadlock (no READY node, no timer, no open gate) | Invariant check each step → safe-stop `scheduler_stalled` (unclassified ⇒ safe-stop) with audit |
| Concurrency bugs in commit phase | Commit in a single thread in node-ID order; per-transition DB transaction |

## Reversibility

Low–medium for the engine as a whole (it is the product); high for the scheduler module, which
sits behind an interface.

## Traceability

- Requirements: FR-ORC-005..008, FR-ORC-011, FR-ORC-023, FR-ORC-027, FR-ORC-029, FR-ORC-030, FR-ORC-037..039, NFR-DET-001
- Spec: Reference Lifecycle Stages; US-2; HD-001
- Plan: §3.1, §3.2, §3.5, §3.7; §12 R-03, R-05; research.md R-03, R-05
- Decisions: DQ-008, PD-004, HD-001

## Validation

State-transition and fork/join suites green (CP-2); repeat-run determinism e2e test on all
scenarios; stall-invariant test.
