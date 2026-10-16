"""200 parallel creates against a real server started with `orch serve`."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

from orchestrator import keys
from orchestrator.engine import SRC_ROOT, kill_tree
from orchestrator.store import Store


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _serve(home) -> tuple[subprocess.Popen, str]:
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "cli.main", "serve", "--port", str(port)],
        env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "ORCH_HOME": str(home)},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        start_new_session=os.name != "nt")
    base = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 20
    while True:
        try:
            if httpx.get(f"{base}/health/live", timeout=1).status_code == 200:
                return proc, base
        except httpx.HTTPError:
            pass
        if time.monotonic() >= deadline:
            kill_tree(proc)
            raise AssertionError("server did not start")
        time.sleep(0.2)


def test_orch_serve_handles_200_parallel_creates_with_unique_codes(tmp_path):
    home = tmp_path / "var"
    store = Store(home / "orchestrator.db")
    consumer_keys = [keys.create_key(store, "consumer", ts=time.time()) for _ in range(4)]  # 50 each < 60/min
    proc, base = _serve(home)
    try:
        def create(i: int) -> httpx.Response:
            return httpx.post(f"{base}/api/v1/links", json={"url": f"https://example.com/{i}"},
                              headers={"X-API-Key": consumer_keys[i % 4]}, timeout=30)

        with ThreadPoolExecutor(max_workers=50) as pool:
            responses = list(pool.map(create, range(200)))
        assert [r.status_code for r in responses] == [201] * 200
        codes = {r.json()["code"] for r in responses}
        assert len(codes) == 200
        sample = responses[17].json()
        r = httpx.get(f"{base}/{sample['code']}", follow_redirects=False)
        assert r.status_code == 302 and r.headers["location"] == "https://example.com/17"
    finally:
        kill_tree(proc)


def test_orch_serve_counts_200_parallel_redirects_exactly(tmp_path):
    """Verifies: FR-SHR-014, A-013 (exact counts while analytics storage is healthy, G6)."""
    home = tmp_path / "var"
    consumer = keys.create_key(Store(home / "orchestrator.db"), "consumer", ts=time.time())
    proc, base = _serve(home)
    try:
        created = httpx.post(f"{base}/api/v1/links", json={"url": "https://example.com/hot"},
                             headers={"X-API-Key": consumer}, timeout=30)
        assert created.status_code == 201
        code = created.json()["code"]

        def redirect(_: int) -> int:
            return httpx.get(f"{base}/{code}", follow_redirects=False, timeout=30).status_code

        with ThreadPoolExecutor(max_workers=50) as pool:
            statuses = list(pool.map(redirect, range(200)))
        assert statuses == [302] * 200
        stats = httpx.get(f"{base}/api/v1/links/{code}/stats", headers={"X-API-Key": consumer}, timeout=30)
        ready = httpx.get(f"{base}/health/ready", timeout=30).json()
        assert stats.json()["clicks"] == 200, f"stats={stats.json()} ready={ready}"
    finally:
        kill_tree(proc)
