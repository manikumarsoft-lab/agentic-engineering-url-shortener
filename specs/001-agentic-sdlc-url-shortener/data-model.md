# Data Model: Agentic Software Engineering System: URL Shortener

**Phase**: 1 (`/speckit-plan`) · **Date**: 2026-10-15 · **Plan**: [plan.md](./plan.md) ·
Schema version: **1.0.0**

All timestamps are UTC ISO-8601 with offset (`Z`). IDs are prefixed sortable ULIDs (R-14).
Persistence is SQLite via SQLAlchemy Core; each service owns its database (plan §1.3). Column
types below are logical; Alembic revisions realize them.

---

## 1. Entities

### 1.1 Shortener (application plane)

#### ShortLink — table `links` (baseline 1.0.0)

| Field | Type | Rules | Req |
|-------|------|-------|-----|
| `code` | text PK | `^[A-Za-z0-9]{4,10}$`; generated codes length 7, base62 CSPRNG | FR-SHR-005/006, A-003 |
| `destination_url` | text not null | normalized; ≤ 2,048 chars; scheme ∈ allow-list | FR-SHR-002–004, PVT-010 |
| `created_at` | timestamp not null | server clock | |
| `creator_key_id` | text not null | key ID, never the secret | HD-003 |
| `expires_at` | timestamp null | *added by SCN-A*; must be > `created_at` at creation | FR-SHR-008/009 |
| `code_origin` | text not null default `generated` | *added by SCN-B*; `generated`/`alias` | FR-SHR-020 |

Derived status: `active` if `expires_at` is null or `now < expires_at`, else `expired` (A-014).
Expired links are retained (A-006).

#### IdempotencyRecord — table `idempotency_records` (baseline)

| Field | Type | Rules |
|-------|------|-------|
| `key_id` | text | part of PK |
| `idempotency_key` | text | part of PK; `^[A-Za-z0-9_-]{1,128}$` |
| `request_fingerprint` | text | SHA-256 of canonical request body |
| `response_status` | int | |
| `response_body` | json | |
| `created_at`, `expires_at` | timestamp | expiry 24 h |

Same `(key_id, idempotency_key)` + same fingerprint → replay; different fingerprint → `409
idempotency_conflict` (FR-SHR-013).

#### LinkAnalytics — table `link_stats` (*added by SCN-A*)

| Field | Type | Rules |
|-------|------|-------|
| `code` | text PK FK→links | |
| `redirect_count` | int not null default 0 | incremented atomically `SET redirect_count = redirect_count + 1` (A-013) |
| `last_redirect_at` | timestamp null | |

No IP addresses, user agents, referrers or other personal data (FR-SHR-012, A-005).

#### LinkDailyStats — table `link_daily_stats` (*added by SCN-C option A, PD-008*)

| Field | Type | Rules |
|-------|------|-------|
| `code` | text FK→links | PK part |
| `day_utc` | date | PK part |
| `count` | int not null | atomic upsert increment |

### 1.2 Orchestrator (control plane)

#### Run — table `runs`

| Field | Type | Rules |
|-------|------|-------|
| `run_id` | text PK | immutable; also the trace ID (128-bit) |
| `scenario_type` | enum `greenfield`/`brownfield`/`ambiguous`/`unspecified` | declared by submitter; ST-02 derives `change_kind` independently |
| `scenario_ref` | text null | e.g. `scn-b` |
| `variant` | text null | e.g. `defective`; non-null ⇒ label `fault-injection` or `finding-injection` |
| `change_set_ref` | text null | `changesets/<id>/<variant>` |
| `agent_mode` | enum `deterministic`/`ai_backed` | default `deterministic` (FR-ORC-027/029) |
| `graph_template_version` | semver | from graph contract |
| `current_graph_instance` | int | increments on topology replanning |
| `policy_set_version` | semver | pinned at creation (FR-GOV-006) |
| `state` | enum (Run state machine §2.1) | |
| `terminal_outcome` | enum `COMPLETED`/`FAILED`/`ABORTED`/`SAFE_STOPPED` null | |
| `terminal_reason` | text null | reason code + message |
| `labels` | json array | always includes `demonstration`; plus `fault-injection`, `finding-injection`, `test` |
| `base_release_id` | text | release the workspace is built from |
| `created_by_key_id`, `created_at`, `updated_at`, `terminal_at` | | |
| `idempotency_key` | text null unique with creator | |
| `row_version` | int | optimistic concurrency |

