# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py
# desc: WarRoom v2 live observation page. Static shell plus fragment-refreshed cockpit body.

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
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.auto_refresh_tick_view import build_cockpit_auto_refresh_packet, fragment_run_every, render_cockpit_auto_refresh_tick
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.chart_view import render_rt_bottom_chart_graph
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.copy_packet_view import build_gpt_copy_packet, render_gpt_copy_packet
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.debug_view import render_rt_debug_packets
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.inference_guidance_view import build_inference_guidance_packet, render_inference_guidance
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.live_packets import select_or_build_rt_display_packets
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_strip_view import build_market_strip_packet, render_market_strip
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.prediction_cards_view import render_rt_prediction_cards
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.runtime_env import endpoint_from_env, runtime_config_from_env
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.status_view import render_rt_runtime_status
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.top_widgets_view import render_rt_top_layout_and_widgets
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.trade_strip_view import build_trade_strip_packet, render_trade_strip

WARROOM_V2_RT_VISIBLE_MOUNT_VERSION = "prediction_warroom.v2.rt_visible_mount.2026_07_05.v5"


def _apply_runtime_endpoint_to_session_state(session_state: Any, endpoint: str) -> bool:
    if not endpoint:
        return False
    previous = session_state.get(WARROOM_RT_LIVE_ENDPOINT_STATE_KEY)
    if previous == endpoint:
        return False
    session_state[WARROOM_RT_LIVE_ENDPOINT_STATE_KEY] = endpoint
    for key in (
        "warroom_v2_rt_display_packet_source",
        "warroom_v2_rt_retained_wp9_page_mount_packet",
        "warroom_v2_rt_retained_wp11_top_layout_packet",
        "warroom_v2_rt_retained_wp12_bottom_chart_packet",
        "warroom_v2_rt_retained_wp13_prediction_card_packet",
    ):
        session_state.pop(key, None)
    return True


def _refresh_warroom_v2_rt_live_observation() -> tuple[dict[str, Any], dict[str, Any]]:
    endpoint = endpoint_from_env()
    _apply_runtime_endpoint_to_session_state(st.session_state, endpoint)
    runtime_status = ensure_warroom_push_widget_live_observation_runtime(
        st.session_state,
        runtime_config=runtime_config_from_env(),
        runtime_key="warroom_v2_visible_mount",
    )
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    bridge_packet = apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state(st.session_state, now_ms=now_ms)
    st.session_state[WARROOM_RT_LIVE_RECEIVER_BRIDGE_SESSION_STATE_KEY] = bridge_packet
    return runtime_status, bridge_packet


def build_warroom_v2_page_mount_packet(*, runtime_status: Mapping[str, Any] | None = None, bridge_packet: Mapping[str, Any] | None = None, display_source: str = "unknown") -> dict[str, Any]:
    runtime = dict(runtime_status or {})
    bridge = dict(bridge_packet or {})
    receiver_started = bool(runtime.get("receiver_runtime_started"))
    socket_opened = bool(runtime.get("socket_opened") or runtime.get("websocket_opened"))
    receive_loop_started = bool(runtime.get("receive_loop_started"))
    messages_applied = int(bridge.get("messages_applied") or 0)
    return {"ok": True, "page_mount_version": WARROOM_V2_RT_VISIBLE_MOUNT_VERSION, "page_key": "warroom_v2", "page_label": "WarRoom v2", "thin_page_shell_only": False, "rt_visible_mount_ready": True, "rt_ui_polish1_modularized": True, "rt_polish2_live_retention_ready": True, "rt_polish3_cockpit_layout_ready": True, "rt_fragment_refresh_ready": True, "rt_display_source": display_source, "fallback_sample_suppressed": True, "runtime_connected": receiver_started, "push_connected": bool(socket_opened or receive_loop_started or messages_applied > 0 or display_source in {"live", "retained"}), "websocket_enabled": bool(socket_opened or receive_loop_started), "receive_loop_started": receive_loop_started, "messages_applied": messages_applied, "page_reload_enabled": False, "websocket_send_enabled": False, "broker_send_enabled": False, "order_intent_submitted": False, "ledger_append_allowed": False, "prediction_invoked": False, "classifier_invoked": False}


def _render_warroom_v2_cockpit_body(auto_refresh_packet: Mapping[str, Any]) -> None:
    runtime_status, bridge_packet = _refresh_warroom_v2_rt_live_observation()
    display_packets = select_or_build_rt_display_packets(st.session_state, bridge_packet)
    display_source = str(display_packets["source"]["display_source"])
    page_packet = build_warroom_v2_page_mount_packet(runtime_status=runtime_status, bridge_packet=bridge_packet, display_source=display_source)
    market_packet = build_market_strip_packet(display_packets["widgets"])
    trade_packet = build_trade_strip_packet(runtime_status, bridge_packet)
    guidance_packet = build_inference_guidance_packet(display_packets["chart"], display_packets["widgets"])
    copy_text = build_gpt_copy_packet(market_strip=market_packet, guidance=guidance_packet, chart_packet=display_packets["chart"], cards_packet=display_packets["cards"])

    st.session_state[WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY] = runtime_status
    render_rt_runtime_status(runtime_status, bridge_packet, st)
    render_cockpit_auto_refresh_tick(auto_refresh_packet, st)
    st.caption(f"display_source={display_source} / fallback_sample_suppressed=true / rt_polish3_cockpit_layout_ready=true / rt_fragment_refresh_ready=true")

    st.divider()
    st.subheader("1. Market strip")
    render_market_strip(market_packet, st)

    st.divider()
    st.subheader("2. Trade strip / orders, position, PnL")
    render_trade_strip(trade_packet, st)

    st.divider()
    st.subheader("3. Inference scenario guidance")
    render_inference_guidance(guidance_packet, st)

    st.divider()
    st.subheader("4. Prediction cards / important context")
    render_rt_prediction_cards(display_packets["cards"], st)

    st.divider()
    st.subheader("5. Bottom chart / realtime context")
    render_rt_bottom_chart_graph(display_packets["chart"], st)
    render_gpt_copy_packet(copy_text, st)

    with st.expander("Realtime widget details", expanded=False):
        render_rt_top_layout_and_widgets(display_packets["top"], display_packets["widgets"], st)
    render_rt_debug_packets({"page_mount": page_packet, "runtime_status": runtime_status, "bridge_packet": bridge_packet, "market_strip": market_packet, "trade_strip": trade_packet, "inference_guidance": guidance_packet}, st)
    st.caption("rt_visible_mount_ready=true / rt_polish3_cockpit_layout_ready=true / rt_fragment_refresh_ready=true / page_reload_enabled=false / fallback_sample_suppressed=true / websocket_send_enabled=false / broker_send_enabled=false / order_intent_submitted=false / prediction_invoked=false / classifier_invoked=false")


def _render_warroom_v2_cockpit_fragment(auto_refresh_packet: Mapping[str, Any]) -> None:
    run_every = fragment_run_every(auto_refresh_packet)
    fragment = getattr(st, "fragment", None)
    if run_every and callable(fragment):
        @fragment(run_every=run_every)
        def _fragment_body() -> None:
            _render_warroom_v2_cockpit_body(auto_refresh_packet)

        _fragment_body()
        return
    _render_warroom_v2_cockpit_body(auto_refresh_packet)


def render() -> None:
    auto_refresh_packet = build_cockpit_auto_refresh_packet(st.session_state)
    st.header("WarRoom v2 / Realtime Cockpit")
    st.caption("D-hot live observation / fragment-refreshed cockpit body / no page reload / no broker")
    _render_warroom_v2_cockpit_fragment(auto_refresh_packet)
