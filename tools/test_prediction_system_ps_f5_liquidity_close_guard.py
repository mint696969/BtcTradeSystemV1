# path: ./tools/test_prediction_system_ps_f5_liquidity_close_guard.py
# desc: Close guard for PS-F5 liquidity_execution_quality deterministic v1 syntax and importability.

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
    ROOT / "tools" / "test_prediction_system_ps_f5_liquidity_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_f5_liquidity_close_guard.py",
]


def test_ps_f5_files_compile_and_import() -> None:
    for path in FILES:
        if not path.exists():
            raise AssertionError(f"missing file: {path}")
        py_compile.compile(str(path), doraise=True)
    rule = importlib.import_module("btcts.prediction.rule_based_v0")
    families = [family.value for family in rule.INITIAL_FAMILIES]
    assert "reversal_zone" in families
    assert "liquidity_execution_quality" in families
    assert "breakout_false_break" in families
    assert "opportunity_participation" in families
    assert "macro_risk_context" in families
    assert len(families) == 10


def main() -> int:
    test_ps_f5_files_compile_and_import()
    print("[OK] Prediction System PS-F5 liquidity_execution_quality close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
