# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_visible_mount_gate.py
# desc: WarRoom v2 compact WS status line visible mount gate. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .compact_ws_status_line_gate_observation import build_warroom_v2_compact_ws_status_line_gate_observation_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_MOUNT_GATE_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_visible_mount_gate.ps_q32g.v1"
_ALLOWED_STATUS_FIELDS: tuple[str, ...] = (
    "transport_state_ja",
    "data_freshness_ja",
    "last_update_age_ja",
    "received_message_count",
    "dropped_count",
    "operator_guidance_ja",
)


def _visible_mount_gate_status(*, mount_requested: bool, mount_ack: bool, status_ready: bool) -> str:
    if not mount_requested:
        return "compact_ws_status_line_visible_mount_hidden_default"
    if not mount_ack:
        return "compact_ws_status_line_visible_mount_blocked_ack_required"
    if not status_ready:
        return "compact_ws_status_line_visible_mount_blocked_status_gate_not_ready"
    return "compact_ws_status_line_visible_mount_ready_not_mounted"


def build_warroom_v2_compact_ws_status_line_visible_mount_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "gate_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_MOUNT_GATE_VERSION,
        "gate_kind": "warroom_v2_compact_ws_status_line_visible_mount_gate_default_off",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "input_pipeline": ["q32f_compact_ws_status_line_gate_observation"],
        "visible_mount_requested_default": False,
        "operator_visible_mount_ack_default": False,
        "status_gate_render_requested_default": False,
        "status_gate_read_only_ack_default": False,
        "default_gate_status": "compact_ws_status_line_visible_mount_hidden_default",
        "ready_gate_status": "compact_ws_status_line_visible_mount_ready_not_mounted",
        "warroom_mount_surface": "top_minimal_operator_status_line",
        "warroom_mount_position": "after_header_before_focus_nav_later",
        "warroom_page_modified": False,
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


def build_warroom_v2_compact_ws_status_line_visible_mount_gate_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    visible_mount_requested: bool = False,
    operator_visible_mount_ack: bool = False,
    status_gate_render_requested: bool = False,
    status_gate_read_only_ack: bool = False,
) -> dict[str, Any]:
    observation = build_warroom_v2_compact_ws_status_line_gate_observation_packet(
        fragment_summary=fragment_summary,
        messages=list(messages or []),
        render_requested=status_gate_render_requested,
        operator_read_only_ack=status_gate_read_only_ack,
    )
    status_ready = bool(observation.get("status_line_ready_for_future_mount"))
    gate_status = _visible_mount_gate_status(
        mount_requested=bool(visible_mount_requested),
        mount_ack=bool(operator_visible_mount_ack),
        status_ready=status_ready,
    )
    ready = gate_status == "compact_ws_status_line_visible_mount_ready_not_mounted"
    status_row = dict(observation.get("status_line_row") or {})
    return {
        **build_warroom_v2_compact_ws_status_line_visible_mount_gate_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_visible_mount_gate_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "compact_status_line_gate_observation_packet": observation,
        "gate_status": gate_status,
        "visible_mount_requested": bool(visible_mount_requested),
        "operator_visible_mount_ack": bool(operator_visible_mount_ack),
        "status_gate_render_requested": bool(status_gate_render_requested),
        "status_gate_read_only_ack": bool(status_gate_read_only_ack),
        "status_gate_ready": bool(status_ready),
        "visible_mount_ready_for_future_mount": bool(ready),
        "status_line_row": {key: status_row.get(key) for key in _ALLOWED_STATUS_FIELDS},
        "status_line_field_count": len(_ALLOWED_STATUS_FIELDS),
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
        "visible_mount_gate_default_off": True,
        "read_only": True,
        "display_only": True,
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
