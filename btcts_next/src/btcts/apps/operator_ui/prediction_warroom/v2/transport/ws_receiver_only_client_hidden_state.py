# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_hidden_state.py
# desc: WarRoom v2 receiver-only client hidden state. Pure packet only; default-off, no socket open, no send, no UI controls.

from __future__ import annotations

from typing import Any, Mapping

from .ws_display_client_observation import build_warroom_v2_ws_display_client_observation_packet
from .ws_receiver_only_client_enable_gate import build_warroom_v2_ws_receiver_only_client_enable_gate_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_hidden_state.ps_q33b.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_KEY = "warroom_v2_ws_receiver_only_client_hidden_state_q33b"


def build_warroom_v2_ws_receiver_only_client_hidden_state_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "state_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_VERSION,
        "state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_KEY,
        "state_kind": "warroom_v2_ws_receiver_only_client_hidden_state_packet",
        "input_pipeline": ["q33a_receiver_only_client_enable_gate", "q32b_hidden_ws_display_client_observation"],
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "agreed_refresh_policy": "push_first_fragment_render_lightweight_state_pluggable_widget_custom_component_island_ready_later",
        "hidden_session_state_recorded": True,
        "warroom_page_modified": True,
        "visible_controls_added": False,
        "receiver_state_default": "receiver_hidden_state_default_off",
        "receiver_enable_requested_default": False,
        "operator_receiver_enable_ack_default": False,
        "receiver_client_enable_allowed_for_next_slice_default": False,
        "receiver_client_enable_allowed_effective": False,
        "receiver_enabled_effective": False,
        "hidden_state_is_observation_only": True,
        "hidden_state_is_not_socket_owner": True,
        "hidden_state_is_not_client_runtime": True,
        "hidden_state_is_not_subscription_runtime": True,
        "hidden_state_is_not_send_path": True,
        "socket_open_requested_default": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "browser_timer_polling_is_legacy_compat_only": True,
        "browser_timer_refresh_replacement_target": True,
        "no_new_polling_fallback": True,
        "no_browser_timer_reload_introduced": True,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_ws_receiver_only_client_hidden_state_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    ws_display_client_observation_packet: Mapping[str, Any] | None = None,
    receiver_enable_gate_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    client_observation = dict(ws_display_client_observation_packet or build_warroom_v2_ws_display_client_observation_packet(fragment_summary=fragment_summary, messages=[]))
    gate_packet = dict(receiver_enable_gate_packet or build_warroom_v2_ws_receiver_only_client_enable_gate_packet())
    allowed_next = bool(gate_packet.get("receiver_client_enable_allowed_for_next_slice"))
    state_status = "receiver_hidden_state_ready_for_next_slice_no_socket" if allowed_next else "receiver_hidden_state_default_off"
    return {
        **build_warroom_v2_ws_receiver_only_client_hidden_state_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_hidden_state_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "ws_display_client_observation_packet": client_observation,
        "receiver_enable_gate_packet": gate_packet,
        "receiver_state_status": state_status,
        "receiver_client_enable_allowed_for_next_slice": allowed_next,
        "receiver_client_enable_allowed_effective": False,
        "receiver_enabled_effective": False,
        "received_message_count": int(client_observation.get("received_message_count") or 0),
        "dropped_count": int(client_observation.get("dropped_count") or 0),
        "receive_buffer_limit": int(client_observation.get("receive_buffer_limit") or 0),
        "subscriptions_count": int(client_observation.get("subscriptions_count") or 0),
        "socket_open_requested": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
