# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health.py
# desc: WarRoom v2 receiver-only compact hidden health summary for registry surface readiness. Metadata-only; no page, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_COMPACT_HIDDEN_HEALTH_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health.ps_q35u.v1"
_Q35T_PACKET_KIND = "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback_packet"


def _status(*, allow_health: bool, present: bool, mapping: bool, kind: str) -> str:
    if not allow_health:
        return "receiver_only_client_registry_surface_compact_hidden_health_blocked_allow_health_required"
    if not present:
        return "receiver_only_client_registry_surface_compact_hidden_health_missing_readback"
    if not mapping:
        return "receiver_only_client_registry_surface_compact_hidden_health_invalid_readback"
    if kind != _Q35T_PACKET_KIND:
        return "receiver_only_client_registry_surface_compact_hidden_health_unrecognized_readback"
    return "receiver_only_client_registry_surface_compact_hidden_health_ready_no_send"


def _health_status(packet: Mapping[str, Any]) -> str:
    if bool(packet.get("socket_opened")):
        return "opened_no_send"
    if bool(packet.get("socket_open_attempted")):
        return "attempted_not_open_no_send"
    if bool(packet.get("registry_surface_ready")) and bool(packet.get("connect_fn_source_ready")):
        return "waiting_socket_guards"
    if bool(packet.get("registry_surface_ready")):
        return "registry_ready"
    return "blocked"


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "compact_hidden_health_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_COMPACT_HIDDEN_HEALTH_VERSION,
        "compact_hidden_health_kind": "warroom_v2_ws_receiver_only_client_registry_surface_compact_hidden_health_metadata_only_no_send",
        "input_pipeline": ["q35t_hidden_record_readback", "q35u_compact_hidden_health"],
        "requires_hidden_record_readback_packet": True,
        "requires_allow_compact_hidden_health_flag": True,
        "read_only": True,
        "metadata_only": True,
        "hidden_health_summary": True,
        "raw_hidden_record_readback_returned": False,
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
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "connect_fn_called_at_compact_health": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "global_registry_mutated": False,
        "receiver_safe_to_remain_idle": True,
        "safe_receiver_preparation_checkpoint": "cp1",
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


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_packet(
    hidden_record_readback_packet: Mapping[str, Any] | object | None = None,
    *,
    allow_compact_hidden_health: bool = False,
) -> dict[str, Any]:
    present = hidden_record_readback_packet is not None
    mapping = isinstance(hidden_record_readback_packet, Mapping)
    packet = dict(hidden_record_readback_packet) if mapping else {}
    kind = str(packet.get("packet_kind") or "")
    status = _status(allow_health=allow_compact_hidden_health, present=present, mapping=mapping, kind=kind)
    ready = status == "receiver_only_client_registry_surface_compact_hidden_health_ready_no_send"
    health_status = _health_status(packet) if ready else "blocked"
    cp1_ready_statuses = {"waiting_socket_guards", "attempted_not_open_no_send", "opened_no_send"}
    return {
        **build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_compact_hidden_health_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_registry_surface_compact_hidden_health_packet",
        "hidden_record_readback_present": present,
        "hidden_record_readback_is_mapping": mapping,
        "hidden_record_readback_kind_recognized": (kind == _Q35T_PACKET_KIND) if ready else False,
        "compact_hidden_health_status": status,
        "compact_hidden_health_ready": ready,
        "receiver_health_status": health_status,
        "receiver_health_label": f"ws_receiver_{health_status}",
        "registry_surface_ready": bool(packet.get("registry_surface_ready")) if ready else False,
        "connect_fn_source_ready": bool(packet.get("connect_fn_source_ready")) if ready else False,
        "adapter_factory_called": bool(packet.get("adapter_factory_called")) if ready else False,
        "socket_open_attempted": bool(packet.get("socket_open_attempted")) if ready else False,
        "socket_opened": bool(packet.get("socket_opened")) if ready else False,
        "client_started": bool(packet.get("client_started")) if ready else False,
        "cp1_health_summary_ready": ready and health_status in cp1_ready_statuses,
        "receiver_safe_to_remain_idle": True,
        "safe_receiver_preparation_checkpoint": "cp1",
        "read_only": True,
        "metadata_only": True,
        "raw_hidden_record_readback_returned": False,
        "raw_hidden_record_value_returned": False,
        "session_state_keys_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "connect_fn_called_at_compact_health": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "global_registry_mutated": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
