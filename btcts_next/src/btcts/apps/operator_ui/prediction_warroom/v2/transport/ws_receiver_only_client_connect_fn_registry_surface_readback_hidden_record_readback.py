# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback.py
# desc: WarRoom v2 receiver-only registry surface hidden-record readback. Metadata-only readback of Q35S record; no raw value, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record import WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_READBACK_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback.ps_q35t.v1"
_RECORD_KIND = "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_value"


def _status(*, allow_readback: bool, present: bool, mapping: bool, kind: str) -> str:
    if not allow_readback:
        return "receiver_only_client_registry_surface_hidden_record_readback_blocked_allow_readback_required"
    if not present:
        return "receiver_only_client_registry_surface_hidden_record_readback_missing_record"
    if not mapping:
        return "receiver_only_client_registry_surface_hidden_record_readback_invalid_record"
    if kind != _RECORD_KIND:
        return "receiver_only_client_registry_surface_hidden_record_readback_unrecognized_record"
    return "receiver_only_client_registry_surface_hidden_record_readback_present_metadata_only_no_send"


def _label(value: Mapping[str, Any]) -> str:
    if bool(value.get("socket_opened")):
        return "recorded_opened_no_send"
    if bool(value.get("socket_open_attempted")):
        return "recorded_attempted_not_open_no_send"
    if bool(value.get("registry_surface_ready")) and bool(value.get("connect_fn_source_ready")):
        return "recorded_ready_waiting_socket_guards"
    if bool(value.get("registry_surface_ready")):
        return "recorded_registry_ready_waiting_source_guard"
    return "recorded_blocked"


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "hidden_record_readback_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_READBACK_VERSION,
        "source_hidden_record_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY,
        "hidden_record_readback_kind": "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_metadata_only_no_send",
        "input_pipeline": ["q35s_hidden_session_state_record", "q35t_hidden_record_readback"],
        "requires_session_state_mapping": True,
        "requires_allow_hidden_record_readback_flag": True,
        "read_only": True,
        "metadata_only": True,
        "hidden_readback_diagnostic": True,
        "raw_hidden_record_value_returned": False,
        "raw_readback_packet_recorded": False,
        "raw_registry_surface_packet_returned": False,
        "session_state_keys_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "connect_fn_called_at_hidden_record_readback": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
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


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet(
    session_state: Mapping[str, Any] | None = None,
    *,
    allow_hidden_record_readback: bool = False,
    state_key: str = WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_KEY,
) -> dict[str, Any]:
    state = session_state or {}
    present = state_key in state
    value = state.get(state_key)
    mapping = isinstance(value, Mapping)
    record = dict(value) if mapping else {}
    kind = str(record.get("packet_kind") or "")
    status = _status(allow_readback=allow_hidden_record_readback, present=present, mapping=mapping, kind=kind)
    ready = status == "receiver_only_client_registry_surface_hidden_record_readback_present_metadata_only_no_send"
    return {
        **build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet",
        "state_key": state_key,
        "hidden_record_present": present,
        "hidden_record_value_is_mapping": mapping,
        "hidden_record_kind_recognized": kind == _RECORD_KIND if ready else False,
        "hidden_record_readback_status": status,
        "hidden_record_readback_ready": ready,
        "hidden_record_readiness_label": _label(record) if ready else "blocked",
        "registry_surface_readback_status": str(record.get("registry_surface_readback_status") or "") if ready else "",
        "readback_readiness_label": str(record.get("readback_readiness_label") or "") if ready else "",
        "registry_surface_ready": bool(record.get("registry_surface_ready")) if ready else False,
        "connect_fn_source_ready": bool(record.get("connect_fn_source_ready")) if ready else False,
        "adapter_factory_called": bool(record.get("adapter_factory_called")) if ready else False,
        "socket_open_attempted": bool(record.get("socket_open_attempted")) if ready else False,
        "socket_opened": bool(record.get("socket_opened")) if ready else False,
        "client_started": bool(record.get("client_started")) if ready else False,
        "read_only": True,
        "metadata_only": True,
        "raw_hidden_record_value_returned": False,
        "raw_readback_packet_recorded": False,
        "raw_registry_surface_packet_returned": False,
        "session_state_keys_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "connect_fn_called_at_hidden_record_readback": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "global_registry_mutated": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
