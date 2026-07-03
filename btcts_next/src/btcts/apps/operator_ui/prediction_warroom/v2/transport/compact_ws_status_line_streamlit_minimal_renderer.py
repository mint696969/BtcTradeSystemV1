# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_streamlit_minimal_renderer.py
# desc: WarRoom v2 compact WS status line minimal renderer spec. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .compact_ws_status_line_visible_render_mount_gate_observation import build_warroom_v2_compact_ws_status_line_visible_render_mount_gate_observation_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_streamlit_minimal_renderer.ps_q32m.v1"
_LABELS_JA: tuple[str, ...] = ("WS状態", "データ鮮度", "最終更新", "受信数", "破棄数", "案内")


def _renderer_status(*, renderer_requested: bool, renderer_ack: bool, mount_ready: bool) -> str:
    if not renderer_requested:
        return "compact_ws_status_line_streamlit_minimal_renderer_hidden_default"
    if not renderer_ack:
        return "compact_ws_status_line_streamlit_minimal_renderer_blocked_ack_required"
    if not mount_ready:
        return "compact_ws_status_line_streamlit_minimal_renderer_blocked_mount_gate_not_ready"
    return "compact_ws_status_line_streamlit_minimal_renderer_model_ready_not_rendered"


def _renderer_model(*, display_items: list[dict[str, Any]], compact_line_ja: str, ready: bool) -> dict[str, Any]:
    return {
        "model_kind": "warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_model",
        "layout_role": "top_minimal_operator_status_line",
        "mount_position": "after_header_before_focus_nav_later",
        "render_instruction_kind": "future_single_line_status_text",
        "aria_label_ja": "WarRoom WebSocket 状態",
        "display_items": display_items,
        "display_item_count": len(display_items),
        "display_item_labels_ja": [str(item.get("label_ja") or "") for item in display_items],
        "compact_line_ja": compact_line_ja,
        "ready_for_future_streamlit_call": bool(ready),
        "streamlit_call_name": "caption_or_markdown_later",
        "streamlit_imported": False,
        "streamlit_render_invoked": False,
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
    }


def build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_VERSION,
        "renderer_kind": "warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_default_off",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "input_pipeline": ["q32l_compact_ws_status_line_visible_render_mount_gate_observation"],
        "renderer_requested_default": False,
        "operator_renderer_ack_default": False,
        "visible_render_mount_requested_default": False,
        "operator_visible_render_mount_ack_default": False,
        "visible_render_adapter_requested_default": False,
        "operator_visible_render_ack_default": False,
        "default_renderer_status": "compact_ws_status_line_streamlit_minimal_renderer_hidden_default",
        "ready_renderer_status": "compact_ws_status_line_streamlit_minimal_renderer_model_ready_not_rendered",
        "warroom_mount_surface": "top_minimal_operator_status_line",
        "warroom_mount_position": "after_header_before_focus_nav_later",
        "warroom_page_modified": False,
        "display_item_labels_ja": list(_LABELS_JA),
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
        "streamlit_imported": False,
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


def build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    renderer_requested: bool = False,
    operator_renderer_ack: bool = False,
    visible_render_mount_requested: bool = False,
    operator_visible_render_mount_ack: bool = False,
    visible_render_adapter_requested: bool = False,
    operator_visible_render_ack: bool = False,
    visible_mount_requested: bool = False,
    operator_visible_mount_ack: bool = False,
    status_gate_render_requested: bool = False,
    status_gate_read_only_ack: bool = False,
) -> dict[str, Any]:
    observation = build_warroom_v2_compact_ws_status_line_visible_render_mount_gate_observation_packet(
        fragment_summary=fragment_summary,
        messages=list(messages or []),
        visible_render_mount_requested=visible_render_mount_requested,
        operator_visible_render_mount_ack=operator_visible_render_mount_ack,
        visible_render_adapter_requested=visible_render_adapter_requested,
        operator_visible_render_ack=operator_visible_render_ack,
        visible_mount_requested=visible_mount_requested,
        operator_visible_mount_ack=operator_visible_mount_ack,
        status_gate_render_requested=status_gate_render_requested,
        status_gate_read_only_ack=status_gate_read_only_ack,
    )
    mount_ready = bool(observation.get("render_mount_ready_for_future_streamlit_mount"))
    renderer_status = _renderer_status(renderer_requested=bool(renderer_requested), renderer_ack=bool(operator_renderer_ack), mount_ready=mount_ready)
    ready = renderer_status == "compact_ws_status_line_streamlit_minimal_renderer_model_ready_not_rendered"
    display_items = list(observation.get("display_items") or [])
    compact_line = str(observation.get("compact_line_ja") or "")
    return {
        **build_warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "compact_ws_status_line_visible_render_mount_gate_observation_packet": observation,
        "renderer_status": renderer_status,
        "renderer_requested": bool(renderer_requested),
        "operator_renderer_ack": bool(operator_renderer_ack),
        "upstream_render_mount_ready": mount_ready,
        "renderer_model_ready_for_future_streamlit_mount": bool(ready),
        "renderer_model": _renderer_model(display_items=display_items, compact_line_ja=compact_line, ready=ready),
        "display_items": display_items,
        "display_item_count": int(observation.get("display_item_count") or 0),
        "compact_line_ja": compact_line,
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
        "streamlit_imported": False,
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
