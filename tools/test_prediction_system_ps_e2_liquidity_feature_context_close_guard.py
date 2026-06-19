# path: ./tools/test_prediction_system_ps_e2_liquidity_feature_context_close_guard.py
# desc: Close guard for PS-E2 liquidity feature-depth context syntax and importability.

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
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_depth.py",
    ROOT / "tools" / "test_prediction_system_ps_e2_liquidity_feature_context_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_e2_liquidity_feature_context_close_guard.py",
]


def test_ps_e2_files_compile_and_import() -> None:
    for path in FILES:
        if not path.exists():
            raise AssertionError(f"missing file: {path}")
        py_compile.compile(str(path), doraise=True)
    rule = importlib.import_module("btcts.prediction.rule_based_v0")
    system = importlib.import_module("btcts.prediction.system")
    assert hasattr(rule, "build_rule_based_v0_outputs")
    assert hasattr(rule, "_apply_liquidity_feature_depth_context")
    assert hasattr(system, "build_prediction_system_result")


def main() -> int:
    test_ps_e2_files_compile_and_import()
    print("[OK] Prediction System PS-E2 liquidity feature-depth context close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
