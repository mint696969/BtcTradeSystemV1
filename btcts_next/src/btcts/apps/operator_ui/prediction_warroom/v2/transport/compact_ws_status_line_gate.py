# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_gate.py
# desc: WarRoom v2 compact WS status line render gate. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .ws_display_connection_status_observation import build_warroom_v2_ws_display_connection_status_observation_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_gate.ps_q32e.v1"
_ALLOWED_STATUS_FIELDS: tuple[str, ...] = (
    "transport_state_ja",
    "data_freshness_ja",
    "last_update_age_ja",
    "received_message_count",
    "dropped_count",
    "operator_guidance_ja",
)


def _gate_status(*, render_requested: bool, operator_read_only_ack: bool, status_line_available: bool) -> str:
    if not render_requested:
        return "compact_ws_status_line_hidden_default"
    if not operator_read_only_ack:
        return "compact_ws_status_line_blocked_read_only_ack_required"
    if not status_line_available:
        return "compact_ws_status_line_blocked_status_unavailable"
    return "compact_ws_status_line_ready_read_only_not_mounted"


def build_warroom_v2_compact_ws_status_line_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "gate_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_VERSION,
        "gate_kind": "warroom_v2_compact_ws_status_line_render_gate_default_off",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "input_pipeline": ["q32d_ws_display_connection_status_observation"],
        "render_requested_default": False,
        "operator_read_only_ack_default": False,
        "status_line_visible_now_default": False,
        "status_line_mounted_now_default": False,
        "default_gate_status": "compact_ws_status_line_hidden_default",
        "warroom_visible_surface": "top_minimal_operator_status_line_later",
        "allowed_status_fields": list(_ALLOWED_STATUS_FIELDS),
        "compact_status_only": True,
        "detailed_diagnostics_default_surface": "audit_or_diagnostics_tab",
        "websocket_display_push_required": True,
        "websocket_display_push_main_path": True,
        "ui_receiver_side": True,
        "server_to_warroom_ui": True,
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


def build_warroom_v2_compact_ws_status_line_gate_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    render_requested: bool = False,
    operator_read_only_ack: bool = False,
) -> dict[str, Any]:
    observation = build_warroom_v2_ws_display_connection_status_observation_packet(
        fragment_summary=fragment_summary,
        messages=list(messages or []),
    )
    status_line = dict(observation.get("status_line") or {})
    row = {key: status_line.get(key) for key in _ALLOWED_STATUS_FIELDS}
    status_line_available = all(key in status_line for key in _ALLOWED_STATUS_FIELDS)
    gate_status = _gate_status(
        render_requested=bool(render_requested),
        operator_read_only_ack=bool(operator_read_only_ack),
        status_line_available=status_line_available,
    )
    ready = gate_status == "compact_ws_status_line_ready_read_only_not_mounted"
    return {
        **build_warroom_v2_compact_ws_status_line_gate_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_gate_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "connection_status_observation_packet": observation,
        "gate_status": gate_status,
        "render_requested": bool(render_requested),
        "operator_read_only_ack": bool(operator_read_only_ack),
        "status_line_available": bool(status_line_available),
        "status_line_ready_for_future_mount": bool(ready),
        "status_line_row": row,
        "status_line_field_count": len(row),
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
        "render_gate_default_off": True,
        "read_only": True,
        "display_only": True,
        "compact_status_only": True,
        "detailed_diagnostics_default_surface": "audit_or_diagnostics_tab",
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
