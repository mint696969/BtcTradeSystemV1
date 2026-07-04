# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_guarded_socket_open.py
# desc: WarRoom v2 receiver-only client guarded socket-open boundary. Injected opener only; no send.

from __future__ import annotations

from typing import Any, Callable, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_GUARDED_SOCKET_OPEN_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_guarded_socket_open.ps_q35l.v1"
SocketOpenFn = Callable[[str], Mapping[str, Any] | object]


def _preflight_ready(packet: Mapping[str, Any]) -> bool:
    return bool(packet.get("ready_for_guarded_socket_open_next_slice")) and bool(packet.get("socket_open_allowed_for_future_slice"))


def _status(
    *,
    preflight_ready: bool,
    socket_open_requested: bool,
    operator_socket_open_ack: bool,
    endpoint_url: str,
    socket_open_callable_present: bool,
    allow_socket_open: bool,
) -> str:
    if not preflight_ready:
        return "receiver_only_client_guarded_socket_open_blocked_preflight_required"
    if not socket_open_requested:
        return "receiver_only_client_guarded_socket_open_waiting_request"
    if not operator_socket_open_ack:
        return "receiver_only_client_guarded_socket_open_blocked_operator_socket_open_ack_required"
    if not endpoint_url.strip():
        return "receiver_only_client_guarded_socket_open_blocked_endpoint_required"
    if not allow_socket_open:
        return "receiver_only_client_guarded_socket_open_blocked_allow_socket_open_flag_required"
    if not socket_open_callable_present:
        return "receiver_only_client_guarded_socket_open_blocked_injected_opener_required"
    return "receiver_only_client_guarded_socket_open_ready_to_call_injected_opener_no_send"


def _result_mapping(result: Mapping[str, Any] | object) -> dict[str, Any]:
    if isinstance(result, Mapping):
        return dict(result)
    return {"result_object_type": type(result).__name__, "opened": bool(result)}


def build_warroom_v2_ws_receiver_only_client_guarded_socket_open_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "guarded_socket_open_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_GUARDED_SOCKET_OPEN_VERSION,
        "boundary_kind": "warroom_v2_ws_receiver_only_client_guarded_socket_open_injected_opener_no_send",
        "input_pipeline": ["q35k_receiver_only_client_start_preflight"],
        "requires_q35k_preflight_ready": True,
        "requires_socket_open_requested": True,
        "requires_operator_socket_open_ack": True,
        "requires_endpoint_url": True,
        "requires_allow_socket_open_flag": True,
        "requires_injected_socket_open_callable": True,
        "no_hardcoded_endpoint": True,
        "injected_opener_only": True,
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
        "socket_open_attempted": False,
        "socket_opened": False,
        "client_started": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
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


def build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(
    *,
    preflight_packet: Mapping[str, Any] | None = None,
    endpoint_url: str = "",
    socket_open_requested: bool = False,
    operator_socket_open_ack: bool = False,
    allow_socket_open: bool = False,
    socket_open_fn: SocketOpenFn | None = None,
) -> dict[str, Any]:
    preflight = dict(preflight_packet or {})
    endpoint = str(endpoint_url or "")
    ready = _preflight_ready(preflight)
    callable_present = socket_open_fn is not None
    initial_status = _status(
        preflight_ready=ready,
        socket_open_requested=bool(socket_open_requested),
        operator_socket_open_ack=bool(operator_socket_open_ack),
        endpoint_url=endpoint,
        socket_open_callable_present=callable_present,
        allow_socket_open=bool(allow_socket_open),
    )
    should_call = initial_status == "receiver_only_client_guarded_socket_open_ready_to_call_injected_opener_no_send"
    result: dict[str, Any] = {}
    error: dict[str, Any] = {}
    if should_call and socket_open_fn is not None:
        try:
            result = _result_mapping(socket_open_fn(endpoint))
        except Exception as exc:  # noqa: BLE001 - boundary reports opener failure as data.
            error = {"error_type": type(exc).__name__, "error_message": str(exc)}
    opened = bool(result.get("socket_opened") or result.get("connected") or result.get("opened")) and not error
    final_status = initial_status
    if should_call:
        final_status = "receiver_only_client_guarded_socket_open_opened_no_send" if opened else "receiver_only_client_guarded_socket_open_attempt_failed_no_send"
    return {
        **build_warroom_v2_ws_receiver_only_client_guarded_socket_open_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_guarded_socket_open_packet",
        "preflight_packet": preflight,
        "preflight_ready_for_guarded_socket_open": ready,
        "endpoint_url_present": bool(endpoint.strip()),
        "endpoint_url_redacted": "<provided>" if endpoint.strip() else "",
        "socket_open_requested": bool(socket_open_requested),
        "operator_socket_open_ack": bool(operator_socket_open_ack),
        "allow_socket_open": bool(allow_socket_open),
        "socket_open_callable_present": callable_present,
        "guarded_socket_open_status": final_status,
        "socket_open_attempted": should_call,
        "socket_open_result": result,
        "socket_open_error": error,
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
