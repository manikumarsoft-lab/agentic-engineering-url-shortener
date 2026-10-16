# ADR-001: Programming Language and Framework

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

Superseded in part by [ADR-020](ADR-020-python-toolchain-as-built.md) (toolchain, test tooling,
validation) — **proposed, CR-009, awaiting human owner approval**. Until approved, this ADR's text
stands and the differences are listed in [docs/reviews/final-assessment.md](../reviews/final-assessment.md) §3.

History: Proposed 2026-10-15. Underlying selection made by the human owner (Mani Kumar Vadugu)
during `/speckit-plan` (research R-01, DQ-008).

## Context

Both services (URL shortener, orchestration engine) plus CLI, deterministic agents, contract
tests and scanners must be built and evidenced within a 2–3 day timebox (CST-005) on a single
Windows 11 workstation without Docker or an AI key (NFR-RUN-001, CST-006). Observed toolchain:
Python 3.12.10, uv 0.13.1, Node 24.20.0; no JDK, Go, .NET or Docker. The assessment rewards
executable API/schema contracts (plan §2.2) and TDD (CON IV).

## Decision Drivers

- Timebox and speed of the red-green-refactor loop.
- Mature tooling for OpenAPI 3.1 / JSON Schema generation and contract testing.
- Property-based testing for validation and concurrency.
- Zero extra infrastructure; reviewer setup < 30 min (PVT-009).
- One language across services, engine, agents, scanners and tests.

## Options Considered

### Option A — Python 3.12 + FastAPI + Pydantic v2 (uv-managed)
- **Approach**: FastAPI for both HTTP services, Pydantic v2 models as schema source, Typer CLI, pytest/Hypothesis/schemathesis.
- **Advantages**: OpenAPI 3.1 + JSON Schema emitted from models; schemathesis and Hypothesis available; installed toolchain; fastest test loop; scanners (pip-audit, detect-secrets) are Python-native.
- **Disadvantages**: dynamic typing; lower raw throughput; GIL limits CPU parallelism (irrelevant: I/O-bound).
- **Risks**: runtime type errors; FastAPI-generated OpenAPI cosmetic drift vs committed contract.
- **Implementation impact**: `mypy --strict` + ruff mandatory in `tools/check.py`; drift test normalization (ADR-007).
- **Assessment implications**: maximizes time available for orchestration, governance and evidence.

### Option B — TypeScript (Node 24) + Fastify + TypeBox/Zod
- **Approach**: Fastify with JSON-Schema-native routes, Vitest.
- **Advantages**: strong static types; native JSON Schema; installed.
- **Disadvantages**: more scaffolding for engine/persistence/migrations; weaker property-based contract testing ecosystem; scanners less integrated.
- **Risks**: timebox overrun on engine plumbing.
- **Implementation impact**: additional tooling decisions (ORM/migrations, CLI framework).
- **Assessment implications**: equal credibility, less time for scenarios/evidence.

### Option C — Java/Kotlin + Spring Boot
- **Approach**: Spring Boot services, JUnit, springdoc.
- **Advantages**: production familiarity, strong typing, mature ecosystem.
- **Disadvantages**: no JDK installed; heavier setup; more ceremony per slice.
- **Risks**: PVT-009 setup target; schedule.
- **Implementation impact**: JDK + build tool installation for reviewers.
- **Assessment implications**: high schedule risk for a 2–3 day window.

## Decision

Option A: Python 3.12, FastAPI, Pydantic v2, managed by uv with a committed `uv.lock`; Typer for
the CLI; pytest + Hypothesis + schemathesis for tests; mypy strict and ruff enforced.

## Rationale

Best fit for timebox, toolchain availability and contract rigor; one language reduces cognitive
and integration cost for a single developer working with an AI assistant.

## Consequences

- **Positive**: fast TDD loop; executable contracts; Python-native security scanners.
- **Negative**: static guarantees depend on mypy discipline; throughput lower than JVM/Go.
- **Operational**: reviewers need Python 3.12 and uv only (plus git).
- **Testing**: Hypothesis for validation/code-gen properties; schemathesis for contract conformance.
- **Governance**: every dependency must be listed in `policy/approved-dependencies.yaml` (DEP-001) and pass LIC-001.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Runtime type errors | mypy strict in CI; Pydantic at all trust boundaries |
| PVT-001/002 latency misses | Non-gating by approval (DQ-009); measured and reported |
| Python version drift on reviewer machines | `requires-python = ">=3.12,<3.13"`; uv installs the interpreter if missing |

## Reversibility

Medium. Services communicate only via versioned HTTP contracts, so either service could be
re-implemented behind the same contract; the engine is the costliest part to port.

## Traceability

- Requirements: NFR-RUN-001, NFR-TST-001, CST-002, CST-005, CST-006, PVT-007, PVT-009
- Spec: Constraints; Clarifications DQ-008
- Plan: Technical Context; §12 R-01; research.md R-01
- Decisions: DQ-008 (human selection 2026-10-15), HD-001

## Validation

Slice 1 exit: `tools/check.py` (ruff, mypy strict, pytest, coverage) green on the skeleton;
slice 3 exit: contract drift + schemathesis suites green; PVT-009 fresh-setup timing recorded.
