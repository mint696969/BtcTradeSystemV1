# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_row_level_detail_overlay_q29p.py
# desc: PS-Q29P guards for WarRoom v2 row-level readable detail overlay.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.card_detail_overlay_html import build_warroom_v2_detail_overlay_renderer_packet, warroom_v2_detail_overlay_css, warroom_v2_detail_overlay_panel_html  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.prediction_cards import build_warroom_v2_prediction_matrix_renderer_packet, warroom_v2_prediction_matrix_height_px, warroom_v2_prediction_matrix_html  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_placeholder_read_models_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
PREDICTION_CARDS = RENDERER_DIR / "prediction_cards.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29P_WARROOM_V2_ROW_LEVEL_DETAIL_OVERLAY_2026-07-02.md"


def _models() -> list[dict]:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T09:20:00Z")
    return [model for model in packet["read_models"] if model["payload"].get("zone") == "prediction_cards"]


def test_q29p_packet_declares_row_level_overlay_not_card_internal() -> None:
    cards = build_warroom_v2_prediction_matrix_renderer_packet(_models())
    detail = build_warroom_v2_detail_overlay_renderer_packet(_models()[0])
    assert cards["detail_disclosure_mode"] == "row_level_overlay_panel"
    assert cards["detail_overlay_card_width_constrained"] is False
    assert cards["detail_overlay_close_button_required"] is True
    assert cards["detail_overlay_layout_pushdown_avoided"] is True
    assert cards["matrix_bottom_padding_px"] >= 96
    assert cards["bottom_row_visibility_guard"] is True
    assert detail["row_level_overlay"] is True
    assert detail["card_width_constrained"] is False
    assert detail["close_button_required"] is True
    assert detail["outside_click_close_enabled"] is True
    assert detail["backdrop_close_layer"] is True
    assert detail["runtime_connected"] is False


def test_q29p_matrix_html_uses_row_overlay_radios_and_close_button() -> None:
    html = warroom_v2_prediction_matrix_html(_models()[:1])
    assert "class='wv2-detail-toggle' type='radio'" in html
    assert "class='wv2-row-overlays'" in html
    assert "class='wv2-row-detail-layer'" in html
    assert "class='wv2-row-detail-panel'" in html
    assert "class='wv2-detail-backdrop'" in html
    assert "class='wv2-detail-close'" in html
    assert "aria-label='詳細外側をクリックして閉じる'" in html
    assert "aria-label='詳細を閉じる'" in html
    assert "<details class='wv2-detail'>" not in html
    assert "<summary" not in html


def test_q29p_overlay_css_is_readability_first_and_not_card_width_bound() -> None:
    css = warroom_v2_detail_overlay_css()
    assert ".wv2-row { position: relative; }" in css
    assert "width: min(960px, calc(100vw - 56px))" in css
    assert "position: absolute" in css
    assert "z-index: 30" in css
    assert "position: fixed" in css
    assert "class='wv2-detail-backdrop'" not in css
    assert "max-height: 260px" in css
    assert "scrollbar-gutter: stable" in css
    assert ".wv2-card" not in css


def test_q29p_overlay_panel_has_title_close_and_display_only_footer() -> None:
    panel = warroom_v2_detail_overlay_panel_html(_models()[0], panel_id="p", close_id="c")
    assert "role='dialog'" in panel
    assert "地合い 詳細" in panel
    assert "class='wv2-detail-backdrop'" in panel
    assert "class='wv2-detail-close'" in panel
    assert "for='c'" in panel
    assert "row-level overlay / display-only" in panel

def test_q29p_component_height_has_bottom_visibility_padding() -> None:
    models = _models()
    html = warroom_v2_prediction_matrix_html(models)
    height = warroom_v2_prediction_matrix_height_px(models)
    assert "padding-bottom:" in html
    assert "WARROOM_V2_MATRIX_BOTTOM_PADDING_PX" in PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert height >= 54 + (len(models) * 202) + 96
    assert height <= 2200



def test_q29p_renderer_files_remain_small_and_side_effect_free() -> None:
    forbidden = (
        "D:" + "\\",
        "E:" + "\\",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "write_runtime_artifact(",
        "websocket.",
        "sse.",
    )
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text


def test_q29p_doc_records_row_level_overlay_decision() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "detail_disclosure_mode=row_level_overlay_panel" in text
    assert "card_width_constrained=false" in text
    assert "close_button_required=true" in text
    assert "layout_pushdown_avoided=true" in text
    assert "bottom_row_visibility_guard=true" in text
    assert "not_connecting_dhot=true" in text
