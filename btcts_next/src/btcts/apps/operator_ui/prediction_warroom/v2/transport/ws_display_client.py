# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_client.py
# desc: WarRoom v2 UI-side WS display client contract. Pure packet only; no socket, IO, Streamlit, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .realtime_read_surface import build_warroom_v2_realtime_japanese_read_surface_packet
from .schema import normalize_warroom_v2_transport_message, validate_warroom_v2_transport_message
from .ws_display_adapter_observation import build_warroom_v2_ws_display_adapter_observation_packet

WARROOM_V2_WS_DISPLAY_CLIENT_VERSION = "prediction_warroom.v2.transport.ws_display_client.ps_q32a.v1"


def build_warroom_v2_ws_display_client_contract() -> dict[str, Any]:
    surface = build_warroom_v2_realtime_japanese_read_surface_packet()
    return {
        "ok": True,
        "client_version": WARROOM_V2_WS_DISPLAY_CLIENT_VERSION,
        "client_kind": "ws_display_client_contract_no_socket_open",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "websocket_display_push_required": True,
        "websocket_display_push_main_path": True,
        "ui_receiver_side": True,
        "server_to_warroom_ui": True,
        "read_model_push_plane": "server_to_warroom_ui",
        "command_intent_plane": "warroom_ui_or_autotrade_to_order_intent_gateway",
        "subscriptions_source": "q31x_realtime_japanese_read_surface_targets",
        "inbound_source": "q31z_ws_display_adapter_observation_outbox",
        "target_topics": list(surface.get("target_topics") or []),
        "reading_order_labels_ja": list(surface.get("reading_order_labels_ja") or []),
        "bounded_receive_buffer": True,
        "receive_buffer_default_limit": 128,
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


def build_warroom_v2_ws_display_client_subscription_packet() -> dict[str, Any]:
    contract = build_warroom_v2_ws_display_client_contract()
    topics = list(contract["target_topics"])
    return {
        **contract,
        "packet_kind": "warroom_v2_ws_display_client_subscription_packet",
        "subscription_count": len(topics),
        "subscriptions": [
            {
                "topic": topic,
                "subscribe_later": True,
                "subscribed_now": False,
                "socket_opened": False,
                "client_sends_messages": False,
                "read_only": True,
                "display_only": True,
                "order_intent_submitted": False,
                "would_send_to_broker": False,
            }
            for topic in topics
        ],
    }


def build_warroom_v2_ws_display_client_receive_buffer(
    *,
    messages: Iterable[Mapping[str, Any]] | None = None,
    limit: int = 128,
) -> dict[str, Any]:
    bounded = max(1, min(512, int(limit or 128)))
    contract = build_warroom_v2_ws_display_client_contract()
    targets = set(contract["target_topics"])
    accepted: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for raw in list(messages or [])[-bounded:]:
        validation = validate_warroom_v2_transport_message(raw)
        normalized = normalize_warroom_v2_transport_message(raw)
        reason = ""
        if not validation["ok"]:
            reason = "schema_invalid"
        elif normalized["topic"] not in targets:
            reason = "not_warroom_display_target"
        if reason:
            dropped.append({"topic": normalized.get("topic", ""), "widget_id": normalized.get("widget_id", ""), "reason": reason})
            continue
        accepted.append(
            {
                **normalized,
                "client_version": WARROOM_V2_WS_DISPLAY_CLIENT_VERSION,
                "accepted_by_client_contract": True,
                "received_over_ws_now": False,
                "socket_opened": False,
                "websocket_enabled": False,
                "client_sends_messages": False,
                "external_message_send_enabled": False,
                "order_intent_submitted": False,
                "would_send_to_broker": False,
            }
        )
    return {
        **contract,
        "packet_kind": "warroom_v2_ws_display_client_receive_buffer_packet",
        "receive_buffer_limit": bounded,
        "received_message_count": len(accepted),
        "dropped_count": len(dropped),
        "messages": accepted,
        "dropped": dropped,
        "all_messages_are_display_targets": all(str(item.get("topic")) in targets for item in accepted),
        "all_messages_are_read_only": all(bool(item.get("read_only", False)) for item in accepted),
        "all_messages_are_display_only": all(bool(item.get("display_only", False)) for item in accepted),
        "all_messages_no_broad_page_reload": all(not bool(item.get("broad_page_reload_required", True)) for item in accepted),
        "client_started": False,
        "socket_opened": False,
        "client_sends_messages": False,
    }


def build_warroom_v2_ws_display_client_packet(
    *,
    messages: Iterable[Mapping[str, Any]] | None = None,
    limit: int = 128,
) -> dict[str, Any]:
    raw_messages = list(messages or [])
    observation = build_warroom_v2_ws_display_adapter_observation_packet(messages=raw_messages)
    receive_buffer = build_warroom_v2_ws_display_client_receive_buffer(messages=observation.get("ws_display_adapter_outbox_packet", {}).get("messages", []), limit=limit)
    return {
        **build_warroom_v2_ws_display_client_contract(),
        "packet_kind": "warroom_v2_ws_display_client_packet",
        "adapter_observation_packet": observation,
        "subscription_packet": build_warroom_v2_ws_display_client_subscription_packet(),
        "receive_buffer_packet": receive_buffer,
        "input_message_count": len(raw_messages),
        "received_message_count": int(receive_buffer.get("received_message_count") or 0),
        "dropped_count": int(observation.get("outbox_dropped_count") or 0) + int(receive_buffer.get("dropped_count") or 0),
        "socket_open_requested": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
    }
