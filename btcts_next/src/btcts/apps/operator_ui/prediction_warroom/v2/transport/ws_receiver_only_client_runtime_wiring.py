# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_runtime_wiring.py
# desc: WarRoom v2 receiver-only client runtime wiring. Composes Q35K preflight and Q35L guarded open; injected opener only; no send.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_guarded_socket_open import SocketOpenFn, build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet
from .ws_receiver_only_client_start_preflight import build_warroom_v2_ws_receiver_only_client_start_preflight_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_RUNTIME_WIRING_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_runtime_wiring.ps_q35m.v1"


def build_warroom_v2_ws_receiver_only_client_runtime_wiring_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "runtime_wiring_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_RUNTIME_WIRING_VERSION,
        "wiring_kind": "warroom_v2_ws_receiver_only_client_runtime_wiring_composes_q35k_q35l_no_send",
        "input_pipeline": ["q35j_compact_status_badge_state_presence", "q35k_receiver_only_client_start_preflight", "q35l_guarded_socket_open"],
        "composes_q35k_preflight": True,
        "composes_q35l_guarded_socket_open": True,
        "requires_compact_status_badge_packet": True,
        "requires_operator_scope_ack_for_preflight": True,
        "requires_socket_open_requested": True,
        "requires_operator_socket_open_ack": True,
        "requires_endpoint_url": True,
        "requires_allow_socket_open_flag": True,
        "requires_injected_socket_open_callable": True,
        "injected_opener_only": True,
        "no_hardcoded_endpoint": True,
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


def build_warroom_v2_ws_receiver_only_client_runtime_wiring_packet(
    *,
    compact_status_badge_packet: Mapping[str, Any] | None = None,
    operator_scope_ack: bool = False,
    endpoint_url: str = "",
    socket_open_requested: bool = False,
    operator_socket_open_ack: bool = False,
    allow_socket_open: bool = False,
    socket_open_fn: SocketOpenFn | None = None,
) -> dict[str, Any]:
    preflight_packet = build_warroom_v2_ws_receiver_only_client_start_preflight_packet(
        compact_status_badge_packet=compact_status_badge_packet,
        operator_scope_ack=operator_scope_ack,
    )
    guarded_open_packet = build_warroom_v2_ws_receiver_only_client_guarded_socket_open_packet(
        preflight_packet=preflight_packet,
        endpoint_url=endpoint_url,
        socket_open_requested=socket_open_requested,
        operator_socket_open_ack=operator_socket_open_ack,
        allow_socket_open=allow_socket_open,
        socket_open_fn=socket_open_fn,
    )
    socket_opened = bool(guarded_open_packet.get("socket_opened"))
    attempted = bool(guarded_open_packet.get("socket_open_attempted"))
    return {
        **build_warroom_v2_ws_receiver_only_client_runtime_wiring_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_runtime_wiring_packet",
        "compact_status_badge_packet": dict(compact_status_badge_packet or {}),
        "preflight_packet": preflight_packet,
        "guarded_socket_open_packet": guarded_open_packet,
        "operator_scope_ack": bool(operator_scope_ack),
        "socket_open_requested": bool(socket_open_requested),
        "operator_socket_open_ack": bool(operator_socket_open_ack),
        "allow_socket_open": bool(allow_socket_open),
        "endpoint_url_present": bool(str(endpoint_url or "").strip()),
        "endpoint_url_redacted": "<provided>" if str(endpoint_url or "").strip() else "",
        "runtime_wiring_status": str(guarded_open_packet.get("guarded_socket_open_status") or ""),
        "preflight_ready_for_guarded_socket_open": bool(preflight_packet.get("ready_for_guarded_socket_open_next_slice")),
        "socket_open_attempted": attempted,
        "socket_opened": socket_opened,
        "client_started": bool(guarded_open_packet.get("client_started")),
        "websocket_enabled": bool(guarded_open_packet.get("websocket_enabled")),
        "runtime_connected": bool(guarded_open_packet.get("runtime_connected")),
        "push_connected": bool(guarded_open_packet.get("push_connected")),
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
