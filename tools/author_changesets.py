"""Author the scenario change sets as test-first patch pairs: `python tools/author_changesets.py`.

Provenance: authored with AI assistance (Claude Code) during development. The human owner reviews
each change set and locks it with `orch changeset lock <dir> --key <approver key>`; runs refuse
change sets that are not locked or differ from the locked version.

For each change set the tool copies the baseline (working tree: src, tests/shortener, the
generated contract, pyproject.toml) to a temp directory, writes the new tests (-> tests.patch),
applies exact-match edits and regenerates the OpenAPI contract inside the copy (-> impl.patch).
"""
from __future__ import annotations

import difflib
import hashlib
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orchestrator import workspace  # noqa: E402
from orchestrator.agents.scenario import CONTRACT_REL, PROVENANCE  # noqa: E402

BASELINE = ("src", "tests/shortener", CONTRACT_REL, "pyproject.toml")


@dataclass
class ChangeSet:
    path: str
    scenario: str
    variant: str
    summary: str
    tests: dict[str, str]
    edits: list[tuple[str, str, str]] = field(default_factory=list)
    contract_version_after: str = "2.1.0"


# ---- SCN-A: link details endpoint (HD-SCN-001), owner-scoped (human decision) ------------------
SCN_A_TESTS = {"tests/shortener/test_link_details.py": '''"""SCN-A (HD-SCN-001): link details endpoint GET /api/v1/links/{code}."""
DEST = "https://example.com/details"


def _details(svc, c, code, key="consumer"):
    return c.get(f"/api/v1/links/{code}", headers={"X-API-Key": svc.keys[key]} if key else {})


def test_details_of_an_active_link(svc):
    c = svc.client()
    created = svc.create(c, DEST, expires_at="2026-10-17T12:00:00Z").json()
    r = _details(svc, c, created["code"])
    assert r.status_code == 200
    assert r.json() == {"code": created["code"], "destination": DEST, "created_at": created["created_at"],
                        "expires_at": "2026-10-17T12:00:00Z", "active": True}


def test_expired_link_details_stay_readable_and_inactive(svc):
    c = svc.client()
    code = svc.create(c, DEST, expires_at="2026-10-16T13:00:00Z").json()["code"]
    svc.clock.advance(hours=2)
    r = _details(svc, c, code)
    assert r.status_code == 200 and r.json()["active"] is False


def test_details_require_a_human_api_key(svc):
    c = svc.client()
    code = svc.create(c, DEST).json()["code"]
    assert _details(svc, c, code, key=None).status_code == 401
    assert _details(svc, c, code, key="agent").status_code == 403


def test_other_keys_and_unknown_codes_get_404(svc):
    c = svc.client()
    code = svc.create(c, DEST).json()["code"]
    other = _details(svc, c, code, key="consumer#2")
    assert other.status_code == 404 and other.json()["code"] == "not_found"
    assert _details(svc, c, "zzzzzzz").status_code == 404
'''}

SCN_A_EDITS = [
    ("src/shortener/app.py", 'API_VERSION = "2.0.0"', 'API_VERSION = "2.1.0"'),
    ("src/shortener/app.py", "class Problem(BaseModel):", '''class LinkDetailsOut(BaseModel):
    code: str
    destination: str
    created_at: str
    expires_at: str | None
    active: bool


class Problem(BaseModel):'''),
    ("src/shortener/app.py", '    @app.get("/health/live", response_model=LiveOut)', '''    @app.get("/api/v1/links/{code}", response_model=LinkDetailsOut,
             responses=_responses(401, 403, 404, 503))
    def link_details(code: str, key_id: Annotated[str, Depends(require_key)]) -> LinkDetailsOut:
        """Details of a link created by the calling key; other keys get 404 (no existence hint)."""
        try:
            link = store.get(code) if codes.CODE_PATTERN.match(code) else None
        except sqlite3.Error:
            raise unavailable() from None
        if link is None or link["creator_key_id"] != key_id:
            raise ProblemError(404, "not_found", "Not found")
        expires = link["expires_at"]
        active = expires is None or clock() < datetime.fromisoformat(expires.replace("Z", "+00:00"))
        return LinkDetailsOut(code=code, destination=link["destination"], created_at=link["created_at"],
                              expires_at=expires, active=active)

    @app.get("/health/live", response_model=LiveOut)'''),
]

