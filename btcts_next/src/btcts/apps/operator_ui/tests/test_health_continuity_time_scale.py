# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_continuity_time_scale.py
# desc: Verifies continuity time-cell scale and labels for each Health range.

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[5] / "src/btcts/apps/operator_ui"
CONTINUITY = ROOT / "components/health_continuity.py"
TOP_PANELS = ROOT / "components/health_top_panels.py"


def test_continuity_scale_changes_by_range() -> None:
    text = CONTINUITY.read_text(encoding="utf-8-sig")
    assert '"1セル＝1分"' in text
    assert '"1セル＝30分"' in text
    assert '"1セル＝3時間"' in text
    assert '"major_every": 10' in text
    assert '"major_every": 6' in text
    assert '"major_every": 8' in text


def test_continuity_rail_renders_visual_time_guides() -> None:
    text = CONTINUITY.read_text(encoding="utf-8-sig")
    assert "health-continuity-cell-major" in text
    assert "health-continuity-scale-track" in text
    assert "first_label" in text
    assert "middle_label" in text
    assert "last_label" in text


def test_continuity_range_key_is_propagated_to_all_rows_and_legend() -> None:
    text = TOP_PANELS.read_text(encoding="utf-8-sig")
    assert text.count("range_key=range_key") >= 3
    assert "render_continuity_legend(range_key=range_key, lang=lang)" in text
    assert "1分・30分・3時間" in text
