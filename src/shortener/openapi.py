"""Generate the shortener OpenAPI contract from the app: `python -m shortener.openapi [path]`.

The generated file is the single source of the contract (CR-007). Never edit it by hand.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

from shortener.app import create_app
from shortener.config import Settings

CONTRACT = (Path(__file__).resolve().parents[2] / "specs" / "001-agentic-sdlc-url-shortener"
            / "contracts" / "shortener-api.openapi.yaml")
HEADER = ("# GENERATED from the running app by `python -m shortener.openapi` (CR-007).\n"
          "# Single source of the shortener contract; do not edit by hand.\n")


def generate() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        settings = Settings(db_path=Path(tmp) / "s.db", keys_db_path=Path(tmp) / "k.db")
        return create_app(settings).openapi()


def render(spec: dict[str, Any]) -> str:
    return HEADER + yaml.safe_dump(spec, sort_keys=True, allow_unicode=True, width=100)


def load(path: Path = CONTRACT) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else CONTRACT
    target.write_text(render(generate()), encoding="utf-8")
    print(f"wrote {target}")
