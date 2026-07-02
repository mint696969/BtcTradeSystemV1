# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_matrix_raw_html_render_fix_q29k.py
# desc: PS-Q29K guards for WarRoom v2 matrix raw HTML render fix.

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
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29K_WARROOM_V2_MATRIX_RAW_HTML_RENDER_FIX_2026-07-02.md"


def _prediction_models() -> list[dict]:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T07:40:00Z")
    return [model for model in packet["read_models"] if model["payload"].get("zone") == "prediction_cards"]


def test_q29k_renderer_packet_uses_components_html_not_markdown_unsafe_html() -> None:
    packet = build_warroom_v2_prediction_matrix_renderer_packet(_prediction_models())
    assert packet["streamlit_components_html_used"] is True
    assert packet["markdown_unsafe_html_used"] is False
    assert packet["raw_html_visible_guard"] is True
    assert packet["html_matrix_renderer"] is True
    assert packet["cards_do_not_shrink"] is True
    assert packet["horizontal_scroll_required"] is True
    assert packet["visual_semantics_from_payload"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False


def test_q29k_prediction_cards_calls_components_html() -> None:
    text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert "from streamlit.components.v1 import html as st_html" in text
    assert "st_html(warroom_v2_prediction_matrix_html(models)" in text
    assert "unsafe_allow_html=True" not in text
    assert "st.markdown(warroom_v2_prediction_matrix_html" not in text
    assert "st.columns(max(1, len(horizon_cards)))" not in text


def test_q29k_card_html_has_no_markdown_code_block_indentation() -> None:
    html = warroom_v2_prediction_matrix_html(_prediction_models())
    assert "\n    <div class='wv2-card" not in html
    assert "<div class='wv2-card" in html
    assert "<style>" in html
    assert "wv2-strip" in html
    assert "wv2-detail-overlay" in html


def test_q29k_component_height_is_bounded_and_scales_by_rows() -> None:
    models = _prediction_models()
    height = warroom_v2_prediction_matrix_height_px(models)
    assert height >= 280
    assert height <= 1800
    assert height > 38 + (3 * 188)


def test_q29k_no_route_legacy_or_runtime_ownership_changed() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    pred_text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", "WarRoom v2", warroom_v2_page)' in app_text
    assert "streamlit.components.v1" not in legacy_text
    assert "prediction_warroom.v2" not in legacy_text
    for token in ("build_market_regime_source_snapshot(", "classify_market_regime_feature_bundle(", "send_to_broker(", "append_ledger(", "write_runtime_artifact("):
        assert token not in pred_text


def test_q29k_doc_records_raw_html_fix_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "streamlit_components_html_used=true" in text
    assert "markdown_unsafe_html_used=false" in text
    assert "raw_html_visible_guard=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_changing_legacy_warroom=true" in text
