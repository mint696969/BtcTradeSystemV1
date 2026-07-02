# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/prediction_cards.py
# desc: WarRoom v2 prediction-card horizon matrix components renderer. Placeholder-only; no live data ownership.

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st
from streamlit.components.v1 import html as st_html

from .card_detail_overlay_html import warroom_v2_detail_button_html, warroom_v2_detail_overlay_css, warroom_v2_detail_overlay_panel_html
from .card_visual_semantics import build_warroom_v2_card_visual_semantics_packet, warroom_v2_card_visual_semantics_css

WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION = "prediction_warroom.v2.prediction_cards_renderer.ps_q29p.v2"
WARROOM_V2_MATRIX_CARD_WIDTH_PX, WARROOM_V2_MATRIX_CARD_MIN_HEIGHT_PX = 208, 128
WARROOM_V2_MATRIX_ROW_HEIGHT_PX, WARROOM_V2_MATRIX_BOTTOM_PADDING_PX = 202, 96

def _text(value: Any) -> str:
    return escape("" if value is None else str(value))

def _slug(value: Any) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in str(value or "row"))[:48]

def _horizon_card_model(parent: dict[str, Any], horizon_card: dict[str, Any]) -> dict[str, Any]:
    payload = dict(parent.get("payload", {}))
    payload.update(horizon_card)
    return {"widget_id": parent.get("widget_id", ""), "topic": parent.get("topic", ""), "title": parent.get("title", ""), "payload": payload}

def _card_html(parent: dict[str, Any], horizon_card: dict[str, Any], *, toggle_id: str) -> str:
    model = _horizon_card_model(parent, horizon_card)
    payload = model["payload"]
    visual = build_warroom_v2_card_visual_semantics_packet(payload)
    classes = f"wv2-card {visual['background_class']} {visual['evidence_class']}"
    return "".join([
        f"<div class='{classes}'>",
        f"<div class='wv2-card-top'><span>{_text(payload.get('horizon'))}</span><span class='wv2-badge {visual['freshness_class']}'>{_text(payload.get('freshness_badge', 'NO_DATA'))}</span></div>",
        f"<div class='wv2-primary'>{_text(payload.get('primary_label', '未接続'))}</div>",
        f"<div class='wv2-score'>{_text(payload.get('confidence_or_score', '--'))}</div>",
        f"<div class='wv2-tag'>{_text(payload.get('short_tag', 'PREVIEW_ONLY'))}</div>",
        warroom_v2_detail_button_html(toggle_id),
        "</div>",
    ])

def _row_html(model: dict[str, Any], row_index: int) -> str:
    title = _text(model.get("title") or model.get("widget_id"))
    row_slug = _slug(model.get("widget_id") or row_index)
    close_id = f"wv2_detail_none_{row_index}_{row_slug}"
    toggles = [f"<input class='wv2-detail-toggle' type='radio' name='wv2_detail_{row_index}_{row_slug}' id='{close_id}' checked>"]
    cards: list[str] = []
    panels: list[str] = []
    for card_index, card in enumerate(list(model.get("payload", {}).get("horizon_cards") or [])):
        toggle_id = f"wv2_detail_{row_index}_{card_index}_{row_slug}"
        panel_id = f"wv2_detail_panel_{row_index}_{card_index}_{row_slug}"
        card_model = _horizon_card_model(model, dict(card))
        toggles.append(f"<input class='wv2-detail-toggle' type='radio' name='wv2_detail_{row_index}_{row_slug}' id='{toggle_id}'>")
        cards.append(_card_html(model, dict(card), toggle_id=toggle_id))
        panels.append(warroom_v2_detail_overlay_panel_html(card_model, panel_id=panel_id, close_id=close_id))
    selector_css = "".join(f"#{'wv2_detail_' + str(row_index) + '_' + str(i) + '_' + row_slug}:checked ~ .wv2-row-overlays #wv2_detail_panel_{row_index}_{i}_{row_slug}{{display:block;}}" for i in range(len(panels)))
    return f"<section class='wv2-row'><style>{selector_css}</style><h3>{title}</h3>{''.join(toggles)}<div class='wv2-strip'>{''.join(cards)}</div><div class='wv2-row-overlays'>{''.join(panels)}</div></section>"

