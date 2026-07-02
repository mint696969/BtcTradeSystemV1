# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/card_detail_overlay_html.py
# desc: WarRoom v2 card detail overlay HTML helpers. Display-only; no live data ownership.

from __future__ import annotations

from html import escape
from typing import Any

from .card_detail_balloon import build_warroom_v2_card_detail_balloon_packet

WARROOM_V2_CARD_DETAIL_OVERLAY_HTML_VERSION = "prediction_warroom.v2.card_detail_overlay_html.ps_q29m.v1"


def _text(value: Any) -> str:
    return escape("" if value is None else str(value))


def warroom_v2_detail_overlay_inner_html(model: dict[str, Any]) -> str:
    packet = build_warroom_v2_card_detail_balloon_packet(model)
    sections: list[str] = []
    for section in packet["sections"]:
        lines = section["lines"] or ["未接続のため未評価です。"]
        items = "".join(f"<li>{_text(line)}</li>" for line in lines[:3])
        sections.append(f"<div class='wv2-detail-section'><b>{_text(section['label'])}</b><ul>{items}</ul></div>")
    return "".join(sections)


def warroom_v2_detail_overlay_html(model: dict[str, Any]) -> str:
    return "".join([
        "<details class='wv2-detail'>",
        "<summary class='wv2-detail-button' aria-label='カード詳細を開く'>詳細</summary>",
        "<div class='wv2-detail-overlay' role='dialog' aria-label='カード詳細'>",
        "<div class='wv2-detail-header'>Placeholder detail</div>",
        warroom_v2_detail_overlay_inner_html(model),
        "<div class='wv2-detail-footer'>クリックで開閉 / display-only</div>",
        "</div></details>",
    ])


def warroom_v2_detail_overlay_css() -> str:
    return """
.wv2-detail-button { display: inline-block; margin-top: 8px; padding: 2px 8px; border: 1px solid rgba(16,24,40,.18); border-radius: 999px; background: #fff; font-size: .78rem; font-weight: 850; cursor: pointer; }
.wv2-detail-overlay { position: absolute; z-index: 5; left: 8px; right: 8px; top: 8px; min-height: calc(100% - 16px); max-height: 230px; overflow-y: auto; padding: 28px 10px 10px 10px; border-radius: 14px; background: #F2F4F7; border: 1px solid rgba(16,24,40,.18); box-shadow: 0 10px 24px rgba(16,24,40,.16); font-size: .82rem; }
.wv2-detail:not([open]) .wv2-detail-overlay { display: none; }
.wv2-detail-header { position: absolute; top: 8px; left: 10px; right: 10px; font-weight: 900; font-size: .78rem; color: #475467; }
.wv2-detail-section ul { margin: 4px 0 8px 18px; padding: 0; }
.wv2-detail-footer { margin-top: 6px; color: #667085; font-size: .74rem; }
""".strip()


def build_warroom_v2_detail_overlay_renderer_packet(model: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "detail_overlay_html_version": WARROOM_V2_CARD_DETAIL_OVERLAY_HTML_VERSION,
        "detail_disclosure_mode": "card_overlay",
        "summary_button_label": "詳細",
        "aria_labels_present": True,
        "overlay_max_height_px": 230,
        "display_only": True,
        "runtime_connected": False,
        "push_connected": False,
        "would_send_to_broker": False,
    }
