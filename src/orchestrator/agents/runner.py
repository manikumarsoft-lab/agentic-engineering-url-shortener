"""Subprocess entry point: `python -m orchestrator.agents.runner <ctx.json> <result.json>`.

A classified failure is written as {"ok": false, "code": ...}. Any other exception exits non-zero
without a result file, which the engine treats as an unclassified failure (safe-stop).

Satisfies: FR-ORC-014, FR-ORC-015, FR-ORC-018 (subprocess isolation, classification, timeouts).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from orchestrator.agents.base import AgentError
from orchestrator.agents.deterministic import AGENTS


def main(ctx_path: str, result_path: str) -> int:
    request = json.loads(Path(ctx_path).read_text(encoding="utf-8"))
    agent = AGENTS.get(request["agent"])
    if agent is None:
        result = {"ok": False, "code": "unknown_agent"}
    else:
        try:
            result = {"ok": True, "outputs": agent(request["ctx"]) or {}}
        except AgentError as err:
            result = {"ok": False, "code": err.code, "message": str(err), "details": err.details}
    Path(result_path).write_text(json.dumps(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
