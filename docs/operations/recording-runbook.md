# Recording Runbook: Scenario Evidence Runs

Human-only procedure for recording the scenario evidence runs with your own keys. Agents never run
these commands (plan §16.3). Run everything in **your own PowerShell terminal at the repository root**,
not inside a coding-assistant session.

Conventions:

- `<A>`, `<B>`, … stand for the run id (`run_` + 16 hex characters) that each `run submit` prints.
  Replace them before running the next command.
- Every `gate approve` / `gate answer` continues the run and prints its new state. Approving a design
  gate takes about 20–30 seconds, because the change is applied and the full test suite runs.
- `--reason` is recorded verbatim in the audit trail and the engineering summary. Write your actual
  rationale, not a placeholder.
- Every `evidence export` refreshes `evidence/index.md`, which lists every run in the database,
  including failed, aborted and safe-stopped runs.

---

## 0. Optional checks

Confirms the code and the repository are in a releasable state before you record anything.

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\orch release check
```

## 1. Create your keys

Each secret is printed once and never written to the repository. Keep the three keys separate so
every decision is attributed to the role that made it.

```powershell
$ENG = .venv\Scripts\orch keys create --role engineer
$APP = .venv\Scripts\orch keys create --role approver
$REL = .venv\Scripts\orch keys create --role release-owner
```

## 2. Review and lock the change sets

**Why**: runs refuse change sets that are not locked, or that changed after locking
(`integrity_mismatch`). Locking with your approver key is what makes the provenance label "reviewed
and locked by the human owner" true. Read `manifest.yaml`, `tests.patch` and `impl.patch` in each
folder before locking it.

```powershell
foreach ($cs in "scn-a/changeset","scn-b/changeset","scn-b/changeset-defective","scn-c/changeset") {
  .venv\Scripts\orch changeset lock "scenarios/$cs" --key $APP }
