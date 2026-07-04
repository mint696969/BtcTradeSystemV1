# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface.py
# desc: WarRoom v2 receiver-only connect_fn registry surface. Explicit in-memory mapping only; composes Q35P and sends nothing.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_connect_fn_source import build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface.ps_q35q.v1"
_REGISTRY_KEY_FIELDS = ("connect_fn_registration_key", "connect_fn_name", "receiver_connect_fn_key")
_DIRECT_CONNECT_FN_FIELDS = ("low_level_connect_fn", "connect_fn")


def _keys(mapping: Mapping[str, Any]) -> list[str]:
    return sorted(str(key) for key in mapping.keys())


def _registration_key(config: Mapping[str, Any]) -> str:
    for key in _REGISTRY_KEY_FIELDS:
        value = str(config.get(key) or "")
        if value.strip():
            return value
    return ""


def _adapter_runtime_config(config: Mapping[str, Any], connect_fn: object | None) -> dict[str, Any]:
    blocked = {*_REGISTRY_KEY_FIELDS, *_DIRECT_CONNECT_FN_FIELDS}
    merged = {str(key): value for key, value in config.items() if str(key) not in blocked}
    if connect_fn is not None:
        merged["low_level_connect_fn"] = connect_fn
    return merged


def _status(*, allow_registration_surface: bool, registration_key: str, registered: bool, callable_value: bool) -> str:
    if not allow_registration_surface:
        return "receiver_only_client_connect_fn_registry_surface_blocked_allow_registration_surface_required"
    if not registration_key.strip():
        return "receiver_only_client_connect_fn_registry_surface_blocked_registration_key_required"
    if not registered:
        return "receiver_only_client_connect_fn_registry_surface_blocked_registration_missing"
    if not callable_value:
        return "receiver_only_client_connect_fn_registry_surface_blocked_registration_not_callable"
    return "receiver_only_client_connect_fn_registry_surface_ready_to_call_q35p_source_no_send"


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "connect_fn_registry_surface_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_VERSION,
        "registry_surface_kind": "warroom_v2_ws_receiver_only_client_in_memory_registry_mapping_no_send",
        "input_pipeline": ["q35q_connect_fn_registry_surface", "q35p_connect_fn_source", "q35o_no_send_adapter", "q35n_adapter_factory", "q35m_runtime_wiring", "q35l_guarded_socket_open"],
        "composes_q35p_connect_fn_source": True,
        "requires_registry_mapping": True,
        "requires_registration_key_from_runtime_config": True,
        "requires_allow_registration_surface_flag": True,
        "requires_allow_connect_fn_source_flag": True,
        "registry_values_returned": False,
        "callable_values_returned": False,
        "callable_values_stored_globally": False,
        "direct_connect_fn_from_runtime_config_ignored": True,
        "global_registry_mutated": False,
        "connect_fn_called_at_registration_surface": False,
        "q35p_source_build_still_does_not_call_connect_fn": True,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": True,
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


def build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet(
    *,
    compact_status_badge_packet: Mapping[str, Any] | None = None,
    runtime_config: Mapping[str, Any] | None = None,
    connect_fn_registry: Mapping[str, object] | None = None,
    allow_registration_surface: bool = False,
    allow_connect_fn_source: bool = False,
    allow_adapter_factory: bool = False,
    operator_scope_ack: bool = False,
    socket_open_requested: bool = False,
    operator_socket_open_ack: bool = False,
    allow_socket_open: bool = False,
) -> dict[str, Any]:
    config = dict(runtime_config or {})
    registry = dict(connect_fn_registry or {})
    registration_key = _registration_key(config)
    registered_value = registry.get(registration_key)
    registered = registration_key in registry
    callable_value = callable(registered_value)
    surface_status = _status(allow_registration_surface=bool(allow_registration_surface), registration_key=registration_key, registered=registered, callable_value=callable_value)
    adapter_config = _adapter_runtime_config(config, registered_value if surface_status.endswith("ready_to_call_q35p_source_no_send") else None)
    source_packet = build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet(
        compact_status_badge_packet=compact_status_badge_packet,
        runtime_config=adapter_config,
        allow_connect_fn_source=allow_connect_fn_source,
        allow_adapter_factory=allow_adapter_factory,
        operator_scope_ack=operator_scope_ack,
        socket_open_requested=socket_open_requested,
        operator_socket_open_ack=operator_socket_open_ack,
        allow_socket_open=allow_socket_open,
    )
    return {
        **build_warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_packet",
        "registry_surface_status": surface_status,
        "allow_registration_surface": bool(allow_registration_surface),
        "registration_key_present": bool(registration_key.strip()),
        "registration_key_redacted": "<provided>" if registration_key.strip() else "",
        "registered_connect_fn_present": registered,
        "registered_connect_fn_callable": callable_value,
        "registry_keys": _keys(registry),
        "runtime_config_present": bool(config),
        "runtime_config_keys": _keys(config),
        "adapter_runtime_config_keys": _keys(adapter_config),
        "runtime_config_redacted": {"present": bool(config), "keys": _keys(config)},
        "connect_fn_source_packet": source_packet,
        "connect_fn_source_status": str(source_packet.get("connect_fn_source_status") or ""),
        "adapter_factory_status": str(source_packet.get("adapter_factory_status") or ""),
        "adapter_factory_called": bool(source_packet.get("adapter_factory_called")),
        "runtime_wiring_status": str(source_packet.get("runtime_wiring_status") or ""),
        "socket_open_attempted": bool(source_packet.get("socket_open_attempted")),
        "socket_opened": bool(source_packet.get("socket_opened")),
        "client_started": bool(source_packet.get("client_started")),
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
