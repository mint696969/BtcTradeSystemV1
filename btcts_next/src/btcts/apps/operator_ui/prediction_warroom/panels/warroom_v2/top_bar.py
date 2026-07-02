# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/top_bar.py
# desc: WarRoom v2 top-zone renderer. Display-only placeholder status widgets.

from __future__ import annotations

from typing import Any

import streamlit as st

WARROOM_V2_TOP_BAR_RENDERER_VERSION = "prediction_warroom.v2.top_bar_renderer.ps_q29j.v1"


def build_warroom_v2_top_bar_renderer_packet(models: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_TOP_BAR_RENDERER_VERSION,
        "top_bar_placeholder_status_polish": True,
        "display_only": True,
        "placeholder_only": True,
        "runtime_connected": False,
        "push_connected": False,
        "would_send_to_broker": False,
        "model_count": len(models),
        "widget_ids": [str(model.get("widget_id", "")) for model in models],
    }


def render_warroom_v2_top_bar(models: list[dict[str, Any]]) -> dict[str, Any]:
    packet = build_warroom_v2_top_bar_renderer_packet(models)
    cols = st.columns(max(1, len(models)))
    for col, model in zip(cols, models):
        payload = model.get("payload", {})
        with col:
            st.metric(str(model.get("title") or model.get("widget_id")), payload.get("state_label", "未接続"))
            st.caption(str(payload.get("status_badge", "NO_DATA")))
            st.write(str(payload.get("status_summary", "placeholder / display-only")))
            lines = list(payload.get("status_lines") or [])
            for line in lines[:3]:
                st.caption(str(line))
    return packet
