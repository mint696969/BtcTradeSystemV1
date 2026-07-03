# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_streamlit_top_minimal_status_line_renderer.py
# desc: WarRoom v2 compact WS status line top minimal renderer contract. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .compact_ws_status_line_streamlit_visible_mount_gate_observation import build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_observation_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_RENDERER_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_streamlit_top_minimal_status_line_renderer.ps_q32q.v1"
_LABELS_JA: tuple[str, ...] = ("WS状態", "データ鮮度", "最終更新", "受信数", "破棄数", "案内")


def _renderer_status(*, requested: bool, ack: bool, upstream_mount_allowed: bool) -> str:
    if not requested:
        return "compact_ws_status_line_streamlit_top_minimal_status_line_renderer_hidden_default"
    if not ack:
        return "compact_ws_status_line_streamlit_top_minimal_status_line_renderer_blocked_ack_required"
    if not upstream_mount_allowed:
        return "compact_ws_status_line_streamlit_top_minimal_status_line_renderer_blocked_mount_gate_not_ready"
    return "compact_ws_status_line_streamlit_top_minimal_status_line_renderer_ready_not_rendered"


def _future_call_model(*, compact_line_ja: str, ready: bool) -> dict[str, Any]:
    return {
        "model_kind": "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_call_model",
        "target_surface": "top_minimal_operator_status_line",
        "target_position": "after_header_before_focus_nav_later",
        "future_call_kind": "single_markdown_status_line_later",
        "future_call_name": "markdown",
        "text_ja": compact_line_ja,
        "aria_label_ja": "WarRoom WebSocket 状態",
        "ready_for_future_streamlit_call": bool(ready),
        "streamlit_imported": False,
        "streamlit_render_invoked": False,
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
    }


def build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_renderer_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_RENDERER_VERSION,
        "renderer_kind": "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_renderer_default_off",
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "input_pipeline": ["q32p_compact_ws_status_line_streamlit_visible_mount_gate_observation"],
        "top_minimal_status_line_render_requested_default": False,
        "operator_top_minimal_status_line_render_ack_default": False,
        "visible_streamlit_mount_requested_default": False,
        "operator_visible_streamlit_mount_ack_default": False,
        "default_renderer_status": "compact_ws_status_line_streamlit_top_minimal_status_line_renderer_hidden_default",
        "ready_renderer_status": "compact_ws_status_line_streamlit_top_minimal_status_line_renderer_ready_not_rendered",
        "ready_requires": "top_minimal_status_line_render_requested_true_and_operator_ack_true_and_upstream_mount_allowed_true",
        "warroom_mount_surface": "top_minimal_operator_status_line",
        "warroom_mount_position": "after_header_before_focus_nav_later",
        "warroom_page_modified": False,
        "future_streamlit_call_prepared": True,
        "future_streamlit_call_kind": "single_markdown_status_line_later",
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


def build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_renderer_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    top_minimal_status_line_render_requested: bool = False,
    operator_top_minimal_status_line_render_ack: bool = False,
    visible_streamlit_mount_requested: bool = False,
    operator_visible_streamlit_mount_ack: bool = False,
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
    observation = build_warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_observation_packet(
        fragment_summary=fragment_summary,
        messages=list(messages or []),
        visible_streamlit_mount_requested=visible_streamlit_mount_requested,
        operator_visible_streamlit_mount_ack=operator_visible_streamlit_mount_ack,
        renderer_requested=renderer_requested,
        operator_renderer_ack=operator_renderer_ack,
        visible_render_mount_requested=visible_render_mount_requested,
        operator_visible_render_mount_ack=operator_visible_render_mount_ack,
        visible_render_adapter_requested=visible_render_adapter_requested,
        operator_visible_render_ack=operator_visible_render_ack,
        visible_mount_requested=visible_mount_requested,
        operator_visible_mount_ack=operator_visible_mount_ack,
        status_gate_render_requested=status_gate_render_requested,
        status_gate_read_only_ack=status_gate_read_only_ack,
    )
    upstream_mount_allowed = bool(observation.get("mount_allowed_for_future_warroom_page"))
    renderer_status = _renderer_status(
        requested=bool(top_minimal_status_line_render_requested),
        ack=bool(operator_top_minimal_status_line_render_ack),
        upstream_mount_allowed=upstream_mount_allowed,
    )
    ready = renderer_status == "compact_ws_status_line_streamlit_top_minimal_status_line_renderer_ready_not_rendered"
    compact_line = str(observation.get("compact_line_ja") or "")
    return {
        **build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_renderer_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_renderer_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "compact_ws_status_line_streamlit_visible_mount_gate_observation_packet": observation,
        "renderer_status": renderer_status,
        "top_minimal_status_line_render_requested": bool(top_minimal_status_line_render_requested),
        "operator_top_minimal_status_line_render_ack": bool(operator_top_minimal_status_line_render_ack),
        "upstream_mount_allowed_for_future_warroom_page": upstream_mount_allowed,
        "future_streamlit_call_ready": bool(ready),
        "future_streamlit_call_model": _future_call_model(compact_line_ja=compact_line, ready=ready),
        "renderer_model": dict(observation.get("renderer_model") or {}),
        "display_items": list(observation.get("display_items") or []),
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
