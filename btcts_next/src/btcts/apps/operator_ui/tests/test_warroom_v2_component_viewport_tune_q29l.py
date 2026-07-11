# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_component_viewport_tune_q29l.py
# desc: PS-Q29L guards for WarRoom v2 component viewport tuning.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.prediction_cards import (  # noqa: E402
    build_warroom_v2_prediction_matrix_renderer_packet,
    warroom_v2_prediction_matrix_height_px,
    warroom_v2_prediction_matrix_html,
)
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_placeholder_read_models_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
PREDICTION_CARDS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/prediction_cards.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29L_WARROOM_V2_COMPONENT_VIEWPORT_TUNE_2026-07-02.md"


def _prediction_models() -> list[dict]:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T08:00:00Z")
    return [model for model in packet["read_models"] if model["payload"].get("zone") == "prediction_cards"]


def test_q29l_renderer_packet_disables_component_internal_vertical_scroll() -> None:
    packet = build_warroom_v2_prediction_matrix_renderer_packet(_prediction_models())
    assert packet["streamlit_components_html_used"] is True
    assert packet["component_scrolling_enabled"] is False
    assert packet["page_scroll_owns_vertical_flow"] is True
    assert packet["internal_vertical_scroll_avoided"] is True
    assert packet["row_horizontal_scroll_preserved"] is True
    assert packet["cards_do_not_shrink"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False


def test_q29l_prediction_renderer_calls_components_without_scrolling() -> None:
    text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert "st_html(warroom_v2_prediction_matrix_html(models)" in text
    assert "scrolling=False" in text
    assert "scrolling=True" not in text
    assert "unsafe_allow_html=True" not in text
    assert "st.markdown(warroom_v2_prediction_matrix_html" not in text


def test_q29l_html_hides_component_body_vertical_overflow_but_keeps_row_x_scroll() -> None:
    html = warroom_v2_prediction_matrix_html(_prediction_models())
    assert "overflow-y: hidden" in html
    assert "overflow-x: auto" in html
    assert "wv2-strip" in html
    assert "wv2-card" in html
    assert "NO_DATA" in html


def test_q29l_component_height_remains_large_enough_for_all_rows() -> None:
    models = _prediction_models()
    height = warroom_v2_prediction_matrix_height_px(models)
    assert len(models) >= 8
    assert height >= 38 + (len(models) * 188)
    assert height <= 2200


def test_q29l_no_route_legacy_or_runtime_ownership_changed() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    pred_text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", get_text(lang, "page_warroom"), warroom_v2_page)' in app_text
    assert 'LEGACY_PAGE_KEY_REDIRECTS = {' in app_text
    assert '"warroom": "warroom_v2"' in app_text
    assert "streamlit.components.v1" not in legacy_text
    assert "prediction_warroom.v2.push_widgets" in legacy_text
    assert "ensure_warroom_push_widget_live_observation_runtime" in legacy_text
    assert "apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state" in legacy_text
    assert "warroom_v2_page" not in legacy_text
    assert "build_warroom_v2_shell_preview_packet" not in legacy_text
    assert "classify_market_regime_feature_bundle(" not in legacy_text
    assert "send_to_broker(" not in legacy_text
    assert "autotrade_trigger_allowed = True" not in legacy_text
    for token in ("build_market_regime_source_snapshot(", "classify_market_regime_feature_bundle(", "send_to_broker(", "append_ledger(", "write_runtime_artifact("):
        assert token not in pred_text


def test_q29l_doc_records_viewport_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "component_scrolling_enabled=false" in text
    assert "page_scroll_owns_vertical_flow=true" in text
    assert "internal_vertical_scroll_avoided=true" in text
    assert "row_horizontal_scroll_preserved=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_changing_legacy_warroom=true" in text
