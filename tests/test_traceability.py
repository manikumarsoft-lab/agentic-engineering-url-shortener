"""The lean traceability check passes on the repository (FR-OBS-010, SC-007 in lean form)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_traceability_check_has_no_gaps():
    spec = importlib.util.spec_from_file_location("trace_check", ROOT / "tools" / "trace_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.check(ROOT) == []