# ---- SCN-B: custom aliases ----------------------------------------------------------------------
SCN_B_TESTS = {"tests/shortener/test_aliases.py": '''"""SCN-B (HD-SCN-001): custom aliases in the existing creation flow."""
import pytest

DEST = "https://example.com/alias"


def test_alias_becomes_the_short_code(svc):
    c = svc.client()
    r = svc.create(c, DEST, alias="promo2026")
    assert r.status_code == 201 and r.json()["code"] == "promo2026"
    assert r.json()["short_url"].endswith("/promo2026")
    assert c.get("/promo2026").headers["location"] == DEST


@pytest.mark.parametrize("alias, status", [
    ("abc", 422), ("abcd", 201), ("abcdefg", 201), ("abcdefghij", 201), ("abcdefghijk", 422),
    ("has-dash", 422), ("spa ce1", 422)])
def test_alias_length_and_characters(svc, alias, status):
    r = svc.create(svc.client(), DEST, alias=alias)
    assert r.status_code == status
    if status == 422:
        assert r.json()["code"] == "alias_invalid"


@pytest.mark.parametrize("alias", ["admin", "Health", "OPENAPI", "static"])
def test_reserved_aliases_are_rejected(svc, alias):
    r = svc.create(svc.client(), DEST, alias=alias)
    assert r.status_code == 422 and r.json()["code"] == "alias_reserved"


def test_alias_conflict_is_409_and_keeps_the_existing_mapping(svc):
    c = svc.client()
    assert svc.create(c, DEST, alias="taken01").status_code == 201
    r = svc.create(c, "https://example.org/other", alias="taken01", key="consumer#2")
    assert r.status_code == 409 and r.json()["code"] == "alias_conflict"
    assert c.get("/taken01").headers["location"] == DEST


def test_requests_without_alias_are_unchanged(svc):
    body = svc.create(svc.client(), DEST).json()
    assert len(body["code"]) == 7 and set(body) == {"code", "short_url", "destination", "created_at",
                                                    "expires_at"}
'''}

SCN_B_EDITS = [
    ("src/shortener/app.py", 'API_VERSION = "2.0.0"', 'API_VERSION = "2.1.0"\n'
     'RESERVED_ALIASES = frozenset({"api", "health", "docs", "openapi", "redoc", "static", "admin"})'),
    ("src/shortener/app.py", "    url: str\n    expires_at: datetime | None = None\n",
     "    url: str\n    expires_at: datetime | None = None\n    alias: str | None = None\n"),
    ("src/shortener/app.py", '            raise ProblemError(422, err.code, "Invalid URL", err.detail) from None\n',
     '''            raise ProblemError(422, err.code, "Invalid URL", err.detail) from None
        if body.alias is not None:
            if not codes.CODE_PATTERN.match(body.alias):
                raise ProblemError(422, "alias_invalid", "Invalid alias",
                                   "an alias is 4 to 10 letters or digits")
            if body.alias.lower() in RESERVED_ALIASES:
                raise ProblemError(422, "alias_reserved", "Reserved alias", "this alias is reserved")
'''),
    ("src/shortener/app.py",
     "        fingerprint = hashlib.sha256(json.dumps([body.url, expires_at]).encode()).hexdigest()",
     "        request_parts = [body.url, expires_at] + ([body.alias] if body.alias else [])\n"
     "        fingerprint = hashlib.sha256(json.dumps(request_parts).encode()).hexdigest()"),
    ("src/shortener/app.py",
     "                idem_key=idempotency_key, fingerprint=fingerprint, new_code=make_code,\n"
     "                attempts=settings.max_code_attempts, render=render)",
     "                idem_key=idempotency_key, fingerprint=fingerprint,\n"
     "                new_code=(lambda: body.alias) if body.alias else make_code,\n"
     "                attempts=1 if body.alias else settings.max_code_attempts, render=render)"),
    ("src/shortener/app.py", '        if status == "exhausted":\n',
     '''        if status == "exhausted" and body.alias:
            raise ProblemError(409, "alias_conflict", "Alias already in use",
                               "the alias is taken; the existing link is unchanged")
        if status == "exhausted":
'''),
]

