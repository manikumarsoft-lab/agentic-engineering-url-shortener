# Agentic Software Engineering System: URL Shortener

## 1. Overview

This repository holds two things:

- **A URL shortener API** (`src/shortener`, FastAPI): create short links (random 7-character
  base62 codes, collision retry, idempotency keys), 302 redirects, expiry (`410`), per-link stats,
  live/ready health checks, URL validation, API keys and rate limiting.
- **An orchestrator** (`src/orchestrator`, CLI `orch`): runs a software-delivery workflow as a
  dependency graph of agent stages and human gates. It applies a requirement to the shortener in
  an isolated workspace, test-first, under versioned policies, and records an append-only,
  hash-chained audit trail and a per-run evidence export.

The repository is the **lean implementation slice HD-CUT-002**
([docs/scope/lean-slice.md](docs/scope/lean-slice.md)). The full specification, plan and task
record are in [specs/001-agentic-sdlc-url-shortener/](specs/001-agentic-sdlc-url-shortener/).
Recorded scenario runs are in [evidence/](evidence/index.md).

## 2. Setup (Windows PowerShell, Python 3.12)

The project requires Python `>=3.12,<3.13` (`pyproject.toml`). From the repository root:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.lock      # pinned dependencies, incl. pytest and pip-audit
.venv\Scripts\python -m pip install --no-deps -e .            # the project itself; installs the `orch` CLI
```

Run the tests:

```powershell
.venv\Scripts\python -m pytest            # full suite
.venv\Scripts\python tools\trace_check.py # traceability check (also run in CI)
.venv\Scripts\orch release check          # release-readiness check (live pip-audit, repository secret scan)
```

At commit `8efdbf8` the suite collects 129 tests. On Windows: 128 passed, 1 skipped (the POSIX
process-kill test; see §7).

Runtime state (the orchestrator SQLite database, isolated workspaces, local staging) goes in the
gitignored `var/` folder.

## 3. Architecture overview

Architecture decisions are recorded in [docs/adr/](docs/adr/README.md) (ADR-001 to ADR-019, all
Accepted at Human Gate 4, 2026-10-15).

| Part | Where | What it does | ADR |
|------|-------|--------------|-----|
| Orchestrator engine | `src/orchestrator/engine.py` | Superstep scheduler. Each step runs every READY node at once in isolated subprocesses (fork), then commits the results in node-ID order. A node becomes READY only when all its predecessors are SUCCEEDED or SKIPPED (join). Every state change is committed together with its audit event. Handles retry (bounded, transient/permanent classification), stage timeout with process-tree kill, fallback, rollback, compensation, safe-stop, startup interruption recovery, human resume and replanning. | 003, 013, 015, 017 |
| Workflow DAG | `src/orchestrator/graph.py`, `scenarios/*/workflow.yaml` | Versioned YAML graph: agent nodes (`consumes`/`produces` artifacts), gate nodes, conditional nodes with a recorded skip reason, `on_failure` (`safe_stop`, `fail_run`, `rollback`, `compensate`), policy checks per node. | 005 |
| Agents | `src/orchestrator/agents/` | Deterministic, rule-based agents (ingest, normalize, quality check, impact analysis, decompose, design, apply tests, apply implementation, run tests, docs, threat review, validate, promote, smoke check, …). They apply **human-locked change sets** (`scenarios/*/changeset/`: manifest, `tests.patch`, `impl.patch`) in an isolated workspace copy. They do not generate code at run time. | 006 |
| Human gates | engine + `orch gate …` | Typed gates bound to the exact artifact versions they approve: `approve-design`, `approve-release`, `approve-corrective`, and `clarify` (options, free text). Approve, reject (bounded rework or terminate), escalate, timeout → `SAFE_STOPPED`. | 016 |
| Roles and keys | `src/common/apikeys.py`, `src/orchestrator/keys.py` | Role-mapped API keys `sk_<key_id>.<secret>`, stored only as SHA-256 hashes. Human roles: `consumer`, `engineer`, `approver`, `release-owner`. The `agent` role is refused at gates, and the refusal is audited. | 010 |
| Policies | `policy/policy-set.yaml` (version 1.2.0), `src/orchestrator/policy.py`, `src/orchestrator/security_scan.py` | Mandatory checks PRIV-001 (no visitor personal data), SEC-002 (no open high threat), SEC-003 (dependency audit, never PASS without evidence), SEC-004 (secret scan), REL-001 (tests executed and passing). A FAIL blocks release. Only a human-approved exception with a compensating control unblocks it. | 009 |
| Audit | `src/orchestrator/audit.py`, `src/orchestrator/store.py` | Append-only audit table (SQLite triggers reject UPDATE/DELETE), one SHA-256 hash chain per run, `orch audit verify`. | 008 |
| Metrics | `src/orchestrator/metrics.py` | Per-run success, retries, rollbacks, compensations, MTTR and node latency, computed from audit events and labelled demonstration data. | 011 |
| Rollback vs compensation | engine, workflow `on_failure` | Rollback (pre-promotion) discards the isolated workspace. Compensation (post-promotion) re-promotes the previous release, then a human-approved corrective action handles effects that cannot be undone. | 012 |
| Evidence | `src/orchestrator/evidence.py`, `src/orchestrator/summary.py` | `orch evidence export <run>` writes `evidence/<run>/` (run, transitions, artifacts, decisions, audit, chain, metrics, recovery, test results, engineering summary) and refreshes `evidence/index.md`, which lists every run, including failed and aborted ones. Every outcome gets a final engineering summary that states why. | — |
| Shortener | `src/shortener/` | FastAPI app. SQLite (WAL) store. CSPRNG base62 codes. Generated OpenAPI contract with a drift test. | 001, 002, 007, 014, 019 |

## 4. Scenario results

Values below are copied from `evidence/<run>/engineering-summary.json`, `metrics.json` and
`chain.json`. "Red" is the new tests run before the implementation patch. "Green" is
`python -m pytest tests/shortener` in the isolated workspace after it. Green counts differ between
scenarios because each change set applies independently to the same baseline (§7).

| Scenario | Run | Labels | State | Reason | Red (tests / failures) | Green (tests / failures) | Policy | Recovery | Audit chain |
|----------|-----|--------|-------|--------|------------------------|--------------------------|--------|----------|-------------|
| SCN-A greenfield: link details endpoint | [run_1491b1c537664814](evidence/run_1491b1c537664814/) | demonstration | COMPLETED | — | 4 / 3 | 64 / 0 | PRIV-001, SEC-002, SEC-003, SEC-004, REL-001: PASS | none | 74 events, valid |
| SCN-B brownfield: custom aliases | [run_bc533834c7dc4e5e](evidence/run_bc533834c7dc4e5e/) | demonstration | COMPLETED | — | 14 / 13 | 74 / 0 | all 5 PASS | none | 79 events, valid |
| SCN-B defective (pre-promotion fault) | [run_77723ef73ccf4ea7](evidence/run_77723ef73ccf4ea7/) | demonstration, fault-injection | FAILED | `rolled_back:tests_failed` | 14 / 13 | 74 / 1 (`tests.shortener.test_api::test_code_collisions_retry_then_give_up_after_five`) | not evaluated (run stopped at `test`) | rollback: 1 | 56 events, valid |
| SCN-B compensate (post-promotion fault) | [run_03a5a6d9a2154bea](evidence/run_03a5a6d9a2154bea/) | demonstration, fault-injection | FAILED | `compensated:smoke_failed` | 14 / 13 | 74 / 0 | all 5 PASS | compensation: 1; corrective action approved | 97 events, valid |
| SCN-C ambiguous, option A: daily aggregate counts | [run_fe1eef2844a541f2](evidence/run_fe1eef2844a541f2/) | demonstration | COMPLETED | — | 3 / 3 | 63 / 0 | all 5 PASS | none | 88 events, valid |
| SCN-C scanner down: policy exception | [run_5defbd091d494e4c](evidence/run_5defbd091d494e4c/) | demonstration, fault-injection | COMPLETED | — | 3 / 3 | 63 / 0 | SEC-003 FAIL (scanner unavailable, injected) → exception `exc_925ccbd0c2414f6b` APPROVED → recorded as `EXCEPTION-REQUESTED`; the other 4 PASS | human resume: 1 | 104 events, valid |
| SCN-C option C: withdraw | [run_4fae12b6c3f14ca6](evidence/run_4fae12b6c3f14ca6/) | demonstration | ABORTED | `clarification option C: Withdraw the request` | — | — | not evaluated | none | 22 events, valid |

What each run shows:

- **SCN-A**: the clarification gate was skipped with a recorded reason. TH-1 (information
  disclosure, high) was mitigated by owner scoping. Design approved by the approver key
  `63320c4d1c94`, release approved by the release-owner key `2788b911e283`.
- **SCN-B**: impact analysis computed from the requirement and the baseline import graph before
  any change, and reviewed at `approve-design`.
- **SCN-B defective**: the `scn-b` workflow with the defective change set (variant `defective`).
  The regression failed before promotion. Recorded result: "ROLLBACK before promotion: the isolated
  workspace was discarded, nothing was promoted, the last known-good release is unchanged". No
  release gate opened.
- **SCN-B compensate**: promoted after the release decision. The injected post-promotion smoke
  check failed. The previous release was restored and verified, and the approver approved the
  corrective action at `approve-corrective`.
- **SCN-C option A**: the engineer key `95b4677fbabf` answered the clarification ("daily aggregate
  click counts per link"). The catalog selected the approved change set and PRIV-001 passed.
- **SCN-C scanner down**: SEC-003 FAILed with the reason "dependency scanner unavailable (injected
  fault): no evidence, never PASS" and the run safe-stopped. The engineer key requested an
  exception (compensating control: "Manual review of dependency manifest; rescan within 24 hours
  when scanner is restored."), the approver key approved it, the run was resumed, and the release
  owner approved the release.
- **SCN-C option C**: "terminated by a human at clarify (engineer key 95b4677fbabf)".

## 5. How to reproduce a run

The full procedure is [docs/operations/recording-runbook.md](docs/operations/recording-runbook.md).

**Keys are created by the human, in their own PowerShell terminal, and never stored in the
repository.** Each secret is printed once. The database keeps only its SHA-256 hash, in the
gitignored `var/` folder. Agents and coding assistants never create keys or decide gates.

```powershell
# 1. Keys (human, own shell); keep them in session variables only
$ENG = .venv\Scripts\orch keys create --role engineer
$APP = .venv\Scripts\orch keys create --role approver
$REL = .venv\Scripts\orch keys create --role release-owner

