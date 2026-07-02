# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py
# desc: Thin orchestrator for WarRoom v2 shell preview renderers. Display-only; no live data or push transport.

from __future__ import annotations

from typing import Any

import streamlit as st

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2 import (
    render_warroom_v2_debug_preview,
    render_warroom_v2_prediction_cards,
    render_warroom_v2_scenario_area,
    render_warroom_v2_top_bar,
    warroom_v2_models_by_zone,
)
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_shell_preview_packet

WARROOM_V2_SHELL_PREVIEW_PANEL_VERSION = "prediction_warroom.v2.shell_preview_panel.ps_q29d.v1"


def build_warroom_v2_shell_preview_panel_packet(*, page_mount_packet: dict | None = None) -> dict[str, Any]:
    shell = build_warroom_v2_shell_preview_packet()
    page = dict(page_mount_packet or {})
    return {
        "ok": True,
        "panel_version": WARROOM_V2_SHELL_PREVIEW_PANEL_VERSION,
        "page_mount_packet": page,
        "shell_preview": shell,
        "display_only": True,
        "renderer_split": True,
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "dhot_read_in_panel": False,
        "classifier_invoked_in_panel": False,
        "would_send_to_broker": False,
    }


def render_warroom_v2_shell_preview_panel(*, page_mount_packet: dict | None = None) -> dict[str, Any]:
    packet = build_warroom_v2_shell_preview_panel_packet(page_mount_packet=page_mount_packet)
    shell = packet["shell_preview"]
    st.caption("WarRoom v2 shell preview / contract-only")
    render_warroom_v2_top_bar(warroom_v2_models_by_zone(shell, "top"))
    st.divider()
    render_warroom_v2_prediction_cards(warroom_v2_models_by_zone(shell, "prediction_cards"))
    st.divider()
    render_warroom_v2_scenario_area(warroom_v2_models_by_zone(shell, "scenario"))
    render_warroom_v2_debug_preview(packet, shell)
    return packet
