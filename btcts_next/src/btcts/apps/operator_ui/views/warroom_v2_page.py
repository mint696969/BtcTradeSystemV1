# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py
# desc: WarRoom v2 live observation page. Mounts RT0-RT6 push-widget runtime, live widgets, bottom chart, and prediction-card context read-only.

from __future__ import annotations

from datetime import datetime, timezone
import os
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
    render_wp9_push_widget_mount,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp11_top_layout_push_widget_polish import (
    WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY,
    build_wp11_top_layout_push_widget_polish_packet,
    render_wp11_top_layout_polish,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp12_bottom_chart_layout import (
    WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY,
    build_wp12_bottom_chart_layout_packet,
    render_wp12_bottom_chart_layout,
)
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp13_prediction_card_connection import (
    WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY,
    build_wp13_prediction_card_connection_packet,
    render_wp13_prediction_card_connection,
)

WARROOM_V2_RT_VISIBLE_MOUNT_VERSION = "prediction_warroom.v2.rt_visible_mount.2026_07_05.v1"


def _bool_env(name: str, default: str = "true") -> bool:
    return str(os.environ.get(name, default)).strip().lower() not in {"0", "false", "no", "off"}


def _runtime_config_from_env() -> dict[str, Any]:
    return {
        "source": os.environ.get("WARROOM_PUSH_WIDGET_SOURCE", "bitflyer_collector_provider"),
        "symbol": os.environ.get("BTCTS_SYMBOL", "FX_BTC_JPY"),
        "ssl_verify": str(_bool_env("BTCTS_WS_SSL_VERIFY", "true")).lower(),
        "ca_file": os.environ.get("BTCTS_WS_CA_FILE", ""),
        "recv_timeout_sec": float(os.environ.get("WARROOM_PUSH_WIDGET_RECV_TIMEOUT_SEC", "60")),
    }


def _packet(key: str, fallback_builder: Any) -> dict[str, Any]:
    value = st.session_state.get(key)
    if isinstance(value, dict):
        return value
    packet = fallback_builder()
    st.session_state[key] = packet
    return packet


def _refresh_warroom_v2_rt_live_observation() -> tuple[dict[str, Any], dict[str, Any]]:
    endpoint = str(os.environ.get("WARROOM_PUSH_WIDGET_WS_URL") or "")
    if endpoint and WARROOM_RT_LIVE_ENDPOINT_STATE_KEY not in st.session_state:
        st.session_state[WARROOM_RT_LIVE_ENDPOINT_STATE_KEY] = endpoint
    runtime_status = ensure_warroom_push_widget_live_observation_runtime(
        st.session_state,
        runtime_config=_runtime_config_from_env(),
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


def _render_runtime_status(runtime_status: Mapping[str, Any], bridge_packet: Mapping[str, Any]) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Runtime", "connected" if runtime_status.get("receiver_runtime_started") else "waiting")
    c2.metric("Push", "receiving" if runtime_status.get("receive_loop_started") or bridge_packet.get("messages_applied") else "waiting")
    c3.metric("Drained", int(runtime_status.get("drained_message_count") or 0))
    c4.metric("Applied", int(bridge_packet.get("messages_applied") or 0))
    endpoint_label = "<provided>" if runtime_status.get("endpoint_url_present") else "not configured"
    st.caption(
        " / ".join(
            [
                f"endpoint={endpoint_label}",
                f"receiver_runtime_started={bool(runtime_status.get('receiver_runtime_started'))}",
                f"socket_opened={bool(runtime_status.get('socket_opened'))}",
                f"receive_loop_started={bool(runtime_status.get('receive_loop_started'))}",
                f"websocket_send_enabled=false",
                f"broker_send_enabled=false",
            ]
        )
    )
    error = runtime_status.get("receiver_error")
    if isinstance(error, Mapping) and error:
        st.warning(f"receiver_error={error.get('error_type')}: {error.get('error_message')}")


def render() -> None:
    runtime_status, bridge_packet = _refresh_warroom_v2_rt_live_observation()
    page_packet = build_warroom_v2_page_mount_packet(runtime_status=runtime_status, bridge_packet=bridge_packet)
    st.header("WarRoom v2 / Realtime Observation")
    st.caption("RT0-RT6 live observation runtime / receive-only WebSocket / per-widget realtime updates / no send / no broker / no order")
    st.session_state[WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY] = runtime_status
    _render_runtime_status(runtime_status, bridge_packet)

    st.divider()
    st.subheader("Top layout / realtime push widgets")
    render_wp11_top_layout_polish(_packet(WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY, build_wp11_top_layout_push_widget_polish_packet), st)
    render_wp9_push_widget_mount(_packet(WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY, build_wp9_warroom_page_mount_packet), st)

    st.divider()
    st.subheader("Bottom chart / realtime context")
    render_wp12_bottom_chart_layout(_packet(WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY, build_wp12_bottom_chart_layout_packet), st)

    st.divider()
    st.subheader("Prediction cards / realtime market context")
    render_wp13_prediction_card_connection(_packet(WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY, build_wp13_prediction_card_connection_packet), st)

    st.caption(
        "rt_visible_mount_ready=true / "
        f"runtime_connected={str(page_packet['runtime_connected']).lower()} / "
        f"push_connected={str(page_packet['push_connected']).lower()} / "
        "websocket_send_enabled=false / broker_send_enabled=false / order_intent_submitted=false / prediction_invoked=false / classifier_invoked=false"
    )
