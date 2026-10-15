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


SKIP_DIRS = frozenset({"__pycache__", ".pytest_cache"})


def create_from(root: Path, run_id: str, source_root: Path, include: tuple[str, ...]) -> Path:
    """Copy selected repo paths into a fresh workspace. Text files are normalized to LF so
    change-set patches apply regardless of the checkout's line endings."""
    dest = _inside(root / run_id, root)
    if dest.exists():
        shutil.rmtree(dest)
    for rel in include:
        src = source_root / rel
        files = [src] if src.is_file() else [p for p in src.rglob("*") if p.is_file()
                                              and not SKIP_DIRS.intersection(p.parts) and p.suffix != ".pyc"]
        for path in files:
            target = dest / path.relative_to(source_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            data = path.read_bytes()
            try:
                data = data.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
            except UnicodeDecodeError:
                pass
            target.write_bytes(data)
    return dest


def discard(root: Path, run_id: str) -> bool:
    dest = _inside(root / run_id, root)
    if not dest.exists():
        return False
    shutil.rmtree(dest)
    return True
