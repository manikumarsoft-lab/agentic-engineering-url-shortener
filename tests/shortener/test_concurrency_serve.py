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


def test_orch_serve_handles_200_parallel_creates_with_unique_codes(tmp_path):
    home = tmp_path / "var"
    store = Store(home / "orchestrator.db")
    consumer_keys = [keys.create_key(store, "consumer", ts=time.time()) for _ in range(4)]  # 50 each < 60/min
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "cli.main", "serve", "--port", str(port)],
        env={**os.environ, "PYTHONPATH": str(SRC_ROOT), "ORCH_HOME": str(home)},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        start_new_session=os.name != "nt")
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 20
        while True:
            try:
                if httpx.get(f"{base}/health/live", timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            assert time.monotonic() < deadline, "server did not start"
            time.sleep(0.2)

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
