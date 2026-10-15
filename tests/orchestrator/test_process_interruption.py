"""Real process-level interruption and process-tree kill tests."""
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from orchestrator import keys
from orchestrator.engine import SRC_ROOT, Engine, kill_tree
from orchestrator.graph import load_workflow_text
from orchestrator.store import Store

FLOW = """
name: interrupt
version: 1.0.0
nodes:
  - {id: a, agent: noop}
  - {id: b, agent: sleep, params: {seconds: 60, first_execution_only: true}, depends_on: [a], timeout_s: 120}
  - {id: c, agent: noop, depends_on: [b]}
"""

DRIVER = """
import sys
from orchestrator.engine import Engine
from orchestrator.graph import load_workflow_text
from orchestrator.store import Store
from pathlib import Path
eng = Engine(Store(sys.argv[1]), load_workflow_text(Path(sys.argv[2]).read_text()), var_dir=sys.argv[3])
run_id = eng.submit()
print(run_id, flush=True)
eng.run(run_id)
"""


def _spawn_group(args: list[str], **kw) -> subprocess.Popen:
    return subprocess.Popen(
        args, env={**os.environ, "PYTHONPATH": str(SRC_ROOT)},
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        start_new_session=os.name != "nt", **kw)


def test_killed_engine_process_is_safe_stopped_and_resumes(tmp_path):
    db, flow, var = tmp_path / "orch.db", tmp_path / "flow.yaml", tmp_path / "var"
    flow.write_text(FLOW, encoding="utf-8")
    approver = keys.create_key(Store(db), "approver", ts=time.time())
    proc = _spawn_group([sys.executable, "-c", DRIVER, str(db), str(flow), str(var)],
                        stdout=subprocess.PIPE, text=True)
    run_id = proc.stdout.readline().strip()
    store = Store(db)
    deadline = time.monotonic() + 30
    while store.nodes(run_id)["b"]["state"] != "RUNNING":
        assert time.monotonic() < deadline, "node b never started"
        time.sleep(0.1)
    kill_tree(proc)  # the engine and its agent subprocess die mid-node

    engine = Engine(store, load_workflow_text(FLOW), var_dir=var)
    assert engine.recover() == [run_id]
    run = store.run(run_id)
    assert (run["state"], run["reason"]) == ("SAFE_STOPPED", "interrupted")
    engine.resume(run_id, approver, "operator restarted the engine")
    assert engine.run(run_id) == "COMPLETED"
    totals = {nid: row["runs_total"] for nid, row in store.nodes(run_id).items()}
    assert totals == {"a": 1, "b": 2, "c": 1}  # a was not re-executed


GRANDCHILD = """
import subprocess, sys, time
subprocess.Popen([sys.executable, "-c",
    "import time, pathlib; time.sleep(3); pathlib.Path(r'{marker}').write_text('alive')"])
time.sleep(60)
"""


def _assert_kill_tree_reaches_grandchild(tmp_path: Path) -> None:
    marker = tmp_path / "grandchild.txt"
    proc = _spawn_group([sys.executable, "-c", GRANDCHILD.format(marker=marker)])
    time.sleep(1.0)
    kill_tree(proc)
    time.sleep(3.5)
    assert proc.returncode is not None
    assert not marker.exists(), "grandchild survived the process-tree kill"


@pytest.mark.skipif(os.name != "nt", reason="Windows kill path (taskkill /T /F)")
def test_kill_tree_windows_path(tmp_path):
    _assert_kill_tree_reaches_grandchild(tmp_path)


@pytest.mark.skipif(os.name == "nt", reason="POSIX kill path (killpg): tested only on a POSIX CI runner")
def test_kill_tree_posix_path(tmp_path):
    _assert_kill_tree_reaches_grandchild(tmp_path)
