# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py
# desc: Streamlit renderer for the WarRoom v2 shell preview packet. Display-only; no live data or push transport.

from __future__ import annotations

from typing import Any

import streamlit as st

from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_shell_preview_packet

WARROOM_V2_SHELL_PREVIEW_PANEL_VERSION = "prediction_warroom.v2.shell_preview_panel.ps_q29c.v1"


def build_warroom_v2_shell_preview_panel_packet(*, page_mount_packet: dict | None = None) -> dict[str, Any]:
    shell = build_warroom_v2_shell_preview_packet()
    page = dict(page_mount_packet or {})
    return {
        "ok": True,
        "panel_version": WARROOM_V2_SHELL_PREVIEW_PANEL_VERSION,
        "page_mount_packet": page,
        "shell_preview": shell,
        "display_only": True,
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "dhot_read_in_panel": False,
        "classifier_invoked_in_panel": False,
        "would_send_to_broker": False,
    }


def _models_by_zone(shell: dict[str, Any], zone: str) -> list[dict[str, Any]]:
    models = shell["placeholder_read_models"]["read_models"]
    return [model for model in models if model.get("payload", {}).get("zone") == zone]


def _render_top_widgets(models: list[dict[str, Any]]) -> None:
    cols = st.columns(max(1, len(models)))
    for col, model in zip(cols, models):
        with col:
            st.metric(model["title"], model["payload"].get("state_label", "未接続"))
            st.caption(model["topic"])


def _render_prediction_cards(models: list[dict[str, Any]]) -> None:
    rows = [models[i : i + 4] for i in range(0, len(models), 4)]
    for row in rows:
        cols = st.columns(len(row))
        for col, model in zip(cols, row):
            payload = model["payload"]
            with col:
                with st.container(border=True):
                    st.subheader(model["title"])
                    st.metric(payload.get("state_label", "未接続"), payload.get("confidence_label", "--"))
                    st.caption(f"{payload.get('freshness_badge', 'NO_DATA')} / {payload.get('short_tag', 'PREVIEW_ONLY')}")
                    with st.expander("詳細", expanded=False):
                        st.write("placeholder only")
                        st.json({
                            "topic": model["topic"],
                            "runtime_connected": payload.get("runtime_connected"),
                            "push_connected": payload.get("push_connected"),
                        })


def _render_scenario(models: list[dict[str, Any]]) -> None:
    for model in models:
        with st.container(border=True):
            st.subheader(model["title"])
            for line in model["payload"].get("scenario_lines", []):
                st.write(line)


def render_warroom_v2_shell_preview_panel(*, page_mount_packet: dict | None = None) -> dict[str, Any]:
    packet = build_warroom_v2_shell_preview_panel_packet(page_mount_packet=page_mount_packet)
    shell = packet["shell_preview"]
    st.caption("WarRoom v2 shell preview / contract-only")
    _render_top_widgets(_models_by_zone(shell, "top"))
    st.divider()
    st.subheader("Prediction cards")
    _render_prediction_cards(_models_by_zone(shell, "prediction_cards"))
    st.divider()
    _render_scenario(_models_by_zone(shell, "scenario"))
    with st.expander("Debug / raw preview packet", expanded=False):
        st.json({
            "panel_version": packet["panel_version"],
            "shell_preview_version": shell["shell_preview_version"],
            "widget_update_unit": shell["widget_update_unit"],
            "runtime_connected": shell["runtime_connected"],
            "push_connected": shell["push_connected"],
        })
    return packet
