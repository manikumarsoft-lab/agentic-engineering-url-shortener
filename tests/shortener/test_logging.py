"""Structured JSON request logs with a per-request correlation ID and no secrets or personal data."""
import json
import logging

from shortener.app import JsonFormatter

SENSITIVE = ("203.0.113.9", "secret-agent-ua", "testclient")


def _lines(caplog) -> list[dict]:
    fmt = JsonFormatter()
    return [json.loads(fmt.format(r)) for r in caplog.records if r.name == "shortener.access"]


def test_each_request_logs_one_json_line_with_its_request_id(svc, caplog):
    caplog.set_level(logging.INFO, logger="shortener")
    c = svc.client()
    key = svc.keys["consumer"]
    r = c.post("/api/v1/links", json={"url": "https://example.com/"},
               headers={"X-API-Key": key, "X-Request-ID": "req-123",
                        "User-Agent": "secret-agent-ua", "X-Forwarded-For": "203.0.113.9"})
    assert r.headers["x-request-id"] == "req-123"
    code = r.json()["code"]
    c.get(f"/{code}?utm=private", headers={"User-Agent": "secret-agent-ua"})
    lines = _lines(caplog)
    assert [(entry["method"], entry["route"], entry["status"]) for entry in lines] == [
        ("POST", "/api/v1/links", 201), ("GET", "/{code}", 302)]
    assert lines[0]["request_id"] == "req-123"
    assert lines[1]["request_id"] != "req-123" and len(lines[1]["request_id"]) == 32
    assert set(lines[0]) == {"ts", "level", "logger", "msg", "request_id", "method", "route",
                             "status", "duration_ms"}
    raw = "\n".join(JsonFormatter().format(rec) for rec in caplog.records)
    for value in (*SENSITIVE, key, key.split(".", 1)[1], "utm=private", code):
        assert value not in raw


def test_invalid_request_id_is_replaced(svc):
    r = svc.client().get("/health/live", headers={"X-Request-ID": "bad id with spaces\n"})
    assert r.headers["x-request-id"] != "bad id with spaces\n" and len(r.headers["x-request-id"]) == 32


def test_errors_also_carry_a_request_id(svc, monkeypatch):
    c = svc.client()
    monkeypatch.setattr(svc.app.state.store, "get", lambda *_: (_ for _ in ()).throw(RuntimeError("x")))
    r = c.get("/abcdefg", headers={"X-Request-ID": "err-1"})
    assert r.status_code == 500 and r.headers["x-request-id"] == "err-1"
