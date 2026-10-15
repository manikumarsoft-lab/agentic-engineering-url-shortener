"""Agent contract: `agent(ctx: dict) -> dict` returning {"artifacts": {...}, "facts": {...}}."""
from __future__ import annotations


class AgentError(Exception):
    """A classified agent failure. `code` is looked up in the node's failure classification."""

    def __init__(self, code: str, message: str = "", details: dict | None = None) -> None:
        super().__init__(message or code)
        self.code = code
        self.details = details or {}  # recorded in the audit trail (e.g. failing test names)
