import sqlite3

import pytest

from orchestrator import audit, keys
from orchestrator.policy import load_policy_text
from orchestrator.store import Store


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "a.db")


def _append(store, n=3):
    with store.tx() as c:
        for i in range(n):
            audit.append(c, "run_x", f"EVENT_{i}", ts=1000.0 + i, data={"i": i})


def test_hash_chain_verifies(store):
    _append(store)
    assert audit.verify_chain(store.conn, "run_x") == (True, None)
    evs = audit.events(store.conn, "run_x")
    assert [e["seq"] for e in evs] == [1, 2, 3]
    assert evs[1]["prev_hash"] == evs[0]["hash"]


def test_update_and_delete_are_refused(store):
    _append(store)
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        store.conn.execute("UPDATE audit SET action = 'X' WHERE seq = 1")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        store.conn.execute("DELETE FROM audit WHERE seq = 1")


def test_out_of_band_tampering_is_detected(store):
    _append(store)
    store.conn.execute("DROP TRIGGER audit_no_update")  # simulate a direct file edit
    store.conn.execute("UPDATE audit SET reason = 'edited' WHERE seq = 2")
    assert audit.verify_chain(store.conn, "run_x") == (False, 2)


def test_append_outside_a_transaction_is_refused(store):
    with pytest.raises(RuntimeError, match="transaction"):
        audit.append(store.conn, "run_x", "LONE", ts=1.0)


def test_keys_are_hashed_and_role_mapped(store):
    secret = keys.create_key(store, "approver", ts=1.0)
    p = keys.resolve(store, secret)
    assert p.role == "approver" and p.actor_type == "human"
    assert keys.resolve(store, keys.create_key(store, "agent", ts=1.0)).actor_type == "agent"
    stored = store.conn.execute("SELECT secret_sha256 FROM keys WHERE key_id = ?", (p.key_id,)).fetchone()[0]
    assert secret.split(".", 1)[1] not in stored
    assert keys.resolve(store, secret[:-1] + "x") is None
    assert keys.resolve(store, "garbage") is None
    with pytest.raises(ValueError):
        keys.create_key(store, "root", ts=1.0)


POLICY = """
version: 1.2.0
checks:
  - {id: PRIV-001, fact: captures_personal_data, expect: false, mandatory: true}
  - {id: LIC-002, fact: copyleft_dependency, expect: false, mandatory: false}
"""


def test_policy_outcomes_and_version():
    policy = load_policy_text(POLICY)
    assert policy.version == "1.2.0"
    out = {e.check_id: e.outcome for e in policy.evaluate(("PRIV-001", "LIC-002"),
                                                          {"captures_personal_data": True})}
    assert out == {"PRIV-001": "FAIL", "LIC-002": "NOT-APPLICABLE"}
    assert policy.evaluate(("PRIV-001",), {"captures_personal_data": False})[0].outcome == "PASS"
