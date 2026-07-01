# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_renderer_q26y.py
# desc: PS-Q26Y tests for market regime card renderer shell. UI shell only; no live data or WarRoom page mount.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (  # noqa: E402
    WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION,
    build_sample_market_regime_cards,
    build_warroom_market_regime_card_renderer_packet,
    market_regime_cards_html,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def test_q26y_sample_cards_cover_horizons_and_unknown() -> None:
    cards = build_sample_market_regime_cards()
    packet = build_warroom_market_regime_card_renderer_packet(cards)
    assert packet["renderer_version"] == WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION
    assert packet["card_count"] == 8
    assert packet["horizons"] == ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]
    assert any(card["regime_code"] == "UNKNOWN" for card in cards)
    assert {card["background_tone"] for card in cards} >= {"GOOD", "CAUTION", "DANGER", "UNKNOWN"}
    assert packet["sample_data_only"] is False
    assert packet["live_data_connected"] is False
    assert packet["other_prediction_cards_implemented"] is False


def test_q26y_html_uses_horizontal_scroll_and_fixed_card_width() -> None:
    html = market_regime_cards_html(build_sample_market_regime_cards())
    assert "market-regime-card-shell" in html
    assert "overflow-x: auto" in html
    assert "min-width: 168px" in html
    assert "flex: 0 0 168px" in html
    assert "scroll-snap-type" in html
    assert "予測不能" in html
    assert "LIVE" in html
    assert "MISSING" in html
    assert "details" in html
    assert "summary>詳細" in html


def test_q26y_packet_preserves_safety_and_no_page_mount() -> None:
    packet = build_warroom_market_regime_card_renderer_packet()
    assert packet["sample_data_only"] is True
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_mounted"] is False
    assert packet["streamlit_render_function_declared"] is True
    assert packet["streamlit_render_invoked_by_page"] is False
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["border_meaning"] == "evidence_quality"
    assert packet["cards_do_not_shrink"] is True
    assert packet["full_width_target_horizon"] == "24時間後"
    assert packet["production_ui_code_changed"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    for key in ("runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False


def test_q26y_does_not_touch_warroom_page() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert "WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION" in panel_text
    assert "render_warroom_market_regime_card_shell" in panel_text
    assert "WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION" not in page_text
    assert "render_warroom_market_regime_card_shell" not in page_text
