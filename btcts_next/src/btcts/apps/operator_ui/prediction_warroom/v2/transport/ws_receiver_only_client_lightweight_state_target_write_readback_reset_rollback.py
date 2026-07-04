# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback.py
# desc: WarRoom v2 receiver-only client lightweight-state target write readback/reset/rollback diagnostics. Default-off/operator-gated, no socket open, no send.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from .ws_receiver_only_client_lightweight_state_target_write_actual import build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_contract

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_READBACK_RESET_ROLLBACK_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback.ps_q33m.v1"


def _value_valid(value: Mapping[str, Any]) -> bool:
    return bool(value.get("target_key")) and int(value.get("message_count") or 0) > 0 and bool(value.get("preview_only"))


def _target_key_from(result_packet: Mapping[str, Any] | None, explicit: str) -> str:
    if explicit:
        return explicit
    packet = dict(result_packet or {})
    return str(packet.get("target_session_state_key") or "")


def build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "target_write_readback_reset_rollback_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_READBACK_RESET_ROLLBACK_VERSION,
        "target_write_readback_reset_rollback_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_default_off_no_socket",
        "input_pipeline": ["q33l_target_write_actual", "q33k_target_write_gate", "q33j_target_write_hidden_record"],
        "readback_diagnostic_available": True,
        "reset_requested_default": False,
        "operator_reset_ack_default": False,
        "rollback_requested_default": False,
        "operator_rollback_ack_default": False,
        "reset_status_default": "target_write_reset_hidden_default",
        "rollback_status_default": "target_write_rollback_hidden_default",
        "target_write_actual_contract_kind": build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_actual_contract()["target_write_actual_kind"],
        "target_write_readback_target": "provided_mutable_session_state_mapping_only",
        "target_write_reset_requires_request_ack": True,
        "target_write_rollback_requires_request_ack_and_valid_value": True,
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


def apply_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback(
    session_state: MutableMapping[str, Any],
    *,
    target_write_actual_result_packet: Mapping[str, Any] | None = None,
    target_session_state_key: str = "",
    reset_requested: bool = False,
    operator_reset_ack: bool = False,
    rollback_requested: bool = False,
    operator_rollback_ack: bool = False,
    rollback_value: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    target_key = _target_key_from(target_write_actual_result_packet, target_session_state_key)
    before_present = bool(target_key and target_key in session_state)
    before_value = session_state.get(target_key) if before_present else None
    before_kind = type(before_value).__name__ if before_present else ""
    reset_status = "target_write_reset_hidden_default"
    rollback_status = "target_write_rollback_hidden_default"
    reset_applied = False
    rollback_applied = False
    if reset_requested:
        if not operator_reset_ack:
            reset_status = "target_write_reset_blocked_operator_ack_required"
        elif not before_present:
            reset_status = "target_write_reset_blocked_target_missing"
        else:
            session_state.pop(target_key, None)
            reset_applied = True
            reset_status = "target_write_reset_applied_no_socket"
    rollback_payload = dict(rollback_value or {})
    if rollback_requested:
        if not operator_rollback_ack:
            rollback_status = "target_write_rollback_blocked_operator_ack_required"
        elif not _value_valid(rollback_payload):
            rollback_status = "target_write_rollback_blocked_valid_rollback_value_required"
        elif target_key and rollback_payload.get("target_key") != target_key:
            rollback_status = "target_write_rollback_blocked_target_key_mismatch"
        else:
            session_state[target_key] = rollback_payload
            rollback_applied = True
            rollback_status = "target_write_rollback_applied_no_socket"
    after_present = bool(target_key and target_key in session_state)
    after_value = session_state.get(target_key) if after_present else None
    after_kind = type(after_value).__name__ if after_present else ""
    mutated = reset_applied or rollback_applied
    return {
        **build_warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_lightweight_state_target_write_readback_reset_rollback_packet",
        "target_write_actual_result_packet": dict(target_write_actual_result_packet or {}),
        "target_session_state_key": target_key,
        "readback_before_present": before_present,
        "readback_before_value_kind": before_kind,
        "readback_before_message_count": int(before_value.get("message_count") or 0) if isinstance(before_value, Mapping) else 0,
        "readback_after_present": after_present,
        "readback_after_value_kind": after_kind,
        "readback_after_message_count": int(after_value.get("message_count") or 0) if isinstance(after_value, Mapping) else 0,
        "reset_requested": bool(reset_requested),
        "operator_reset_ack": bool(operator_reset_ack),
        "reset_status": reset_status,
        "reset_applied": bool(reset_applied),
        "rollback_requested": bool(rollback_requested),
        "operator_rollback_ack": bool(operator_rollback_ack),
        "rollback_status": rollback_status,
        "rollback_applied": bool(rollback_applied),
        "rollback_value_validated": _value_valid(rollback_payload),
        "target_session_state_mutated": bool(mutated),
        "state_mutated": bool(mutated),
        "messages_committed_now": 1 if rollback_applied else 0,
        "messages_removed_now": 1 if reset_applied else 0,
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
