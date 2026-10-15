# ADR-006: Change Application via Pre-Authored Change Sets in Isolated Workspaces

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Related plan-gate approvals: PD-009 (baseline ref), PD-012 (test
failure → rollback → FAILED) (Mani Kumar Vadugu, 2026-10-15). Change-set format (research R-06) is
pending this ADR.

## Context

In deterministic mode, ST-08 applies a pre-authored, human-reviewed change set to an isolated copy
of the system under change; a run never modifies the main working tree (Clarification Q1,
FR-ORC-032..036). Integrity must be verified against the approved version (CHG-001), the
actually-touched scope must stay within the approved impact analysis (SCN-B-AC5, CHG-002), and a
deliberately defective variant must exist to demonstrate rollback (FR-ORC-036). Scenarios build
on each other (R0 → R1 → R2 → R3). The reference workstation has `core.autocrlf=true` and no
`.gitattributes` (observed 2026-10-15).

## Decision Drivers

- Human reviewability of the change (it is applied, not generated).
- Precise extraction of touched files for scope enforcement.
- Tamper evidence from approval to application.
- Reproducibility across demo resets and after manual merges.
- Windows line-ending robustness.

## Options Considered

### Option A — Unified diff + manifest + lock, applied with `git apply` in a copied workspace
- **Approach**: `changesets/<id>/<variant>/{manifest.yaml, patch.diff, REVIEW.md}`; `changesets/approved.lock.yaml` holds SHA-256 of each bundle (manifest+patch), committed by the human after review. ST-08: verify lock == bundle == G-DESIGN-bound fingerprint → copy base release snapshot to `var/work/<run>/<attempt>/` → `git apply --check` → `git apply` → compute touched files → compare with approved components.
- **Advantages**: standard, reviewable format; exact scope extraction; cheap integrity check.
- **Disadvantages**: diffs are base-sensitive (must match the base release).
- **Risks**: CRLF/LF mismatches on Windows; patch not applying after base changes.
- **Implementation impact**: `PatchApplier` interface wrapping `git`; `.gitattributes` enforcing LF for `src/`, `tests/`, `changesets/`, `specs/**/contracts/`; manifest declares `base_release`.
- **Assessment implications**: brownfield change is concrete and inspectable.

### Option B — Full-file overlay directories
- **Approach**: replacement files copied over the workspace.
- **Advantages**: no patch tooling; base-insensitive.
- **Disadvantages**: intent hidden; scope = whole files; review harder.
- **Risks**: silently overwriting unrelated edits in the base.
- **Implementation impact**: simple copy.
- **Assessment implications**: weaker impact/scope evidence.

### Option C — Programmatic AST transforms
- **Approach**: Python codemods.
- **Advantages**: base-tolerant.
- **Disadvantages**: over-engineered; transforms themselves need review and tests.
- **Risks**: timebox.
- **Implementation impact**: large.
- **Assessment implications**: no added governance value.

## Decision

Option A. Additional rules:
1. Manifest fields: `scenario`, `variant` (`normal`/`defective`/`undeclared-scope`/…), `base_release`, `declared_components`, `contract_version_after`, `migration_class`, `reviewer`, `ai_assistance_disclosure`.
2. Provenance label on applied artifacts: "pre-authored, human-reviewed change set, applied by deterministic agent" (FR-ORC-034).
3. **Change sets may not add or change third-party dependencies** (the lockfile is repository-level and outside the workspace); a manifest declaring dependency changes is rejected (`manifest_invalid`). *(Ruled by the human owner at Human Gate 4, ruling 3, 2026-10-15: change sets may NOT add or
   change dependencies.)*
4. Release snapshots: R0 from git ref `shortener-baseline-v1` (PD-009) via `git archive`; R(n+1) = workspace of the run that promoted it. Snapshots are immutable under `var/releases/`.
5. Fault-injection variants are labeled and only runnable with the variant named explicitly.

## Rationale

Diffs give the strongest reviewability and scope evidence; integrity hashing makes approval
binding; snapshots make the brownfield chain reproducible without touching the working tree.

## Consequences

- **Positive**: tamper-evident, scoped, reproducible change application.
- **Negative**: change sets must be authored against the correct base release; order SCN-A → B → C matters.
- **Operational**: `.gitattributes` must be added in slice 1; human must tag the baseline and commit the lock after review.
- **Testing**: integrity mismatch test, undeclared-scope test, patch-rejection test, defective-variant rollback e2e, CRLF test on Windows.
- **Governance**: CHG-001/002 evaluated at ST-08; change-set approval is bound at G-DESIGN.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| CRLF conversion breaks `git apply` | `.gitattributes` `eol=lf` for relevant paths; `--whitespace=nowarn`; Windows integration test |
| Base drift after manual merges | Pinned `base_release` + R0 from tag (PD-009) |
| Lock edited together with patch to bypass integrity | Lock changes are repository commits reviewed by the human; G-DESIGN binds the fingerprint shown to the approver |

## Reversibility

High. Format and applier are isolated behind `ChangeSetStore` / `PatchApplier`.

## Traceability

- Requirements: FR-ORC-032, FR-ORC-033, FR-ORC-034, FR-ORC-035, FR-ORC-036, FR-ORC-043, SCN-B-AC2, SCN-B-AC5, CST-007
- Spec: Clarification Q1; SCN-B; Edge Cases (integrity mismatch, isolated copy failure)
- Plan: §3.1 `sut/`, §6.2 ST-08 row, §11 intro, §12 R-06; research.md R-06; workflow-graph ST-08
- Decisions: PD-009, PD-012, HD-002

## Validation

ST-08 policy tests (CHG-001, CHG-002); defective-variant e2e shows `ROLLBACK_COMPLETED` and
staging unchanged; working-tree byte-identity check after every e2e run.
