# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_session_state_apply_hidden_record.py
# desc: WarRoom v2 receiver-only client session_state apply hidden record. Pure packet only; default-off, no socket open, no send, no target state mutation.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_session_state_apply_preview import build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_session_state_apply_hidden_record.ps_q33g.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_KEY = "warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_q33g"


def _hidden_record_status(*, requested: bool, ack: bool, preview_ready: bool) -> str:
    if not requested:
        return "session_state_apply_hidden_record_hidden_default"
    if not ack:
        return "session_state_apply_hidden_record_blocked_operator_ack_required"
    if not preview_ready:
        return "session_state_apply_hidden_record_blocked_preview_required"
    return "session_state_apply_hidden_record_ready_for_next_slice_no_socket"


def build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "hidden_record_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_VERSION,
        "hidden_record_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_HIDDEN_RECORD_KEY,
        "hidden_record_kind": "warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_default_off_no_socket",
        "input_pipeline": ["q33f_session_state_apply_preview", "q33e_lightweight_state_apply_gate", "q33d_lightweight_state_drain_preview"],
        "session_state_apply_hidden_record_requested_default": False,
        "operator_session_state_apply_hidden_record_ack_default": False,
        "hidden_record_status_default": "session_state_apply_hidden_record_hidden_default",
        "hidden_record_status_ready": "session_state_apply_hidden_record_ready_for_next_slice_no_socket",
        "hidden_record_session_state_recorded": True,
        "warroom_page_modified": True,
        "visible_controls_added": False,
        "hidden_record_source": "q33f_session_state_write_preview",
        "hidden_record_target": "warroom_hidden_session_state_diagnostic_key",
        "hidden_record_is_not_target_lightweight_state_write": True,
        "hidden_record_effective_mutation_scope": "hidden_diagnostic_record_only",
        "target_session_state_write_allowed_effective": False,
        "target_session_state_write_applied": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "messages_committed_now": 0,
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


def build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    session_state_apply_preview_packet: Mapping[str, Any] | None = None,
    session_state_apply_hidden_record_requested: bool = False,
    operator_session_state_apply_hidden_record_ack: bool = False,
) -> dict[str, Any]:
    preview_packet = dict(session_state_apply_preview_packet or build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet())
    write_preview = dict(preview_packet.get("session_state_write_preview") or {})
    preview_ready = bool(preview_packet.get("session_state_apply_preview_allowed_for_next_slice"))
    status = _hidden_record_status(requested=bool(session_state_apply_hidden_record_requested), ack=bool(operator_session_state_apply_hidden_record_ack), preview_ready=preview_ready)
    allowed_next = status == "session_state_apply_hidden_record_ready_for_next_slice_no_socket"
    return {
        **build_warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_session_state_apply_hidden_record_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "session_state_apply_preview_packet": preview_packet,
        "session_state_write_preview": write_preview if allowed_next else {},
        "session_state_apply_hidden_record_requested": bool(session_state_apply_hidden_record_requested),
        "operator_session_state_apply_hidden_record_ack": bool(operator_session_state_apply_hidden_record_ack),
        "session_state_apply_preview_ready_for_next_slice": preview_ready,
        "hidden_record_status": status,
        "hidden_record_allowed_for_next_slice": bool(allowed_next),
        "hidden_record_session_state_recorded": True,
        "target_session_state_key": str(write_preview.get("target_key") or ""),
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
