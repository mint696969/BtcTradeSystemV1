# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_no_send_adapter.py
# desc: WarRoom v2 receiver-only no-send adapter implementation. Explicit low-level connect function injection only; no default network client and no send.

from __future__ import annotations

from typing import Any, Callable, Mapping

from .ws_receiver_only_client_guarded_socket_open import SocketOpenFn

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_no_send_adapter.ps_q35o.v1"
LowLevelConnectFn = Callable[[str, Mapping[str, Any]], Mapping[str, Any] | object]
_SENSITIVE_KEY_PARTS = ("endpoint", "url", "token", "secret", "password", "auth", "credential", "key")
_OPEN_KIND = "warroom_v2_ws_receiver_only_client_no_send_adapter_open_packet"
_PACKET_KIND = "warroom_v2_ws_receiver_only_client_no_send_adapter_packet"


def _config_keys(config: Mapping[str, Any]) -> list[str]:
    return sorted(str(key) for key in config.keys())


def _redacted_config(config: Mapping[str, Any]) -> dict[str, Any]:
    return {"present": bool(config), "keys": _config_keys(config)}


def _false_open_fields() -> dict[str, Any]:
    return {
        "connect_called": False, "connect_result": {}, "connect_error": {},
        "socket_opened": False, "client_started": False, "websocket_enabled": False,
        "runtime_connected": False, "push_connected": False,
        "client_sends_messages": False, "external_message_send_enabled": False, "send_disabled": True,
    }


def _sanitize_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    return {str(k): "<redacted>" if any(p in str(k).lower() for p in _SENSITIVE_KEY_PARTS) else v for k, v in data.items()}


def _result_mapping(result: Mapping[str, Any] | object) -> dict[str, Any]:
    return dict(result) if isinstance(result, Mapping) else {"result_object_type": type(result).__name__, "opened": bool(result)}


def build_warroom_v2_ws_receiver_only_client_no_send_adapter_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "no_send_adapter_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_VERSION,
        "adapter_kind": "warroom_v2_ws_receiver_only_client_no_send_adapter_explicit_connect_fn_only",
        "input_pipeline": ["q35n_adapter_factory", "q35m_runtime_wiring", "q35l_guarded_socket_open"],
        "requires_low_level_connect_fn": True,
        "requires_endpoint_url": True,
        "requires_allow_adapter_open_flag": True,
        "low_level_connect_fn_injected_only": True,
        "connect_called_only_on_adapter_open": True,
        "adapter_open_allowed_only_after_allow_flag": True,
        "factory_embeds_allow_adapter_open_from_runtime_config": True,
        "factory_creation_connects": False,
        "injected_adapter_factory_compatible": True,
        "injected_opener_compatible": True,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": True,
        "connect_result_sanitized": True,
        "endpoint_url_values_returned": False,
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


