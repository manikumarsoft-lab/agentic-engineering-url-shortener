"""Typed settings with secure defaults; environment overrides for `orch serve`.

Satisfies: FR-SHR-004 (self-referential host), FR-SHR-017 (rate limit), PVT-010, PVT-011.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    db_path: Path
    keys_db_path: Path
    public_base_url: str = "https://sho.rt"
    rate_limit_per_minute: int = 60
    max_url_length: int = 2048
    code_length: int = 7
    max_code_attempts: int = 5

    @property
    def self_hosts(self) -> frozenset[str]:
        return frozenset({(urlsplit(self.public_base_url).hostname or "").lower()})

    @classmethod
    def from_env(cls) -> "Settings":
        home = Path(os.environ.get("ORCH_HOME", "var"))
        return cls(
            db_path=Path(os.environ.get("SHORTENER_DB", home / "shortener.db")),
            keys_db_path=Path(os.environ.get("SHORTENER_KEYS_DB", home / "orchestrator.db")),
            public_base_url=os.environ.get("SHORTENER_PUBLIC_BASE_URL", "https://sho.rt"),
        )