#### GraphInstance — table `graph_instances`

`(run_id, version)` PK, `template_version`, `nodes` json (resolved node definitions incl.
dynamic nodes), `edges` json, `created_reason` (`initial`/`replan:<replan_id>`), `created_at`.

#### NodeState — table `node_states`

| Field | Type | Rules |
|-------|------|-------|
| `run_id`, `node_id` | PK | node IDs from the graph (e.g. `ST-08`, `G-DESIGN`, `G-CLARIFY-1`) |
| `state` | enum (Node state machine §2.2) | |
| `attempts_used` | int | ≤ `retry.max_attempts` |
| `rework_cycles` | int | gates: ≤ 2 (PVT-013) |
| `degraded` | bool | fallback used |
| `input_hash` | text null | memoization key over input artifact versions |
| `next_eligible_at` | timestamp null | retry backoff timer |
| `row_version` | int | claim via conditional update |

#### NodeAttempt — table `node_attempts`

`attempt_id` PK, `run_id`, `node_id`, `attempt_no`, `started_at`, `ended_at`, `outcome`
(`succeeded`/`failed_transient`/`failed_permanent`/`timed_out`/`interrupted`/`refused`),
`failure_class`, `error_code`, `error_message` (sanitized), `input_versions` json,
`output_versions` json, `span_id`.

#### Artifact / ArtifactVersion — tables `artifacts`, `artifact_versions`

| Field | Rules |
|-------|-------|
| `artifact_id`, `run_id`, `type` | type ∈ `raw-requirement`, `normalized-requirement`, `quality-report`, `clarification-decision`, `additive-change-check` (ST-05a, SCN-A-AC6), `impact-analysis`, `change-record`, `task-plan`, `design`, `assumption-register`, `workspace`, `change-application-record`, `test-results`, `docs-draft`, `docs`, `threat-review`, `security-report`, `readiness-assessment`, `release-decision`, `release`, `smoke-result`, `compensation-record`, `corrective-action-decision`, `engineering-summary`, `safe-stop-report` |
| `version` | int ≥ 1, monotonically increasing per artifact |
| `content` | json (or `content_path` for large files under `var/`) |
| `content_hash` | SHA-256 of canonical content |
| `status` | `current` / `stale` / `superseded` / `rolled_back` |
| `degraded` | bool |
| provenance | `produced_by_node`, `attempt_id`, `actor_type`, `actor_id`, `agent_mode`, `input_versions` json `[{artifact_id, version, hash}]`, `created_at`, `provenance_label` (for change sets the fixed text "Authored with AI assistance (Claude Code) during development; reviewed and locked by the human owner (Mani Kumar Vadugu); applied by the deterministic agent, not generated at run time."; FR-ORC-034, CR-004) |

#### Requirement — table `requirements` (run level)

`req_id` (`RQ-<run-short>-nnn`), `run_id`, `artifact_version` (normalized-requirement version),
`kind` (`FR`/`NFR`/`constraint`), `text`, `acceptance_criteria` json, `spec_refs` json (matched
spec IDs, e.g. `FR-SHR-008`), `status` (`current`/`superseded`).

#### Gate — table `gates`

