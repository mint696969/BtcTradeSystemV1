# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_readiness.py
# desc: WarRoom v2 receiver-only client page-mount path readiness contract. Default-off/operator-gated, no page edit, no socket open, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_READINESS_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_readiness.ps_q35a.v1"


def _target_state_ready(packet: Mapping[str, Any]) -> bool:
    return bool(packet.get("readback_after_present")) and int(packet.get("readback_after_message_count") or 0) > 0


def _mount_point_ready(packet: Mapping[str, Any]) -> bool:
    return bool(packet.get("streamlit_markdown_allowed") or packet.get("status_line_mounted_now") or packet.get("status_line_visible_now"))


def _readiness_status(*, requested: bool, ack: bool, target_ready: bool, mount_ready: bool) -> str:
    if not requested:
        return "receiver_page_mount_path_hidden_default"
    if not ack:
        return "receiver_page_mount_path_blocked_operator_ack_required"
    if not target_ready:
        return "receiver_page_mount_path_blocked_receiver_state_readback_required"
    if not mount_ready:
        return "receiver_page_mount_path_blocked_visible_mount_point_readiness_required"
    return "receiver_page_mount_path_ready_no_socket_no_send"


def build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "page_mount_path_readiness_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_READINESS_VERSION,
        "page_mount_path_readiness_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_readiness_default_off_operator_gated_no_send",
        "input_pipeline": ["q33m_target_write_readback_reset_rollback", "q32y_visible_mount_point", "q32z_manual_smoke_observation"],
        "receiver_page_mount_path_requested_default": False,
        "operator_receiver_page_mount_path_ack_default": False,
        "page_mount_path_status_default": "receiver_page_mount_path_hidden_default",
        "page_mount_path_status_ready": "receiver_page_mount_path_ready_no_socket_no_send",
        "target_receiver_state_readback_required": True,
        "visible_mount_point_readiness_required": True,
        "metadata_only": True,
        "warroom_page_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "receiver_only": True,
        "send_disabled": True,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "page_mount_invoked_now": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
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


def build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet(
    *,
    target_write_readback_reset_rollback_packet: Mapping[str, Any] | None = None,
    visible_mount_point_packet: Mapping[str, Any] | None = None,
    receiver_page_mount_path_requested: bool = False,
    operator_receiver_page_mount_path_ack: bool = False,
) -> dict[str, Any]:
    target_packet = dict(target_write_readback_reset_rollback_packet or {})
    mount_packet = dict(visible_mount_point_packet or {})
    target_ready = _target_state_ready(target_packet)
    mount_ready = _mount_point_ready(mount_packet)
    status = _readiness_status(
        requested=bool(receiver_page_mount_path_requested),
        ack=bool(operator_receiver_page_mount_path_ack),
        target_ready=target_ready,
        mount_ready=mount_ready,
    )
    ready = status == "receiver_page_mount_path_ready_no_socket_no_send"
    return {
        **build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet",
        "target_write_readback_reset_rollback_packet": target_packet,
        "visible_mount_point_packet": mount_packet,
        "receiver_page_mount_path_requested": bool(receiver_page_mount_path_requested),
        "operator_receiver_page_mount_path_ack": bool(operator_receiver_page_mount_path_ack),
        "target_receiver_state_readback_ready": target_ready,
        "visible_mount_point_ready_for_page_mount_path": mount_ready,
        "receiver_page_mount_path_status": status,
        "receiver_page_mount_path_ready_for_next_slice": ready,
        "receiver_state_target_key": str(target_packet.get("target_session_state_key") or ""),
        "receiver_state_message_count": int(target_packet.get("readback_after_message_count") or 0),
        "mount_point_status": str(mount_packet.get("mount_point_status") or mount_packet.get("q32y_mount_point_status") or ""),
        "metadata_only": True,
        "warroom_page_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "page_mount_invoked_now": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
