# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_adapter_factory.py
# desc: WarRoom v2 receiver-only client adapter factory boundary. Builds injected opener from explicit runtime config only; no default network client and no send.

from __future__ import annotations

from typing import Any, Callable, Mapping

from .ws_receiver_only_client_guarded_socket_open import SocketOpenFn
from .ws_receiver_only_client_runtime_wiring import build_warroom_v2_ws_receiver_only_client_runtime_wiring_packet
from .ws_receiver_only_client_start_preflight import build_warroom_v2_ws_receiver_only_client_start_preflight_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_ADAPTER_FACTORY_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_adapter_factory.ps_q35n.v1"
AdapterFactoryFn = Callable[[Mapping[str, Any]], SocketOpenFn | object]


def _endpoint_url(config: Mapping[str, Any]) -> str:
    return str(config.get("receiver_endpoint_url") or config.get("endpoint_url") or "")


def _factory_status(
    *,
    preflight_ready: bool,
    endpoint_url: str,
    adapter_factory_present: bool,
    allow_adapter_factory: bool,
    socket_open_requested: bool,
    operator_socket_open_ack: bool,
    allow_socket_open: bool,
) -> str:
    if not preflight_ready:
        return "receiver_only_client_adapter_factory_blocked_preflight_required"
    if not endpoint_url.strip():
        return "receiver_only_client_adapter_factory_blocked_endpoint_config_required"
    if not allow_adapter_factory:
        return "receiver_only_client_adapter_factory_blocked_allow_adapter_factory_flag_required"
    if not socket_open_requested:
        return "receiver_only_client_adapter_factory_blocked_socket_open_request_required"
    if not operator_socket_open_ack:
        return "receiver_only_client_adapter_factory_blocked_operator_socket_open_ack_required"
    if not allow_socket_open:
        return "receiver_only_client_adapter_factory_blocked_allow_socket_open_flag_required"
    if not adapter_factory_present:
        return "receiver_only_client_adapter_factory_blocked_injected_adapter_factory_required"
    return "receiver_only_client_adapter_factory_ready_to_build_injected_opener_no_send"


def build_warroom_v2_ws_receiver_only_client_adapter_factory_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "adapter_factory_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_ADAPTER_FACTORY_VERSION,
        "adapter_factory_kind": "warroom_v2_ws_receiver_only_client_adapter_factory_runtime_config_injected_factory_no_send",
        "input_pipeline": ["q35j_compact_status_badge_state_presence", "q35k_preflight", "q35m_runtime_wiring"],
        "composes_q35k_preflight": True,
        "composes_q35m_runtime_wiring": True,
        "requires_runtime_config": True,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": True,
        "requires_endpoint_url_from_runtime_config": True,
        "requires_allow_adapter_factory_flag": True,
        "requires_injected_adapter_factory": True,
        "adapter_factory_called_only_after_preflight_ready": True,
        "adapter_factory_called_only_after_endpoint_present": True,
        "adapter_factory_called_only_after_allow_flag": True,
        "adapter_factory_called_only_after_socket_open_requested": True,
        "adapter_factory_called_only_after_operator_socket_open_ack": True,
        "adapter_factory_called_only_after_allow_socket_open": True,
        "injected_adapter_factory_only": True,
        "injected_opener_only": True,
        "no_hardcoded_endpoint": True,
        "no_default_network_client": True,
        "send_disabled": True,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "renders_badge_now": False,
        "renders_card_now": False,
        "renders_balloon_now": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "streamlit_imported": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
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


def build_warroom_v2_ws_receiver_only_client_adapter_factory_packet(
    *,
    compact_status_badge_packet: Mapping[str, Any] | None = None,
    runtime_config: Mapping[str, Any] | None = None,
    adapter_factory: AdapterFactoryFn | None = None,
    allow_adapter_factory: bool = False,
    operator_scope_ack: bool = False,
    socket_open_requested: bool = False,
    operator_socket_open_ack: bool = False,
    allow_socket_open: bool = False,
) -> dict[str, Any]:
    config = dict(runtime_config or {})
    endpoint = _endpoint_url(config)
    preflight_packet = build_warroom_v2_ws_receiver_only_client_start_preflight_packet(
        compact_status_badge_packet=compact_status_badge_packet,
        operator_scope_ack=operator_scope_ack,
    )
    preflight_ready = bool(preflight_packet.get("ready_for_guarded_socket_open_next_slice"))
    factory_status = _factory_status(
        preflight_ready=preflight_ready,
        endpoint_url=endpoint,
        adapter_factory_present=adapter_factory is not None,
        allow_adapter_factory=bool(allow_adapter_factory),
        socket_open_requested=bool(socket_open_requested),
        operator_socket_open_ack=bool(operator_socket_open_ack),
        allow_socket_open=bool(allow_socket_open),
    )
    opener: SocketOpenFn | None = None
    factory_error: dict[str, Any] = {}
    factory_called = False
    if factory_status == "receiver_only_client_adapter_factory_ready_to_build_injected_opener_no_send" and adapter_factory is not None:
        factory_called = True
        try:
            candidate = adapter_factory(config)
            opener = candidate if callable(candidate) else None
            if opener is None:
                factory_error = {"error_type": "AdapterFactoryReturnedNonCallable", "error_message": type(candidate).__name__}
                factory_status = "receiver_only_client_adapter_factory_failed_non_callable_opener_no_send"
        except Exception as exc:  # noqa: BLE001 - boundary reports factory failure as data.
            factory_error = {"error_type": type(exc).__name__, "error_message": str(exc)}
            factory_status = "receiver_only_client_adapter_factory_failed_exception_no_send"
    runtime_wiring_packet = build_warroom_v2_ws_receiver_only_client_runtime_wiring_packet(
        compact_status_badge_packet=compact_status_badge_packet,
        operator_scope_ack=operator_scope_ack,
        endpoint_url=endpoint,
        socket_open_requested=socket_open_requested,
        operator_socket_open_ack=operator_socket_open_ack,
        allow_socket_open=allow_socket_open,
        socket_open_fn=opener,
    )
    return {
        **build_warroom_v2_ws_receiver_only_client_adapter_factory_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_adapter_factory_packet",
        "runtime_config_present": bool(config),
        "runtime_config_keys": sorted(str(key) for key in config.keys()),
        "runtime_config_redacted": {"present": bool(config), "keys": sorted(str(key) for key in config.keys())},
        "endpoint_url_present": bool(endpoint.strip()),
        "endpoint_url_redacted": "<provided>" if endpoint.strip() else "",
        "allow_adapter_factory": bool(allow_adapter_factory),
        "adapter_factory_present": adapter_factory is not None,
        "adapter_factory_called": factory_called,
        "adapter_factory_error": factory_error,
        "adapter_factory_status": factory_status,
        "preflight_packet": preflight_packet,
        "runtime_wiring_packet": runtime_wiring_packet,
        "runtime_wiring_status": str(runtime_wiring_packet.get("runtime_wiring_status") or ""),
        "socket_open_attempted": bool(runtime_wiring_packet.get("socket_open_attempted")),
        "socket_opened": bool(runtime_wiring_packet.get("socket_opened")),
        "client_started": bool(runtime_wiring_packet.get("client_started")),
        "websocket_enabled": bool(runtime_wiring_packet.get("websocket_enabled")),
        "runtime_connected": bool(runtime_wiring_packet.get("runtime_connected")),
        "push_connected": bool(runtime_wiring_packet.get("push_connected")),
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