| Field | Rules |
|-------|-------|
| `gate_id` PK, `run_id`, `node_id` | node_id = gate node (`G-DESIGN`) or dynamic (`G-CLARIFY-1`, `G-EXCEPTION-1`; numbered per run) |
| `gate_type` | `clarify`/`design`/`security`/`exception`/`release`/`corrective` |
| `required_roles` | json, e.g. `["approver"]` |
| `bound_artifacts` | json `[{artifact_id, version, hash}]` (FR-GOV-004) |
| `state` | Gate state machine §2.3 |
| `opened_at`, `deadline_at`, `closed_at` | deadline = opened + gate timeout |
| `instance_no` | increments when re-opened after rework/revocation |
| `questions` | json (clarify gates: id, text, classification, options[], recommended) |

#### Decision — table `decisions`

`decision_id` PK (client-supplied for idempotency, unique), `run_id`, `gate_id` null, `type`
(`clarification`/`approval`/`rejection`/`escalation`/`exception`/`release`/`corrective`/`resume`/`abort`),
`choice` (`approve`/`reject_rework`/`reject_terminate`/`escalate`/`answer`/`ready`/`not_ready`/`resume`),
`actor_type` (`human` only for these types; others refused), `actor_key_id`, `actor_role`,
`rationale`, `answers` json, `accepted_risks` json, `bound_artifacts` json,
`decision_source` (`interactive`/`scripted`), `created_at`. Schema:
[gate-decision.schema.json](./contracts/schemas/gate-decision.schema.json).

#### PolicyEvaluation — table `policy_evaluations` (append-only)

See [policy-evaluation.schema.json](./contracts/schemas/policy-evaluation.schema.json): `eval_id`,
`run_id`, `node_id`, `policy_set_version`, `check_id`, `domain`, `mandatory`, `outcome`,
`subject_artifacts`, `evidence`, `reason`, `exception_id`, `supersedes_eval_id`, `evaluated_at`.

#### PolicyException — table `policy_exceptions`

See [policy-exception.schema.json](./contracts/schemas/policy-exception.schema.json): `exception_id`,
`run_id`, `check_id`, `policy_set_version`, `reason`, `scope`, `compensating_control`,
`requested_by_key_id`, `status` (`REQUESTED`/`APPROVED`/`REJECTED`/`EXPIRED`), `approving_authority`
(key ID + role), `approved_at`, `expires_at` and/or `review_condition`.

#### Replan — table `replans`

`replan_id`, `run_id`, `trigger` (`artifact_superseded`/`late_ambiguity`/`rework`/`scope_violation_resume`),
`superseded_artifacts` json, `stale_nodes` json, `revoked_gates` json, `graph_version_before`,
`graph_version_after`, `started_at`, `completed_at`.

#### FailureEpisode — table `failure_episodes` (materialized from audit; recomputable)

`episode_id`, `run_id`, `node_id`, `failure_detected_at`, `recovery_started_at`,
`recovery_completed_at`, `mechanism`, `status` (`recovered`/`unrecovered`/`open`),
`includes_human_wait`, `fault_injected`. Recomputable from audit at any time (CON IX: metrics
derive from events).

#### AuditEvent — table `audit_events` (append-only, triggers block UPDATE/DELETE)

See [audit-event.schema.json](./contracts/schemas/audit-event.schema.json). Key fields:
`event_id`, `run_id` (null only for system-wide events such as key issuance), `seq` (per-run,
gapless), `ts`, `event_type`, `actor {type, id, role, key_id}`, `action`, `target {type, id,
version}`, `result`, `reason`, `data`, `policy_set_version`, `graph_version`, `labels`,
`trace {trace_id, span_id}`, `episode_id`, `prev_hash`, `hash`. Unique `(run_id, seq)` and unique
`transition_key` (idempotent transitions, FR-ORC-028).

#### Span — table `spans`

`trace_id` (= run ID hex), `span_id`, `parent_span_id`, `name`, `kind`
(`node_attempt`/`http_client`/`subprocess`/`gate_wait`), `start`, `end`, `status`, `attributes`.