# Defective variant (fault-injection, FR-ORC-036): a "simplification" drops collision retry for
# generated codes, breaking the existing regression test for code collisions.
SCN_B_DEFECTIVE_EDITS = [*SCN_B_EDITS[:4], (
    "src/shortener/app.py",
    "                idem_key=idempotency_key, fingerprint=fingerprint, new_code=make_code,\n"
    "                attempts=settings.max_code_attempts, render=render)",
    "                idem_key=idempotency_key, fingerprint=fingerprint,\n"
    "                new_code=(lambda: body.alias) if body.alias else make_code,\n"
    "                attempts=1, render=render)"), SCN_B_EDITS[5]]

# ---- SCN-C option A: daily aggregate counts, no personal data -----------------------------------
SCN_C_TESTS = {"tests/shortener/test_daily_stats.py": '''"""SCN-C option A: daily aggregate click counts per link (UTC), no personal data."""
import sqlite3

DEST = "https://example.com/daily"


def _daily(svc, c, code, key="consumer"):
    return c.get(f"/api/v1/links/{code}/stats/daily", headers={"X-API-Key": svc.keys[key]} if key else {})


def test_clicks_are_counted_per_utc_day(svc):
    c = svc.client()
    code = svc.create(c, DEST).json()["code"]
    c.get(f"/{code}")
    c.get(f"/{code}")
    svc.clock.advance(days=1)
    c.get(f"/{code}")
    r = _daily(svc, c, code)
    assert r.status_code == 200
    assert r.json() == {"code": code, "days": {"2026-10-16": 2, "2026-10-17": 1}}


def test_daily_counts_store_no_personal_data(svc):
    c = svc.client()
    code = svc.create(c, DEST).json()["code"]
    c.get(f"/{code}", headers={"User-Agent": "ua-marker", "X-Forwarded-For": "198.51.100.7"})
    db = sqlite3.connect(svc.settings.db_path)
    columns = [row[1] for row in db.execute("PRAGMA table_info(link_daily_stats)")]
    assert columns == ["code", "day", "clicks"]
    assert "ua-marker" not in str(db.execute("SELECT * FROM link_daily_stats").fetchall())


def test_daily_stats_need_a_key_and_a_known_code(svc):
    c = svc.client()
    code = svc.create(c, DEST).json()["code"]
    assert _daily(svc, c, code, key=None).status_code == 401
    assert _daily(svc, c, "zzzzzzz").status_code == 404
'''}

SCN_C_EDITS = [
    ("src/shortener/app.py", 'API_VERSION = "2.0.0"', 'API_VERSION = "2.1.0"'),
    ("src/shortener/app.py", "class Problem(BaseModel):", '''class DailyStatsOut(BaseModel):
    code: str
    days: dict[str, int]


class Problem(BaseModel):'''),
    ("src/shortener/app.py", '    @app.get("/health/live", response_model=LiveOut)', '''    @app.get("/api/v1/links/{code}/stats/daily", response_model=DailyStatsOut,
             responses=_responses(401, 403, 404, 503))
    def link_daily_stats(code: str, _: Annotated[str, Depends(require_key)]) -> DailyStatsOut:
        try:
            link = store.get(code) if codes.CODE_PATTERN.match(code) else None
            rows = store.daily(code) if link else []
        except sqlite3.Error:
            raise unavailable() from None
        if link is None:
            raise ProblemError(404, "not_found", "Not found")
        return DailyStatsOut(code=code, days={row["day"]: row["clicks"] for row in rows})

    @app.get("/health/live", response_model=LiveOut)'''),
    ("src/shortener/store.py", "    PRIMARY KEY (key_id, idem_key));\n", '''    PRIMARY KEY (key_id, idem_key));
CREATE TABLE IF NOT EXISTS link_daily_stats (
    code TEXT, day TEXT, clicks INTEGER NOT NULL, PRIMARY KEY (code, day));
'''),
    ("src/shortener/store.py", '"clicks = clicks + 1, last_click_at = excluded.last_click_at", (code, at))\n',
     '''"clicks = clicks + 1, last_click_at = excluded.last_click_at", (code, at))
            conn.execute(
                "INSERT INTO link_daily_stats VALUES (?, ?, 1) ON CONFLICT(code, day) DO UPDATE SET "
                "clicks = clicks + 1", (code, at[:10]))
'''),
    ("src/shortener/store.py", "    def ping(self) -> None:", '''    def daily(self, code: str) -> list[sqlite3.Row]:
        with closing(self._connect()) as conn:
            return conn.execute("SELECT day, clicks FROM link_daily_stats WHERE code = ? ORDER BY day",
                                (code,)).fetchall()

    def ping(self) -> None:'''),
]

