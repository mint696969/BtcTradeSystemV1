# path: ./tools/test_prediction_system_ps_f_complete_review_close_guard.py
# desc: Close guard for PS-F complete review document and guard importability.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_F_COMPLETE_11_FAMILY_REVIEW_BTC_BITFLYER_2026-06-19.md"
FILES = [
    ROOT / "tools" / "test_prediction_system_ps_f_complete_review_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_f_complete_review_close_guard.py",
]


def test_review_doc_and_guards_exist_and_compile() -> None:
    if not DOC.exists():
        raise AssertionError(f"missing review doc: {DOC}")
    text = DOC.read_text(encoding="utf-8")
    assert "PS-H1: Scenario Core lite integration" in text
    assert "PS-E: feature layer strengthening" in text
    for path in FILES:
        if not path.exists():
            raise AssertionError(f"missing file: {path}")
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_review_doc_and_guards_exist_and_compile()
    print("[OK] Prediction System PS-F complete review close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
