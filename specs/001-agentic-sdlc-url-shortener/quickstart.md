# Quickstart and Validation Guide: Feature 001

**Status**: planned commands. **Nothing below has been executed yet.** The commands describe the
validation path that implementation must make true. Expected outcomes are acceptance targets,
not recorded results. Recorded evidence will come only from real runs (CON X).

References: [plan.md](./plan.md) · [contracts/](./contracts/README.md) ·
[data-model.md](./data-model.md)

## 1. Prerequisites

- Python 3.12, `uv` ≥ 0.13, `git` (on PATH)
- No Docker, no cloud account, no AI API key (NFR-RUN-001, CST-006)
- Network access is needed only for `uv sync` and the dependency vulnerability scan (SEC-003).
  Offline, SEC-003 FAILs and requires an approved exception. It never silently passes.

## 2. Setup (target: under 30 minutes end to end including scenarios, PVT-009)

```sh
uv sync                                  # install locked dependencies
uv run orch keys init                    # writes var/secrets/api-keys.json; prints one key per role ONCE
#   → copy the printed keys into your shell session, e.g.:
export ORCH_ENGINEER_KEY=sk_...  ORCH_APPROVER_KEY=sk_...  ORCH_RELEASE_KEY=sk_...  SHORTENER_KEY=sk_...
uv run python tools/check.py             # lint (ruff), types (mypy --strict), tests, coverage
```

Expected: all checks green; coverage of domain, engine, policy and observability ≥ 85% (PVT-007).

## 3. Run the shortener baseline (US-1)

```sh
uv run shortener serve --port 8000       # dev instance, DB var/dev/shortener.db
curl -s -X POST localhost:8000/api/v1/links -H "X-API-Key: $SHORTENER_KEY" \
     -H "Content-Type: application/json" -d '{"url":"https://example.org/a"}'
#   → 201 {code, short_url, url, created_at}
curl -si localhost:8000/<code>           # → 302 Location: https://example.org/a
curl -si -X POST ... -d '{"url":"javascript:alert(1)"}'   # → 422 code=scheme_not_allowed
curl -si localhost:8000/health/ready     # → 200 {"status":"ok"}
```

## 4. Start the orchestrator

```sh
uv run orch serve --port 8200            # control plane; DB var/orchestrator/orchestrator.db
uv run orch staging bootstrap --ref shortener-baseline-v1   # release-owner key; creates R0 and starts staging :8100
```

Expected: `orch staging status` shows `R0 active`, smoke passing.

## 5. Execute the scenarios (recorded evidence runs use interactive decisions)

### SCN-A: greenfield (expiration + analytics)

```sh
uv run orch run submit --scenario scn-a --change-set changesets/scn-a/normal
uv run orch run watch <run_id>           # live node states; G-CLARIFY shown as SKIPPED with reasons
uv run orch gate list --run <run_id>     # G-DESIGN open
uv run orch gate show <gate_id>          # bound artifacts: design v1, task-plan v1, change-set fingerprint
uv run orch gate decide <gate_id> --approve --rationale "..."          # approver key
uv run orch gate decide <gate_id> --ready --accept-risk R-1:"..."      # release-owner key at G-RELEASE
```

Expected: terminal `COMPLETED`; staging `R1`; `curl` on staging returns `410` for an expired
link; `orch evidence export <run_id>` lists EV-001..EV-007.

Variant (finding-injection, labeled): `--variant late-ambiguity` → ST-11a `SUSPENDED`, G-CLARIFY-1
open while ST-09/ST-10a finish and SP-1 holds; answering it re-runs only the affected nodes.

### SCN-B: brownfield (custom aliases)

```sh
uv run orch run submit --scenario scn-b --change-set changesets/scn-b/normal
```

Expected: ST-05 impact analysis present (EV-005); G-DESIGN binds the change-set fingerprint;
G-SECURITY opens (validation component is security-sensitive); regression and new tests pass;
terminal `COMPLETED`, staging `R2`.

Fault-injection variant (labeled): `--change-set changesets/scn-b/defective` → ST-09 fails →
`ROLLBACK_COMPLETED`, workspace discarded, staging still `R1`, terminal `FAILED`.

### SCN-C: ambiguous ("track who clicks links")

```sh
uv run orch run submit --scenario scn-c
uv run orch gate show <gate_id>          # classified items: missing_information, unclear_term, policy_conflict (PRIV-001)
uv run orch gate decide <gate_id> --answer Q1=A --answer Q2="lifetime of link" --rationale "..."
```

Expected (option A): requirement v2, replanning events, resume at the earliest affected stage,
change set `scn-c/aggregate-daily` applied, terminal `COMPLETED`, staging `R3`.
Option B without exception: PRIV-001 `FAIL` → `SAFE_STOPPED`. No answer before the gate timeout
(demo profile): `SAFE_STOPPED` "no decision". Option C: `ABORTED`.

## 6. Inspect and verify (US-5)

```sh
uv run orch run show <run_id>            # workflow-state document (schema-valid)
uv run orch run timeline <run_id>        # ordered audit events + terminal outcome
uv run orch audit verify --run <run_id>  # hash chain valid
uv run orch trace FR-SHR-020             # requirement → decision → task → artifact → test → evidence
uv run orch metrics                      # success/failure, retries, rollback/compensation, MTTR (labeled demonstration)
```

## 7. Governance negative checks (SC-004, SC-011)

```sh
uv run orch gate decide <gate_id> --approve --key $ORCH_AGENT_KEY   # → 403 agent_not_permitted; audited
uv run orch gate decide <gate_id> --approve  # with stale bound version → 409 stale_artifact_version
```

## 8. Automated end-to-end and determinism

```sh
uv run pytest tests/e2e -m "scenario"    # scripted decisions (labeled test); all three scenarios + variants
uv run pytest tests/e2e -k determinism   # repeat runs → identical stage sequence, gate events, terminal outcomes
```

## 9. Release readiness (repository level)

```sh
uv run orch release check                # scans, traceability --check, coverage, audit verify
uv run python tools/trace/build_matrix.py --check   # EV-008 docs/traceability.md
```

Expected: report written to `docs/release-readiness.md` with every condition and its evidence;
final sign-off is a human action.

## 10. Reset

```sh
uv run orch demo reset                   # confirms interactively; only touches var/; rebuilds R0 from the baseline ref
```
