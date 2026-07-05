# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py
# desc: WarRoom v2 live observation page. Orchestrates RT0-RT6 runtime and delegates visual rendering to small rt_ui modules.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

import streamlit as st

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.rt_live_receiver_bridge import (
    WARROOM_RT_LIVE_ENDPOINT_STATE_KEY,
    WARROOM_RT_LIVE_RECEIVER_BRIDGE_SESSION_STATE_KEY,
    WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY,
    apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state,
    ensure_warroom_push_widget_live_observation_runtime,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp9_warroom_page_mount import (
    WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY,
    build_wp9_warroom_page_mount_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp11_top_layout_push_widget_polish import (
    WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY,
    build_wp11_top_layout_push_widget_polish_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp12_bottom_chart_layout import (
    WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY,
    build_wp12_bottom_chart_layout_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp13_prediction_card_connection import (
    WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY,
    build_wp13_prediction_card_connection_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.chart_view import render_rt_bottom_chart_graph
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.debug_view import render_rt_debug_packets
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.prediction_cards_view import render_rt_prediction_cards
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.runtime_env import endpoint_from_env, runtime_config_from_env
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.status_view import render_rt_runtime_status
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.top_widgets_view import render_rt_top_layout_and_widgets

WARROOM_V2_RT_VISIBLE_MOUNT_VERSION = "prediction_warroom.v2.rt_visible_mount.2026_07_05.v2"


def _packet(key: str, fallback_builder: Any) -> dict[str, Any]:
    value = st.session_state.get(key)
    if isinstance(value, dict):
        return value
    packet = fallback_builder()
    st.session_state[key] = packet
    return packet


def _refresh_warroom_v2_rt_live_observation() -> tuple[dict[str, Any], dict[str, Any]]:
    endpoint = endpoint_from_env()
    if endpoint and WARROOM_RT_LIVE_ENDPOINT_STATE_KEY not in st.session_state:
        st.session_state[WARROOM_RT_LIVE_ENDPOINT_STATE_KEY] = endpoint
    runtime_status = ensure_warroom_push_widget_live_observation_runtime(
        st.session_state,
        runtime_config=runtime_config_from_env(),
        runtime_key="warroom_v2_visible_mount",
    )
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    bridge_packet = apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state(st.session_state, now_ms=now_ms)
    st.session_state[WARROOM_RT_LIVE_RECEIVER_BRIDGE_SESSION_STATE_KEY] = bridge_packet
    return runtime_status, bridge_packet


def build_warroom_v2_page_mount_packet(*, runtime_status: Mapping[str, Any] | None = None, bridge_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    runtime = dict(runtime_status or {})
    bridge = dict(bridge_packet or {})
    receiver_started = bool(runtime.get("receiver_runtime_started"))
    socket_opened = bool(runtime.get("socket_opened") or runtime.get("websocket_opened"))
    receive_loop_started = bool(runtime.get("receive_loop_started"))
    messages_applied = int(bridge.get("messages_applied") or 0)
    return {
        "ok": True,
        "page_mount_version": WARROOM_V2_RT_VISIBLE_MOUNT_VERSION,
        "page_key": "warroom_v2",
        "page_label": "WarRoom v2",
        "thin_page_shell_only": False,
        "rt_visible_mount_ready": True,
        "rt_ui_polish1_modularized": True,
        "renders_rt_live_observation_runtime": True,
        "warroom_page_starts_receiver_runtime_when_endpoint_present": True,
        "warroom_page_uses_live_packet_when_present": True,
        "runtime_connected": bool(receiver_started),
        "push_connected": bool(socket_opened or receive_loop_started or messages_applied > 0),
        "websocket_enabled": bool(socket_opened or receive_loop_started),
        "receive_loop_started": receive_loop_started,
        "messages_applied": messages_applied,
        "live_widget_count": int(dict(st.session_state.get(WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY) or {}).get("live_widget_count") or 0),
        "dhot_read_in_page": False,
        "classifier_invoked_in_page": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "would_send_to_broker": False,
        "websocket_send_enabled": False,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def render() -> None:
    runtime_status, bridge_packet = _refresh_warroom_v2_rt_live_observation()
    page_packet = build_warroom_v2_page_mount_packet(runtime_status=runtime_status, bridge_packet=bridge_packet)
    st.header("WarRoom v2 / Realtime Observation")
    st.caption("RT0-RT6 live observation runtime / receive-only WebSocket / modular top-chart-card UI / no send / no broker / no order")
    st.session_state[WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY] = runtime_status
    render_rt_runtime_status(runtime_status, bridge_packet, st)

    top_packet = _packet(WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY, build_wp11_top_layout_push_widget_polish_packet)
    widgets_packet = _packet(WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY, build_wp9_warroom_page_mount_packet)
    chart_packet = _packet(WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY, build_wp12_bottom_chart_layout_packet)
    cards_packet = _packet(WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY, build_wp13_prediction_card_connection_packet)

    st.divider()
    st.subheader("Top layout / realtime push widgets")
    render_rt_top_layout_and_widgets(top_packet, widgets_packet, st)

    st.divider()
    st.subheader("Bottom chart / realtime context")
    render_rt_bottom_chart_graph(chart_packet, st)

    st.divider()
    st.subheader("Prediction cards / realtime market context")
    render_rt_prediction_cards(cards_packet, st)

    render_rt_debug_packets(
        {
            "page_mount": page_packet,
            "runtime_status": runtime_status,
            "bridge_packet": bridge_packet,
        },
        st,
    )
    st.caption(
        "rt_visible_mount_ready=true / rt_ui_polish1_modularized=true / "
        f"runtime_connected={str(page_packet['runtime_connected']).lower()} / "
        f"push_connected={str(page_packet['push_connected']).lower()} / "
        "websocket_send_enabled=false / broker_send_enabled=false / order_intent_submitted=false / prediction_invoked=false / classifier_invoked=false"
    )
