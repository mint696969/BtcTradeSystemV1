# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback.py
# desc: WarRoom v2 receiver-only connect_fn registry surface hidden readback. Pure metadata readback only; no registry values, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback.ps_q35r.v1"
_READY_SURFACE = "receiver_only_client_connect_fn_registry_surface_ready_to_call_q35p_source_no_send"
_READY_SOURCE = "receiver_only_client_connect_fn_source_ready_to_build_q35o_adapter_factory_no_send"


def _status(*, allow_readback: bool, present: bool, mapping: bool, kind: str) -> str:
    if not allow_readback:
        return "receiver_only_client_connect_fn_registry_surface_readback_blocked_allow_readback_required"
    if not present:
        return "receiver_only_client_connect_fn_registry_surface_readback_missing_packet"
    if not mapping:
        return "receiver_only_client_connect_fn_registry_surface_readback_invalid_packet"
    if kind != "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet":
        return "receiver_only_client_connect_fn_registry_surface_readback_unrecognized_packet"
    return "receiver_only_client_connect_fn_registry_surface_readback_present_hidden_no_send"


def _readiness_label(*, surface_ready: bool, source_ready: bool, socket_opened: bool, socket_attempted: bool) -> str:
    if socket_opened:
        return "opened_no_send"
    if socket_attempted:
        return "attempted_not_open_no_send"
    if surface_ready and source_ready:
        return "ready_waiting_socket_guards"
    if surface_ready:
        return "registry_ready_waiting_source_guard"
    return "blocked"


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "registry_surface_readback_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_VERSION,
        "registry_surface_readback_kind": "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_metadata_only_no_send",
        "input_pipeline": ["q35q_connect_fn_registry_surface", "q35r_hidden_readback"],
        "requires_registry_surface_packet": True,
        "requires_allow_registry_surface_readback_flag": True,
        "read_only": True,
        "metadata_only": True,
        "hidden_readback_diagnostic": True,
        "raw_registry_surface_packet_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "connect_fn_called_at_readback": False,
        "global_registry_mutated": False,
        "no_hardcoded_endpoint": True,
        "no_default_network_client": True,
        "send_disabled": True,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "streamlit_imported": False,
        "streamlit_render_invoked": False,
        "aggregator_exports_added": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet(
    registry_surface_packet: Mapping[str, Any] | object | None = None,
    *,
    allow_registry_surface_readback: bool = False,
) -> dict[str, Any]:
    present = registry_surface_packet is not None
    mapping = isinstance(registry_surface_packet, Mapping)
    packet = dict(registry_surface_packet) if mapping else {}
    kind = str(packet.get("packet_kind") or "")
    readback_status = _status(allow_readback=allow_registry_surface_readback, present=present, mapping=mapping, kind=kind)
    ready = readback_status == "receiver_only_client_connect_fn_registry_surface_readback_present_hidden_no_send"
    surface_status = str(packet.get("registry_surface_status") or "") if ready else ""
    source_status = str(packet.get("connect_fn_source_status") or "") if ready else ""
    adapter_status = str(packet.get("adapter_factory_status") or "") if ready else ""
    runtime_status = str(packet.get("runtime_wiring_status") or "") if ready else ""
    surface_ready = surface_status == _READY_SURFACE
    source_ready = source_status == _READY_SOURCE
    socket_attempted = bool(packet.get("socket_open_attempted")) if ready else False
    socket_opened = bool(packet.get("socket_opened")) if ready else False
    label = _readiness_label(surface_ready=surface_ready, source_ready=source_ready, socket_opened=socket_opened, socket_attempted=socket_attempted)
    return {
        **build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_packet",
        "registry_surface_packet_present": present,
        "registry_surface_packet_is_mapping": mapping,
        "registry_surface_packet_kind_recognized": kind == "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet" if ready else False,
        "registry_surface_readback_status": readback_status,
        "registry_surface_readback_ready": ready,
        "registry_surface_status": surface_status,
        "connect_fn_source_status": source_status,
        "adapter_factory_status": adapter_status,
        "runtime_wiring_status": runtime_status,
        "registry_surface_ready": surface_ready,
        "connect_fn_source_ready": source_ready,
        "adapter_factory_called": bool(packet.get("adapter_factory_called")) if ready else False,
        "socket_open_attempted": socket_attempted,
        "socket_opened": socket_opened,
        "client_started": bool(packet.get("client_started")) if ready else False,
        "readback_readiness_label": label,
        "read_only": True,
        "metadata_only": True,
        "hidden_readback_diagnostic": True,
        "raw_registry_surface_packet_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "connect_fn_called_at_readback": False,
        "global_registry_mutated": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
