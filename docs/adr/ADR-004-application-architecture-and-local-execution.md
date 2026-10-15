# ADR-004: Application Architecture, Deployment Topology and Local Execution Model

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Topology (two services + CLI, one repository) selected by the human
owner (research R-04, DQ-008).

## Context

The system has an application plane (URL shortener) and a control plane (orchestration engine).
Runs must change the shortener only in isolated copies (FR-ORC-032), promote to a separate local
staging instance (FR-ORC-040) and never modify the repository (FR-ORC-043). Concerns must be
separated (CON VII), trust boundaries explicit (CON V), and everything must run on one
workstation with no Docker or cloud (NFR-RUN-001, EXC-004).

## Decision Drivers

- Clear trust boundary between control plane and system under change (TB-4).
- Process isolation for staging and isolated copies.
- Human gates over HTTP with role keys (HD-003).
- Simple, documented local startup (PVT-009).

## Options Considered

### Option A — Two services + CLI in one repository
- **Approach**: `shortener` FastAPI service (launched as dev, staging, or isolated-copy process, each with its own DB); `orchestrator` FastAPI service + `orch` Typer CLI; shared `common/` limited to infrastructure utilities; packages layered (api → domain → persistence) per service.
- **Advantages**: explicit boundaries; least privilege; real HTTP smoke checks; CLI and API share engine services.
- **Disadvantages**: process supervision on Windows; port management.
- **Risks**: orphaned processes; port collisions.
- **Implementation impact**: `StagingManager`/`WorkspaceManager` with process groups, readiness polling, ephemeral ports.
- **Assessment implications**: rollback/compensation evidence is credible because effects cross a process boundary.

### Option B — Single process, two modules
- **Approach**: orchestrator imports shortener modules in-process.
- **Advantages**: simplest to run.
- **Disadvantages**: system under change hosted inside control plane; staging still needs separate processes.
- **Risks**: blurred trust boundary; misleading isolation evidence.
- **Implementation impact**: less process code, more coupling.
- **Assessment implications**: weaker governance story.

### Option C — CLI-only orchestrator
- **Approach**: no orchestrator HTTP API; gates via local CLI against the DB.
- **Advantages**: less code.
- **Disadvantages**: role-key authorization reduces to local file semantics.
- **Risks**: SC-011 evidence weaker.
- **Implementation impact**: simpler.
- **Assessment implications**: weaker HD-003 enforcement.

## Decision

Option A. Package layout per plan "Project Structure": `src/shortener/{api,domain,persistence,telemetry}`,
`src/orchestrator/{engine,policy,agents,sut,audit,observability,trace,security,persistence,definitions,api,cli}`,
`src/common/` (logging, correlation, Clock, IdGenerator — no domain types). Local execution:

| Process | Port | Data |
|---------|------|------|
| shortener (dev) | 8000 | `var/dev/shortener.db` |
| shortener (staging) | 8100 | `var/staging/shortener.db`; code from `var/releases/<id>/` |
| shortener (isolated copy, per attempt) | ephemeral | `var/work/<run>/<attempt>/` |
| orchestrator + CLI | 8200 | `var/orchestrator/orchestrator.db` |

All services bind to `127.0.0.1`. Prerequisites: Python 3.12, uv, git. Runtime data lives only in
gitignored `var/`; `orch demo reset` (interactive confirmation) touches nothing outside `var/`.

## Rationale

Isolation and authorization requirements already imply separate shortener processes; making the
control plane a separate service keeps the boundary honest at modest cost.

## Consequences

- **Positive**: explicit trust boundaries TB-1..TB-6; credible isolation; HTTP-level authz evidence.
- **Negative**: process lifecycle complexity; more integration tests.
- **Operational**: documented start order (orchestrator, `orch staging bootstrap`); health endpoints on all services.
- **Testing**: integration tests spawn real processes; unit tests use in-process ASGI clients.
- **Governance**: runs have no write capability outside `var/` (FR-ORC-043 enforced by capability design, ADR-010).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Orphaned processes on Windows | `CREATE_NEW_PROCESS_GROUP`, terminate→kill with timeout, PID files in `var/`, startup sweep |
| Port in use | Configurable ports; transient failure class `port_busy` (ADR-013) |
| `common/` grows into a shared domain | Rule: no domain types in `common/`; ruff import-boundary check |

## Reversibility

Medium. Contracts are the integration surface; merging into one process later is possible but
would weaken TB-4.

## Traceability

- Requirements: FR-ORC-032, FR-ORC-040, FR-ORC-043, FR-ORC-024, FR-GOV-003, NFR-RUN-001, NFR-MNT-001, NFR-SCL-002, CST-003
- Spec: System Context; EXC-001, EXC-004; A-011, A-012
- Plan: §1 (System Context), §3.1, Project Structure, Complexity Tracking; §12 R-04; research.md R-04
- Decisions: DQ-008, HD-002, HD-003

## Validation

Integration tests: staging promote/compensate across processes; workspace isolation test asserts
the main working tree is byte-identical before/after a run; PVT-009 fresh-setup run.