CHANGE_SETS = [
    ChangeSet("scenarios/scn-a/changeset", "scn-a", "normal",
              "Add GET /api/v1/links/{code}: link details (destination, created_at, expires_at, active) "
              "for the creating API key; other keys get 404.", SCN_A_TESTS, SCN_A_EDITS),
    ChangeSet("scenarios/scn-b/changeset", "scn-b", "normal",
              "Add an optional custom alias to POST /api/v1/links (4-10 letters/digits, reserved words "
              "blocked, conflicts return 409 and never overwrite).", SCN_B_TESTS, SCN_B_EDITS),
    ChangeSet("scenarios/scn-b/changeset-defective", "scn-b", "defective",
              "FAULT-INJECTION DEMONSTRATION (FR-ORC-036): aliases as in the normal change set, plus a "
              "defect that removes collision retry for generated codes.", SCN_B_TESTS, SCN_B_DEFECTIVE_EDITS),
    ChangeSet("scenarios/scn-c/changeset", "scn-c", "option-A",
              "Add daily aggregate click counts per link (UTC day) at GET /api/v1/links/{code}/stats/daily; "
              "no visitor personal data.", SCN_C_TESTS, SCN_C_EDITS),
]


def _lf(path: Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def file_diff(rel: str, before: str | None, after: str) -> str:
    lines = difflib.unified_diff((before or "").splitlines(keepends=True), after.splitlines(keepends=True),
                                 "/dev/null" if before is None else f"a/{rel}", f"b/{rel}")
    header = f"diff --git a/{rel} b/{rel}\n" + ("new file mode 100644\n" if before is None else "")
    return header + "".join(lines)


def build(cs: ChangeSet) -> None:
    out = ROOT / cs.path
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        work = workspace.create_from(Path(tmp), "after", ROOT, BASELINE)
        tests_patch = "".join(file_diff(rel, None, text) for rel, text in sorted(cs.tests.items()))
        edited: set[str] = set()
        for rel, old, new in cs.edits:
            target = work / rel
            text = _lf(target)
            if text.count(old) != 1:
                raise SystemExit(f"{cs.path}: edit anchor not found exactly once in {rel}: {old[:60]!r}")
            target.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
            edited.add(rel)
        env = {**os.environ, "PYTHONPATH": str(work / "src")}
        subprocess.run([sys.executable, "-m", "shortener.openapi", str(work / CONTRACT_REL)],
                       cwd=work, env=env, check=True, capture_output=True)
        impl_patch = "".join(file_diff(rel, _lf(ROOT / rel), _lf(work / rel))
                             for rel in sorted(edited | {CONTRACT_REL}))
    (out / "tests.patch").write_text(tests_patch, encoding="utf-8", newline="\n")
    (out / "impl.patch").write_text(impl_patch, encoding="utf-8", newline="\n")
    digest = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()  # noqa: E731
    manifest = {
        "scenario": cs.scenario, "variant": cs.variant, "summary": cs.summary, "provenance": PROVENANCE,
        "base": {"description": "the baseline commit's src, tests/shortener, contract and pyproject; each "
                                "change set applies to that baseline independently (no release chain)",
                 "files_sha256": {rel: digest(_lf(ROOT / rel)) for rel in sorted(edited | {CONTRACT_REL})}},
        "tests_patch": "tests.patch", "impl_patch": "impl.patch", "new_tests": sorted(cs.tests),
        "touched_files": sorted(set(cs.tests) | edited | {CONTRACT_REL}),
        "contract_version_after": cs.contract_version_after,
        "sha256": {"tests_patch": digest(tests_patch), "impl_patch": digest(impl_patch)},
        "review": "Not applied by any run until the human owner locks it: "
                  f"orch changeset lock {cs.path} --key <approver key>",
    }
    (out / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False, width=100),
                                       encoding="utf-8", newline="\n")
    print(f"{cs.path}: tests.patch {manifest['sha256']['tests_patch'][:12]} "
          f"impl.patch {manifest['sha256']['impl_patch'][:12]}")


if __name__ == "__main__":
    for change_set in CHANGE_SETS:
        build(change_set)
