# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_client_observation.py
# desc: WarRoom v2 hidden WS display client observation. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .ws_display_client import build_warroom_v2_ws_display_client_contract, build_warroom_v2_ws_display_client_packet

WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_VERSION = "prediction_warroom.v2.transport.ws_display_client_observation.ps_q32b.v1"
WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_STATE_KEY = "warroom_v2_ws_display_client_observation_q32b"


def build_warroom_v2_ws_display_client_observation_contract() -> dict[str, Any]:
    contract = build_warroom_v2_ws_display_client_contract()
    return {
        "ok": True,
        "observation_version": WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_ws_display_client_observation_packet",
        "input_pipeline": ["q31z_ws_display_adapter_observation", "q32a_ws_display_client_contract"],
        "current_small_goal": contract["current_small_goal"],
        "websocket_display_push_required": True,
        "websocket_display_push_main_path": True,
        "ui_receiver_side": True,
        "server_to_warroom_ui": True,
        "bounded_receive_buffer": True,
        "socket_open_requested": False,
        "socket_open_requested_default": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "browser_timer_polling_is_legacy_compat_only": True,
        "browser_timer_refresh_replacement_target": True,
        "no_new_polling_fallback": True,
        "no_browser_timer_reload_introduced": True,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
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


def build_warroom_v2_ws_display_client_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    limit: int = 128,
) -> dict[str, Any]:
    raw_messages = list(messages or [])
    client_packet = build_warroom_v2_ws_display_client_packet(messages=raw_messages, limit=limit)
    return {
        **build_warroom_v2_ws_display_client_observation_contract(),
        "packet_kind": "warroom_v2_ws_display_client_observation_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "default_streamlit_message_count": len(raw_messages),
        "ws_display_client_packet": client_packet,
        "received_message_count": int(client_packet.get("received_message_count") or 0),
        "dropped_count": int(client_packet.get("dropped_count") or 0),
        "receive_buffer_limit": int(client_packet.get("receive_buffer_packet", {}).get("receive_buffer_limit") or 0),
        "subscriptions_count": int(client_packet.get("subscription_packet", {}).get("subscription_count") or 0),
        "all_messages_are_display_targets": bool(client_packet.get("receive_buffer_packet", {}).get("all_messages_are_display_targets", True)),
        "all_messages_no_broad_page_reload": bool(client_packet.get("receive_buffer_packet", {}).get("all_messages_no_broad_page_reload", True)),
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
    }
