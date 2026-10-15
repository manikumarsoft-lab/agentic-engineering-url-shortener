# ADR-005: Dependency Graph Representation

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15.

## Context

Execution must be governed by an explicit dependency graph in which each stage declares inputs,
outputs, entry/exit criteria, owner, permissions and failure behavior (FR-ORC-005, CON II). The
graph needs forks F1/F2 and sync points SP-1/SP-2 (FR-ORC-037/038), conditional nodes
(FR-ORC-007), dynamically inserted gates (late clarification, exceptions) and versioning under
replanning (FR-ORC-020). Graph changes are change-controlled (FR-GOV-009).

## Decision Drivers

- Human-reviewable and diffable definition (change control).
- Machine-validated at load time; references (nodes, policy checks, roles) must resolve.
- Per-run immutability and versioning for reproducibility and lineage.
- Support for dynamic nodes without mutating the template.

## Options Considered

### Option A — Versioned YAML template + per-run graph instances
- **Approach**: `contracts/workflow-graph.v2.yaml` (semver) validated by a meta-schema; on run creation the engine instantiates a **graph instance v1** (resolved nodes/edges) stored in `graph_instances`; topology changes (replanning, dynamic gates) create instance v+1 with `created_reason`.
- **Advantages**: reviewable contract; immutable per-run versions; lineage of topology changes.
- **Disadvantages**: YAML prose fields need discipline (quoting); meta-schema to maintain.
- **Risks**: template/meta-schema drift.
- **Implementation impact**: loader + validator + instance builder; cross-reference checks (already prototyped during planning).
- **Assessment implications**: graph is an inspectable artifact reviewers can read.

### Option B — Graph defined in Python code (decorators/builders)
- **Approach**: nodes declared as Python objects.
- **Advantages**: type-checked; refactorable.
- **Disadvantages**: changes are code changes, not reviewable contracts; harder to version per run.
- **Risks**: governance metadata scattered across modules.
- **Implementation impact**: simpler loader.
- **Assessment implications**: graph less visible as a governed artifact.

### Option C — Graph stored only in the database, edited via API
- **Approach**: runtime-editable graph.
- **Advantages**: flexible.
- **Disadvantages**: weak change control; no repository history.
- **Risks**: unreviewed topology changes.
- **Implementation impact**: admin API.
- **Assessment implications**: conflicts with FR-GOV-009.

## Decision

Option A. Node kinds: `agent`, `gate`, `sync`, `system`. Edges are derived from `depends_on`
(plus `depends_on_any` for ST-13). Conditions are named predicates over artifact fields evaluated
by the engine (no arbitrary code in YAML). Optional inputs are declared explicitly
(`optional_inputs`). Dynamic node patterns (`G-CLARIFY-{n}`, `G-EXCEPTION-{n}`) are declared in
the template and instantiated per run. Runs pin `graph_template_version`.

## Rationale

The graph is itself a governed artifact; YAML + meta-schema + per-run instances gives
reviewability, validation and lineage together.

## Consequences

- **Positive**: topology visible and diffable; per-run reproducibility.
- **Negative**: condition predicates must be implemented and registered in code (closed set).
- **Operational**: invalid templates refuse to load (engine readiness fails).
- **Testing**: definition tests (schema, cycles, unresolved refs, reachability of terminals).
- **Governance**: template changes require version bump + Change Record + human approval.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Unknown predicate name in YAML | Loader rejects; test enumerates predicates |
| Cycle introduced | Loader topological check |
| Prose fields break YAML | Quoted strings policy; parse test in CI (issue already found and fixed in planning) |

## Reversibility

High: representation is isolated in the loader; instances are plain data.

## Traceability

- Requirements: FR-ORC-005, FR-ORC-006, FR-ORC-007, FR-ORC-008, FR-ORC-020, FR-ORC-037, FR-ORC-038, FR-GOV-009
- Spec: Reference Lifecycle Stages; Clarification Q2
- Plan: §3.2, §3.4, §3.6; contracts/workflow-graph.v2.yaml; contracts/README.md
- Decisions: PD-007 (G-SECURITY conditional node)

## Validation

`tests/orchestrator/contract/test_definitions.py`: schema, references, acyclicity, every node
has the CON II fields; graph-instance versioning test under replanning.
