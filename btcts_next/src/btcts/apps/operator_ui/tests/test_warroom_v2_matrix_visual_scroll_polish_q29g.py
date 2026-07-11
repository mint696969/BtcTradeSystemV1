# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_matrix_visual_scroll_polish_q29g.py
# desc: PS-Q29G guards for WarRoom v2 no-shrink horizontal-scroll matrix renderer.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.prediction_cards import (  # noqa: E402
    WARROOM_V2_MATRIX_CARD_WIDTH_PX,
    WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION,
    build_warroom_v2_prediction_matrix_renderer_packet,
    warroom_v2_prediction_matrix_html,
)
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_placeholder_read_models_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
PREDICTION_CARDS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/prediction_cards.py"
DETAIL_OVERLAY = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/card_detail_overlay_html.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29G_WARROOM_V2_MATRIX_VISUAL_SCROLL_POLISH_2026-07-02.md"


def _prediction_models() -> list[dict]:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T06:20:00Z")
    return [model for model in packet["read_models"] if model["payload"].get("zone") == "prediction_cards"]


def test_q29g_renderer_packet_preserves_no_shrink_scroll_contract() -> None:
    packet = build_warroom_v2_prediction_matrix_renderer_packet(_prediction_models())
    assert packet["renderer_version"] == WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION
    assert packet["html_matrix_renderer"] is True
    assert packet["streamlit_columns_used"] is False
    assert packet["cards_do_not_shrink"] is True
    assert packet["horizontal_scroll_required"] is True
    assert packet["card_width_px"] == 208
    assert packet["card_shape"] == "horizontal_rectangle"
    assert packet["detail_disclosure_mode"] == "row_level_overlay_panel"
    assert packet["detail_overlay_close_button_required"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False


def test_q29g_matrix_html_uses_fixed_width_horizontal_scroll_rows() -> None:
    html = warroom_v2_prediction_matrix_html(_prediction_models())
    assert "overflow-x: auto" in html
    assert "flex: 0 0 208px" in html
    assert "min-width: 208px" in html
    assert "scroll-snap-type: x proximity" in html
    assert "wv2-strip" in html
    assert "wv2-card" in html
    assert "現在" in html
    assert "24時間後" in html
    assert "地合い" in html
    assert "方向感" in html


def test_q29g_prediction_cards_no_longer_use_streamlit_columns_for_matrix() -> None:
    text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert "st.columns(max(1, len(horizon_cards)))" not in text
    assert "warroom_v2_prediction_matrix_html" in text
    assert "st_html(warroom_v2_prediction_matrix_html(models)" in text
    assert "unsafe_allow_html=True" not in text
    overlay_text = DETAIL_OVERLAY.read_text(encoding="utf-8-sig")
    assert "warroom_v2_detail_button_html" in text
    assert "warroom_v2_detail_overlay_panel_html" in text
    assert "build_warroom_v2_card_detail_balloon_packet" in overlay_text
    assert "build_warroom_v2_card_visual_semantics_packet" in text
    assert 'with st.expander("詳細"' not in text
    assert WARROOM_V2_MATRIX_CARD_WIDTH_PX == 208


def test_q29g_no_route_or_legacy_warroom_change() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", get_text(lang, "page_warroom"), warroom_v2_page)' in app_text
    assert 'LEGACY_PAGE_KEY_REDIRECTS = {' in app_text
    assert '"warroom": "warroom_v2"' in app_text
    assert "warroom_v2_matrix" not in legacy_text
    assert "prediction_warroom.v2.push_widgets" in legacy_text
    assert "ensure_warroom_push_widget_live_observation_runtime" in legacy_text
    assert "apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state" in legacy_text
    assert "warroom_v2_page" not in legacy_text
    assert "build_warroom_v2_shell_preview_packet" not in legacy_text
    assert "classify_market_regime_feature_bundle(" not in legacy_text
    assert "send_to_broker(" not in legacy_text
    assert "autotrade_trigger_allowed = True" not in legacy_text


def test_q29g_doc_records_visual_scroll_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "horizontal_scroll_required=true" in text
    assert "cards_do_not_shrink=true" in text
    assert "card_shape=horizontal_rectangle" in text
    assert "not_connecting_dhot=true" in text
    assert "not_changing_legacy_warroom=true" in text
