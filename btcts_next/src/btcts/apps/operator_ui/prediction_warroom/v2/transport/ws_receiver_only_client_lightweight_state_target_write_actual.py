# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_lightweight_state_target_write_actual.py
# desc: WarRoom v2 receiver-only client lightweight-state first actual target write helper. Default-off/operator-gated, no socket open, no send.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from .ws_receiver_only_client_lightweight_state_target_write_gate import build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_gate_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_ACTUAL_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_lightweight_state_target_write_actual.ps_q33l.v1"


def _target_write_actual_status(*, requested: bool, ack: bool, gate_ready: bool, value_preview_valid: bool) -> str:
    if not requested:
        return "lightweight_state_target_write_actual_hidden_default"
    if not ack:
        return "lightweight_state_target_write_actual_blocked_operator_ack_required"
    if not gate_ready:
        return "lightweight_state_target_write_actual_blocked_target_write_gate_required"
    if not value_preview_valid:
        return "lightweight_state_target_write_actual_blocked_target_value_preview_required"
    return "lightweight_state_target_write_actual_applied_no_socket"


def _target_value_preview_valid(value_preview: Mapping[str, Any]) -> bool:
    return bool(value_preview.get("target_key")) and int(value_preview.get("message_count") or 0) > 0 and bool(value_preview.get("preview_only"))


def build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "target_write_actual_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_ACTUAL_VERSION,
        "target_write_actual_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_first_actual_default_off_no_socket",
        "input_pipeline": ["q33k_target_write_gate", "q33j_target_write_hidden_record", "q33i_lightweight_state_target_write_preview"],
        "lightweight_state_target_write_actual_requested_default": False,
        "operator_lightweight_state_target_write_actual_ack_default": False,
        "target_write_actual_status_default": "lightweight_state_target_write_actual_hidden_default",
        "target_write_actual_status_applied": "lightweight_state_target_write_actual_applied_no_socket",
        "target_write_actual_capability": True,
        "actual_target_session_state_write_default": False,
        "target_write_allowed_effective_default": False,
        "target_session_state_write_allowed_effective_default": False,
        "target_session_state_write_applied_default": False,
        "target_session_state_mutated_default": False,
        "state_mutated_default": False,
        "messages_committed_now_default": 0,
        "target_write_actual_source": "q33k_target_lightweight_state_write_candidate",
        "target_write_actual_target": "provided_mutable_session_state_mapping_only",
        "target_write_actual_checks_gate_ready": True,
        "target_write_actual_checks_target_key": True,
        "target_write_actual_checks_message_count": True,
        "target_write_actual_checks_preview_only": True,
        "warroom_page_modified": False,
        "visible_controls_added": False,
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


def apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual(
    session_state: MutableMapping[str, Any],
    *,
    target_write_gate_packet: Mapping[str, Any] | None = None,
    lightweight_state_target_write_actual_requested: bool = False,
    operator_lightweight_state_target_write_actual_ack: bool = False,
) -> dict[str, Any]:
    gate_packet = dict(target_write_gate_packet or build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_gate_packet())
    value_preview = dict(gate_packet.get("target_lightweight_state_write_candidate") or gate_packet.get("target_lightweight_state_value_preview") or {})
    gate_ready = bool(gate_packet.get("target_write_gate_allowed_for_next_slice"))
    value_preview_valid = _target_value_preview_valid(value_preview)
    status = _target_write_actual_status(
        requested=bool(lightweight_state_target_write_actual_requested),
        ack=bool(operator_lightweight_state_target_write_actual_ack),
        gate_ready=gate_ready,
        value_preview_valid=value_preview_valid,
    )
    applied = status == "lightweight_state_target_write_actual_applied_no_socket"
    target_key = str(value_preview.get("target_key") or "")
    previous_value_present = bool(target_key and target_key in session_state)
    previous_value_kind = type(session_state.get(target_key)).__name__ if previous_value_present else ""
    if applied:
        session_state[target_key] = dict(value_preview)
    return {
        **build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_result_packet",
        "target_write_gate_packet": gate_packet,
        "target_lightweight_state_write_candidate": value_preview if applied else {},
        "lightweight_state_target_write_actual_requested": bool(lightweight_state_target_write_actual_requested),
        "operator_lightweight_state_target_write_actual_ack": bool(operator_lightweight_state_target_write_actual_ack),
        "target_write_gate_ready_for_next_slice": gate_ready,
        "target_lightweight_state_value_preview_validated": value_preview_valid,
        "target_write_actual_status": status,
        "actual_target_session_state_write": bool(applied),
        "target_write_allowed_effective": bool(applied),
        "target_session_state_write_allowed_effective": bool(applied),
        "target_session_state_write_applied": bool(applied),
        "target_session_state_mutated": bool(applied),
        "state_mutated": bool(applied),
        "messages_committed_now": 1 if applied else 0,
        "target_session_state_key": target_key,
        "target_message_count": int(value_preview.get("message_count") or 0),
        "target_latest_topic": str(value_preview.get("latest_topic") or ""),
        "target_latest_widget_id": str(value_preview.get("latest_widget_id") or ""),
        "target_latest_sequence": int(value_preview.get("latest_sequence") or 0),
        "previous_value_present": previous_value_present,
        "previous_value_kind": previous_value_kind,
        "written_value_present": bool(applied and target_key in session_state),
        "written_value_kind": type(session_state.get(target_key)).__name__ if applied else "",
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
