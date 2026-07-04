# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_source.py
# desc: WarRoom v2 receiver-only connect function source. Runtime-config callable source only; composes Q35N/Q35O and sends nothing.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_adapter_factory import build_warroom_v2_ws_receiver_only_client_adapter_factory_packet
from .ws_receiver_only_client_no_send_adapter import LowLevelConnectFn, build_warroom_v2_ws_receiver_only_client_no_send_adapter_factory

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_SOURCE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_source.ps_q35p.v1"
_CONNECT_FN_KEYS = ("low_level_connect_fn", "connect_fn")


def _runtime_keys(config: Mapping[str, Any]) -> list[str]:
    return sorted(str(key) for key in config.keys())


def _adapter_runtime_config(config: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in config.items() if str(key) not in _CONNECT_FN_KEYS}


def _connect_fn(config: Mapping[str, Any]) -> object:
    for key in _CONNECT_FN_KEYS:
        if key in config:
            return config[key]
    return None


def _status(*, allow_connect_fn_source: bool, connect_fn_present: bool, connect_fn_callable: bool) -> str:
    if not allow_connect_fn_source:
        return "receiver_only_client_connect_fn_source_blocked_allow_connect_fn_source_required"
    if not connect_fn_present:
        return "receiver_only_client_connect_fn_source_blocked_connect_fn_required"
    if not connect_fn_callable:
        return "receiver_only_client_connect_fn_source_blocked_connect_fn_not_callable"
    return "receiver_only_client_connect_fn_source_ready_to_build_q35o_adapter_factory_no_send"


def build_warroom_v2_ws_receiver_only_client_connect_fn_source_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "connect_fn_source_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CONNECT_FN_SOURCE_VERSION,
        "connect_fn_source_kind": "warroom_v2_ws_receiver_only_client_runtime_config_callable_source_no_send",
        "input_pipeline": ["q35p_connect_fn_source", "q35o_no_send_adapter", "q35n_adapter_factory", "q35m_runtime_wiring", "q35l_guarded_socket_open"],
        "composes_q35n_adapter_factory": True,
        "composes_q35o_no_send_adapter": True,
        "requires_runtime_config": True,
        "requires_low_level_connect_fn_from_runtime_config": True,
        "requires_allow_connect_fn_source_flag": True,
        "requires_q35n_q35m_q35l_guards": True,
        "connect_fn_called_at_source_build": False,
        "adapter_factory_created_only_after_source_allow_and_callable": True,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": True,
        "connect_fn_value_returned": False,
        "callable_values_forwarded_to_adapter_runtime_config": False,
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


def build_warroom_v2_ws_receiver_only_client_connect_fn_source_packet(
    *,
    compact_status_badge_packet: Mapping[str, Any] | None = None,
    runtime_config: Mapping[str, Any] | None = None,
    allow_connect_fn_source: bool = False,
    allow_adapter_factory: bool = False,
    operator_scope_ack: bool = False,
    socket_open_requested: bool = False,
    operator_socket_open_ack: bool = False,
    allow_socket_open: bool = False,
) -> dict[str, Any]:
    config = dict(runtime_config or {})
    source_value = _connect_fn(config)
    connect_fn_present = source_value is not None
    connect_fn_callable = callable(source_value)
    source_status = _status(
        allow_connect_fn_source=bool(allow_connect_fn_source),
        connect_fn_present=connect_fn_present,
        connect_fn_callable=connect_fn_callable,
    )
    adapter_config = _adapter_runtime_config(config)
    adapter_factory = None
    adapter_factory_created = False
    if source_status == "receiver_only_client_connect_fn_source_ready_to_build_q35o_adapter_factory_no_send":
        adapter_factory_created = True
        adapter_factory = build_warroom_v2_ws_receiver_only_client_no_send_adapter_factory(connect_fn=source_value)  # type: ignore[arg-type]
    adapter_factory_packet = build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
        compact_status_badge_packet=compact_status_badge_packet,
        runtime_config=adapter_config,
        adapter_factory=adapter_factory,
        allow_adapter_factory=allow_adapter_factory,
        operator_scope_ack=operator_scope_ack,
        socket_open_requested=socket_open_requested,
        operator_socket_open_ack=operator_socket_open_ack,
        allow_socket_open=allow_socket_open,
    )
    return {
        **build_warroom_v2_ws_receiver_only_client_connect_fn_source_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_connect_fn_source_packet",
        "connect_fn_source_status": source_status,
        "allow_connect_fn_source": bool(allow_connect_fn_source),
        "connect_fn_present": connect_fn_present,
        "connect_fn_callable": connect_fn_callable,
        "adapter_factory_created": adapter_factory_created,
        "runtime_config_present": bool(config),
        "runtime_config_keys": _runtime_keys(config),
        "adapter_runtime_config_keys": _runtime_keys(adapter_config),
        "runtime_config_redacted": {"present": bool(config), "keys": _runtime_keys(config)},
        "adapter_factory_packet": adapter_factory_packet,
        "adapter_factory_status": str(adapter_factory_packet.get("adapter_factory_status") or ""),
        "adapter_factory_called": bool(adapter_factory_packet.get("adapter_factory_called")),
        "runtime_wiring_status": str(adapter_factory_packet.get("runtime_wiring_status") or ""),
        "socket_open_attempted": bool(adapter_factory_packet.get("socket_open_attempted")),
        "socket_opened": bool(adapter_factory_packet.get("socket_opened")),
        "client_started": bool(adapter_factory_packet.get("client_started")),
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
