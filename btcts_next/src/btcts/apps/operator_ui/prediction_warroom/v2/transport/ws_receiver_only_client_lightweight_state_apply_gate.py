# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_lightweight_state_apply_gate.py
# desc: WarRoom v2 receiver-only client lightweight state apply gate. Pure packet only; default-off, no socket open, no send, no state mutation.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_lightweight_state_drain_preview import build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_APPLY_GATE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_lightweight_state_apply_gate.ps_q33e.v1"


def _apply_status(*, requested: bool, ack: bool, preview_ready: bool, candidate_valid: bool) -> str:
    if not requested:
        return "lightweight_state_apply_gate_hidden_default"
    if not ack:
        return "lightweight_state_apply_gate_blocked_operator_ack_required"
    if not preview_ready:
        return "lightweight_state_apply_gate_blocked_preview_required"
    if not candidate_valid:
        return "lightweight_state_apply_gate_blocked_candidate_required"
    return "lightweight_state_apply_gate_ready_for_next_slice_no_socket"


def build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "apply_gate_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_APPLY_GATE_VERSION,
        "apply_gate_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_default_off_no_socket",
        "input_pipeline": ["q33d_lightweight_state_drain_preview", "q33c_receive_buffer_drain_contract", "q33b_receiver_only_client_hidden_state", "q32a_ws_display_client_receive_buffer"],
        "lightweight_state_apply_requested_default": False,
        "operator_lightweight_state_apply_ack_default": False,
        "lightweight_state_apply_gate_status_default": "lightweight_state_apply_gate_hidden_default",
        "lightweight_state_apply_gate_status_ready": "lightweight_state_apply_gate_ready_for_next_slice_no_socket",
        "lightweight_state_apply_allowed_for_next_slice_default": False,
        "lightweight_state_apply_allowed_effective": False,
        "candidate_state_update_validated": False,
        "candidate_state_update_applied": False,
        "messages_committed_now": 0,
        "state_mutated": False,
        "session_state_write_allowed": False,
        "warroom_page_modified": False,
        "visible_controls_added": False,
        "apply_gate_source": "q33d_candidate_state_update_preview",
        "apply_gate_target": "future_session_state_apply_slice",
        "apply_gate_checks_candidate_message_count": True,
        "apply_gate_checks_preview_only": True,
        "apply_gate_effective_mutation": False,
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


def _candidate_valid(candidate: Mapping[str, Any]) -> bool:
    return bool(candidate.get("preview_only")) and int(candidate.get("message_count") or 0) > 0


def build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet(
    *,
    lightweight_state_drain_preview_packet: Mapping[str, Any] | None = None,
    lightweight_state_apply_requested: bool = False,
    operator_lightweight_state_apply_ack: bool = False,
) -> dict[str, Any]:
    preview_packet = dict(lightweight_state_drain_preview_packet or build_warroom_v2_ws_receiver_only_client_lightweight_state_drain_preview_packet())
    candidate = dict(preview_packet.get("candidate_state_update_preview") or {})
    preview_ready = bool(preview_packet.get("lightweight_state_drain_allowed_for_next_slice"))
    valid = _candidate_valid(candidate)
    status = _apply_status(requested=bool(lightweight_state_apply_requested), ack=bool(operator_lightweight_state_apply_ack), preview_ready=preview_ready, candidate_valid=valid)
    allowed_next = status == "lightweight_state_apply_gate_ready_for_next_slice_no_socket"
    return {
        **build_warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_apply_gate_packet",
        "lightweight_state_drain_preview_packet": preview_packet,
        "candidate_state_update_preview": candidate,
        "lightweight_state_apply_requested": bool(lightweight_state_apply_requested),
        "operator_lightweight_state_apply_ack": bool(operator_lightweight_state_apply_ack),
        "lightweight_state_drain_preview_ready_for_next_slice": preview_ready,
        "candidate_state_update_validated": valid,
        "lightweight_state_apply_gate_status": status,
        "candidate_message_count": int(candidate.get("message_count") or 0),
        "candidate_latest_topic": str(candidate.get("latest_topic") or ""),
        "candidate_latest_sequence": int(candidate.get("latest_sequence") or 0),
        "lightweight_state_apply_allowed_for_next_slice": bool(allowed_next),
        "lightweight_state_apply_allowed_effective": False,
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
