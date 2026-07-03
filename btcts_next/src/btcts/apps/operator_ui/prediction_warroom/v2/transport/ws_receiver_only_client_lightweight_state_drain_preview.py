# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_lightweight_state_drain_preview.py
# desc: WarRoom v2 receiver-only client lightweight state drain preview. Pure packet only; default-off, no socket open, no send, no state mutation.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_receive_buffer_drain_contract import build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_DRAIN_PREVIEW_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_lightweight_state_drain_preview.ps_q33d.v1"


def _preview_status(*, requested: bool, ack: bool, drain_ready: bool) -> str:
    if not requested:
        return "lightweight_state_drain_preview_hidden_default"
    if not ack:
        return "lightweight_state_drain_preview_blocked_operator_ack_required"
    if not drain_ready:
        return "lightweight_state_drain_preview_blocked_drain_contract_required"
    return "lightweight_state_drain_preview_ready_for_next_slice_no_socket"


def build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "preview_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_DRAIN_PREVIEW_VERSION,
        "preview_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_default_off_no_socket",
        "input_pipeline": ["q33c_receive_buffer_drain_contract", "q33b_receiver_only_client_hidden_state", "q32a_ws_display_client_receive_buffer"],
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "agreed_refresh_policy": "push_first_fragment_render_lightweight_state_pluggable_widget_custom_component_island_ready_later",
        "lightweight_state_update_requested_default": False,
        "operator_lightweight_state_ack_default": False,
        "lightweight_state_drain_preview_status_default": "lightweight_state_drain_preview_hidden_default",
        "lightweight_state_drain_preview_status_ready": "lightweight_state_drain_preview_ready_for_next_slice_no_socket",
        "lightweight_state_drain_allowed_for_next_slice_default": False,
        "lightweight_state_update_allowed_effective": False,
        "candidate_state_update_is_preview_only": True,
        "candidate_state_update_applied": False,
        "messages_committed_now": 0,
        "state_mutated": False,
        "session_state_write_allowed": False,
        "warroom_page_modified": False,
        "visible_controls_added": False,
        "preview_source": "q33c_drain_preview_messages",
        "preview_target": "future_lightweight_receiver_state_update_next_slice",
        "preview_includes_latest_message_sequence": True,
        "preview_includes_message_count": True,
        "preview_includes_topics": True,
        "preview_effective_mutation": False,
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


def _candidate_preview(messages: list[Mapping[str, Any]]) -> dict[str, Any]:
    topics = sorted({str(item.get("topic") or "") for item in messages if item.get("topic")})
    latest = messages[-1] if messages else {}
    return {
        "candidate_kind": "future_lightweight_receiver_state_update_preview",
        "message_count": len(messages),
        "topics": topics,
        "latest_topic": str(latest.get("topic") or ""),
        "latest_widget_id": str(latest.get("widget_id") or ""),
        "latest_sequence": int(latest.get("sequence") or 0),
        "messages": [dict(item) for item in messages],
        "preview_only": True,
        "applied_now": False,
    }


def build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet(
    *,
    receive_buffer_drain_packet: Mapping[str, Any] | None = None,
    lightweight_state_update_requested: bool = False,
    operator_lightweight_state_ack: bool = False,
    max_preview_items: int = 16,
) -> dict[str, Any]:
    drain_packet = dict(receive_buffer_drain_packet or build_warroom_v2_ws_receiver_only_client_receive_buffer_drain_packet())
    drain_ready = bool(drain_packet.get("receive_buffer_drain_allowed_for_next_slice"))
    status = _preview_status(requested=bool(lightweight_state_update_requested), ack=bool(operator_lightweight_state_ack), drain_ready=drain_ready)
    allowed_next = status == "lightweight_state_drain_preview_ready_for_next_slice_no_socket"
    bounded = max(1, min(64, int(max_preview_items or 16)))
    source_messages = list(drain_packet.get("drain_preview_messages") or [])
    preview_messages = source_messages[:bounded] if allowed_next else []
    candidate = _candidate_preview(preview_messages)
    return {
        **build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet",
        "receive_buffer_drain_packet": drain_packet,
        "lightweight_state_update_requested": bool(lightweight_state_update_requested),
        "operator_lightweight_state_ack": bool(operator_lightweight_state_ack),
        "receive_buffer_drain_ready_for_next_slice": drain_ready,
        "lightweight_state_drain_preview_status": status,
        "source_drain_preview_count": len(source_messages),
        "lightweight_state_preview_max": bounded,
        "lightweight_state_preview_count": len(preview_messages),
        "candidate_state_update_preview": candidate,
        "lightweight_state_drain_allowed_for_next_slice": bool(allowed_next),
        "lightweight_state_update_allowed_effective": False,
        "candidate_state_update_applied": False,
        "messages_committed_now": 0,
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
