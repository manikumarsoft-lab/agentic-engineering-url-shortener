import itertools
import sqlite3

import pytest

DEST = "https://example.com/landing"


def _no_internals(text: str) -> None:
    for leak in ("Traceback", "sqlite", "File \"", "secret-detail", "C:\\"):
        assert leak not in text


def test_create_and_redirect(svc):
    c = svc.client()
    r = svc.create(c, DEST)
    assert r.status_code == 201
    body = r.json()
    assert body["short_url"] == f"https://sho.rt/{body['code']}" and len(body["code"]) == 7
    assert body["destination"] == DEST and body["expires_at"] is None
    r = c.get(f"/{body['code']}")
    assert r.status_code == 302 and r.headers["location"] == DEST
    assert "no-store" in r.headers["cache-control"] and "no-cache" in r.headers["cache-control"]
    assert r.headers["referrer-policy"] == "no-referrer"


@pytest.mark.parametrize("headers, status", [({}, 401), ({"X-API-Key": "sk_bogus.key"}, 401)])
def test_create_requires_a_valid_key(svc, headers, status):
    c = svc.client()
    r = c.post("/api/v1/links", json={"url": DEST}, headers=headers)
    assert r.status_code == status and r.json()["code"] == "unauthorized"


def test_agent_key_cannot_create_links(svc):
    r = svc.create(svc.client(), DEST, key="agent")
    assert r.status_code == 403 and r.json()["code"] == "forbidden"


def test_invalid_url_is_rejected_without_storing(svc):
    c = svc.client()
    r = svc.create(c, "javascript:alert(document.cookie)")
    assert r.status_code == 422 and r.json()["code"] == "scheme_not_allowed"
    assert r.headers["content-type"].startswith("application/problem+json")
    assert sqlite3.connect(svc.settings.db_path).execute("SELECT COUNT(*) FROM links").fetchone()[0] == 0


def test_malformed_body_does_not_echo_input(svc):
    r = svc.client().post("/api/v1/links", json={"url": DEST, "evil": "secret-detail"},
                          headers={"X-API-Key": svc.keys["consumer"]})
    assert r.status_code == 422 and r.json()["code"] == "invalid_request"
    _no_internals(r.text)


@pytest.mark.parametrize("path", ["/zzzzzzz", "/abc", "/has-dash", "/" + "a" * 11])
def test_unknown_or_malformed_codes_are_404(svc, path):
    r = svc.client().get(path)
    assert r.status_code == 404 and r.json()["code"] == "not_found"


def test_expired_link_returns_410_not_404(svc):
    c = svc.client()
    code = svc.create(c, DEST, expires_at="2026-10-16T13:00:00Z").json()["code"]
    assert c.get(f"/{code}").status_code == 302
    svc.clock.advance(hours=1)  # resolution time == expiry -> expired
    r = c.get(f"/{code}")
    assert r.status_code == 410 and r.json()["code"] == "link_expired"


@pytest.mark.parametrize("expires_at", ["2026-10-16T11:59:59Z", "2026-10-16T13:00:00", "not-a-date"])
def test_past_naive_or_malformed_expiry_is_rejected(svc, expires_at):
    r = svc.create(svc.client(), DEST, expires_at=expires_at)
    assert r.status_code == 422 and r.json()["code"] in {"invalid_expiration", "invalid_request"}


def test_stats_count_clicks_without_personal_data(svc):
    c = svc.client()
    code = svc.create(c, DEST).json()["code"]
    headers = {"X-API-Key": svc.keys["consumer"]}
    assert c.get(f"/api/v1/links/{code}/stats", headers=headers).json() == {
        "code": code, "clicks": 0, "last_click_at": None}
    for _ in range(3):
        c.get(f"/{code}", headers={"User-Agent": "tracker", "X-Forwarded-For": "203.0.113.9"})
    stats = c.get(f"/api/v1/links/{code}/stats", headers=headers).json()
    assert stats == {"code": code, "clicks": 3, "last_click_at": "2026-10-16T12:00:00Z"}
    stored = sqlite3.connect(svc.settings.db_path).execute("SELECT * FROM link_stats").fetchall()
    assert "203.0.113.9" not in str(stored) and "tracker" not in str(stored)
    assert c.get(f"/api/v1/links/{code}/stats").status_code == 401
    assert c.get("/api/v1/links/zzzzzzz/stats", headers=headers).status_code == 404


