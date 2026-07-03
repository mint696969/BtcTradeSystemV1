# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_visible_render_adapter.py
# desc: WarRoom v2 compact WS status line visible render adapter. Pure payload only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .compact_ws_status_line_visible_mount_gate_observation import build_warroom_v2_compact_ws_status_line_visible_mount_gate_observation_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_ADAPTER_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_visible_render_adapter.ps_q32i.v1"
_FIELD_ORDER: tuple[str, ...] = (
    "transport_state_ja",
    "data_freshness_ja",
    "last_update_age_ja",
    "received_message_count",
    "dropped_count",
    "operator_guidance_ja",
)
_LABELS_JA: dict[str, str] = {
    "transport_state_ja": "WS状態",
    "data_freshness_ja": "データ鮮度",
    "last_update_age_ja": "最終更新",
    "received_message_count": "受信数",
    "dropped_count": "破棄数",
    "operator_guidance_ja": "案内",
}


def _adapter_status(*, render_requested: bool, render_ack: bool, mount_ready: bool) -> str:
    if not render_requested:
        return "compact_ws_status_line_visible_render_hidden_default"
    if not render_ack:
        return "compact_ws_status_line_visible_render_blocked_ack_required"
    if not mount_ready:
        return "compact_ws_status_line_visible_render_blocked_mount_gate_not_ready"
    return "compact_ws_status_line_visible_render_payload_ready_not_rendered"


def _value_text(value: object) -> str:
    return "" if value is None else str(value)


def _display_items(status_row: Mapping[str, Any]) -> list[dict[str, str]]:
    return [
        {"field": field, "label_ja": _LABELS_JA[field], "value": _value_text(status_row.get(field))}
        for field in _FIELD_ORDER
    ]


def _compact_line(items: Iterable[Mapping[str, str]]) -> str:
    return " / ".join(f"{item.get('label_ja')}: {item.get('value')}" for item in items)


def build_warroom_v2_compact_ws_status_line_visible_render_adapter_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "adapter_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_ADAPTER_VERSION,
        "adapter_kind": "warroom_v2_compact_ws_status_line_visible_render_adapter_default_off",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "input_pipeline": ["q32h_compact_ws_status_line_visible_mount_gate_observation"],
        "visible_render_adapter_requested_default": False,
        "operator_visible_render_ack_default": False,
        "visible_mount_requested_default": False,
        "operator_visible_mount_ack_default": False,
        "status_gate_render_requested_default": False,
        "status_gate_read_only_ack_default": False,
        "default_adapter_status": "compact_ws_status_line_visible_render_hidden_default",
        "ready_adapter_status": "compact_ws_status_line_visible_render_payload_ready_not_rendered",
        "warroom_mount_surface": "top_minimal_operator_status_line",
        "warroom_mount_position": "after_header_before_focus_nav_later",
        "warroom_page_modified": False,
        "field_order": list(_FIELD_ORDER),
        "labels_ja": dict(_LABELS_JA),
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
        "streamlit_render_invoked": False,
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


def build_warroom_v2_compact_ws_status_line_visible_render_adapter_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    visible_render_adapter_requested: bool = False,
    operator_visible_render_ack: bool = False,
    visible_mount_requested: bool = False,
    operator_visible_mount_ack: bool = False,
    status_gate_render_requested: bool = False,
    status_gate_read_only_ack: bool = False,
) -> dict[str, Any]:
    observation = build_warroom_v2_compact_ws_status_line_visible_mount_gate_observation_packet(
        fragment_summary=fragment_summary,
        messages=list(messages or []),
        visible_mount_requested=visible_mount_requested,
        operator_visible_mount_ack=operator_visible_mount_ack,
        status_gate_render_requested=status_gate_render_requested,
        status_gate_read_only_ack=status_gate_read_only_ack,
    )
    mount_ready = bool(observation.get("visible_mount_ready_for_future_mount"))
    status_row = dict(observation.get("status_line_row") or {})
    display_items = _display_items(status_row)
    adapter_status = _adapter_status(
        render_requested=bool(visible_render_adapter_requested),
        render_ack=bool(operator_visible_render_ack),
        mount_ready=mount_ready,
    )
    payload_ready = adapter_status == "compact_ws_status_line_visible_render_payload_ready_not_rendered"
    return {
        **build_warroom_v2_compact_ws_status_line_visible_render_adapter_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_visible_render_adapter_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "compact_ws_status_line_visible_mount_gate_observation_packet": observation,
        "adapter_status": adapter_status,
        "visible_render_adapter_requested": bool(visible_render_adapter_requested),
        "operator_visible_render_ack": bool(operator_visible_render_ack),
        "visible_mount_requested": bool(visible_mount_requested),
        "operator_visible_mount_ack": bool(operator_visible_mount_ack),
        "status_gate_render_requested": bool(status_gate_render_requested),
        "status_gate_read_only_ack": bool(status_gate_read_only_ack),
        "upstream_visible_mount_ready": mount_ready,
        "render_payload_ready_for_future_streamlit_mount": bool(payload_ready),
        "display_items": display_items,
        "display_item_count": len(display_items),
        "compact_line_ja": _compact_line(display_items),
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
        "streamlit_render_invoked": False,
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
