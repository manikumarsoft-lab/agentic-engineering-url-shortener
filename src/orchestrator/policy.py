"""Versioned policy set: each check yields PASS, FAIL, EXCEPTION-REQUESTED or NOT-APPLICABLE.

Satisfies: FR-GOV-005, FR-GOV-006, FR-GOV-007.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

OUTCOMES = ("PASS", "FAIL", "EXCEPTION-REQUESTED", "NOT-APPLICABLE")


@dataclass(frozen=True)
class Check:
    id: str
    fact: str
    expect: Any
    mandatory: bool = True
    description: str = ""


@dataclass(frozen=True)
class Evaluation:
    check_id: str
    outcome: str
    mandatory: bool
    reason: str


@dataclass(frozen=True)
class PolicySet:
    version: str
    checks: dict[str, Check]

    def evaluate(self, check_ids: tuple[str, ...], facts: dict[str, Any]) -> list[Evaluation]:
        results = []
        for cid in check_ids:
            check = self.checks[cid]
            detail = facts.get(f"{check.fact}_detail")  # evidence the agent recorded for this fact
            suffix = f"; {detail}" if detail else ""
            if check.fact not in facts:
                results.append(Evaluation(cid, "NOT-APPLICABLE", check.mandatory,
                                          f"fact '{check.fact}' not present"))
            elif facts[check.fact] == check.expect:
                results.append(Evaluation(cid, "PASS", check.mandatory,
                                          f"{check.fact} == {check.expect!r}{suffix}"))
            else:
                results.append(Evaluation(cid, "FAIL", check.mandatory,
                                          f"{check.fact} = {facts[check.fact]!r}, expected {check.expect!r}{suffix}"))
        return results


def load_policy_text(text: str) -> PolicySet:
    raw = yaml.safe_load(text)
    checks = {
        c["id"]: Check(id=c["id"], fact=c["fact"], expect=c["expect"],
                       mandatory=bool(c.get("mandatory", True)), description=c.get("description", ""))
        for c in raw["checks"]
    }
    return PolicySet(version=str(raw["version"]), checks=checks)


def load_policy(path: str | Path) -> PolicySet:
    return load_policy_text(Path(path).read_text(encoding="utf-8"))
