# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_adapter.py
# desc: WarRoom v2 WS display push adapter contract. Pure packet only; no socket, IO, Streamlit, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .realtime_read_surface import build_warroom_v2_realtime_japanese_read_surface_packet
from .schema import normalize_warroom_v2_transport_message, validate_warroom_v2_transport_message

WARROOM_V2_WS_DISPLAY_ADAPTER_VERSION = "prediction_warroom.v2.transport.ws_display_adapter.ps_q31y.v1"
_ALLOWED_DIAGNOSTIC_SUMMARY_FIELDS: tuple[str, ...] = ("safety_state", "data_freshness", "transport_state", "last_update_age")


def build_warroom_v2_ws_display_push_adapter_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "adapter_version": WARROOM_V2_WS_DISPLAY_ADAPTER_VERSION,
        "adapter_kind": "ws_display_push_transport_adapter_contract_no_socket",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "websocket_display_push_required": True,
        "websocket_display_push_main_path": True,
        "bidirectional_websocket_premise": True,
        "read_model_push_plane": "server_to_warroom_ui",
        "command_intent_plane": "warroom_ui_or_autotrade_to_order_intent_gateway",
        "browser_timer_polling_is_legacy_compat_only": True,
        "browser_timer_refresh_replacement_target": True,
        "no_new_polling_fallback": True,
        "no_browser_timer_reload_introduced": True,
        "adapter_sends_messages": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "warroom_diagnostic_policy": "minimal_status_only",
        "diagnostic_minimal_summary_allowed_in_warroom": True,
        "detailed_diagnostics_default_surface": "audit_or_diagnostics_tab",
        "warroom_visible_diagnostic_panel_default": False,
        "visible_panel_render_plan_deprioritized": True,
        "allowed_warroom_diagnostic_summary_fields": list(_ALLOWED_DIAGNOSTIC_SUMMARY_FIELDS),
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


def _display_target_topics() -> set[str]:
    surface = build_warroom_v2_realtime_japanese_read_surface_packet()
    return {str(topic) for topic in surface.get("target_topics", [])}


def build_warroom_v2_ws_display_push_outbox(
    *,
    messages: Iterable[Mapping[str, Any]] | None = None,
    max_messages: int = 64,
) -> dict[str, Any]:
    bounded = max(1, min(512, int(max_messages or 64)))
    targets = _display_target_topics()
    normalized: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for raw in list(messages or [])[-bounded:]:
        validation = validate_warroom_v2_transport_message(raw)
        message = normalize_warroom_v2_transport_message(raw)
        reason = ""
        if not validation["ok"]:
            reason = "schema_invalid"
        elif message["topic"] not in targets:
            reason = "not_warroom_display_target"
        if reason:
            dropped.append({"topic": message.get("topic", ""), "widget_id": message.get("widget_id", ""), "reason": reason})
            continue
        normalized.append(
            {
                **message,
                "adapter_version": WARROOM_V2_WS_DISPLAY_ADAPTER_VERSION,
                "adapter_kind": "ws_display_push_transport_adapter_contract_no_socket",
                "websocket_display_push_main_path": True,
                "would_send_over_ws_later": True,
                "adapter_sends_messages": False,
                "socket_opened": False,
                "external_message_send_enabled": False,
                "websocket_enabled": False,
                "runtime_connected": False,
                "push_connected": False,
                "order_intent_submitted": False,
                "would_send_to_broker": False,
            }
        )
    return {
        **build_warroom_v2_ws_display_push_adapter_contract(),
        "packet_kind": "warroom_v2_ws_display_push_outbox_contract_packet",
        "max_messages": bounded,
        "message_count": len(normalized),
        "dropped_count": len(dropped),
        "messages": normalized,
        "dropped": dropped,
        "target_topics": sorted(targets),
        "all_messages_are_display_targets": all(str(item.get("topic")) in targets for item in normalized),
        "all_messages_are_read_only": all(bool(item.get("read_only", False)) for item in normalized),
        "all_messages_are_display_only": all(bool(item.get("display_only", False)) for item in normalized),
        "all_messages_no_broad_page_reload": all(not bool(item.get("broad_page_reload_required", True)) for item in normalized),
    }
