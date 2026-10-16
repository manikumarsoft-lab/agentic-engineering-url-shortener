# ADR-020: Python Toolchain as Built

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-16, CR-009)**

Supersedes in part: [ADR-001](ADR-001-language-and-framework.md) §Decision (toolchain and test
tooling), §Consequences (Operational, Testing, Governance), §Validation. ADR-001 remains accepted
for the language and framework choice (Option A: Python 3.12, FastAPI, Pydantic v2).

History: drafted 2026-10-16 with AI assistance (Claude Code) from the final assessment
([docs/reviews/final-assessment.md](../reviews/final-assessment.md) §3). Accepted by the human owner
with CR-009 on 2026-10-16.

## Context

ADR-001 chose Python 3.12 + FastAPI + Pydantic v2, managed by uv with a committed `uv.lock`,
Typer for the CLI, pytest + Hypothesis + schemathesis for tests, and mypy strict + ruff enforced
through `tools/check.py`. Under HD-CUT-002 (lean slice) the implementation used a smaller
toolchain. The final assessment found that the repository does not match ADR-001 on the
installer, the lock file, the test tooling, static analysis and dependency governance. The plan
guardrail requires a CR and a superseding ADR for a change to an accepted decision.

## Decision

Python 3.12 (`requires-python = ">=3.12,<3.13"`) with FastAPI, Pydantic v2, Uvicorn, Typer
(`orch` CLI), PyYAML and httpx.

- **Installation**: dependencies are installed with `pip` into a virtual environment from the
  committed, fully pinned `requirements.lock`; the project itself is installed with
  `pip install --no-deps -e .`. `pyproject.toml` lists the direct dependencies unpinned.
  uv and `uv.lock` are not used.
- **Tests**: pytest only. Contract conformance is the drift test of the app-generated OpenAPI
  document (`tests/shortener/test_contract.py`, CR-007), not schemathesis. Hypothesis is not
  used.
- **Static analysis**: ruff, mypy and `tools/check.py` are not part of the build.
- **CI**: `.github/workflows/ci.yml` (ubuntu-latest, Python 3.12) installs `requirements.lock`,
  runs the full pytest suite, `tools/trace_check.py`, and a live `pip-audit` of
  `requirements.lock`.
- **Dependency governance**: `pip-audit` over `requirements.lock` (SEC-003: hash-pinned
  snapshot in runs, live in `orch release check` and CI). Approved-dependency and licence checks
  (DEP-001, LIC-001; `policy/approved-dependencies.yaml`, pip-licenses) are **not implemented**
  and are disclosed in `docs/scope/lean-slice.md` §2.2 (task T253).

## Consequences

- **Positive**: reviewers need Python 3.12 and git only; one pinned lock file for local and CI
  installs.
- **Negative**: static typing is not machine-checked (accepted risk, mitigated by Pydantic at
  trust boundaries and the test suite); no property-based or schema-fuzz testing; no coverage
  gate (PVT-007 partial, task T281); no licence or approved-dependency policy (task T253).
- **Operational**: setup per README §2 and `specs/001-agentic-sdlc-url-shortener/quickstart.md`.
- **Testing**: `python -m pytest` (129 tests at commit `f92f672`: 128 passed, 1 skipped on
  Windows).

## Traceability

- Requirements: NFR-RUN-001, NFR-TST-001, CST-006, PVT-007 (partial), PVT-009
- Supersedes in part: ADR-001
- CR: CR-009 (plan.md Change Log)
- Tasks: T281 (coverage), T289 (ruff, mypy, import boundaries), T253 (DEP/LIC)

## Validation

CI green on push; README §2 setup executed on a fresh clone (PVT-009 timing still to be recorded
by the human owner, T251).
