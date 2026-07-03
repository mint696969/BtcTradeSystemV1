# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_enable_gate.py
# desc: WarRoom v2 receiver-only client enable gate. Pure packet only; default-off, no socket open, no send, no UI controls.

from __future__ import annotations

from typing import Any, Mapping

from .compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation import build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet
from .ws_display_client import build_warroom_v2_ws_display_client_contract

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_ENABLE_GATE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_enable_gate.ps_q33a.v1"


def _gate_status(*, requested: bool, ack: bool, q32_ready: bool) -> str:
    if not requested:
        return "receiver_enable_gate_hidden_default"
    if not ack:
        return "receiver_enable_gate_blocked_operator_ack_required"
    if not q32_ready:
        return "receiver_enable_gate_blocked_q32_display_mount_preparation_required"
    return "receiver_enable_gate_ready_for_next_slice_no_socket"


def build_warroom_v2_ws_receiver_only_client_enable_gate_contract() -> dict[str, Any]:
    client = build_warroom_v2_ws_display_client_contract()
    return {
        "ok": True,
        "gate_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_ENABLE_GATE_VERSION,
        "gate_kind": "warroom_v2_ws_receiver_only_client_enable_gate_default_off_no_send",
        "input_pipeline": ["q32z_visible_mount_point_operator_ack_observation", "q32b_hidden_ws_display_client_observation", "q32a_ws_display_client_contract"],
        "current_small_goal": "warroom_tab_ws_push_realtime_update_and_japanese_readability",
        "agreed_refresh_policy": "push_first_fragment_render_lightweight_state_pluggable_widget_custom_component_island_ready_later",
        "receiver_enable_requested_default": False,
        "operator_receiver_enable_ack_default": False,
        "receiver_enable_gate_status_default": "receiver_enable_gate_hidden_default",
        "receiver_enable_gate_status_ready": "receiver_enable_gate_ready_for_next_slice_no_socket",
        "q32_display_mount_preparation_required": True,
        "q32_display_mount_preparation_default": False,
        "manual_smoke_ready_required": True,
        "receiver_only": True,
        "send_disabled": True,
        "receive_only_boundary": True,
        "receiver_client_enable_allowed_for_next_slice_default": False,
        "receiver_client_enable_allowed_effective": False,
        "receiver_enabled_effective": False,
        "client_kind": client.get("client_kind"),
        "target_topics": list(client.get("target_topics") or []),
        "receive_buffer_default_limit": int(client.get("receive_buffer_default_limit") or 128),
        "bounded_receive_buffer": True,
        "socket_open_requested_default": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "warroom_page_modified": False,
        "visible_controls_added": False,
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


def build_warroom_v2_ws_receiver_only_client_enable_gate_packet(
    *,
    q32z_operator_ack_observation_packet: Mapping[str, Any] | None = None,
    receiver_enable_requested: bool = False,
    operator_receiver_enable_ack: bool = False,
) -> dict[str, Any]:
    q32z_packet = dict(q32z_operator_ack_observation_packet or build_warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_visible_mount_point_operator_ack_observation_packet())
    q32_ready = bool(q32z_packet.get("manual_smoke_ready_for_operator_visual_check"))
    status = _gate_status(requested=bool(receiver_enable_requested), ack=bool(operator_receiver_enable_ack), q32_ready=q32_ready)
    allowed_next = status == "receiver_enable_gate_ready_for_next_slice_no_socket"
    return {
        **build_warroom_v2_ws_receiver_only_client_enable_gate_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_enable_gate_packet",
        "receiver_enable_requested": bool(receiver_enable_requested),
        "operator_receiver_enable_ack": bool(operator_receiver_enable_ack),
        "q32_display_mount_preparation_ready": q32_ready,
        "q32z_operator_ack_observation_packet": q32z_packet,
        "receiver_enable_gate_status": status,
        "receiver_client_enable_allowed_for_next_slice": bool(allowed_next),
        "receiver_client_enable_allowed_effective": False,
        "receiver_enabled_effective": False,
        "socket_open_requested": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