#### Release — table `releases` + directory `var/releases/<release_id>/`

`release_id` (`R0`, `R1`, …), `source` (`baseline-ref:<ref>` or `run:<run_id>`),
`change_set_fingerprint`, `contract_version`, `schema_revision`, `created_at`, `promoted_at`,
`status` (`staged`/`active`/`superseded`/`failed`). Exactly one `active` at a time.

#### StagingPromotion — table `promotions`

`promotion_id`, `run_id`, `from_release`, `to_release`, `started_at`, `smoke_result` json,
`outcome` (`active`/`smoke_failed`/`compensated`/`compensation_failed`),
`non_rollbackable_effects` json (e.g. links created in `[promoted_at, compensated_at)`),
`corrective_action_decision_id`.

#### APIKey — file `var/secrets/api-keys.json` (not a DB table; never committed)

`key_id`, `secret_sha256`, `role` (`consumer`/`engineer`/`approver`/`release-owner`/`agent`),
`actor_type` (`human`/`agent`), `label`, `status` (`active`/`revoked`), `created_at`.

#### Component registry — `src/orchestrator/definitions/registry/components.yaml`

`component_id`, `paths` (globs), `interfaces` (OpenAPI operation IDs), `tests` (globs), `docs`,
`security_sensitive` (bool), `owner`. Used by ST-05 impact analysis, CHG-002 and SEC-004.

### 1.3 Relationships

```text
Run 1─* GraphInstance · Run 1─* NodeState 1─* NodeAttempt
Run 1─* Artifact 1─* ArtifactVersion ─(input_versions)→ ArtifactVersion
NodeAttempt 1─* ArtifactVersion (produced)
Run 1─* Gate 1─* Decision ; Gate *─* ArtifactVersion (bound)
Run 1─* PolicyEvaluation *─0..1 PolicyException
Run 1─* Replan ; Run 1─* AuditEvent ; Run 1─* Span ; Run 1─* FailureEpisode
Run *─1 Release (base) ; Run 0..1─1 Release (produced) ; Run 0..*─ Promotion
Requirement *─1 ArtifactVersion(normalized-requirement) ; Requirement *─* spec IDs
```

---

## 2. State Machines

Transition tables are implemented as data (`engine/state.py`) and tested exhaustively: every
allowed transition has a test, and every pair not listed is rejected with `IllegalTransition`
(audited `ILLEGAL_TRANSITION_REFUSED`).

### 2.1 Run

| From | To | Trigger | Actor |
|------|----|---------|-------|
| — | `CREATED` | `POST /runs` accepted | human (engineer) |
| `CREATED` | `RUNNING` | scheduler start | system |
| `RUNNING` | `AWAITING_HUMAN` | no node runnable and ≥1 gate open | system |
| `AWAITING_HUMAN` | `RUNNING` | gate decision unblocks a node | human (via gate) |
| `RUNNING` | `REPLANNING` | replanning trigger | system |
| `REPLANNING` | `RUNNING` | replan completed | system |
| `RUNNING`/`AWAITING_HUMAN` | `COMPLETED` | ST-13 succeeded after smoke pass | system |
| `RUNNING`/`AWAITING_HUMAN` | `FAILED` | permanent failure path (bad input, rollback, compensated smoke failure) or G-RELEASE `not_ready` (CR-002), and ST-13 done | system (after the human release decision, for `not_ready`) |
| `RUNNING`/`AWAITING_HUMAN` | `ABORTED` | `reject_terminate` or `POST /runs/{id}/abort` | human (approver) |
| `RUNNING`/`AWAITING_HUMAN`/`REPLANNING` | `SAFE_STOPPED` | FR-ORC-018 trigger, gate timeout, rework limit, interruption detected at startup, compensation failure, scheduler stall (CR-002) | system |
| `SAFE_STOPPED` | `RESUMING` | `POST /runs/{id}/resume` with preconditions met (A-016) | human (approver) |
| `RESUMING` | `RUNNING` | recovery plan applied | system |
| `RESUMING` | `SAFE_STOPPED` | preconditions re-checked and failed | system |

