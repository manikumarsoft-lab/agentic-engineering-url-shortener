"""Export the shortener OpenAPI contract: `python -m shortener.openapi [path]`."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from shortener.app import create_app
from shortener.config import Settings

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "shortener-api.openapi.json"


def generate() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        settings = Settings(db_path=Path(tmp) / "s.db", keys_db_path=Path(tmp) / "k.db")
        return create_app(settings).openapi()


def render(spec: dict[str, Any]) -> str:
    return json.dumps(spec, indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else CONTRACT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(generate()), encoding="utf-8")
    print(f"wrote {target}")
