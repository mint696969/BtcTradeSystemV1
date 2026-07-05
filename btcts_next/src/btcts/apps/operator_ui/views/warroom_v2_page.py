# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py
# desc: WarRoom v2 live observation page. Static shell plus section-fragment-refreshed cockpit lanes.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Mapping

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
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.compact_layout_view import (
    COMPACT_VIEWPORT_LAYOUT_VERSION,
    compact_footer_caption,
    render_compact_page_header,
    render_compact_section_label,
)
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

WARROOM_V2_RT_VISIBLE_MOUNT_VERSION = "prediction_warroom.v2.rt_visible_mount.2026_07_05.v7_compact_viewport"


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


def _build_cockpit_snapshot() -> dict[str, Any]:
    runtime_status, bridge_packet = _refresh_warroom_v2_rt_live_observation()
    display_packets = select_or_build_rt_display_packets(st.session_state, bridge_packet)
    display_source = str(display_packets["source"]["display_source"])
    page_packet = build_warroom_v2_page_mount_packet(runtime_status=runtime_status, bridge_packet=bridge_packet, display_source=display_source)
    market_packet = build_market_strip_packet(display_packets["widgets"])
    trade_packet = build_trade_strip_packet(runtime_status, bridge_packet)
    guidance_packet = build_inference_guidance_packet(display_packets["chart"], display_packets["widgets"])
    copy_text = build_gpt_copy_packet(market_strip=market_packet, guidance=guidance_packet, chart_packet=display_packets["chart"], cards_packet=display_packets["cards"])
    st.session_state[WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY] = runtime_status
    return {"runtime_status": runtime_status, "bridge_packet": bridge_packet, "display_packets": display_packets, "display_source": display_source, "page_packet": page_packet, "market_packet": market_packet, "trade_packet": trade_packet, "guidance_packet": guidance_packet, "copy_text": copy_text}


def build_warroom_v2_page_mount_packet(*, runtime_status: Mapping[str, Any] | None = None, bridge_packet: Mapping[str, Any] | None = None, display_source: str = "unknown") -> dict[str, Any]:
    runtime = dict(runtime_status or {})
    bridge = dict(bridge_packet or {})
    receiver_started = bool(runtime.get("receiver_runtime_started"))
    socket_opened = bool(runtime.get("socket_opened") or runtime.get("websocket_opened"))
    receive_loop_started = bool(runtime.get("receive_loop_started"))
    messages_applied = int(bridge.get("messages_applied") or 0)
    return {"ok": True, "page_mount_version": WARROOM_V2_RT_VISIBLE_MOUNT_VERSION, "page_key": "warroom_v2", "page_label": "WarRoom v2", "thin_page_shell_only": False, "rt_visible_mount_ready": True, "rt_ui_polish1_modularized": True, "rt_polish2_live_retention_ready": True, "rt_polish3_cockpit_layout_ready": True, "rt_fragment_refresh_ready": True, "rt_section_fragment_refresh_ready": True, "rt_display_source": display_source, "fallback_sample_suppressed": True, "runtime_connected": receiver_started, "push_connected": bool(socket_opened or receive_loop_started or messages_applied > 0 or display_source in {"live", "retained"}), "websocket_enabled": bool(socket_opened or receive_loop_started), "receive_loop_started": receive_loop_started, "messages_applied": messages_applied, "page_reload_enabled": False, "websocket_send_enabled": False, "broker_send_enabled": False, "order_intent_submitted": False, "ledger_append_allowed": False, "prediction_invoked": False, "classifier_invoked": False}


def _render_section_fragment(name: str, auto_refresh_packet: Mapping[str, Any], body: Callable[[dict[str, Any]], None]) -> None:
    run_every = fragment_run_every(auto_refresh_packet)
    fragment = getattr(st, "fragment", None)
    if run_every and callable(fragment):
        @fragment(run_every=run_every)
        def _section_body() -> None:
            body(_build_cockpit_snapshot())

        _section_body()
        return
    body(_build_cockpit_snapshot())


def _runtime_section(snapshot: dict[str, Any], auto_refresh_packet: Mapping[str, Any]) -> None:
    render_rt_runtime_status(snapshot["runtime_status"], snapshot["bridge_packet"], st)
    render_cockpit_auto_refresh_tick(auto_refresh_packet, st)
    st.caption(f"display_source={snapshot['display_source']} / fallback_sample_suppressed=true / rt_section_fragment_refresh_ready=true")


def render() -> None:
    auto_refresh_packet = build_cockpit_auto_refresh_packet(st.session_state)
    render_compact_page_header(st)

    _render_section_fragment("runtime", auto_refresh_packet, lambda snapshot: _runtime_section(snapshot, auto_refresh_packet))

    render_compact_section_label(st, index=1, title="Market strip", note="manual-trade market essentials")
    _render_section_fragment("market", auto_refresh_packet, lambda snapshot: render_market_strip(snapshot["market_packet"], st))

    render_compact_section_label(st, index=2, title="Trade strip", note="orders / position / PnL")
    _render_section_fragment("trade", auto_refresh_packet, lambda snapshot: render_trade_strip(snapshot["trade_packet"], st))

    with st.expander("3. Inference scenario guidance — deferred compact review", expanded=False):
        _render_section_fragment("guidance", auto_refresh_packet, lambda snapshot: render_inference_guidance(snapshot["guidance_packet"], st))

    with st.expander("4. Prediction cards — deferred to next thread", expanded=False):
        _render_section_fragment("cards", auto_refresh_packet, lambda snapshot: render_rt_prediction_cards(snapshot["display_packets"]["cards"], st))

    render_compact_section_label(st, index=5, title="Bottom chart", note="bid/ask board layer + trade points")
    _render_section_fragment("chart", auto_refresh_packet, lambda snapshot: (render_rt_bottom_chart_graph(snapshot["display_packets"]["chart"], st), render_gpt_copy_packet(snapshot["copy_text"], st)))

    with st.expander("Realtime widget details", expanded=False):
        _render_section_fragment("details", auto_refresh_packet, lambda snapshot: render_rt_top_layout_and_widgets(snapshot["display_packets"]["top"], snapshot["display_packets"]["widgets"], st))
    with st.expander("RT debug packets", expanded=False):
        _render_section_fragment("debug", auto_refresh_packet, lambda snapshot: render_rt_debug_packets({"page_mount": snapshot["page_packet"], "runtime_status": snapshot["runtime_status"], "bridge_packet": snapshot["bridge_packet"], "market_strip": snapshot["market_packet"], "trade_strip": snapshot["trade_packet"], "inference_guidance": snapshot["guidance_packet"]}, st))
    st.caption(compact_footer_caption())
