# SCN-A: Link details endpoint
change_kind: new_capability

## Intent
Give API consumers a read-only view of the details of a short link they created (HD-SCN-001).

## Acceptance criteria
- AC1: GET /api/v1/links/{code} with the creating API key returns 200 with code, destination, created_at, expires_at and active.
- AC2: For an expired link the endpoint returns 200 with active false; the details stay readable after expiry.
- AC3: A request without a valid API key returns 401; an agent key returns 403.
- AC4: An unknown code, or a code created by a different API key, returns 404 without revealing whether the link exists.

## Constraints
- Existing endpoints and their responses are unchanged.
- No personal data is stored or returned.
