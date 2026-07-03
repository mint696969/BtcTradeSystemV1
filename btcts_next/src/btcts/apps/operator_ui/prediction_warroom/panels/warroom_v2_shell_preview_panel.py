# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py
# desc: Thin orchestrator for WarRoom v2 shell preview renderers. Display-only; fragment refresh; no push transport.

from __future__ import annotations

from typing import Any

import streamlit as st

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2 import (
    build_warroom_v2_auto_refresh_control_packet,
    build_warroom_v2_chart_review_panel_packet,
    build_warroom_v2_market_snapshot_strip_packet,
    build_warroom_v2_panel_event_bridge_packet,
    render_warroom_v2_auto_refresh_control,
    render_warroom_v2_chart_review_panel,
    render_warroom_v2_debug_preview,
    render_warroom_v2_fragment_refresh_block,
    render_warroom_v2_market_snapshot_strip,
    render_warroom_v2_prediction_cards,
    render_warroom_v2_scenario_area,
    render_warroom_v2_top_bar,
    warroom_v2_models_by_zone,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_shell_preview_packet

WARROOM_V2_SHELL_PREVIEW_PANEL_VERSION = "prediction_warroom.v2.shell_preview_panel.ps_q30e.v1"


def _placeholder_source() -> dict[str, Any]:
    return {"data_connected": False, "runtime_connected": False, "push_connected": False, "read_only": True, "display_only": True, "would_send_to_broker": False}


def build_warroom_v2_shell_preview_panel_packet(*, page_mount_packet: dict | None = None, source_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    shell = build_warroom_v2_shell_preview_packet()
    source = dict(source_packet or _placeholder_source())
    refresh = build_warroom_v2_auto_refresh_control_packet()
    market_snapshot = build_warroom_v2_market_snapshot_strip_packet(source_packet=source)
    chart_review = build_warroom_v2_chart_review_panel_packet(source_packet=source)
    event_bridge = build_warroom_v2_panel_event_bridge_packet(market_snapshot_packet=market_snapshot, chart_review_packet=chart_review)
    return {"ok": True, "panel_version": WARROOM_V2_SHELL_PREVIEW_PANEL_VERSION, "page_mount_packet": dict(page_mount_packet or {}), "shell_preview": shell, "auto_refresh_control": refresh, "market_snapshot_source": source, "market_snapshot_strip": market_snapshot, "chart_review_panel": chart_review, "read_model_event_bridge": event_bridge, "panel_packet_event_bridge_bound": True, "fragment_refresh_enabled": False, "page_reload_enabled": False, "auto_refresh_control_below_top_bar": True, "market_snapshot_strip_above_prediction_cards": True, "chart_review_panel_bottom": True, "display_only": True, "renderer_split": True, "push_ready": True, "auto_refresh_ready": True, "data_connected": bool(source.get("data_connected")), "runtime_connected": False, "push_connected": False, "websocket_enabled": False, "sse_enabled": False, "dhot_read_in_panel": bool(source.get("data_connected")), "classifier_invoked_in_panel": False, "would_send_to_broker": False}


def render_warroom_v2_shell_preview_panel(*, page_mount_packet: dict | None = None) -> dict[str, Any]:
    source = build_warroom_v2_market_snapshot_dhot_read_model()
    packet = build_warroom_v2_shell_preview_panel_packet(page_mount_packet=page_mount_packet, source_packet=source)
    shell = packet["shell_preview"]
    st.caption("WarRoom v2 shell preview / Streamlit fragment refresh / no page reload")
    render_warroom_v2_top_bar(warroom_v2_models_by_zone(shell, "top"))
    packet["auto_refresh_control"] = render_warroom_v2_auto_refresh_control()

    def _render_snapshot() -> None:
        source = build_warroom_v2_market_snapshot_dhot_read_model()
        render_warroom_v2_market_snapshot_strip(source_packet=source)

    st.divider()
    render_warroom_v2_fragment_refresh_block(label="market_snapshot_strip", refresh_packet=packet["auto_refresh_control"], render_body=_render_snapshot)
    st.divider()
    render_warroom_v2_prediction_cards(warroom_v2_models_by_zone(shell, "prediction_cards"))
    st.divider()
    render_warroom_v2_scenario_area(warroom_v2_models_by_zone(shell, "scenario"))
    render_warroom_v2_debug_preview(packet, shell)

    def _render_chart() -> None:
        source = build_warroom_v2_market_snapshot_dhot_read_model()
        render_warroom_v2_chart_review_panel(source_packet=source)

    st.divider()
    render_warroom_v2_fragment_refresh_block(label="chart_review_panel", refresh_packet=packet["auto_refresh_control"], render_body=_render_chart)
    return packet