def _packet(*, status: str, endpoint_url_present: bool, endpoint_url_redacted: str, runtime_config: Mapping[str, Any], packet_kind: str = _OPEN_KIND, allow_adapter_open: bool | None = None, extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = {
        **build_warroom_v2_ws_receiver_only_client_no_send_adapter_contract(),
        "packet_kind": packet_kind,
        "adapter_open_status": status,
        "endpoint_url_present": endpoint_url_present,
        "endpoint_url_redacted": endpoint_url_redacted,
        "runtime_config_redacted": _redacted_config(runtime_config),
        "runtime_config_keys": _config_keys(runtime_config),
        **_false_open_fields(),
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
    if allow_adapter_open is not None:
        packet["allow_adapter_open"] = allow_adapter_open
    if extra:
        packet.update(extra)
    return packet


class WarRoomV2ReceiverOnlyClientNoSendAdapter:
    """Receiver-only adapter wrapper around an explicitly injected low-level connect function."""

    def __init__(self, *, connect_fn: LowLevelConnectFn, runtime_config: Mapping[str, Any] | None = None, allow_adapter_open: bool = False) -> None:
        self._connect_fn = connect_fn
        self._runtime_config = dict(runtime_config or {})
        self._allow_adapter_open = bool(allow_adapter_open)

    def __call__(self, endpoint_url: str) -> dict[str, Any]:
        return self.open(endpoint_url)

    def open(self, endpoint_url: str) -> dict[str, Any]:
        endpoint = str(endpoint_url or "")
        if not endpoint.strip():
            return _packet(status="receiver_only_client_no_send_adapter_blocked_endpoint_required", endpoint_url_present=False, endpoint_url_redacted="", runtime_config=self._runtime_config)
        if not self._allow_adapter_open:
            return _packet(status="receiver_only_client_no_send_adapter_blocked_allow_adapter_open_flag_required", endpoint_url_present=True, endpoint_url_redacted="<provided>", runtime_config=self._runtime_config, allow_adapter_open=False)
        raw_result: dict[str, Any] = {}
        error: dict[str, Any] = {}
        try:
            raw_result = _result_mapping(self._connect_fn(endpoint, dict(self._runtime_config)))
        except Exception as exc:  # noqa: BLE001 - adapter reports connect failure as data.
            error = {"error_type": type(exc).__name__, "error_message": str(exc)}
        opened = bool(raw_result.get("socket_opened") or raw_result.get("connected") or raw_result.get("opened")) and not error
        return _packet(
            status="receiver_only_client_no_send_adapter_opened_no_send" if opened else "receiver_only_client_no_send_adapter_attempt_failed_no_send",
            endpoint_url_present=True,
            endpoint_url_redacted="<provided>",
            runtime_config=self._runtime_config,
            allow_adapter_open=True,
            extra={"connect_called": True, "connect_result": _sanitize_mapping(raw_result), "connect_error": error, "socket_opened": opened, "client_started": opened, "websocket_enabled": opened, "runtime_connected": opened, "push_connected": opened},
        )


def build_warroom_v2_ws_receiver_only_client_no_send_adapter_factory(*, connect_fn: LowLevelConnectFn, base_runtime_config: Mapping[str, Any] | None = None) -> Callable[[Mapping[str, Any]], SocketOpenFn]:
    base_config = dict(base_runtime_config or {})

    def adapter_factory(runtime_config: Mapping[str, Any]) -> SocketOpenFn:
        merged_config = {**base_config, **dict(runtime_config or {})}
        adapter = WarRoomV2ReceiverOnlyClientNoSendAdapter(connect_fn=connect_fn, runtime_config=merged_config, allow_adapter_open=bool(merged_config.get("allow_adapter_open")))
        return adapter.open

    return adapter_factory


def build_warroom_v2_ws_receiver_only_client_no_send_adapter_packet(*, endpoint_url: str = "", runtime_config: Mapping[str, Any] | None = None, connect_fn: LowLevelConnectFn | None = None, allow_adapter_open: bool = False) -> dict[str, Any]:
    config = dict(runtime_config or {})
    endpoint = str(endpoint_url or "")
    endpoint_present = bool(endpoint.strip())
    endpoint_redacted = "<provided>" if endpoint_present else ""
    if connect_fn is None:
        return _packet(status="receiver_only_client_no_send_adapter_blocked_injected_connect_fn_required", endpoint_url_present=endpoint_present, endpoint_url_redacted=endpoint_redacted, runtime_config=config, packet_kind=_PACKET_KIND, allow_adapter_open=bool(allow_adapter_open))
    if not allow_adapter_open:
        return _packet(status="receiver_only_client_no_send_adapter_blocked_allow_adapter_open_flag_required", endpoint_url_present=endpoint_present, endpoint_url_redacted=endpoint_redacted, runtime_config=config, packet_kind=_PACKET_KIND, allow_adapter_open=False)
    adapter = WarRoomV2ReceiverOnlyClientNoSendAdapter(connect_fn=connect_fn, runtime_config=config, allow_adapter_open=True)
    return {**adapter.open(endpoint_url), "packet_kind": _PACKET_KIND, "allow_adapter_open": True}