def warroom_v2_prediction_matrix_html(models: list[dict[str, Any]]) -> str:
    rows = [_row_html(model, row_index) for row_index, model in enumerate(models)]
    style = f"""
<style>
html, body {{ margin: 0; overflow-y: hidden; }}
body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #101828; }}
.wv2-matrix {{ display: flex; flex-direction: column; gap: 14px; width: 100%; padding-bottom: {WARROOM_V2_MATRIX_BOTTOM_PADDING_PX}px; box-sizing: border-box; }}
.wv2-row h3 {{ margin: 0 0 6px 0; font-size: 1.0rem; color: #101828; }}
.wv2-strip {{ display: flex; gap: 12px; overflow-x: auto; padding: 2px 2px 10px 2px; scroll-snap-type: x proximity; }}
.wv2-card {{ position: relative; flex: 0 0 {WARROOM_V2_MATRIX_CARD_WIDTH_PX}px; min-width: {WARROOM_V2_MATRIX_CARD_WIDTH_PX}px; min-height: {WARROOM_V2_MATRIX_CARD_MIN_HEIGHT_PX}px; border-radius: 16px; padding: 10px 10px 9px 10px; color: #101828; scroll-snap-align: start; box-sizing: border-box; }}
{warroom_v2_card_visual_semantics_css()}
{warroom_v2_detail_overlay_css()}
.wv2-card-top {{ display: flex; justify-content: space-between; align-items: center; font-size: .92rem; font-weight: 800; }}
.wv2-badge {{ min-width: 42px; padding: 3px 8px; border-radius: 999px; border: 1px solid rgba(16,24,40,.22); background: rgba(255,255,255,.82); text-align: center; font-size: .78rem; font-weight: 900; }}
.wv2-primary {{ margin-top: 8px; font-size: 1.14rem; font-weight: 850; }}
.wv2-score {{ margin-top: 10px; font-size: 1.60rem; font-weight: 900; }}
.wv2-tag {{ font-size: 1.04rem; font-weight: 800; }}
</style>
""".strip()
    return f"{style}<div class='wv2-matrix'>{''.join(rows)}</div>"

def warroom_v2_prediction_matrix_height_px(models: list[dict[str, Any]]) -> int:
    return max(280, min(2200, 54 + (len(models) * WARROOM_V2_MATRIX_ROW_HEIGHT_PX) + WARROOM_V2_MATRIX_BOTTOM_PADDING_PX))

def build_warroom_v2_prediction_matrix_renderer_packet(models: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True, "renderer_version": WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION, "html_matrix_renderer": True,
        "streamlit_components_html_used": True, "markdown_unsafe_html_used": False, "raw_html_visible_guard": True,
        "component_scrolling_enabled": False, "page_scroll_owns_vertical_flow": True, "internal_vertical_scroll_avoided": True,
        "row_horizontal_scroll_preserved": True, "streamlit_columns_used": False, "cards_do_not_shrink": True,
        "horizontal_scroll_required": True, "card_width_px": WARROOM_V2_MATRIX_CARD_WIDTH_PX, "card_shape": "horizontal_rectangle",
        "visual_semantics_from_payload": True, "background_color_never_encodes_freshness": True, "freshness_encoded_by_badge_only": True,
        "freshness_not_encoded_by_border": True, "border_meaning": "evidence_quality", "detail_disclosure_mode": "row_level_overlay_panel",
        "detail_overlay_card_width_constrained": False, "detail_overlay_close_button_required": True, "detail_overlay_layout_pushdown_avoided": True, "matrix_bottom_padding_px": WARROOM_V2_MATRIX_BOTTOM_PADDING_PX, "bottom_row_visibility_guard": True,
        "runtime_connected": False, "push_connected": False, "would_send_to_broker": False,
        "row_count": len(models), "component_height_px": warroom_v2_prediction_matrix_height_px(models),
    }

def render_warroom_v2_prediction_cards(models: list[dict[str, Any]]) -> None:
    st.subheader("Prediction cards")
    st_html(warroom_v2_prediction_matrix_html(models), height=warroom_v2_prediction_matrix_height_px(models), scrolling=False)
