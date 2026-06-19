# path: ./tools/test_prediction_system_ps_i1_revision_lifetime_close_guard.py
# desc: Close guard for PS-I1 revision lifetime syntax and importability.

from __future__ import annotations

import importlib
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FILES = [
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py",
    ROOT / "tools" / "test_prediction_system_ps_i1_revision_lifetime_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_i1_revision_lifetime_close_guard.py",
]


def test_ps_i1_files_compile_and_import() -> None:
    for path in FILES:
        if not path.exists():
            raise AssertionError(f"missing file: {path}")
        py_compile.compile(str(path), doraise=True)
    system = importlib.import_module("btcts.prediction.system")
    assert hasattr(system, "build_prediction_system_result")
    assert hasattr(system, "_refresh_decision_from_scenario_lite")
    assert hasattr(system, "_build_revision_summary")


def main() -> int:
    test_ps_i1_files_compile_and_import()
    print("[OK] Prediction System PS-I1 revision lifetime close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
