# path: ./tools/test_prediction_system_standalone_design_roadmap_close_guard.py
# desc: Close guard for standalone Prediction System design roadmap guard syntax and document presence.
from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "tools" / "test_prediction_system_standalone_design_roadmap_guard.py"
THIS = ROOT / "tools" / "test_prediction_system_standalone_design_roadmap_close_guard.py"
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_STANDALONE_DESIGN_AND_ROADMAP_BTC_BITFLYER_2026-06-19.md"


def main() -> int:
    if not DOC.exists():
        raise AssertionError(f"missing doc: {DOC}")
    py_compile.compile(str(GUARD), doraise=True)
    py_compile.compile(str(THIS), doraise=True)
    print("[OK] Prediction System standalone design/roadmap close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
