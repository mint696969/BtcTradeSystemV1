# path: ./tools/test_prediction_system_ps_b_current_code_gap_index_close_guard.py
# desc: Close guard for PS-B Prediction System current code gap index guard syntax and document presence.

from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_CURRENT_CODE_GAP_INDEX_BTC_BITFLYER_2026-06-19.md"
GUARD = ROOT / "tools" / "test_prediction_system_ps_b_current_code_gap_index_guard.py"
THIS = ROOT / "tools" / "test_prediction_system_ps_b_current_code_gap_index_close_guard.py"


def main() -> int:
    if not DOC.exists():
        raise AssertionError(f"missing doc: {DOC}")
    py_compile.compile(str(GUARD), doraise=True)
    py_compile.compile(str(THIS), doraise=True)
    print("[OK] Prediction System PS-B current code gap index close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
