from __future__ import annotations

import time
from contextlib import closing
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from common import apikeys
from shortener.app import create_app
from shortener.config import Settings
import sqlite3


class FakeNow:
    def __init__(self) -> None:
        self.now = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kw: float) -> None:
        self.now += timedelta(**kw)


def make_keys(path, *roles: str) -> dict[str, str]:
    with closing(sqlite3.connect(path, isolation_level=None)) as conn:
        conn.execute(apikeys.SCHEMA)
        return {role: apikeys.insert(conn, role.split("#")[0], role, time.time())[1] for role in roles}


@pytest.fixture
def svc(tmp_path):
    settings = Settings(db_path=tmp_path / "shortener.db", keys_db_path=tmp_path / "keys.db")
    keys = make_keys(settings.keys_db_path, "consumer", "consumer#2", "agent")
    clock = FakeNow()
    ns = SimpleNamespace(settings=settings, keys=keys, clock=clock)

    def client(**kw) -> TestClient:
        app = create_app(settings, clock=clock, **kw)
        ns.app = app
        return TestClient(app, follow_redirects=False, raise_server_exceptions=False)

    def create(c: TestClient, url: str, key: str = "consumer", **body):
        return c.post("/api/v1/links", json={"url": url, **body}, headers={"X-API-Key": keys[key]})

    ns.client, ns.create = client, create
    return ns