# 2. Review, then lock each change set (runs refuse unlocked or modified change sets)
.venv\Scripts\orch changeset lock "scenarios/scn-a/changeset" --key $APP

# 3. Submit a scenario and decide its gates (example: SCN-A)
.venv\Scripts\orch run submit scn-a                       # prints the run id
.venv\Scripts\orch gate show "<run>:approve-design"
.venv\Scripts\orch gate approve "<run>:approve-design"  --key $APP --reason "<your rationale>"
.venv\Scripts\orch gate approve "<run>:approve-release" --key $REL --reason "<your rationale>"

# 4. Verify and export
.venv\Scripts\orch audit verify <run>
.venv\Scripts\orch metrics <run>
.venv\Scripts\orch evidence export <run>
```

Scenario names (`scenarios/registry.yaml`): `scn-a`, `scn-b`, `scn-b-defective`,
`scn-b-compensate`, `scn-c`, `scn-c-scanner-down`. SCN-C uses
`orch gate answer "<run>:clarify" --option A|C --key $ENG --reason "…"`. The exception path uses
`orch exception request`, `orch exception approve` and `orch run resume`.

A new run gets a new run id, timestamps and key ids. Run ids, states and test counts from your
runs will not match §4 exactly unless the code and change sets are unchanged.

## 6. Testing approach

- **Test-first (red/green) in every scenario run.** The orchestrator applies the change set's
  `tests.patch` first and requires the new tests to fail (`tests_not_red` is a permanent failure
  otherwise). It records that red result, then applies `impl.patch` and records the green result of
  the full shortener suite. Both are in each run's `test-results.json`.
- **Regression suite.** The green phase runs all of `tests/shortener`, not just the new tests.
  That is how SCN-B defective was caught: the new alias tests passed, but the existing
  `test_code_collisions_retry_then_give_up_after_five` failed, and the run rolled back.
- **Repository suite** (`tests/`, 129 tests): shortener API, validation, logging, OpenAPI contract
  drift, 200 parallel creates against a real server (`tests/shortener`); graph, flow and gates,
  reliability (retry, timeout, fallback, safe-stop), real process interruption and recovery,
  replanning, policy and audit, dependency and secret scanning, summary and compensation
  (`tests/orchestrator`); CLI (`tests/cli`); end-to-end scenarios (`tests/e2e`); and a
  traceability check (`tests/test_traceability.py`).
- **CI** (`.github/workflows/ci.yml`, Ubuntu, Python 3.12): installs `requirements.lock`, runs the
  full suite (including the POSIX process-kill test), runs `tools/trace_check.py` and runs a live
  `pip-audit` of `requirements.lock`.

## 7. Limitations and trade-offs

- **Lean slice (HD-CUT-002).** On 2026-10-15 the human owner decided to deliver a lean
  implementation that demonstrates every assessed capability, without per-task ceremony.
  [docs/scope/lean-slice.md](docs/scope/lean-slice.md) §1 lists what is built and tested. §2 lists
  what is **planned, not implemented**, for example: the orchestrator HTTP API (the CLI is the only
  interface), a repeat-run determinism test, attempt fencing tokens, interruption tests at every
  stage boundary, ARCH/AUD/DEP/LIC policy domains, separation of duties between key identities,
  exception expiry, bidirectional traceability, a coverage gate, and an AI-backed agent.
- **Metrics are demonstration data.** Every `metrics.json` is labelled `"demonstration data"`, from
  single runs on one workstation. Durations and MTTR include human decision time. They are not
  performance measurements, and PVT-001/002 load latency is not measured.
- **POSIX kill path skipped on Windows.** `test_kill_tree_posix_path` (`killpg`) is skipped on
  Windows and runs only on the Ubuntu CI runner. The Windows path (`taskkill /T /F`) is tested
  locally.
- **Deterministic agents, not generative ones.** Agents apply pre-authored, human-reviewed and
  locked change sets. This makes runs reproducible and reviewable, but the system does not
  demonstrate run-time code generation.
- **One baseline, independent change sets.** Every change set is authored against the same
  baseline and applies independently: SCN-B does not build on SCN-A, and there is no release chain.
  Editing the baseline files breaks the patches (`patch_does_not_apply`) until they are re-authored
  and re-locked.
- **SEC-003 in scenario runs uses a pinned snapshot.** The snapshot is a real `pip-audit` run
  (recorded: "pip-audit 2.10.1 … 49 pinned dependencies, 0 known vulnerabilities"), hash-pinned in
  the policy set. The live audit runs in `orch release check` and CI.
- **Local releases only.** Promotion goes to a local snapshot or local staging. Merging into the
  repository remains a manual human action.
- **Persistence and tooling differ from the ADR text.** The implementation uses stdlib `sqlite3`
  (WAL, `CREATE TABLE IF NOT EXISTS`, append-only triggers) rather than SQLAlchemy Core + Alembic
  (ADR-002), and pip with `requirements.lock` rather than `uv` (ADR-001).
- **TDD record for the baseline.** Scenario change sets record red then green. The baseline
  shortener code was not developed red-first per task (lean-slice §3, open question 3).

## 8. How AI assistance was used and governed

- **What AI did.** Claude Code, driven through the SpecKit workflow (`.claude/skills/speckit-*`,
  `.specify/`), wrote the drafts of the specification, plan, ADRs, tasks and checklists, the
  application and orchestrator code, the tests, and the scenario change sets
  (`tools/author_changesets.py`).
- **What the human owner did.** Mani Kumar Vadugu, the human owner:
  - reviewed and accepted the ADRs (Human Gate 4) and made the scope decisions (HD-CUT-002, HD-SCN-001);
  - reviewed and locked every change set with his approver key (`scenarios/changesets.lock.yaml`);
  - created all keys in his own shell, following the runbook (secrets are never stored in the repository; only their hashes exist, in the gitignored `var/` database);
  - made every gate decision in the recorded runs himself, with his own written reasons: design, release, clarification, corrective action, and the SEC-003 exception and resume.
- **How it is enforced.** Gates accept only human role keys. An `agent` key is refused and the
  refusal is audited. Each decision is bound to the artifact versions it approved, and replanning
  revokes stale approvals. Change sets that are unlocked or modified after locking are refused
  (`integrity_mismatch`). Every decision, with its key id and reason, is in the hash-chained audit
  trail and the run's `decisions.json`. The runbook directs that agents never run the recording
  commands.
