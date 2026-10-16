# SCN-C option A: Daily aggregate click counts
change_kind: new_capability

## Intent
Show link creators how many redirects each of their links received per UTC day, without storing any data about the people following the links.

## Acceptance criteria
- AC1: GET /api/v1/links/{code}/stats/daily with a valid API key returns 200 with the redirect count per UTC day.
- AC2: Each successful redirect increments exactly one daily bucket, so the endpoint returns exact counts.
- AC3: A request without a valid API key returns 401; an unknown code returns 404.
- AC4: The daily table stores only the code, the UTC day and the count; existing stats responses are unchanged.

## Constraints
- No personal data is stored or returned (FR-SHR-012).