Prohibited: any transition from `COMPLETED`, `FAILED`, `ABORTED`; `SAFE_STOPPED → RUNNING` direct;
`RESUMING` by non-approver; terminal outcome set twice.

### 2.2 Node (agent and system nodes)

| From | To | Condition |
|------|----|-----------|
| `PENDING` | `READY` | all predecessors `SUCCEEDED`/`SKIPPED`, condition true, entry criteria met |
| `PENDING` | `SKIPPED` | condition evaluated false (reason recorded) |
| `PENDING` | `BLOCKED` | predecessors done but entry criteria unmet (refusal recorded, FR-ORC-008) |
| `BLOCKED` | `READY` | entry criteria later met (e.g. exception approved) |
| `READY` | `RUNNING` | claimed by scheduler (conditional update) |
| `RUNNING` | `SUCCEEDED` | exit criteria verified (incl. mandatory policy checks at this node) |
| `RUNNING` | `FAILED_TRANSIENT` | classified transient / timeout |
| `FAILED_TRANSIENT` | `RETRY_WAIT` | attempts_used < max_attempts |
| `RETRY_WAIT` | `RUNNING` | timer fired |
| `FAILED_TRANSIENT` | `FAILED_PERMANENT` | budget exhausted |
| `RUNNING` | `FAILED_PERMANENT` | classified permanent or exit criteria failed |
| `RUNNING` | `SUSPENDED` | node returned `needs_clarification` (late ambiguity) |
| `SUSPENDED` | `READY` | clarification answered and replanning confirmed node still valid |
| `RUNNING` | `INTERRUPTED` | detected at startup recovery |
| `INTERRUPTED` | `RETRY_WAIT` | resume and node idempotent and budget remains |
| `SUCCEEDED`/`FAILED_*`/`SUSPENDED`/`BLOCKED` | `STALE` | replanning closure |
| `STALE` | `PENDING` | replanning re-schedules node |
| `SUCCEEDED` | `ROLLED_BACK` | rollback of ST-08/ST-09 effects |
| `SUCCEEDED` | `COMPENSATED` | REL-01 effects compensated by REL-02 |

Prohibited: `FAILED_PERMANENT → RETRY_WAIT`; `PENDING → RUNNING`; `READY` with an unfinished
predecessor; `SUCCEEDED → RUNNING` without `STALE`.

**Sync nodes (SP-1, SP-2)**: `PENDING → SUCCEEDED` only when every incoming branch terminal node
is `SUCCEEDED` (or `SKIPPED` where conditional). They never release while a branch is
`SUSPENDED`, `BLOCKED`, `RETRY_WAIT`, `RUNNING` or `FAILED_*` (FR-ORC-039).

### 2.3 Gate

| From | To | Actor / condition |
|------|----|-------------------|
| — | `OPEN` | gate node becomes READY; bound artifacts captured |
| `OPEN` | `APPROVED` | human with required role; bound versions current |
| `OPEN` | `REJECTED_REWORK` | human, reason required, rework_cycles < 2 |
| `OPEN` | `REJECTED_TERMINATE` | human, reason required |
| `OPEN` | `ESCALATED` | human, reason required |
| `ESCALATED` | `APPROVED`/`REJECTED_REWORK`/`REJECTED_TERMINATE` | human `approver` (or `release-owner` for release) |
| `OPEN`/`ESCALATED` | `TIMED_OUT` | system timer at `deadline_at` |
| `OPEN`/`ESCALATED`/`APPROVED` | `REVOKED` | replanning invalidated bound artifacts |
| `TIMED_OUT` | `OPEN` (same instance) | run resumed (FR-GOV-014) |

