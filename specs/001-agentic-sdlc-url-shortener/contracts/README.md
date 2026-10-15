# Contracts: Feature 001

Design-approved interface and schema contracts. **Contract-first**: these files are
authoritative. Implementation must reproduce them, and executable tests enforce this (plan §2.2,
R-07).

| File | Kind | Version | Owner | Consumers |
|------|------|---------|-------|-----------|
| `shortener-api.openapi.yaml` | OpenAPI 3.1 | 1.0.0 (baseline) | Human owner (API owner) | API consumers, public redirect clients, orchestrator smoke checks, contract tests |
| `orchestrator-api.openapi.yaml` | OpenAPI 3.1 | 2.0.0 (CR-002) | Human owner | `orch` CLI, human reviewers, e2e tests |
| `workflow-graph.v2.yaml` | Graph definition (YAML, validated by meta-schema) | 2.0.0 (CR-002) | Human owner (workflow owner) | Engine, tests, docs |
| `policy-set.v1.yaml` | Policy set (YAML) | 1.0.0 | Human owner (policy owner) | Policy evaluator, readiness, docs |
| `schemas/problem.schema.json` | JSON Schema 2020-12 | 1.0.0 | Shared | Both APIs |
| `schemas/workflow-state.schema.json` | JSON Schema | 1.0.0 | Orchestrator | API, CLI, evidence export |
| `schemas/gate-decision.schema.json` | JSON Schema | 2.0.0 (CR-002) | Orchestrator | API, CLI, scripted decisions |
| `schemas/audit-event.schema.json` | JSON Schema | 1.0.0 | Orchestrator | Audit store, query API, evidence |
| `schemas/policy-evaluation.schema.json` | JSON Schema | 1.0.0 | Orchestrator | Policy evaluator, readiness |
| `schemas/policy-exception.schema.json` | JSON Schema | 1.0.0 | Orchestrator | Exception workflow |
| `examples/*.json` | Representative examples (illustrative, **not execution evidence**) | — | — | Contract tests validate them |

Persistence schemas are specified in [../data-model.md](../data-model.md) §1 and §3 and realized
as Alembic revisions owned by each service.

## Versioning and compatibility rules

1. Every contract carries a semantic version (`info.version` or `version:`).
2. **PATCH**: documentation/description/example fixes with no shape or behavior change.
3. **MINOR (backward compatible)**: new optional request fields; new response fields; new
   endpoints; new enum values in *response-only* or error `code` fields; new audit event types;
   new policy checks that are `advisory`.
4. **MAJOR (breaking)**: removal or rename of fields, endpoints or enum values; type or format
   changes; new required request fields; semantic changes of status codes; a new `mandatory`
   policy check; graph topology changes that alter gate requirements.
5. **Consumers MUST ignore unknown response fields.** Producers MUST NOT emit fields not in the
   contract (drift test).
6. **Database migrations** are additive-only within a major version (data-model §3; policy
   CHG-003).
7. **Runs pin versions**: a workflow run records `graph_template_version` and
   `policy_set_version` at creation and is evaluated against those for its whole lifecycle.

## Executable validation

| Check | Tool | Where |
|-------|------|-------|
| App OpenAPI == committed contract (normalized) | pytest drift test | `tests/*/contract/test_openapi_drift.py` |
| Responses conform for generated inputs | schemathesis | `tests/*/contract/test_schemathesis.py` |
| Emitted audit events / evaluations / decisions / workflow-state documents conform | jsonschema | contract + observability suites |
| Examples conform | jsonschema / openapi example validation | `tests/contract/test_examples.py` |
| Graph and policy YAML conform to meta-schema; references resolve (nodes, checks, roles) | engine loader + tests | `tests/orchestrator/contract/test_definitions.py` |

## Change Record (required for every contract or schema change)

Copy into the PR description (repository changes) or produce as the `change-record` artifact
(engine runs, ST-05/ST-07):

```markdown
### Change Record: <contract> <old> → <new>
- Owner / approver:
- Version impact: PATCH | MINOR | MAJOR (justify against rules above)
- Backward-compatibility impact: none | consumer action required (describe)
- Affected consumers:
- Affected requirements (IDs):
- Tests added/changed:
- Documentation updated:
- Rollout / migration steps (incl. migration class: additive | destructive):
- Rollback / compensation consideration:
- Required approval: G-DESIGN (run) | human owner PR approval (repo) | + policy exception (if destructive)
- Approval reference (decision ID / PR):
```

## Change history

### Change Record: G-RELEASE rework removal (CR-002), 2026-10-15
- Owner / approver: human owner, Mani Kumar Vadugu (Human Gate 4, CR-002)
- Version impact: **MAJOR** for three contracts (rule 4):
  - `workflow-graph` 1.0.0 → 2.0.0 (file renamed `workflow-graph.v1.yaml` → `workflow-graph.v2.yaml`): G-RELEASE `rework_target` removed and `not_ready` now terminates the run, which changes gate decision semantics.
  - `gate-decision.schema.json` 1.0.0 → 2.0.0: field `not_ready_action` removed.
  - `orchestrator-api.openapi.yaml` 1.0.0 → 2.0.0: `decideGate` request body changed via the schema.
- Backward-compatibility impact: none in practice. No implementation, consumer or run exists that
  pinned 1.0.0 (pre-implementation).
- Affected consumers: engine (planned), `orch` CLI (planned), e2e tests (planned).
- Affected requirements (IDs): FR-GOV-002, FR-GOV-011, FR-GOV-015 (interpretation recorded in plan §5.3), FR-ORC-023, US-4.
- Tests added/changed: planned governance tests must assert `not_ready` → run `FAILED` with blocking reasons, and no rework option at G-RELEASE.
- Documentation updated: plan.md §3.2, §3.4, §5.1, §5.3 and Change Log; data-model.md §2.1, §2.3; ADR-016.
- Rollout / migration steps: none (no data); migration class n/a.
- Rollback / compensation consideration: revert the three files to 1.0.0 via a new change record.
- Required approval: human owner (repository change).
- Approval reference: CR-002 (Human Gate 4, 2026-10-15).

## Planned increments (delivered only through orchestrated runs, CST-007)

| Run | Shortener API | DB | Class |
|-----|---------------|----|-------|
| SCN-A | 1.1.0: `expires_at` (optional) on create; `410 link_expired`; `422 invalid_expiration`; `GET /api/v1/links/{code}/analytics` | `0002`: `links.expires_at`, `link_stats` | MINOR / additive |
| SCN-B | 1.2.0: `alias` (optional) on create; `409 alias_conflict`; `422 alias_invalid`, `alias_reserved` | `0003`: `links.code_origin` default `generated` | MINOR / additive |
| SCN-C (option A) | 1.3.0: `daily` object in analytics response | `0004`: `link_daily_stats` | MINOR / additive |
