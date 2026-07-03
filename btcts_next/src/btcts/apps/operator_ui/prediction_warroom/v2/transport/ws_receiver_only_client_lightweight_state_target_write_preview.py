# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_lightweight_state_target_write_preview.py
# desc: WarRoom v2 receiver-only client lightweight-state target write preview. Pure packet only; default-off, no socket open, no send, no target write.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_lightweight_state_target_apply_gate import build_warroom_v2_ws_receiver_only_client_lightweight_state_target_apply_gate_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_PREVIEW_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_lightweight_state_target_write_preview.ps_q33i.v1"


def _target_write_preview_status(*, requested: bool, ack: bool, gate_ready: bool, preview_valid: bool) -> str:
    if not requested:
        return "lightweight_state_target_write_preview_hidden_default"
    if not ack:
        return "lightweight_state_target_write_preview_blocked_operator_ack_required"
    if not gate_ready:
        return "lightweight_state_target_write_preview_blocked_target_apply_gate_required"
    if not preview_valid:
        return "lightweight_state_target_write_preview_blocked_target_preview_required"
    return "lightweight_state_target_write_preview_ready_for_next_slice_no_socket"


def build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "target_write_preview_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_PREVIEW_VERSION,
        "target_write_preview_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_default_off_no_socket",
        "input_pipeline": ["q33h_lightweight_state_target_apply_gate", "q33g_session_state_apply_hidden_record", "q33f_session_state_apply_preview"],
        "lightweight_state_target_write_preview_requested_default": False,
        "operator_lightweight_state_target_write_preview_ack_default": False,
        "target_write_preview_status_default": "lightweight_state_target_write_preview_hidden_default",
        "target_write_preview_status_ready": "lightweight_state_target_write_preview_ready_for_next_slice_no_socket",
        "target_write_preview_allowed_for_next_slice_default": False,
        "target_write_allowed_effective": False,
        "target_session_state_write_allowed_effective": False,
        "target_session_state_write_applied": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "messages_committed_now": 0,
        "warroom_page_modified": False,
        "visible_controls_added": False,
        "target_write_preview_source": "q33h_target_session_state_write_preview",
        "target_write_preview_target": "future_lightweight_receiver_state_session_state_write_slice",
        "target_write_value_kind": "receiver_only_lightweight_state_value_preview",
        "target_write_preview_checks_gate_ready": True,
        "target_write_preview_checks_message_count": True,
        "target_write_preview_effective_mutation": False,
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


def _source_preview_valid(target_write_preview: Mapping[str, Any]) -> bool:
    return bool(target_write_preview.get("target_key")) and int(target_write_preview.get("message_count") or 0) > 0 and bool(target_write_preview.get("preview_only"))


def _build_target_value_preview(target_write_preview: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "value_kind": "receiver_only_lightweight_state_value_preview",
        "target_key": str(target_write_preview.get("target_key") or ""),
        "message_count": int(target_write_preview.get("message_count") or 0),
        "latest_topic": str(target_write_preview.get("latest_topic") or ""),
        "latest_widget_id": str(target_write_preview.get("latest_widget_id") or ""),
        "latest_sequence": int(target_write_preview.get("latest_sequence") or 0),
        "topics": list(target_write_preview.get("topics") or []),
        "messages": list(target_write_preview.get("messages") or []),
        "receiver_only": True,
        "preview_only": True,
        "target_write_applied_now": False,
        "state_mutated_now": False,
    }


def build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet(
    *,
    lightweight_state_target_apply_gate_packet: Mapping[str, Any] | None = None,
    lightweight_state_target_write_preview_requested: bool = False,
    operator_lightweight_state_target_write_preview_ack: bool = False,
) -> dict[str, Any]:
    gate_packet = dict(lightweight_state_target_apply_gate_packet or build_warroom_v2_ws_receiver_only_client_lightweight_state_target_apply_gate_packet())
    source_preview = dict(gate_packet.get("target_session_state_write_preview") or {})
    gate_ready = bool(gate_packet.get("target_apply_gate_allowed_for_next_slice"))
    preview_valid = _source_preview_valid(source_preview)
    status = _target_write_preview_status(requested=bool(lightweight_state_target_write_preview_requested), ack=bool(operator_lightweight_state_target_write_preview_ack), gate_ready=gate_ready, preview_valid=preview_valid)
    allowed_next = status == "lightweight_state_target_write_preview_ready_for_next_slice_no_socket"
    value_preview = _build_target_value_preview(source_preview) if allowed_next else {}
    return {
        **build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_preview_packet",
        "lightweight_state_target_apply_gate_packet": gate_packet,
        "source_target_session_state_write_preview": source_preview,
        "target_lightweight_state_value_preview": value_preview,
        "lightweight_state_target_write_preview_requested": bool(lightweight_state_target_write_preview_requested),
        "operator_lightweight_state_target_write_preview_ack": bool(operator_lightweight_state_target_write_preview_ack),
        "target_apply_gate_ready_for_next_slice": gate_ready,
        "source_target_write_preview_validated": preview_valid,
        "target_write_preview_status": status,
        "target_write_preview_allowed_for_next_slice": bool(allowed_next),
        "target_session_state_key": str(source_preview.get("target_key") or ""),
        "target_message_count": int(source_preview.get("message_count") or 0),
        "target_latest_topic": str(source_preview.get("latest_topic") or ""),
        "target_latest_sequence": int(source_preview.get("latest_sequence") or 0),
        "target_write_allowed_effective": False,
        "target_session_state_write_allowed_effective": False,
        "target_session_state_write_applied": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "messages_committed_now": 0,
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