def test_health_live_and_ready(svc):
    c = svc.client()
    assert c.get("/health/live").json() == {"status": "ok"}
    assert c.get("/health/ready").json() == {"status": "ready", "database": "ok",
                                             "analytics_write_failures": 0}


def test_analytics_failure_never_blocks_redirect(svc, monkeypatch):
    c = svc.client()
    code = svc.create(c, DEST).json()["code"]

    def broken(*_):
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(svc.app.state.store, "record_click", broken)
    r = c.get(f"/{code}")
    assert r.status_code == 302 and r.headers["location"] == DEST
    assert c.get("/health/ready").json()["analytics_write_failures"] == 1


def test_storage_outage_never_redirects_and_ready_reports_it(svc, monkeypatch):
    c = svc.client()
    code = svc.create(c, DEST).json()["code"]

    def down(*_):
        raise sqlite3.OperationalError("unable to open database file")

    monkeypatch.setattr(svc.app.state.store, "get", down)
    monkeypatch.setattr(svc.app.state.store, "ping", down)
    r = c.get(f"/{code}")
    assert r.status_code == 503 and "location" not in r.headers
    _no_internals(r.text)
    assert c.get("/health/ready").status_code == 503


def test_unexpected_errors_do_not_leak_internals(svc, monkeypatch):
    c = svc.client()

    def boom(*_):
        raise RuntimeError(r"secret-detail at C:\internal\path")

    monkeypatch.setattr(svc.app.state.store, "get", boom)
    r = c.get("/abcdefg")
    assert r.status_code == 500 and r.json()["code"] == "internal_error"
    _no_internals(r.text)


def test_rate_limit_is_60_creates_per_minute_per_key(svc):
    c = svc.client()
    for _ in range(60):
        assert svc.create(c, DEST).status_code == 201
    r = svc.create(c, DEST)
    assert r.status_code == 429 and r.json()["code"] == "rate_limited"
    assert int(r.headers["retry-after"]) >= 1
    assert svc.create(c, DEST, key="consumer#2").status_code == 201  # other keys unaffected
    svc.clock.advance(seconds=60)
    assert svc.create(c, DEST).status_code == 201


def test_idempotency_key_replays_or_conflicts(svc):
    c = svc.client()
    headers = {"X-API-Key": svc.keys["consumer"], "Idempotency-Key": "order-42"}
    first = c.post("/api/v1/links", json={"url": DEST}, headers=headers)
    again = c.post("/api/v1/links", json={"url": DEST}, headers=headers)
    assert first.status_code == 201 and again.status_code == 200
    assert again.json() == first.json() and again.headers["idempotent-replayed"] == "true"
    other = c.post("/api/v1/links", json={"url": "https://example.org/"}, headers=headers)
    assert other.status_code == 409 and other.json()["code"] == "idempotency_conflict"
    assert sqlite3.connect(svc.settings.db_path).execute("SELECT COUNT(*) FROM links").fetchone()[0] == 1


def test_same_url_without_key_creates_distinct_links(svc):
    c = svc.client()
    assert svc.create(c, DEST).json()["code"] != svc.create(c, DEST).json()["code"]


def test_code_collisions_retry_then_give_up_after_five(svc):
    seq = itertools.chain(["AAAAAAA", "AAAAAAA", "BBBBBBB"], itertools.repeat("BBBBBBB"))
    c = svc.client(new_code=lambda: next(seq))
    assert svc.create(c, DEST).json()["code"] == "AAAAAAA"
    assert svc.create(c, DEST).json()["code"] == "BBBBBBB"  # one collision, then a fresh code
    r = svc.create(c, DEST)  # BBBBBBB five times in a row
    assert r.status_code == 503 and r.json()["code"] == "code_generation_exhausted"
    assert sqlite3.connect(svc.settings.db_path).execute("SELECT COUNT(*) FROM links").fetchone()[0] == 2
