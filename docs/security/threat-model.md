# Threat Model: URL Shortener and Orchestrator

**Date**: 2026-10-16 · **Satisfies**: NFR-SEC-003, Constitution V (threat scenarios,
authentication assumptions, rate limiting and security trade-offs documented) · **Source**:
the final assessment ([docs/reviews/final-assessment.md](../reviews/final-assessment.md), gap
F4/T255) and the threat reviews recorded by the deterministic `threat_review` agent in the
evidence runs. Drafted with AI assistance (Claude Code); review by the human owner Mani Kumar
Vadugu: pending.

Status values: **mitigated** (a control exists, with its location), **accepted** (documented
risk, no further control in this prototype), **open** (needs a human decision or a fix).

## 1. Scope and trust boundaries

| Boundary | Crosses | Authentication |
|----------|---------|----------------|
| Public internet → shortener redirect `GET /{code}` | anyone | none (A-001: redirect is public) |
| API client → shortener `POST /api/v1/links`, `GET /api/v1/links/{code}/stats` | key holders | `X-API-Key`, human role (`consumer` or higher); `agent` keys refused (`src/shortener/app.py` `require_key`) |
| Human operator → orchestrator CLI `orch` | local user | `--key` / `ORCH_KEY`; role checked per action (`src/orchestrator/engine.py` `_principal`) |
| Orchestrator → agent subprocess | engine | none; agent receives a context file, writes a result file (`src/orchestrator/agents/runner.py`) |
| Agent → isolated workspace / staging | agent | filesystem only; workspace confined to `var/work/<run_id>/` (`src/orchestrator/workspace.py` `_inside`) |

**Authentication assumptions** (HD-003): static API keys `sk_<key_id>.<secret>`, stored only as
SHA-256 hashes and compared in constant time (`src/common/apikeys.py`). Keys are created by the
human owner in their own terminal and never stored in the repository. Key rotation, revocation
and expiry are not implemented (accepted limitation, HD-003). One person holds all human keys
(A-008), so separation of duties is between key identities, not people — and FR-GOV-017 is not
enforced yet (T262).

## 2. Threats recorded by scenario runs

These entries are copied from the `threat-review` artifacts in `evidence/`. TH-1 and TH-2 concern
interfaces added by scenario change sets; those exist only in the run workspaces and staging
releases, not in the main working tree (CST-007).

| ID | Category | Interface | Severity | Status | Recorded detail | Evidence |
|----|----------|-----------|----------|--------|-----------------|----------|
| TH-0 | Denial of service | all new operations | low | accepted | "abuse volume on new operations: creation is rate limited; reads are an accepted risk" | `run_1491b1c537664814`, `run_bc533834c7dc4e5e`, `run_fe1eef2844a541f2` |
| TH-1 | Information disclosure | `GET /api/v1/links/{code}` (SCN-A) | high | mitigated | "details limited to the creating key" | `run_1491b1c537664814` |
| TH-2 | Spoofing | `POST /api/v1/links` with `alias` (SCN-B) | medium | mitigated | "creator-chosen aliases could imitate service routes or other links; reserved words are blocked and conflicts never overwrite" | `run_bc533834c7dc4e5e` |

TH-1 control: the SCN-A change set returns 404 to keys other than the creator. TH-2 controls:
`RESERVED_ALIASES` (`api`, `health`, `docs`, `openapi`, `redoc`, `static`, `admin`), the code
pattern `^[A-Za-z0-9]{4,10}$`, and `409 alias_conflict` that never overwrites
(`scenarios/scn-b/changeset/impl.patch`).

## 3. Accepted risk: unauthenticated redirect volume

| ID | Threat | Status | Rationale |
|----|--------|--------|-----------|
| AR-1 | High-volume resolution of public short links (`GET /{code}`): load on the service and inflated click counts | **accepted** (NFR-SEC-003, CR-003) | Redirects are public by design (A-001) and are not rate limited in this prototype. Redirect rate limiting is backlog item BL-13. Click counts are therefore not abuse-resistant. Local, single-workstation deployment only (EXC-004). |

## 4. Baseline threat scenarios (Constitution V list)

