# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_receive_buffer_drain_contract.py
# desc: WarRoom v2 receiver-only client receive-buffer drain contract. Pure packet only; default-off, no socket open, no send, no state mutation.

from __future__ import annotations

from typing import Any, Mapping

from .ws_display_client import build_warroom_v2_ws_display_client_receive_buffer
from .ws_receiver_only_client_hidden_state import build_warroom_v2_ws_receiver_only_client_hidden_state_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_RECEIVE_BUFFER_DRAIN_CONTRACT_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_receive_buffer_drain_contract.ps_q33c.v1"


def _drain_status(*, requested: bool, ack: bool, hidden_ready: bool) -> str:
    if not requested:
        return "receive_buffer_drain_hidden_default"
    if not ack:
        return "receive_buffer_drain_blocked_operator_ack_required"
    if not hidden_ready:
        return "receive_buffer_drain_blocked_receiver_hidden_state_required"
    return "receive_buffer_drain_ready_for_next_slice_no_socket"


def build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "drain_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_RECEIVE_BUFFER_DRAIN_CONTRACT_VERSION,
        "drain_kind": "warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract_default_off_no_socket",
        "input_pipeline": ["q33b_receiver_only_client_hidden_state", "q32a_ws_display_client_receive_buffer"],
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "agreed_refresh_policy": "push_first_fragment_render_lightweight_state_pluggable_widget_custom_component_island_ready_later",
        "drain_requested_default": False,
        "operator_drain_ack_default": False,
        "drain_contract_status_default": "receive_buffer_drain_hidden_default",
        "drain_contract_status_ready": "receive_buffer_drain_ready_for_next_slice_no_socket",
        "receive_buffer_drain_allowed_for_next_slice_default": False,
        "receive_buffer_drain_allowed_effective": False,
        "messages_drained_now": 0,
        "state_mutated": False,
        "session_state_write_allowed": False,
        "warroom_page_modified": False,
        "visible_controls_added": False,
        "drain_contract_is_preview_only": True,
        "drain_contract_is_not_socket_owner": True,
        "drain_contract_is_not_client_runtime": True,
        "drain_contract_is_not_subscription_runtime": True,
        "drain_contract_is_not_send_path": True,
        "drain_source": "existing_q32a_receive_buffer_packet_messages",
        "drain_target": "future_lightweight_receiver_state_next_slice",
        "drain_preview_max_default": 16,
        "drain_effective_mutation": False,
        "receiver_only": True,
        "send_disabled": True,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
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


def _extract_receive_buffer(hidden_state: Mapping[str, Any]) -> Mapping[str, Any]:
    observation = hidden_state.get("ws_display_client_observation_packet")
    if isinstance(observation, Mapping):
        client = observation.get("ws_display_client_packet")
        if isinstance(client, Mapping):
            buffer = client.get("receive_buffer_packet")
            if isinstance(buffer, Mapping):
                return buffer
    return build_warroom_v2_ws_display_client_receive_buffer(messages=[])


def build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet(
    *,
    receiver_hidden_state_packet: Mapping[str, Any] | None = None,
    receive_buffer_packet: Mapping[str, Any] | None = None,
    drain_requested: bool = False,
    operator_drain_ack: bool = False,
    max_drain_items: int = 16,
) -> dict[str, Any]:
    hidden_state = dict(receiver_hidden_state_packet or build_warroom_v2_ws_receiver_only_client_hidden_state_packet())
    hidden_ready = bool(hidden_state.get("receiver_client_enable_allowed_for_next_slice"))
    buffer_packet = dict(receive_buffer_packet or _extract_receive_buffer(hidden_state))
    messages = list(buffer_packet.get("messages") or [])
    bounded = max(1, min(64, int(max_drain_items or 16)))
    status = _drain_status(requested=bool(drain_requested), ack=bool(operator_drain_ack), hidden_ready=hidden_ready)
    allowed_next = status == "receive_buffer_drain_ready_for_next_slice_no_socket"
    preview = messages[:bounded] if allowed_next else []
    return {
        **build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet",
        "receiver_hidden_state_packet": hidden_state,
        "receive_buffer_packet": buffer_packet,
        "drain_requested": bool(drain_requested),
        "operator_drain_ack": bool(operator_drain_ack),
        "receiver_hidden_state_ready_for_next_slice": hidden_ready,
        "drain_contract_status": status,
        "receive_buffer_message_count": len(messages),
        "receive_buffer_dropped_count": int(buffer_packet.get("dropped_count") or 0),
        "drain_preview_max": bounded,
        "drain_preview_count": len(preview),
        "drain_preview_messages": preview,
        "receive_buffer_drain_allowed_for_next_slice": bool(allowed_next),
        "receive_buffer_drain_allowed_effective": False,
        "messages_drained_now": 0,
        "state_mutated": False,
        "session_state_write_allowed": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
