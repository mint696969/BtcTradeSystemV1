# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/card_detail_overlay_html.py
# desc: WarRoom v2 row-level detail overlay HTML helpers. Display-only; no live data ownership.

from __future__ import annotations

from html import escape
from typing import Any

from .card_detail_balloon import build_warroom_v2_card_detail_balloon_packet

WARROOM_V2_CARD_DETAIL_OVERLAY_HTML_VERSION = "prediction_warroom.v2.card_detail_overlay_html.ps_q29p.v2"


def _text(value: Any) -> str:
    return escape("" if value is None else str(value))


def warroom_v2_detail_overlay_inner_html(model: dict[str, Any]) -> str:
    packet = build_warroom_v2_card_detail_balloon_packet(model)
    sections: list[str] = []
    for section in packet["sections"]:
        lines = section["lines"] or ["未接続のため未評価です。"]
        items = "".join(f"<li>{_text(line)}</li>" for line in lines[:4])
        sections.append(f"<section class='wv2-detail-section'><b>{_text(section['label'])}</b><ul>{items}</ul></section>")
    return "".join(sections)


def warroom_v2_detail_button_html(toggle_id: str) -> str:
    return f"<label class='wv2-detail-button' for='{_text(toggle_id)}'>詳細</label>"


def warroom_v2_detail_overlay_panel_html(model: dict[str, Any], *, panel_id: str, close_id: str) -> str:
    title = _text(model.get("title") or model.get("widget_id") or "詳細")
    return "".join([
        f"<div id='{_text(panel_id)}' class='wv2-row-detail-layer'>",
        f"<label class='wv2-detail-backdrop' for='{_text(close_id)}' aria-label='詳細外側をクリックして閉じる'></label>",
        f"<article class='wv2-row-detail-panel' role='dialog' aria-label='{title} 詳細'>",
        "<div class='wv2-detail-head'>",
        f"<strong>{title} 詳細</strong>",
        f"<label class='wv2-detail-close' for='{_text(close_id)}' aria-label='詳細を閉じる'>×</label>",
        "</div>",
        "<div class='wv2-detail-body'>",
        warroom_v2_detail_overlay_inner_html(model),
        "</div><div class='wv2-detail-footer'>row-level overlay / display-only</div></article></div>",
    ])



def warroom_v2_detail_overlay_html(model: dict[str, Any]) -> str:
    # Compatibility wrapper for older Q29M/Q29O guards. Q29P no longer uses
    # card-internal details/summary expansion; this returns a row-level panel.
    return warroom_v2_detail_overlay_panel_html(model, panel_id="wv2_detail_panel_preview", close_id="wv2_detail_none_preview")

def warroom_v2_detail_overlay_css() -> str:
    return """
.wv2-detail-button { display: inline-block; margin-top: 8px; padding: 2px 8px; border: 1px solid rgba(16,24,40,.18); border-radius: 999px; background: #fff; font-size: .78rem; font-weight: 850; cursor: pointer; }
.wv2-detail-toggle { position: absolute; opacity: 0; pointer-events: none; }
.wv2-row { position: relative; }
.wv2-row-detail-layer { display: none; }
.wv2-detail-backdrop { position: fixed; inset: 0; z-index: 29; cursor: default; background: rgba(255,255,255,0); }
.wv2-row-detail-panel { position: absolute; z-index: 30; top: 30px; left: 0; width: min(960px, calc(100vw - 56px)); max-height: 260px; overflow-y: auto; scrollbar-gutter: stable; box-sizing: border-box; padding: 12px 14px 14px 14px; border-radius: 14px; background: #F2F4F7; border: 1px solid rgba(16,24,40,.20); box-shadow: 0 18px 40px rgba(16,24,40,.22); font-size: .92rem; line-height: 1.45; }
.wv2-detail-body { padding-bottom: 10px; }
.wv2-detail-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 6px; color: #101828; }
.wv2-detail-close { display: inline-flex; width: 24px; height: 24px; border-radius: 999px; align-items: center; justify-content: center; background: #fff; border: 1px solid rgba(16,24,40,.22); cursor: pointer; font-weight: 900; }
.wv2-detail-section ul { margin: 4px 0 8px 20px; padding: 0; }
.wv2-detail-footer { margin-top: 6px; color: #667085; font-size: .78rem; }
""".strip()


def build_warroom_v2_detail_overlay_renderer_packet(model: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "detail_overlay_html_version": WARROOM_V2_CARD_DETAIL_OVERLAY_HTML_VERSION,
        "detail_disclosure_mode": "row_level_overlay_panel",
        "summary_button_label": "詳細",
        "close_button_label": "×",
        "close_button_required": True,
        "outside_click_close_enabled": True,
        "backdrop_close_layer": True,
        "card_width_constrained": False,
        "row_level_overlay": True,
        "layout_pushdown_avoided": True,
        "aria_labels_present": True,
        "overlay_max_height_px": 260,
        "display_only": True,
        "runtime_connected": False,
        "push_connected": False,
        "would_send_to_broker": False,
    }
