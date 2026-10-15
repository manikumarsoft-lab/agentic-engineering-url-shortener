"""Isolated workspace copies of the system under change; rollback discards the copy.

Satisfies: FR-ORC-032, FR-ORC-035.
"""
from __future__ import annotations

import shutil
from pathlib import Path


def _inside(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"workspace path {path} escapes {root}")
    return resolved


def create(root: Path, run_id: str, source: Path) -> Path:
    dest = _inside(root / run_id, root)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    return dest


def discard(root: Path, run_id: str) -> bool:
    dest = _inside(root / run_id, root)
    if not dest.exists():
        return False
    shutil.rmtree(dest)
    return True
