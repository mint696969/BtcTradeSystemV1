# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/prediction_cards.py
# desc: WarRoom v2 prediction-card horizon matrix HTML renderer. Placeholder-only; no live data ownership.

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from .card_detail_balloon import build_warroom_v2_card_detail_balloon_packet
from .card_visual_semantics import build_warroom_v2_card_visual_semantics_packet, warroom_v2_card_visual_semantics_css

WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION = "prediction_warroom.v2.prediction_cards_renderer.ps_q29i.v1"
WARROOM_V2_MATRIX_CARD_WIDTH_PX = 208
WARROOM_V2_MATRIX_CARD_MIN_HEIGHT_PX = 128


def _text(value: Any) -> str:
    return escape("" if value is None else str(value))


def _detail_html(model: dict[str, Any]) -> str:
    packet = build_warroom_v2_card_detail_balloon_packet(model)
    sections: list[str] = []
    for section in packet["sections"]:
        lines = section["lines"] or ["未接続のため未評価です。"]
        items = "".join(f"<li>{_text(line)}</li>" for line in lines[:3])
        sections.append(f"<div class='wv2-detail-section'><b>{_text(section['label'])}</b><ul>{items}</ul></div>")
    return "".join(sections)


def _horizon_card_model(parent: dict[str, Any], horizon_card: dict[str, Any]) -> dict[str, Any]:
    payload = dict(parent.get("payload", {}))
    payload.update(horizon_card)
    return {"widget_id": parent.get("widget_id", ""), "topic": parent.get("topic", ""), "title": parent.get("title", ""), "payload": payload}


def _card_html(parent: dict[str, Any], horizon_card: dict[str, Any]) -> str:
    model = _horizon_card_model(parent, horizon_card)
    payload = model["payload"]
    detail = _detail_html(model)
    visual = build_warroom_v2_card_visual_semantics_packet(payload)
    classes = f"wv2-card {visual['background_class']} {visual['evidence_class']}"
    return f"""
    <div class='{classes}'>
      <div class='wv2-card-top'><span>{_text(payload.get('horizon'))}</span><span class='wv2-badge {visual['freshness_class']}'>{_text(payload.get('freshness_badge', 'NO_DATA'))}</span></div>
      <div class='wv2-primary'>{_text(payload.get('primary_label', '未接続'))}</div>
      <div class='wv2-score'>{_text(payload.get('confidence_or_score', '--'))}</div>
      <div class='wv2-tag'>{_text(payload.get('short_tag', 'PREVIEW_ONLY'))}</div>
      <details class='wv2-detail'><summary>詳細</summary><div class='wv2-detail-overlay'>{detail}</div></details>
    </div>
    """


def warroom_v2_prediction_matrix_html(models: list[dict[str, Any]]) -> str:
    rows: list[str] = []
    for model in models:
        title = _text(model.get("title") or model.get("widget_id"))
        cards = "".join(_card_html(model, dict(card)) for card in list(model.get("payload", {}).get("horizon_cards") or []))
        rows.append(f"<section class='wv2-row'><h3>{title}</h3><div class='wv2-strip'>{cards}</div></section>")
    return f"""
<style>
.wv2-matrix {{ display: flex; flex-direction: column; gap: 14px; }}
.wv2-row h3 {{ margin: 0 0 6px 0; font-size: 1.0rem; color: #101828; }}
.wv2-strip {{ display: flex; gap: 12px; overflow-x: auto; padding: 2px 2px 10px 2px; scroll-snap-type: x proximity; }}
.wv2-card {{ position: relative; flex: 0 0 {WARROOM_V2_MATRIX_CARD_WIDTH_PX}px; min-width: {WARROOM_V2_MATRIX_CARD_WIDTH_PX}px; min-height: {WARROOM_V2_MATRIX_CARD_MIN_HEIGHT_PX}px; border-radius: 16px; padding: 10px 10px 9px 10px; color: #101828; scroll-snap-align: start; box-sizing: border-box; }}
{warroom_v2_card_visual_semantics_css()}
.wv2-card-top {{ display: flex; justify-content: space-between; align-items: center; font-size: .92rem; font-weight: 800; }}
.wv2-badge {{ min-width: 42px; padding: 3px 8px; border-radius: 999px; border: 1px solid rgba(16,24,40,.22); background: rgba(255,255,255,.82); text-align: center; font-size: .78rem; font-weight: 900; }}
.wv2-primary {{ margin-top: 8px; font-size: 1.14rem; font-weight: 850; }}
.wv2-score {{ margin-top: 10px; font-size: 1.60rem; font-weight: 900; }}
.wv2-tag {{ font-size: 1.04rem; font-weight: 800; }}
.wv2-detail summary {{ display: inline-block; margin-top: 8px; padding: 2px 8px; border: 1px solid rgba(16,24,40,.18); border-radius: 999px; background: #fff; font-size: .78rem; font-weight: 850; cursor: pointer; }}
.wv2-detail-overlay {{ position: absolute; z-index: 5; left: 8px; right: 8px; top: 8px; min-height: calc(100% - 16px); padding: 28px 10px 10px 10px; border-radius: 14px; background: #F2F4F7; border: 1px solid rgba(16,24,40,.18); box-shadow: 0 10px 24px rgba(16,24,40,.16); font-size: .82rem; }}
.wv2-detail:not([open]) .wv2-detail-overlay {{ display: none; }}
.wv2-detail-section ul {{ margin: 4px 0 8px 18px; padding: 0; }}
</style>
<div class='wv2-matrix'>{''.join(rows)}</div>
"""


def build_warroom_v2_prediction_matrix_renderer_packet(models: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_PREDICTION_CARDS_RENDERER_VERSION,
        "html_matrix_renderer": True,
        "streamlit_columns_used": False,
        "cards_do_not_shrink": True,
        "horizontal_scroll_required": True,
        "card_width_px": WARROOM_V2_MATRIX_CARD_WIDTH_PX,
        "card_shape": "horizontal_rectangle",
        "visual_semantics_from_payload": True,
        "background_color_never_encodes_freshness": True,
        "freshness_encoded_by_badge_only": True,
        "freshness_not_encoded_by_border": True,
        "border_meaning": "evidence_quality",
        "detail_disclosure_mode": "card_overlay",
        "runtime_connected": False,
        "push_connected": False,
        "would_send_to_broker": False,
        "row_count": len(models),
    }


def render_warroom_v2_prediction_cards(models: list[dict[str, Any]]) -> None:
    st.subheader("Prediction cards")
    st.markdown(warroom_v2_prediction_matrix_html(models), unsafe_allow_html=True)
