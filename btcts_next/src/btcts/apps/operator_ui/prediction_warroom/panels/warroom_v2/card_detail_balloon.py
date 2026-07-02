# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/card_detail_balloon.py
# desc: WarRoom v2 prediction-card detail balloon placeholder renderer. Display-only; no live data ownership.

from __future__ import annotations

from typing import Any

import streamlit as st

WARROOM_V2_CARD_DETAIL_BALLOON_RENDERER_VERSION = "prediction_warroom.v2.card_detail_balloon_renderer.ps_q29e.v1"

_DETAIL_FIELDS = (
    ("detail_lines", "理由"),
    ("source_lines", "参照"),
    ("warning_lines", "警告"),
    ("invalidation_lines", "無効化条件"),
)


def build_warroom_v2_card_detail_balloon_packet(model: dict[str, Any]) -> dict[str, Any]:
    payload = dict(model.get("payload", {}))
    sections = [
        {
            "field": field,
            "label": label,
            "lines": list(payload.get(field) or []),
        }
        for field, label in _DETAIL_FIELDS
    ]
    return {
        "ok": True,
        "detail_balloon_version": WARROOM_V2_CARD_DETAIL_BALLOON_RENDERER_VERSION,
        "widget_id": str(model.get("widget_id", "")),
        "topic": str(model.get("topic", "")),
        "title": str(model.get("title", "")),
        "placeholder_only": bool(payload.get("placeholder_only", True)),
        "runtime_connected": False,
        "push_connected": False,
        "display_only": True,
        "sections": sections,
    }


def render_warroom_v2_card_detail_balloon(model: dict[str, Any]) -> dict[str, Any]:
    packet = build_warroom_v2_card_detail_balloon_packet(model)
    with st.expander("詳細", expanded=False):
        st.caption("placeholder detail balloon / display-only")
        for section in packet["sections"]:
            st.markdown(f"**{section['label']}**")
            lines = section["lines"] or ["未接続のため未評価です。"]
            for line in lines:
                st.write(line)
        st.json({
            "topic": packet["topic"],
            "runtime_connected": packet["runtime_connected"],
            "push_connected": packet["push_connected"],
        })
    return packet