Effects: `APPROVED` → gate node `SUCCEEDED`. `REJECTED_REWORK` → producing node `STALE → PENDING`
with the rejection reason as input; at the third request → run `SAFE_STOPPED` ("rework limit
exceeded"). `REJECTED_TERMINATE` → run `ABORTED`, except at G-RELEASE: there, `not_ready` is
recorded as `REJECTED_TERMINATE` and the run ends `FAILED` with blocking reasons. G-RELEASE has
no `REJECTED_REWORK` (CR-002). `TIMED_OUT` → run `SAFE_STOPPED`. `REVOKED` → new
gate instance when re-reached.

Prohibited: any agent/system actor → `APPROVED`/`REJECTED_*`/`ESCALATED`; `TIMED_OUT → APPROVED`;
decisions bound to non-current versions; decisions on `REVOKED` gates.

### 2.4 Policy exception

`REQUESTED → APPROVED | REJECTED`; `APPROVED → EXPIRED` (clock passes `expires_at` or review
condition triggered). Non-waivable checks (Governance §3) cannot be `REQUESTED`.
`REQUESTED → APPROVED | REJECTED` is refused when the deciding key identity equals
`requested_by.key_id` (FR-GOV-017; `403 separation_of_duties_violation`, audited
`GATE_DECISION_REFUSED`).

### 2.5 Release

`staged → active → superseded`; `staged → failed` (smoke failed); compensation sets the previous
release from `superseded → active`.

---

## 3. Persistence Schemas and Migration Rules

- Each service has its own Alembic environment. Revision IDs are human-readable
  (`0001_baseline`, `0002_scn_a_expiration_analytics`, …).
- **Additive-only** within a major version (CHG-003): allowed ops are `create_table`,
  `add_column` (nullable or with server default), `create_index`. Disallowed without an approved
  exception and a major bump: `drop_table`, `drop_column`, `alter_column` (type/nullability
  narrowing), renames.
- Audit and policy-evaluation tables get `BEFORE UPDATE` / `BEFORE DELETE` triggers that
  `RAISE(ABORT, 'append-only')`.
- Every migration is tested up-from-empty and up-from-previous-release with data.
- Shortener baseline revision `0001_baseline`: `links` (without `expires_at`/`code_origin`),
  `idempotency_records`. Orchestrator `0001_baseline`: all §1.2 tables.

---

## 4. Validation Rules Summary (shortener)

| Rule | Outcome code (problem+json `code`) | HTTP |
|------|-----------------------------------|------|
| Body/field shape invalid | `invalid_request` | 422 |
| Unparseable URL / missing host | `malformed_url` | 422 |
| Scheme not in allow-list | `scheme_not_allowed` | 422 |
| Length > 2,048 | `url_too_long` | 422 |
| User-info present | `credentials_in_url` | 422 |
| Control / non-printable chars | `invalid_characters` | 422 |
| Host is the shortener's own host | `self_referential_url` | 422 |
| Private/loopback/link-local IP literal or `localhost` (PD-001) | `private_address_not_allowed` | 422 |
| Missing/invalid key | `unauthorized` | 401 |
| Wrong role | `forbidden` | 403 |
| Idempotency key reuse with different payload | `idempotency_conflict` | 409 |
| Rate limit exceeded | `rate_limited` | 429 |
| Code generation exhausted (5 collisions) | `code_generation_exhausted` | 503 |
| Persistence unavailable | `persistence_unavailable` | 503 |
| Unknown code | `not_found` | 404 |
| *(SCN-A)* expired | `link_expired` | 410 |
| *(SCN-A)* expiration in past / malformed | `invalid_expiration` | 422 |
| *(SCN-B)* alias taken | `alias_conflict` | 409 |
| *(SCN-B)* alias charset/length invalid | `alias_invalid` | 422 |
| *(SCN-B)* alias reserved | `alias_reserved` | 422 |
