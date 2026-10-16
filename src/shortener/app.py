"""Shortener HTTP API (FastAPI).

Satisfies: FR-SHR-001..019 (baseline incl. expiry and stats per HD-CUT-002), FR-OBS-009, NFR-SEC-001,
NFR-SEC-004.
No `from __future__ import annotations`: FastAPI must resolve the local dependency annotations.
"""
import hashlib
import json
import logging
import math
import re
import sqlite3
import threading
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import closing
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict
from starlette.exceptions import HTTPException as StarletteHTTPException

from common import apikeys
from shortener import codes
from shortener.config import Settings
from shortener.store import LinkStore
from shortener.validation import InvalidURL, validate_url

log = logging.getLogger("shortener")
access_log = logging.getLogger("shortener.access")
Clock = Callable[[], datetime]
PROBLEM = "application/problem+json"
REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
API_VERSION = "2.0.0"


class JsonFormatter(logging.Formatter):
    """One JSON object per line. Only fields passed explicitly in `fields` are emitted, so
    headers, keys, client addresses and user agents can never leak into the log (FR-OBS-009)."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {"ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
                   "level": record.levelname, "logger": record.name, "msg": record.getMessage(),
                   **getattr(record, "fields", {})}
        return json.dumps(payload, sort_keys=True)


def configure_logging() -> None:
    logger = logging.getLogger("shortener")
    if not any(isinstance(h.formatter, JsonFormatter) for h in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


# ---- models -------------------------------------------------------------------------------------
class CreateLink(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str
    expires_at: datetime | None = None


class LinkOut(BaseModel):
    code: str
    short_url: str
    destination: str
    created_at: str
    expires_at: str | None


class StatsOut(BaseModel):
    code: str
    clicks: int
    last_click_at: str | None


class Problem(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    code: str
    detail: str | None = None


class LiveOut(BaseModel):
    status: str


class ReadyOut(BaseModel):
    status: str
    database: str
    analytics_write_failures: int


class ProblemError(Exception):
    def __init__(self, status: int, code: str, title: str, detail: str | None = None,
                 headers: dict[str, str] | None = None) -> None:
        super().__init__(code)
        self.status, self.code, self.title, self.detail = status, code, title, detail
        self.headers = headers or {}


def _problem(status: int, code: str, title: str, detail: str | None = None,
             headers: dict[str, str] | None = None) -> JSONResponse:
    body = Problem(title=title, status=status, code=code, detail=detail).model_dump()
    return JSONResponse(body, status_code=status, media_type=PROBLEM, headers=headers)


def _responses(*statuses: int) -> dict[int | str, dict[str, Any]]:
    return {s: {"model": Problem, "content": {PROBLEM: {}}} for s in statuses}


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# ---- rate limiting ------------------------------------------------------------------------------
class RateLimiter:
    """Sliding one-minute window per API key (FR-SHR-017, PVT-011, A-015)."""

    def __init__(self, limit: int, clock: Clock) -> None:
        self.limit, self.clock = limit, clock
        self.hits: dict[str, deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()

    def check(self, key_id: str) -> None:
        now = self.clock().timestamp()
        with self.lock:
            window = self.hits[key_id]
            while window and window[0] <= now - 60:
                window.popleft()
            if len(window) >= self.limit:
                retry = max(1, math.ceil(window[0] + 60 - now))
                raise ProblemError(429, "rate_limited", "Too many requests",
                                   "creation rate limit exceeded", {"Retry-After": str(retry)})
            window.append(now)


# ---- application --------------------------------------------------------------------------------
def create_app(settings: Settings | None = None, *, clock: Clock | None = None,
               new_code: Callable[[], str] | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    clock = clock or (lambda: datetime.now(timezone.utc))
    store = LinkStore(settings.db_path)
    limiter = RateLimiter(settings.rate_limit_per_minute, clock)
    make_code = new_code or (lambda: codes.generate(settings.code_length))
    counters = {"analytics_write_failures": 0}
    counter_lock = threading.Lock()

    configure_logging()
    app = FastAPI(title="URL Shortener", version=API_VERSION, docs_url=None, redoc_url=None)
    app.state.store, app.state.counters = store, counters

    @app.middleware("http")
    async def request_log(request: Request, call_next: Callable) -> Any:
        """Correlation ID per request (X-Request-ID) and one structured access-log line."""
        presented = request.headers.get("x-request-id", "")
        request_id = presented if REQUEST_ID.match(presented) else uuid.uuid4().hex
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log.exception("unhandled error", extra={"fields": {"request_id": request_id}})
            response = _problem(500, "internal_error", "Internal error")
        response.headers["X-Request-ID"] = request_id
        route = request.scope.get("route")
        access_log.info("request", extra={"fields": {
            "request_id": request_id, "method": request.method,
            "route": getattr(route, "path", "unmatched"), "status": response.status_code,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2)}})
        return response

    @app.exception_handler(ProblemError)
    async def _on_problem(_: Request, exc: ProblemError) -> JSONResponse:
        return _problem(exc.status, exc.code, exc.title, exc.detail, exc.headers)

    @app.exception_handler(RequestValidationError)
    async def _on_invalid(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields = sorted({".".join(str(p) for p in e["loc"][1:]) for e in exc.errors()})
        return _problem(422, "invalid_request", "Invalid request", f"invalid fields: {', '.join(fields)}")

    @app.exception_handler(StarletteHTTPException)
    async def _on_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _problem(exc.status_code, "not_found" if exc.status_code == 404 else "http_error",
                        "Not found" if exc.status_code == 404 else "Request failed")

    @app.exception_handler(Exception)
    async def _on_error(_: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error")  # details go to the server log only
        return _problem(500, "internal_error", "Internal error")

    def require_key(x_api_key: Annotated[str | None, Header()] = None) -> str:
        found = None
        if settings.keys_db_path.exists():
            uri = f"file:{settings.keys_db_path.as_posix()}?mode=ro"
            with closing(sqlite3.connect(uri, uri=True)) as conn:
                found = apikeys.resolve(conn, x_api_key)
        if found is None:
            raise ProblemError(401, "unauthorized", "Missing or invalid API key")
        key_id, role = found
        if role not in apikeys.HUMAN_ROLES:
            raise ProblemError(403, "forbidden", "This key may not perform this operation")
        return key_id

    def unavailable() -> ProblemError:
        return ProblemError(503, "persistence_unavailable", "Service unavailable",
                            "storage is unavailable; retry later", {"Retry-After": "5"})

    @app.post("/api/v1/links", status_code=201, response_model=LinkOut,
              responses={200: {"model": LinkOut, "description": "Idempotent replay"},
                         **_responses(401, 403, 409, 422, 429, 503)})
    def create_link(body: CreateLink, key_id: Annotated[str, Depends(require_key)],
                    idempotency_key: Annotated[str | None, Header(max_length=128)] = None) -> Any:
        limiter.check(key_id)
        try:
            destination = validate_url(body.url, self_hosts=settings.self_hosts,
                                       max_length=settings.max_url_length)
        except InvalidURL as err:
            raise ProblemError(422, err.code, "Invalid URL", err.detail) from None
        now = clock()
        expires_at = None
        if body.expires_at is not None:
            if body.expires_at.tzinfo is None:
                raise ProblemError(422, "invalid_expiration", "Invalid expiration",
                                   "expires_at must include a UTC offset")
            if body.expires_at <= now:
                raise ProblemError(422, "invalid_expiration", "Invalid expiration",
                                   "expires_at must be in the future")
            expires_at = _iso(body.expires_at)
        fingerprint = hashlib.sha256(json.dumps([body.url, expires_at]).encode()).hexdigest()
        created_at = _iso(now)
        render = lambda code: LinkOut(  # noqa: E731
            code=code, short_url=f"{settings.public_base_url}/{code}", destination=destination,
            created_at=created_at, expires_at=expires_at).model_dump()
        try:
            status, out = store.create(
                key_id=key_id, destination=destination, created_at=created_at, expires_at=expires_at,
                idem_key=idempotency_key, fingerprint=fingerprint, new_code=make_code,
                attempts=settings.max_code_attempts, render=render)
        except sqlite3.Error:
            raise unavailable() from None
        if status == "conflict":
            raise ProblemError(409, "idempotency_conflict", "Idempotency conflict",
                               "this Idempotency-Key was used with a different request")
        if status == "exhausted":
            raise ProblemError(503, "code_generation_exhausted", "Service unavailable",
                               "could not allocate a unique code; retry later")
        if status == "replayed":
            return JSONResponse(out, status_code=200, headers={"Idempotent-Replayed": "true"})
        return out

    @app.get("/api/v1/links/{code}/stats", response_model=StatsOut,
             responses=_responses(401, 403, 404, 503))
    def link_stats(code: str, _: Annotated[str, Depends(require_key)]) -> StatsOut:
        try:
            link = store.get(code) if codes.CODE_PATTERN.match(code) else None
            row = store.stats(code) if link else None
        except sqlite3.Error:
            raise unavailable() from None
        if link is None:
            raise ProblemError(404, "not_found", "Not found")
        return StatsOut(code=code, clicks=row["clicks"] if row else 0,
                        last_click_at=row["last_click_at"] if row else None)

    @app.get("/health/live", response_model=LiveOut)
    def live() -> LiveOut:
        return LiveOut(status="ok")

    @app.get("/health/ready", response_model=ReadyOut, responses={503: {"model": ReadyOut}})
    def ready() -> Any:
        failures = counters["analytics_write_failures"]
        try:
            store.ping()
        except sqlite3.Error:
            body = ReadyOut(status="unavailable", database="unreachable", analytics_write_failures=failures)
            return JSONResponse(body.model_dump(), status_code=503)
        return ReadyOut(status="ready", database="ok", analytics_write_failures=failures)

    @app.get("/{code}", status_code=302, response_class=RedirectResponse,
             responses={302: {"description": "Redirect to the destination"}, **_responses(404, 410, 503)})
    def redirect(code: str) -> RedirectResponse:
        if not codes.CODE_PATTERN.match(code):
            raise ProblemError(404, "not_found", "Not found")
        try:
            link = store.get(code)
        except sqlite3.Error:
            raise unavailable() from None  # never redirect to an unverified destination
        if link is None:
            raise ProblemError(404, "not_found", "Not found")
        now = clock()
        if link["expires_at"] and now >= datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00")):
            raise ProblemError(410, "link_expired", "Link expired")
        try:
            store.record_click(code, _iso(now))
        except Exception:  # analytics must never block the redirect (FR-SHR-011)
            with counter_lock:
                counters["analytics_write_failures"] += 1
            log.warning("analytics write failed for a redirect")
        return RedirectResponse(link["destination"], status_code=302, headers={
            "Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer"})

    return app
