# path: ./tools/test_prediction_system_ps_e1_feature_depth_close_guard.py
# desc: Close guard for PS-E1 feature-depth syntax and importability.

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
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_depth.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "__init__.py",
    ROOT / "tools" / "test_prediction_system_ps_e1_feature_depth_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_e1_feature_depth_close_guard.py",
]


def test_ps_e1_files_compile_and_import() -> None:
    for path in FILES:
        if not path.exists():
            raise AssertionError(f"missing file: {path}")
        py_compile.compile(str(path), doraise=True)
    prediction = importlib.import_module("btcts.prediction")
    assert hasattr(prediction, "FeatureDepthSnapshot")
    assert hasattr(prediction, "OrderBookFeatureSummary")
    assert hasattr(prediction, "TradeFlowFeatureSummary")
    assert hasattr(prediction, "build_feature_depth_snapshot")


def main() -> int:
    test_ps_e1_files_compile_and_import()
    print("[OK] Prediction System PS-E1 feature depth close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
