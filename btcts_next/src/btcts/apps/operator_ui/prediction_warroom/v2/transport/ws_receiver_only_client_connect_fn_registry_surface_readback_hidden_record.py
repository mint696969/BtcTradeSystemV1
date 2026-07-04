# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record.py
# desc: WarRoom v2 receiver-only registry surface readback hidden session-state record. Default-off metadata-only record; no page, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record.ps_q35s.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY = "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_q35s"


def _record_status(*, requested: bool, ack: bool, readback_ready: bool, session_state_present: bool) -> str:
    if not requested:
        return "receiver_only_client_registry_surface_readback_hidden_record_default_off"
    if not ack:
        return "receiver_only_client_registry_surface_readback_hidden_record_blocked_operator_ack_required"
    if not readback_ready:
        return "receiver_only_client_registry_surface_readback_hidden_record_blocked_readback_ready_required"
    if not session_state_present:
        return "receiver_only_client_registry_surface_readback_hidden_record_blocked_session_state_required"
    return "receiver_only_client_registry_surface_readback_hidden_record_applied_no_send"


def _metadata_record(readback_packet: Mapping[str, Any], *, state_key: str) -> dict[str, Any]:
    return {
        "packet_kind": "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_value",
        "state_key": state_key,
        "registry_surface_readback_status": str(readback_packet.get("registry_surface_readback_status") or ""),
        "readback_readiness_label": str(readback_packet.get("readback_readiness_label") or ""),
        "registry_surface_ready": bool(readback_packet.get("registry_surface_ready")),
        "connect_fn_source_ready": bool(readback_packet.get("connect_fn_source_ready")),
        "adapter_factory_called": bool(readback_packet.get("adapter_factory_called")),
        "socket_open_attempted": bool(readback_packet.get("socket_open_attempted")),
        "socket_opened": bool(readback_packet.get("socket_opened")),
        "client_started": bool(readback_packet.get("client_started")),
        "metadata_only": True,
        "raw_registry_surface_packet_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "would_send_to_broker": False,
    }


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "registry_surface_readback_hidden_record_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_VERSION,
        "hidden_record_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY,
        "hidden_record_kind": "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_default_off_no_send",
        "input_pipeline": ["q35r_registry_surface_readback", "q35s_hidden_session_state_record"],
        "requires_registry_surface_readback_packet": True,
        "requires_hidden_record_request": True,
        "requires_operator_hidden_record_ack": True,
        "requires_mutable_session_state_mapping": True,
        "hidden_record_requested_default": False,
        "operator_hidden_record_ack_default": False,
        "hidden_session_state_recorded": True,
        "hidden_record_effective_mutation_scope": "provided_session_state_key_only",
        "record_metadata_only": True,
        "raw_readback_packet_recorded": False,
        "raw_registry_surface_packet_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "connect_fn_called_at_hidden_record": False,
        "global_registry_mutated": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "streamlit_imported": False,
        "streamlit_render_invoked": False,
        "aggregator_exports_added": False,
        "receiver_only": True,
        "send_disabled": True,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def apply_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record(
    session_state: MutableMapping[str, Any] | None,
    *,
    registry_surface_readback_packet: Mapping[str, Any] | None = None,
    hidden_record_requested: bool = False,
    operator_hidden_record_ack: bool = False,
    state_key: str = WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY,
) -> dict[str, Any]:
    readback = dict(registry_surface_readback_packet or {})
    readback_ready = bool(readback.get("registry_surface_readback_ready")) and readback.get("packet_kind") == "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet"
    before_present = bool(session_state is not None and state_key in session_state)
    status = _record_status(requested=hidden_record_requested, ack=operator_hidden_record_ack, readback_ready=readback_ready, session_state_present=session_state is not None)
    record_applied = status == "receiver_only_client_registry_surface_readback_hidden_record_applied_no_send"
    record = _metadata_record(readback, state_key=state_key) if record_applied else {}
    if record_applied and session_state is not None:
        session_state[state_key] = record
    after_present = bool(session_state is not None and state_key in session_state)
    return {
        **build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_packet",
        "state_key": state_key,
        "hidden_record_requested": bool(hidden_record_requested),
        "operator_hidden_record_ack": bool(operator_hidden_record_ack),
        "registry_surface_readback_packet_present": bool(registry_surface_readback_packet),
        "registry_surface_readback_ready": readback_ready,
        "hidden_record_status": status,
        "hidden_record_applied": record_applied,
        "hidden_record_before_present": before_present,
        "hidden_record_after_present": after_present,
        "hidden_record_value": record,
        "target_session_state_mutated": record_applied,
        "state_mutated": record_applied,
        "messages_committed_now": 1 if record_applied else 0,
        "raw_readback_packet_recorded": False,
        "raw_registry_surface_packet_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "connect_fn_called_at_hidden_record": False,
        "global_registry_mutated": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
