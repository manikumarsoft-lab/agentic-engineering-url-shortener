"""Human lock for change sets: records the patch hashes the human owner reviewed (CHG-001, lean).

Only a human approver key may lock. Runs refuse change sets that are unlocked or differ from the
locked hashes (`integrity_mismatch` -> SAFE_STOPPED).

Satisfies: FR-ORC-033, FR-ORC-034 (CHG-001, plan §16.3 lock).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from orchestrator.agents.scenario import LOCK_REL, PROVENANCE, sha256_lf
from orchestrator.keys import Principal


class LockError(ValueError):
    pass


def lock(repo_root: Path, rel: str, principal: Principal) -> dict:
    if principal.actor_type != "human" or principal.role != "approver":
        raise LockError("only a human approver key may lock a change set")
    path = repo_root / rel
    manifest = yaml.safe_load((path / "manifest.yaml").read_text(encoding="utf-8"))
    if manifest.get("provenance") != PROVENANCE:
        raise LockError("manifest provenance label is missing or altered")
    hashes = {"tests_patch": sha256_lf(path / manifest["tests_patch"]),
              "impl_patch": sha256_lf(path / manifest["impl_patch"])}
    if hashes != manifest["sha256"]:
        raise LockError("patches differ from the hashes recorded in the manifest")
    lock_path = repo_root / LOCK_REL
    data = yaml.safe_load(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else None
    data = data or {"change_sets": {}}
    entry = {"sha256": hashes, "locked_by": principal.key_id, "role": principal.role,
             "locked_at": datetime.now(timezone.utc).isoformat()}
    data["change_sets"][rel] = entry
    lock_path.write_text("# Written by `orch changeset lock` (human approver key). Do not edit by hand.\n"
                         + yaml.safe_dump(data, sort_keys=True), encoding="utf-8", newline="\n")
    return entry
