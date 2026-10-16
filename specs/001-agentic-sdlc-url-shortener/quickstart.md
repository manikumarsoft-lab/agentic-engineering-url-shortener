# Quickstart and Validation Guide: Feature 001

**Status**: rewritten 2026-10-16 (final assessment gap G3, NFR-DOC-001) from README §2 and §5.
Every command below exists in this repository. It replaces the earlier planning draft, whose
commands (`uv sync`, `orch keys init`, `tools/check.py`, `shortener serve`, `orch staging`,
`orch trace`, `orch demo reset`) were never built. No automated test runs these commands yet
(NFR-DOC-001 remains PARTIAL, task T282).

Shell: Windows PowerShell, from the repository root. On Linux/macOS replace
`.venv\Scripts\` with `.venv/bin/`.

References: [README.md](../../README.md) ·
[recording runbook](../../docs/operations/recording-runbook.md) ·
[plan.md](./plan.md)

## 1. Prerequisites

- Python 3.12 (`requires-python = ">=3.12,<3.13"`) and git on PATH.
- No Docker, cloud account or AI API key (NFR-RUN-001, CST-006).
- Network access for `pip install` and for the live dependency audit in `orch release check`.
  Scenario runs use the hash-pinned advisory snapshot (`policy/advisory-snapshot.json`) and need
  no network.

## 2. Setup

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.lock      # pinned dependencies, incl. pytest and pip-audit
.venv\Scripts\python -m pip install --no-deps -e .            # the project; installs the `orch` CLI
```

## 3. Run the checks

```powershell
.venv\Scripts\python -m pytest              # full suite: 129 tests (on Windows 1 POSIX-only test is skipped)
.venv\Scripts\python tools\trace_check.py   # traceability check (built scope only)
.venv\Scripts\orch release check            # live pip-audit, repository secret scan, traceability; exit 1 on any FAIL
```

Runtime state goes to `var/` (gitignored). Set `ORCH_HOME` to use another folder.

## 4. Create keys (human, in your own terminal)

Each secret is printed once; only its SHA-256 hash is stored in `var/orchestrator.db`. Keep the
keys in session variables; never write them to a file in the repository.

```powershell
$CON = .venv\Scripts\orch keys create --role consumer
$ENG = .venv\Scripts\orch keys create --role engineer
$APP = .venv\Scripts\orch keys create --role approver
$REL = .venv\Scripts\orch keys create --role release-owner
```

## 5. Run the shortener (US-1)

```powershell
.venv\Scripts\orch serve --port 8000        # binds 127.0.0.1; DB var\shortener.db; keys from var\orchestrator.db
```

In a second terminal:

```powershell
$r = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/v1/links `
       -Headers @{ "X-API-Key" = $CON } -ContentType "application/json" `
       -Body '{"url":"https://example.org/a"}'
$r                                                    # 201: code, short_url, destination, created_at, expires_at
curl.exe -si http://127.0.0.1:8000/$($r.code)         # 302, Location: https://example.org/a
curl.exe -s  http://127.0.0.1:8000/api/v1/links/$($r.code)/stats -H "X-API-Key: $CON"   # clicks, last_click_at
curl.exe -s  http://127.0.0.1:8000/health/ready       # {"status":"ready","database":"ok",...}
```

Negative checks: a `javascript:` URL returns `422 scheme_not_allowed`; an unknown code returns
`404`; an `expires_at` in the past returns `422 invalid_expiration`; a missing key returns `401`.

## 6. Lock the change sets (human approver)

Runs refuse change sets that are unlocked or changed after locking. The repository already
contains a lock (`scenarios/changesets.lock.yaml`) made with the human owner's approver key, so
the scenarios run without this step. Re-lock only after reviewing a changed change set;
`orch changeset lock` rewrites the committed lock file with your key ID:

```powershell
.venv\Scripts\orch changeset lock "scenarios/scn-a/changeset" --key $APP
.venv\Scripts\orch changeset lock "scenarios/scn-b/changeset" --key $APP
.venv\Scripts\orch changeset lock "scenarios/scn-b/changeset-defective" --key $APP
.venv\Scripts\orch changeset lock "scenarios/scn-c/changeset" --key $APP
```

## 7. Execute the scenarios

Scenario names (`scenarios/registry.yaml`): `scn-a`, `scn-b`, `scn-b-defective`,
`scn-b-compensate`, `scn-c`, `scn-c-scanner-down`. `orch run submit` prints the run ID and runs
until a gate or the end. Gate IDs have the form `<run>:<node>`.

### SCN-A: greenfield (link details endpoint)

```powershell
.venv\Scripts\orch run submit scn-a
.venv\Scripts\orch gate show "<run>:approve-design"
.venv\Scripts\orch gate approve "<run>:approve-design"  --key $APP --reason "<rationale>"
.venv\Scripts\orch gate approve "<run>:approve-release" --key $REL --reason "<rationale>"
```

Expected: `clarify` SKIPPED with the reason "all five requirement-quality checks passed; no
clarification required"; run `COMPLETED`.

### SCN-B: brownfield (custom aliases) and its fault-injection variants

```powershell
.venv\Scripts\orch run submit scn-b              # impact analysis before any change; then the same two gates
.venv\Scripts\orch run submit scn-b-defective    # regression fails before promotion -> rollback -> FAILED
.venv\Scripts\orch run submit scn-b-compensate   # smoke check fails after promotion -> compensation
.venv\Scripts\orch gate approve "<run>:approve-corrective" --key $APP --reason "<rationale>"
```

### SCN-C: ambiguous ("track who clicks links")

```powershell
.venv\Scripts\orch run submit scn-c
.venv\Scripts\orch gate show "<run>:clarify"                                  # classified items and options A, C
.venv\Scripts\orch gate answer "<run>:clarify" --option A --key $ENG --reason "<rationale>"
#   option C withdraws the request -> ABORTED; --text "<free text>" reopens the gate (2 rounds max, then SAFE_STOPPED)
```

Policy exception path (fault injection: dependency scanner unavailable):

```powershell
.venv\Scripts\orch run submit scn-c-scanner-down                              # ... -> SAFE_STOPPED policy_fail:SEC-003
.venv\Scripts\orch exception request <run> SEC-003 --key $ENG --reason "<why>" --control "<compensating control>"   # prints <exception_id>
.venv\Scripts\orch exception approve <run> <exception_id> --key $APP --reason "<why>"
.venv\Scripts\orch run resume <run> --key $APP --reason "<why>"
```

Other gate decisions: `orch gate reject "<run>:<gate>" --key … --reason …` (terminates; add
`--rework` to re-run the producing stage, at most 2 times) and `orch gate escalate …` (the next
decision needs a release-owner key). `orch gate list` shows open gates.

## 8. Inspect and verify (US-5)

```powershell
.venv\Scripts\orch run status <run>
.venv\Scripts\orch run watch <run>               # step a run and print node state changes
.venv\Scripts\orch audit show <run>              # ordered audit events
.venv\Scripts\orch audit verify <run>            # hash chain valid
.venv\Scripts\orch metrics <run>                 # per-run metrics, labelled "demonstration data"
.venv\Scripts\orch evidence export <run> --out var\evidence
```

Use `--out` for your own runs: without it, `orch evidence export` writes to `evidence\` and
rewrites the committed `evidence\index.md` from your local database.

After an engine crash: `orch run recover <workflow>` marks interrupted runs `SAFE_STOPPED`; resume
them with `orch run resume` and an approver key.

## 9. Not available (planned, not implemented)

`orch trace`, audit query filters, aggregate metrics, `orch staging bootstrap|status`,
`orch demo reset` (delete `var\` instead), an orchestrator HTTP API, and an automated
repeat-run determinism test. See README "Known gaps (final assessment)".
