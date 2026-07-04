# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_no_send_adapter.py
# desc: WarRoom v2 receiver-only no-send adapter implementation. Explicit low-level connect function injection only; no default network client and no send.

from __future__ import annotations

from typing import Any, Callable, Mapping

from .ws_receiver_only_client_guarded_socket_open import SocketOpenFn

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_no_send_adapter.ps_q35o.v1"
LowLevelConnectFn = Callable[[str, Mapping[str, Any]], Mapping[str, Any] | object]
_SENSITIVE_KEY_PARTS = ("endpoint", "url", "token", "secret", "password", "auth", "credential", "key")


def _config_keys(config: Mapping[str, Any]) -> list[str]:
    return sorted(str(key) for key in config.keys())


def _redacted_config(config: Mapping[str, Any]) -> dict[str, Any]:
    return {"present": bool(config), "keys": _config_keys(config)}


def _sanitize_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in data.items():
        key_text = str(key)
        lowered = key_text.lower()
        if any(part in lowered for part in _SENSITIVE_KEY_PARTS):
            sanitized[key_text] = "<redacted>"
        else:
            sanitized[key_text] = value
    return sanitized


def _result_mapping(result: Mapping[str, Any] | object) -> dict[str, Any]:
    if isinstance(result, Mapping):
        return dict(result)
    return {"result_object_type": type(result).__name__, "opened": bool(result)}


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


class WarRoomV2ReceiverOnlyClientNoSendAdapter:
    """Receiver-only adapter wrapper around an explicitly injected low-level connect function."""

    def __init__(self, *, connect_fn: LowLevelConnectFn, runtime_config: Mapping[str, Any] | None = None) -> None:
        self._connect_fn = connect_fn
        self._runtime_config = dict(runtime_config or {})

    def __call__(self, endpoint_url: str) -> dict[str, Any]:
        return self.open(endpoint_url)

    def open(self, endpoint_url: str) -> dict[str, Any]:
        endpoint = str(endpoint_url or "")
        if not endpoint.strip():
            return {
                **build_warroom_v2_ws_receiver_only_client_no_send_adapter_contract(),
                "packet_kind": "warroom_v2_ws_receiver_only_client_no_send_adapter_open_packet",
                "adapter_open_status": "receiver_only_client_no_send_adapter_blocked_endpoint_required",
                "endpoint_url_present": False,
                "endpoint_url_redacted": "",
                "runtime_config_redacted": _redacted_config(self._runtime_config),
                "runtime_config_keys": _config_keys(self._runtime_config),
                "connect_called": False,
                "connect_result": {},
                "connect_error": {},
                "socket_opened": False,
                "client_started": False,
                "websocket_enabled": False,
                "runtime_connected": False,
                "push_connected": False,
                "client_sends_messages": False,
                "external_message_send_enabled": False,
                "send_disabled": True,
            }
        raw_result: dict[str, Any] = {}
        error: dict[str, Any] = {}
        try:
            raw_result = _result_mapping(self._connect_fn(endpoint, dict(self._runtime_config)))
        except Exception as exc:  # noqa: BLE001 - adapter reports connect failure as data.
            error = {"error_type": type(exc).__name__, "error_message": str(exc)}
        opened = bool(raw_result.get("socket_opened") or raw_result.get("connected") or raw_result.get("opened")) and not error
        sanitized_result = _sanitize_mapping(raw_result)
        return {
            **build_warroom_v2_ws_receiver_only_client_no_send_adapter_contract(),
            "packet_kind": "warroom_v2_ws_receiver_only_client_no_send_adapter_open_packet",
            "adapter_open_status": "receiver_only_client_no_send_adapter_opened_no_send" if opened else "receiver_only_client_no_send_adapter_attempt_failed_no_send",
            "endpoint_url_present": True,
            "endpoint_url_redacted": "<provided>",
            "runtime_config_redacted": _redacted_config(self._runtime_config),
            "runtime_config_keys": _config_keys(self._runtime_config),
            "connect_called": True,
            "connect_result": sanitized_result,
            "connect_error": error,
            "socket_opened": opened,
            "client_started": opened,
            "websocket_enabled": opened,
            "runtime_connected": opened,
            "push_connected": opened,
            "client_sends_messages": False,
            "external_message_send_enabled": False,
            "send_disabled": True,
            "order_intent_submitted": False,
            "would_send_to_broker": False,
        }


def build_warroom_v2_ws_receiver_only_client_no_send_adapter_factory(
    *,
    connect_fn: LowLevelConnectFn,
    base_runtime_config: Mapping[str, Any] | None = None,
) -> Callable[[Mapping[str, Any]], SocketOpenFn]:
    base_config = dict(base_runtime_config or {})

    def adapter_factory(runtime_config: Mapping[str, Any]) -> SocketOpenFn:
        merged_config = {**base_config, **dict(runtime_config or {})}
        adapter = WarRoomV2ReceiverOnlyClientNoSendAdapter(connect_fn=connect_fn, runtime_config=merged_config)
        return adapter.open

    return adapter_factory


def build_warroom_v2_ws_receiver_only_client_no_send_adapter_packet(
    *,
    endpoint_url: str = "",
    runtime_config: Mapping[str, Any] | None = None,
    connect_fn: LowLevelConnectFn | None = None,
    allow_adapter_open: bool = False,
) -> dict[str, Any]:
    config = dict(runtime_config or {})
    if connect_fn is None:
        return {
            **build_warroom_v2_ws_receiver_only_client_no_send_adapter_contract(),
            "packet_kind": "warroom_v2_ws_receiver_only_client_no_send_adapter_packet",
            "adapter_open_status": "receiver_only_client_no_send_adapter_blocked_injected_connect_fn_required",
            "endpoint_url_present": bool(str(endpoint_url or "").strip()),
            "endpoint_url_redacted": "<provided>" if str(endpoint_url or "").strip() else "",
            "runtime_config_redacted": _redacted_config(config),
            "runtime_config_keys": _config_keys(config),
            "allow_adapter_open": bool(allow_adapter_open),
            "connect_called": False,
            "connect_result": {},
            "connect_error": {},
            "socket_opened": False,
            "client_started": False,
            "websocket_enabled": False,
            "runtime_connected": False,
            "push_connected": False,
            "client_sends_messages": False,
            "external_message_send_enabled": False,
            "send_disabled": True,
        }
    if not allow_adapter_open:
        return {
            **build_warroom_v2_ws_receiver_only_client_no_send_adapter_contract(),
            "packet_kind": "warroom_v2_ws_receiver_only_client_no_send_adapter_packet",
            "adapter_open_status": "receiver_only_client_no_send_adapter_blocked_allow_adapter_open_flag_required",
            "endpoint_url_present": bool(str(endpoint_url or "").strip()),
            "endpoint_url_redacted": "<provided>" if str(endpoint_url or "").strip() else "",
            "runtime_config_redacted": _redacted_config(config),
            "runtime_config_keys": _config_keys(config),
            "allow_adapter_open": False,
            "connect_called": False,
            "connect_result": {},
            "connect_error": {},
            "socket_opened": False,
            "client_started": False,
            "websocket_enabled": False,
            "runtime_connected": False,
            "push_connected": False,
            "client_sends_messages": False,
            "external_message_send_enabled": False,
            "send_disabled": True,
        }
    adapter = WarRoomV2ReceiverOnlyClientNoSendAdapter(connect_fn=connect_fn, runtime_config=config)
    return {**adapter.open(endpoint_url), "allow_adapter_open": True}
