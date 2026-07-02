# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/scenario_area.py
# desc: WarRoom v2 Japanese scenario-area renderer. Placeholder-only; display-safe.

from __future__ import annotations

from typing import Any

import streamlit as st

WARROOM_V2_SCENARIO_AREA_RENDERER_VERSION = "prediction_warroom.v2.scenario_area_renderer.ps_q29h.v1"


def build_warroom_v2_scenario_area_renderer_packet(models: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_SCENARIO_AREA_RENDERER_VERSION,
        "scenario_area_below_cards": True,
        "display_only": True,
        "placeholder_only": True,
        "runtime_connected": False,
        "push_connected": False,
        "would_send_to_broker": False,
        "model_count": len(models),
    }


def render_warroom_v2_scenario_area(models: list[dict[str, Any]]) -> dict[str, Any]:
    packet = build_warroom_v2_scenario_area_renderer_packet(models)
    for model in models:
        payload = model.get("payload", {})
        with st.container(border=True):
            st.subheader(str(model.get("title") or "日本語シナリオ"))
            st.caption("placeholder scenario composition / display-only")
            for line in payload.get("scenario_lines", []):
                st.write(line)
            watch_points = list(payload.get("watch_points") or [])
            if watch_points:
                st.markdown("**見るポイント**")
                for line in watch_points:
                    st.write(f"- {line}")
            invalidation_lines = list(payload.get("invalidation_lines") or [])
            if invalidation_lines:
                st.markdown("**無効化条件**")
                for line in invalidation_lines:
                    st.write(f"- {line}")
    return packet