```

Recommended next step: commit the baseline and `scenarios/changesets.lock.yaml`, then tag that
commit so the baseline the change sets apply to is fixed:

```powershell
git tag -a shortener-baseline-v1 -m "baseline for locked change sets"
```

---

## 3. SCN-A: greenfield (link details endpoint)

```powershell
.venv\Scripts\orch run submit scn-a
.venv\Scripts\orch gate show "<A>:approve-design"
```

**Gate `approve-design` (approver)**: you approve the design and authorize applying the change set in
an isolated copy. Check in `gate show` that the quality checks all passed (clarification was skipped
with its reason), the task plan covers every acceptance criterion, and the design matches the
requirement.

```powershell
.venv\Scripts\orch gate approve "<A>:approve-design" --key $APP --reason "<rationale>"
```

**Gate `approve-release` (release-owner)**: you decide the release. Check that the red-then-green test
results, the threat review (TH-1 mitigated by owner scoping) and every policy check passed.

```powershell
.venv\Scripts\orch gate approve "<A>:approve-release" --key $REL --reason "<rationale>"
.venv\Scripts\orch evidence export <A>
```

## 4. SCN-B: brownfield (custom aliases)

```powershell
.venv\Scripts\orch run submit scn-b
.venv\Scripts\orch gate show "<B>:approve-design"
```

**Gate `approve-design` (approver)**: you approve the change *after* reviewing the impact analysis.
It was computed from the requirement and the baseline code's import graph before any change. Check
the impacted components, interfaces, regression tests and risks shown in `gate show`.

```powershell
.venv\Scripts\orch gate approve "<B>:approve-design" --key $APP --reason "<rationale>"
```

**Gate `approve-release` (release-owner)**: you decide the release. Check that the new alias tests
and the full regression suite passed, and that the change stayed inside the approved impact
analysis.

```powershell
.venv\Scripts\orch gate approve "<B>:approve-release" --key $REL --reason "<rationale>"
.venv\Scripts\orch evidence export <B>
```

## 5. SCN-B defective: pre-promotion ROLLBACK (fault-injection label)

```powershell
.venv\Scripts\orch run submit scn-b-defective
```

**Gate `approve-design` (approver)**: you approve the design exactly as for SCN-B. The defect is in
the implementation patch and is only revealed by testing. Expected result: the regression suite fails
before anything is promoted, the isolated workspace is discarded (rollback), and the run ends
`FAILED (rolled_back:tests_failed)`. No release gate opens.

```powershell
.venv\Scripts\orch gate approve "<BD>:approve-design" --key $APP --reason "<rationale>"
.venv\Scripts\orch evidence export <BD>
```

## 6. SCN-B compensate: post-promotion COMPENSATION (fault-injection label)

```powershell
.venv\Scripts\orch run submit scn-b-compensate
```

**Gate `approve-design` (approver)**: same review as SCN-B. The change passes every pre-promotion
check.

```powershell
.venv\Scripts\orch gate approve "<BC>:approve-design" --key $APP --reason "<rationale>"
```

**Gate `approve-release` (release-owner)**: you approve promotion to the local staging release.
Expected result: the change is promoted and serves alias traffic, then the post-promotion smoke check
fails (injected). The engine restores and verifies the previous release, and the run waits for a
corrective-action decision.

```powershell
.venv\Scripts\orch gate approve "<BC>:approve-release" --key $REL --reason "<rationale>"
.venv\Scripts\orch gate show "<BC>:approve-corrective"
```

**Gate `approve-corrective` (approver)**: you approve the corrective action for effects that
compensation cannot undo. Check the listed aliases created while the failed release was live.
Approving moves them to `links_quarantine` (reversible; audit records are never altered). Expected
result: `FAILED (compensated:smoke_failed)`.

```powershell
.venv\Scripts\orch gate approve "<BC>:approve-corrective" --key $APP --reason "disable the listed aliases"
.venv\Scripts\orch evidence export <BC>
```

## 7. SCN-C: ambiguous requirement (option A)

```powershell
.venv\Scripts\orch run submit scn-c
.venv\Scripts\orch gate show "<C>:clarify"
```

**Gate `clarify` (engineer)**: you answer the clarification. `gate show` lists the classified
problems: missing information, the unclear term "who", and the personal-data policy conflict. Option
A (daily aggregate counts, no personal data) selects the approved change set from the catalog. The
run never proceeds on a guessed interpretation.

```powershell
.venv\Scripts\orch gate answer "<C>:clarify" --option A --key $ENG --reason "<rationale>"
```

**Gate `approve-design` (approver)**: you approve the design for the clarified requirement (option A)
and the selected change set.

```powershell
.venv\Scripts\orch gate approve "<C>:approve-design" --key $APP --reason "<rationale>"
```

**Gate `approve-release` (release-owner)**: you decide the release. Check that PRIV-001 passed (no
personal data) along with the other policy checks and tests.

```powershell
.venv\Scripts\orch gate approve "<C>:approve-release" --key $REL --reason "<rationale>"
.venv\Scripts\orch evidence export <C>
```

## 8. Optional: policy FAIL + human-approved exception (fault-injection label)

```powershell
.venv\Scripts\orch run submit scn-c-scanner-down
```

**Gate `clarify` (engineer)**: as in step 7, answer option A.

```powershell
.venv\Scripts\orch gate answer "<X>:clarify" --option A --key $ENG --reason "<rationale>"
```

**Gate `approve-design` (approver)**: as in step 7. Expected result: the dependency scanner is
unavailable (injected), so SEC-003 FAILs. The release gate never opens and the run is
`SAFE_STOPPED (policy_fail:SEC-003)`.

```powershell
.venv\Scripts\orch gate approve "<X>:approve-design" --key $APP --reason "<rationale>"
```

**Exception (engineer requests, approver approves)**: release stays blocked until a human approves an
exception with a compensating control. Then you resume the run with the approver key.

```powershell
$EXC = .venv\Scripts\orch exception request <X> SEC-003 --key $ENG --reason "<why>" --control "<compensating control>"
.venv\Scripts\orch exception approve <X> $EXC --key $APP --reason "<rationale>"
.venv\Scripts\orch run resume <X> --key $APP --reason "<rationale>"
```

**Gate `approve-release` (release-owner)**: you decide the release with the approved exception on
record.

```powershell
.venv\Scripts\orch gate approve "<X>:approve-release" --key $REL --reason "<rationale>"
.venv\Scripts\orch evidence export <X>
```

## 9. Optional: SCN-C option C (withdraw)

**Gate `clarify` (engineer)**: answering option C withdraws the request. Expected result: `ABORTED`,
with an engineering summary that records who terminated the run and why.

```powershell
.venv\Scripts\orch run submit scn-c
.venv\Scripts\orch gate answer "<C2>:clarify" --option C --key $ENG --reason "withdraw the request"
.venv\Scripts\orch evidence export <C2>
```

---

## 10. Verify every recorded run

Checks each run's hash chain and shows its labelled demonstration metrics. Repeat for every run id.

```powershell
.venv\Scripts\orch audit verify <id>
.venv\Scripts\orch metrics <id>
.venv\Scripts\orch run status <id>
```

## 11. Export and commit

Re-export any run whose evidence is missing (this also refreshes `evidence/index.md`), then review
and commit `scenarios/changesets.lock.yaml` and `evidence/` yourself. The orchestrator database
stays in the gitignored `var/` folder.

```powershell
foreach ($id in "<A>","<B>","<BD>","<BC>","<C>") { .venv\Scripts\orch evidence export $id }
git status
```
