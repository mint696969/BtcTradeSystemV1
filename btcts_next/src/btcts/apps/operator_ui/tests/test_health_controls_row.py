# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_controls_row.py
# desc: Verifies Health range controls and update timestamp share one row.

from __future__ import annotations

from pathlib import Path

TARGET = Path(__file__).resolve().parents[5] / "src/btcts/apps/operator_ui/views/health_page.py"


def test_health_range_and_live_tick_share_one_compact_row() -> None:
    text = TARGET.read_text(encoding="utf-8-sig")

    assert 'controls_left, controls_right = st.columns([1.25, 5.75], gap="large")' in text
    assert "with controls_left:" in text
    assert "with controls_right:" in text
    assert 'health_widget_slot("live_tick_caption")' in text
    assert "range_cols = st.columns([1, 6])" not in text


def test_health_live_tick_is_visually_aligned_with_selector() -> None:
    text = TARGET.read_text(encoding="utf-8-sig")

    assert "padding-top:1.9rem" in text
    assert "white-space:nowrap" in text
    assert "unsafe_allow_html=True" in text
