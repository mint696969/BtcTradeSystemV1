# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation.py
# desc: WarRoom v2 compact WS status line top minimal visible mount point operator ack observation/manual smoke guide. Pure packet only; no UI controls, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Mapping

from .compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point import build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_OBSERVATION_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation.ps_q32z.v1"


def _manual_smoke_status(*, requested: bool, ack: bool, markdown_allowed: bool) -> str:
    if not requested:
        return "manual_smoke_not_requested"
    if not ack:
        return "manual_smoke_blocked_operator_ack_required"
    if not markdown_allowed:
        return "manual_smoke_blocked_mount_point_not_markdown_allowed"
    return "manual_smoke_ready_for_operator_visual_check_no_socket"


def build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "observation_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_OBSERVATION_VERSION,
        "observation_kind": "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet",
        "input_pipeline": ["q32x_visible_render_mount_gate_observation", "q32y_visible_mount_point"],
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "agreed_refresh_policy": "push_first_fragment_render_lightweight_state_pluggable_widget_custom_component_island_ready_later",
        "manual_smoke_guide_added": True,
        "manual_smoke_default_enabled": False,
        "manual_smoke_requires_operator_ack": True,
        "manual_smoke_status_default": "manual_smoke_not_requested",
        "manual_smoke_status_ready": "manual_smoke_ready_for_operator_visual_check_no_socket",
        "visible_controls_added": False,
        "warroom_page_modified": False,
        "visible_mount_point_requested_default": False,
        "operator_visible_mount_point_ack_default": False,
        "operator_ack_observed_default": False,
        "mount_point_status_default": "compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_hidden_default",
        "streamlit_markdown_allowed_default": False,
        "streamlit_markdown_invoked_default": False,
        "status_line_visible_now_default": False,
        "status_line_mounted_now_default": False,
        "manual_smoke_steps": [
            "open_WarRoom_normally",
            "confirm_default_UI_unchanged_and_no_top_minimal_WS_line",
            "inspect_hidden_session_state_packet_if_needed",
            "set_request_key_true_and_operator_ack_key_true_only_in_manual_dev_session",
            "confirm_compact_line_can_render_only_when_gate_allows_markdown",
            "reset_request_key_false_and_operator_ack_key_false",
        ],
        "rollback": "reset_hidden_request_and_operator_ack_keys_to_false",
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


def build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet(
    *,
    visible_render_mount_gate_observation_packet: Mapping[str, Any] | None = None,
    visible_mount_point_requested: bool = False,
    operator_visible_mount_point_ack: bool = False,
    manual_smoke_requested: bool = False,
    operator_manual_smoke_ack: bool = False,
) -> dict[str, Any]:
    mount_point_packet = build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_packet(
        visible_render_mount_gate_observation_packet=visible_render_mount_gate_observation_packet,
        visible_mount_point_requested=visible_mount_point_requested,
        operator_visible_mount_point_ack=operator_visible_mount_point_ack,
    )
    markdown_allowed = bool(mount_point_packet.get("streamlit_markdown_allowed"))
    manual_status = _manual_smoke_status(requested=bool(manual_smoke_requested), ack=bool(operator_manual_smoke_ack), markdown_allowed=markdown_allowed)
    ready = manual_status == "manual_smoke_ready_for_operator_visual_check_no_socket"
    return {
        **build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet",
        "visible_mount_point_packet": mount_point_packet,
        "visible_mount_point_requested": bool(visible_mount_point_requested),
        "operator_visible_mount_point_ack": bool(operator_visible_mount_point_ack),
        "operator_ack_observed": bool(operator_visible_mount_point_ack),
        "manual_smoke_requested": bool(manual_smoke_requested),
        "operator_manual_smoke_ack": bool(operator_manual_smoke_ack),
        "manual_smoke_status": manual_status,
        "manual_smoke_ready_for_operator_visual_check": bool(ready),
        "q32y_mount_point_status": str(mount_point_packet.get("mount_point_status") or ""),
        "q32y_markdown_allowed": markdown_allowed,
        "streamlit_markdown_allowed": markdown_allowed,
        "streamlit_markdown_invoked": False,
        "status_line_visible_now": bool(mount_point_packet.get("status_line_visible_now")),
        "status_line_mounted_now": bool(mount_point_packet.get("status_line_mounted_now")),
        "compact_line_ja": str(mount_point_packet.get("compact_line_ja") or ""),
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
