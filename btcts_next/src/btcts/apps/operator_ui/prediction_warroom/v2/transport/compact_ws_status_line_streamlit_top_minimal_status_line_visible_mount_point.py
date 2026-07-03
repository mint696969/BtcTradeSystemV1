# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point.py
# desc: WarRoom v2 compact WS status line top minimal visible mount point decision. Pure packet only; no sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Mapping

from .compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation import build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point.ps_q32y.v1"
WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_STATE_KEY = "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_q32y"
WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_REQUEST_STATE_KEY = "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_requested_q32y"
WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_STATE_KEY = "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_q32y"
_LABELS_JA: tuple[str, ...] = ("WS状態", "データ鮮度", "最終更新", "受信数", "破棄数", "案内")


def _status(*, requested: bool, ack: bool, ready: bool) -> str:
    if not requested:
        return "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_hidden_default"
    if not ack:
        return "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_blocked_operator_ack_required"
    if not ready:
        return "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_blocked_ready_observation_required"
    return "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed"


def build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "mount_point_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_VERSION,
        "state_key": WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_STATE_KEY,
        "request_state_key": WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_REQUEST_STATE_KEY,
        "operator_ack_state_key": WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_STATE_KEY,
        "mount_point_kind": "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_default_off_operator_ack",
        "input_pipeline": ["q32x_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation"],
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "agreed_refresh_policy": "push_first_fragment_render_lightweight_state_pluggable_widget_custom_component_island_ready_later",
        "visible_mount_point_requested_default": False,
        "operator_visible_mount_point_ack_default": False,
        "q32x_ready_required": True,
        "mount_point_status_default": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_hidden_default",
        "mount_point_status_ready": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed",
        "warroom_mount_surface": "top_minimal_operator_status_line",
        "warroom_mount_position": "after_header_before_focus_nav_later",
        "streamlit_call_name": "markdown",
        "streamlit_markdown_allowed_default": False,
        "streamlit_markdown_invoked_default": False,
        "status_line_visible_now_default": False,
        "status_line_mounted_now_default": False,
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


def build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet(
    *,
    visible_render_mount_gate_observation_packet: Mapping[str, Any] | None = None,
    visible_mount_point_requested: bool = False,
    operator_visible_mount_point_ack: bool = False,
) -> dict[str, Any]:
    observation = dict(visible_render_mount_gate_observation_packet or build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation_packet())
    ready = bool(observation.get("render_mount_ready_for_future_streamlit_mount"))
    mount_status = _status(requested=bool(visible_mount_point_requested), ack=bool(operator_visible_mount_point_ack), ready=ready)
    allowed = mount_status == "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_markdown_allowed"
    compact_line = str(observation.get("compact_line_ja") or "")
    return {
        **build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet",
        "visible_mount_point_requested": bool(visible_mount_point_requested),
        "operator_visible_mount_point_ack": bool(operator_visible_mount_point_ack),
        "q32x_ready_observation": ready,
        "mount_point_status": mount_status,
        "streamlit_markdown_allowed": bool(allowed),
        "streamlit_markdown_invoked": False,
        "status_line_visible_now": bool(allowed),
        "status_line_mounted_now": bool(allowed),
        "streamlit_call_name": "markdown",
        "compact_ws_status_line_streamlit_top_minimal_status_line_visible_render_mount_gate_observation_packet": observation,
        "future_streamlit_call_model": dict(observation.get("future_streamlit_call_model") or {}),
        "renderer_model": dict(observation.get("renderer_model") or {}),
        "display_items": list(observation.get("display_items") or []),
        "display_item_count": int(observation.get("display_item_count") or 0),
        "compact_line_ja": compact_line,
        "visible_ui_decoration_added": bool(allowed),
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