| ID | Threat | Status | Control (location) |
|----|--------|--------|--------------------|
| TB-1 | Open-redirect misuse: shortener used to disguise malicious destinations | mitigated in part; residual **accepted** | Only key holders can create links; scheme allow-list `http`/`https`; credentials in URL rejected (`src/shortener/validation.py`). No reputation lookup of destinations (EXC-006, documented limitation). |
| TB-2 | Malicious or self-referential targets (redirect loops, internal hosts) | mitigated | Self domain, `localhost`, private, loopback, link-local, multicast, reserved and unspecified IP literals rejected (`validation.py` `_blocked_ip`, `self_referential_url`). The shortener never fetches destinations (no SSRF path). Host names that *resolve* to private addresses are not checked (DNS is not resolved). |
| TB-3 | Enumeration of short codes | mitigated in part | CSPRNG base62 codes of length 7 (~3.5 × 10¹² values, `src/shortener/codes.py`); unknown and malformed codes return the same 404. Redirects are not rate limited (AR-1), so enumeration volume is bounded only by that accepted risk. |
| TB-4 | Enumeration through the API | mitigated | Missing/invalid keys get 401 before any lookup, so existence is never revealed to unauthenticated callers (FR-SHR-019). |
| TB-5 | Stats read by a different key holder (`GET /api/v1/links/{code}/stats`) | **accepted risk (human owner, 2026-10-16)** | Any valid human key can read the click count and last-click time of any link; no destination is returned. Not owner-scoped in the baseline (unlike TH-1). Low severity. Accepted for this submission (G10): stats contain only aggregate counts and no personal data, and restricting reads to the creating key would change the baseline the locked change sets apply to. Owner-scoping is future work (T290). |
| TB-6 | Injection (SQL, header, log) | mitigated | Parameterized SQL only (`src/shortener/store.py`, `src/orchestrator/store.py`); request body `extra="forbid"`; `X-Request-ID` accepted only if it matches `^[A-Za-z0-9._-]{1,64}$`; JSON log formatter emits explicit fields only (`src/shortener/app.py`). |
| TB-7 | Abuse volume on creation | mitigated | 60 creations per minute per key, sliding window, 429 with `Retry-After` (`app.py` `RateLimiter`, PVT-011). In-memory and per process (see README "Horizontal scaling"). |
| TB-8 | Approval spoofing (an agent or wrong role records a decision) | mitigated | Every gate decision, resume, exception and replan request is checked for a human key with the required role; refusals are audited as `AUTH_REFUSED` (`engine.py` `_principal`; `tests/orchestrator/test_flow_and_gates.py`). Decisions record key ID and role (FR-GOV-013). |
| TB-9 | Approval of a stale artifact version | mitigated | Gate decisions are bound to artifact versions; a mismatch is refused and audited (`DECISION_REFUSED`, `engine.decide`). |
| TB-10 | Tampered change set or audit trail | mitigated | Change sets must match human-locked hashes (`integrity_mismatch`, `scenario.py` `_verify_lock`); audit is append-only (triggers) and hash-chained per run (`src/orchestrator/audit.py`, `orch audit verify`). Refused tamper attempts are not themselves audited yet (T277). The lock is not anchored to the git tag (T279). |
| TB-11 | Secrets or personal data in logs, audit or repository | mitigated | Keys stored hashed and never logged; logs carry no IP or user agent (`tests/shortener/test_logging.py`); regex secret scan in runs (SEC-004) and in `orch release check`; no visitor personal data stored (PRIV-001, FR-SHR-012). |
| TB-12 | Vulnerable dependencies | mitigated | SEC-003: hash-pinned pip-audit snapshot in runs; live pip-audit in `orch release check` and CI. Licence and approved-dependency checks are not implemented (T253). |
| TB-13 | Agent acting outside its role | mitigated in part | Undeclared artifact outputs refused (`PERMISSION_REFUSED`); agents cannot hold human roles. Agents run as unrestricted subprocesses on the local filesystem; no capability guard (FR-ORC-025, T275). |

## 5. Security trade-offs

- Static API keys instead of an identity provider (HD-003): simple and offline, no rotation or
  revocation.
- Public redirects without rate limiting (AR-1, BL-13).
- No DNS resolution during URL validation: avoids network calls and SSRF, but a public host name
  pointing to a private address is accepted.
- Single-person separation of duties (plan §16.4).
- Stats readable by any key holder (TB-5): accepted risk for this submission (human owner,
  2026-10-16); owner-scoping is T290.

## 6. Open items

| Item | Owner | Task |
|------|-------|------|
| TB-5 stats visible to any key holder: accepted risk (human owner, 2026-10-16); owner-scope the stats endpoint | Engineering | T290 |
| Separation of duties between key identities | Engineering | T262 |
| Audit of refused tamper attempts | Engineering | T277 |
| Agent capability guard | Engineering | T275 |
| Change-set lock anchored to the annotated tag | Engineering | T279 |
