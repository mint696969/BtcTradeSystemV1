# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_session_state_apply_preview.py
# desc: WarRoom v2 receiver-only client session_state apply preview. Pure packet only; default-off, no socket open, no send, no state mutation.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_lightweight_state_apply_gate import build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_session_state_apply_preview.ps_q33f.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_KEY = "warroom_v2_ws_receiver_only_client_lightweight_state_q33f_preview"


def _preview_status(*, requested: bool, ack: bool, apply_gate_ready: bool) -> str:
    if not requested:
        return "session_state_apply_preview_hidden_default"
    if not ack:
        return "session_state_apply_preview_blocked_operator_ack_required"
    if not apply_gate_ready:
        return "session_state_apply_preview_blocked_apply_gate_required"
    return "session_state_apply_preview_ready_for_next_slice_no_socket"


def build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "preview_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_VERSION,
        "session_state_target_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_KEY,
        "preview_kind": "warroom_v2_ws_receiver_only_client_session_state_apply_preview_default_off_no_socket",
        "input_pipeline": ["q33e_lightweight_state_apply_gate", "q33d_lightweight_state_drain_preview", "q33c_receive_buffer_drain_contract"],
        "session_state_apply_preview_requested_default": False,
        "operator_session_state_apply_preview_ack_default": False,
        "session_state_apply_preview_status_default": "session_state_apply_preview_hidden_default",
        "session_state_apply_preview_status_ready": "session_state_apply_preview_ready_for_next_slice_no_socket",
        "session_state_apply_preview_allowed_for_next_slice_default": False,
        "session_state_write_allowed_effective": False,
        "session_state_write_applied": False,
        "session_state_mutated": False,
        "state_mutated": False,
        "messages_committed_now": 0,
        "warroom_page_modified": False,
        "visible_controls_added": False,
        "preview_source": "q33e_apply_gate_candidate_state_update_preview",
        "preview_target": "future_streamlit_session_state_key",
        "session_state_preview_value_kind": "receiver_only_lightweight_state_update_preview",
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


def _write_preview(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "write_preview_kind": "future_streamlit_session_state_write_preview",
        "target_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_SESSION_STATE_APPLY_PREVIEW_KEY,
        "value_kind": "receiver_only_lightweight_state_update_preview",
        "message_count": int(candidate.get("message_count") or 0),
        "latest_topic": str(candidate.get("latest_topic") or ""),
        "latest_widget_id": str(candidate.get("latest_widget_id") or ""),
        "latest_sequence": int(candidate.get("latest_sequence") or 0),
        "topics": list(candidate.get("topics") or []),
        "messages": list(candidate.get("messages") or []),
        "preview_only": True,
        "write_applied_now": False,
    }


def build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet(
    *,
    lightweight_state_apply_gate_packet: Mapping[str, Any] | None = None,
    session_state_apply_preview_requested: bool = False,
    operator_session_state_apply_preview_ack: bool = False,
) -> dict[str, Any]:
    apply_gate = dict(lightweight_state_apply_gate_packet or build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet())
    candidate = dict(apply_gate.get("candidate_state_update_preview") or {})
    gate_ready = bool(apply_gate.get("lightweight_state_apply_allowed_for_next_slice"))
    status = _preview_status(requested=bool(session_state_apply_preview_requested), ack=bool(operator_session_state_apply_preview_ack), apply_gate_ready=gate_ready)
    allowed_next = status == "session_state_apply_preview_ready_for_next_slice_no_socket"
    write_preview = _write_preview(candidate) if allowed_next else {}
    return {
        **build_warroom_v2_ws_receiver_only_client_session_state_apply_preview_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_session_state_apply_preview_packet",
        "lightweight_state_apply_gate_packet": apply_gate,
        "candidate_state_update_preview": candidate,
        "session_state_apply_preview_requested": bool(session_state_apply_preview_requested),
        "operator_session_state_apply_preview_ack": bool(operator_session_state_apply_preview_ack),
        "lightweight_state_apply_gate_ready_for_next_slice": gate_ready,
        "session_state_apply_preview_status": status,
        "candidate_message_count": int(candidate.get("message_count") or 0),
        "session_state_write_preview": write_preview,
        "session_state_apply_preview_allowed_for_next_slice": bool(allowed_next),
        "session_state_write_allowed_effective": False,
        "session_state_write_applied": False,
        "session_state_mutated": False,
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
