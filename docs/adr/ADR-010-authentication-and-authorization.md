# ADR-010: Authentication and Authorization (Role-Mapped API Keys; Capability-Based Agent Permissions)

## Status

**Accepted (Mani Kumar Vadugu, human owner, 2026-10-15)**

History: Proposed 2026-10-15. Access-control model fixed by HD-003 (human decision, 2026-10-15);
key scheme (research R-09) pending this ADR.

## Context

HD-003 requires static API keys mapped to roles `consumer`, `engineer`, `approver`,
`release-owner` (human) and `agent`; redirect is public; human-reserved decisions require a
human-role key with the right role; agent credentials are refused and audited (FR-GOV-003,
FR-SHR-019, NFR-AUT-001, SC-011). Audit must record role and key identity but never the secret
(FR-GOV-013, NFR-SEC-004). In-process agents must be limited to declared permissions
(FR-ORC-025).

## Decision Drivers

- Non-waivable human governance (CON III).
- No secrets in logs, audit or repository (CON V).
- Simple local issuance; no external identity provider (HD-003 rejected option C).
- Enforcement at both API and engine layers.

## Options Considered

### Option A — `sk_<key_id>.<secret>` keys, SHA-256 at rest, role map file; capability objects for agents
- **Approach**: `orch keys init` generates 256-bit secrets, stores `{key_id, sha256(secret), role, actor_type}` in `var/secrets/api-keys.json` (gitignored), prints secrets once; constant-time compare; `key_id` is the audit identity. Agents receive only the capability objects declared for their role in the graph contract; human-reserved capabilities are never grantable.
- **Advantages**: simple; non-secret audit identity; defense in depth (HTTP role check + engine actor-type check + capability absence).
- **Disadvantages**: manual rotation/revocation.
- **Risks**: key file exposure on the workstation.
- **Implementation impact**: auth dependency, role matrix from OpenAPI `x-required-roles`, permission guard, refusal audit.
- **Assessment implications**: concrete evidence for SC-004/SC-011.

### Option B — Slow-KDF hashed keys (bcrypt/argon2)
- **Approach**: Slow-KDF hashed keys (bcrypt/argon2).
- **Advantages**: resists offline guessing of low-entropy secrets. **Disadvantages**: per-request CPU cost; secrets are already 256-bit random, so no practical benefit. **Risks**: latency. **Implementation impact**: extra dependency. **Assessment implications**: none gained.

### Option C — Signed JWTs
- **Approach**: Signed JWTs.
- **Advantages**: expiry claims. **Disadvantages**: key management, clock skew, more surface. **Risks**: misconfiguration. **Implementation impact**: signing keys. **Assessment implications**: exceeds HD-003 scope.

## Decision

Option A. Authorization matrix: shortener create/analytics → `consumer` or higher human role;
redirect → public; orchestrator operations per `x-required-roles` / `x-required-roles-by-gate-type`.
Engine re-checks `actor.type == human` for every decision/resume/abort/exception approval even if
the HTTP layer passed. A single human may hold several roles but each decision records the role
used (A-008). Unauthenticated reads never reveal link existence.

## Rationale

Meets HD-003 exactly with minimal machinery and layered enforcement.

## Consequences

- **Positive**: verifiable refusal of agent approvals; secrets never persisted in plaintext.
- **Negative**: no rotation tooling (BL-10, documented limitation).
- **Operational**: keys printed once; reviewers copy them into the shell (quickstart §2).
- **Testing**: role matrix tests per endpoint; agent-key refusal + audit; log/audit secret-pattern scan.
- **Governance**: approvals carry `key_id` and role (FR-GOV-013).

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Key file read by other local users | File permissions restricted where supported; documented local-trust assumption |
| Secret echoed in errors/logs | Redaction filter; problem+json never echoes headers; tests |
| Agent obtains human key via environment | Agents get capability objects only — no access to environment or key store |

## Reversibility

High. Auth is a dependency layer; can be replaced by an IdP later.

## Traceability

- Requirements: FR-SHR-019, FR-GOV-003, FR-GOV-013, FR-ORC-025, NFR-SEC-004, NFR-AUT-001, SC-004, SC-011, A-001, A-008
- Spec: HD-003; US-3 AC4
- Plan: §1.1, §1.2 (TB-2, TB-3), §3.7, §8 (Authentication, Authorization, Least privilege), §12 R-09
- Decisions: HD-003

## Validation

Security suites: auth matrix, agent refusal audited, no-secret scans; e2e negative checks
(quickstart §7).
