# SCN-B: Custom aliases
change_kind: modification

## Intent
Let link creators choose a custom alias as the short code in the existing POST /api/v1/links creation flow (HD-SCN-001).

## Acceptance criteria
- AC1: POST /api/v1/links with alias "promo2026" returns 201 and the alias as the code; resolving it redirects to the destination.
- AC2: An alias shorter than 4 or longer than 10 characters, or with characters other than letters and digits, returns 422 alias_invalid.
- AC3: A reserved alias (api, health, docs, openapi, redoc, static, admin; case-insensitive) returns 422 alias_reserved.
- AC4: An alias already in use returns 409 alias_conflict and the existing mapping is unchanged.
- AC5: A request without an alias is unchanged: it returns 201 with a random 7-character code.

## Constraints
- Requests without an alias behave exactly as before (regression suite passes unchanged).
- No personal data is stored or returned.
