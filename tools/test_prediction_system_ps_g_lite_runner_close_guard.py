# path: ./tools/test_prediction_system_ps_g_lite_runner_close_guard.py
# desc: Close guard for PS-G-lite standalone Prediction System runner syntax and importability.

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
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "horizons.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "ohlcv.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_registry.py",
    ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_close_guard.py",
]


def test_ps_g_lite_files_compile_and_import() -> None:
    for path in FILES:
        if not path.exists():
            raise AssertionError(f"missing file: {path}")
        py_compile.compile(str(path), doraise=True)
    module = importlib.import_module("btcts.prediction.system")
    assert module.LOGIC_VERSION == "prediction_system.ps_g_lite.v1"
    public = importlib.import_module("btcts.prediction")
    assert hasattr(public, "build_prediction_system_result")


def main() -> int:
    test_ps_g_lite_files_compile_and_import()
    print("[OK] Prediction System PS-G-lite runner close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
