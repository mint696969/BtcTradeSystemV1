# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_status_cards.py
# desc: Verifies compact Health current-status cards.

from __future__ import annotations

from pathlib import Path

TARGET = Path(__file__).resolve().parents[5] / "src/btcts/apps/operator_ui/components/health_top_panels.py"


def test_health_summary_cards_are_equal_height_and_color_coded() -> None:
    text = TARGET.read_text(encoding="utf-8-sig")

    assert "def _health_summary_level(value: str) -> str:" in text
    assert "def _render_health_summary_card(*, title: str, value: str, details: list[str])" in text
    assert '"green":' in text
    assert '"yellow":' in text
    assert '"red":' in text
    assert '"gray":' in text
    assert "height:88px" in text
    assert "border-left:4px solid {accent}" in text
    assert "-webkit-line-clamp:2" in text
    assert "overflow:hidden" in text


def test_health_summary_cards_replace_metric_blocks_without_data_logic_changes() -> None:
    text = TARGET.read_text(encoding="utf-8-sig")

    assert text.count("_render_health_summary_card(") >= 5
    assert "collector_summary_label(status_payload, health_payload, lang)" in text
    assert "api_summary_label(bitflyer_rate, lang)" in text
    assert "ws_summary_label(origin_payload, lang)" in text
    assert "layer3_summary_label(market_latest, market_diag, lang)" in text
