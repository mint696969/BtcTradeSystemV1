# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_lightweight_state_target_apply_gate.py
# desc: WarRoom v2 receiver-only client lightweight-state target apply gate. Pure packet only; default-off, no socket open, no send, no target write.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_session_state_apply_hidden_record import build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_APPLY_GATE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_lightweight_state_target_apply_gate.ps_q33h.v1"


def _target_apply_status(*, requested: bool, ack: bool, hidden_ready: bool, target_valid: bool) -> str:
    if not requested:
        return "lightweight_state_target_apply_gate_hidden_default"
    if not ack:
        return "lightweight_state_target_apply_gate_blocked_operator_ack_required"
    if not hidden_ready:
        return "lightweight_state_target_apply_gate_blocked_hidden_record_required"
    if not target_valid:
        return "lightweight_state_target_apply_gate_blocked_target_preview_required"
    return "lightweight_state_target_apply_gate_ready_for_next_slice_no_socket"


def build_warroom_v2_ws_receiver_only_client_lightweight_state_target_apply_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "target_apply_gate_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_APPLY_GATE_VERSION,
        "target_apply_gate_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_target_apply_gate_default_off_no_socket",
        "input_pipeline": ["q33g_session_state_apply_hidden_record", "q33f_session_state_apply_preview", "q33e_lightweight_state_apply_gate"],
        "lightweight_state_target_apply_requested_default": False,
        "operator_lightweight_state_target_apply_ack_default": False,
        "target_apply_gate_status_default": "lightweight_state_target_apply_gate_hidden_default",
        "target_apply_gate_status_ready": "lightweight_state_target_apply_gate_ready_for_next_slice_no_socket",
        "target_apply_gate_allowed_for_next_slice_default": False,
        "target_apply_allowed_effective": False,
        "target_session_state_write_allowed_effective": False,
        "target_session_state_write_applied": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "messages_committed_now": 0,
        "warroom_page_modified": False,
        "visible_controls_added": False,
        "target_apply_gate_source": "q33g_session_state_write_preview",
        "target_apply_gate_target": "future_lightweight_receiver_state_session_state_write_slice",
        "target_apply_gate_checks_hidden_record_ready": True,
        "target_apply_gate_checks_target_key": True,
        "target_apply_gate_checks_message_count": True,
        "target_apply_gate_effective_mutation": False,
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


def _target_valid(write_preview: Mapping[str, Any]) -> bool:
    return bool(write_preview.get("target_key")) and int(write_preview.get("message_count") or 0) > 0 and bool(write_preview.get("preview_only"))


def build_warroom_v2_ws_receiver_only_client_lightweight_state_target_apply_gate_packet(
    *,
    session_state_apply_hidden_record_packet: Mapping[str, Any] | None = None,
    lightweight_state_target_apply_requested: bool = False,
    operator_lightweight_state_target_apply_ack: bool = False,
) -> dict[str, Any]:
    hidden_record = dict(session_state_apply_hidden_record_packet or build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet())
    write_preview = dict(hidden_record.get("session_state_write_preview") or {})
    hidden_ready = bool(hidden_record.get("hidden_record_allowed_for_next_slice"))
    valid = _target_valid(write_preview)
    status = _target_apply_status(requested=bool(lightweight_state_target_apply_requested), ack=bool(operator_lightweight_state_target_apply_ack), hidden_ready=hidden_ready, target_valid=valid)
    allowed_next = status == "lightweight_state_target_apply_gate_ready_for_next_slice_no_socket"
    return {
        **build_warroom_v2_ws_receiver_only_client_lightweight_state_target_apply_gate_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_target_apply_gate_packet",
        "session_state_apply_hidden_record_packet": hidden_record,
        "target_session_state_write_preview": write_preview if allowed_next else {},
        "lightweight_state_target_apply_requested": bool(lightweight_state_target_apply_requested),
        "operator_lightweight_state_target_apply_ack": bool(operator_lightweight_state_target_apply_ack),
        "hidden_record_ready_for_next_slice": hidden_ready,
        "target_write_preview_validated": valid,
        "target_apply_gate_status": status,
        "target_apply_gate_allowed_for_next_slice": bool(allowed_next),
        "target_session_state_key": str(write_preview.get("target_key") or ""),
        "target_message_count": int(write_preview.get("message_count") or 0),
        "target_latest_topic": str(write_preview.get("latest_topic") or ""),
        "target_latest_sequence": int(write_preview.get("latest_sequence") or 0),
        "target_apply_allowed_effective": False,
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
