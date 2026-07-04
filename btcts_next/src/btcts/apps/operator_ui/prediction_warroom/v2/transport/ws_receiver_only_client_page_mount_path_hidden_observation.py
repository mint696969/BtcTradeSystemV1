# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_hidden_observation.py
# desc: WarRoom v2 receiver page-mount path hidden observation packet. Default-off, no visible UI, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_page_mount_path_readiness import build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_hidden_observation.ps_q35b.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY = "warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_q35b"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_REQUEST_STATE_KEY = "warroom_v2_ws_receiver_only_client_page_mount_path_requested_q35b"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_OPERATOR_ACK_STATE_KEY = "warroom_v2_ws_receiver_only_client_page_mount_path_operator_ack_q35b"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_TARGET_READBACK_STATE_KEY = "warroom_v2_ws_receiver_only_client_page_mount_path_target_readback_q35b"


def build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "hidden_observation_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_VERSION,
        "hidden_observation_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_default_off_no_visible_ui_no_send",
        "state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY,
        "request_state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_REQUEST_STATE_KEY,
        "operator_ack_state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_OPERATOR_ACK_STATE_KEY,
        "target_readback_state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_TARGET_READBACK_STATE_KEY,
        "input_pipeline": ["q35a_page_mount_path_readiness", "q32y_visible_mount_point_session_state", "optional_q33m_target_readback_session_state"],
        "hidden_session_state_observation": True,
        "default_requested": False,
        "default_operator_ack": False,
        "metadata_only": True,
        "warroom_page_hidden_record_allowed": True,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "streamlit_render_allowed": False,
        "page_mount_invoked_now": False,
        "receiver_only": True,
        "send_disabled": True,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
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


def build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    target_write_readback_reset_rollback_packet: Mapping[str, Any] | None = None,
    visible_mount_point_packet: Mapping[str, Any] | None = None,
    receiver_page_mount_path_requested: bool = False,
    operator_receiver_page_mount_path_ack: bool = False,
) -> dict[str, Any]:
    readiness_packet = build_warroom_v2_ws_receiver_only_client_page_mount_path_readiness_packet(
        target_write_readback_reset_rollback_packet=target_write_readback_reset_rollback_packet,
        visible_mount_point_packet=visible_mount_point_packet,
        receiver_page_mount_path_requested=receiver_page_mount_path_requested,
        operator_receiver_page_mount_path_ack=operator_receiver_page_mount_path_ack,
    )
    ready = bool(readiness_packet.get("receiver_page_mount_path_ready_for_next_slice"))
    return {
        **build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "page_mount_path_readiness_packet": readiness_packet,
        "receiver_page_mount_path_requested": bool(receiver_page_mount_path_requested),
        "operator_receiver_page_mount_path_ack": bool(operator_receiver_page_mount_path_ack),
        "receiver_page_mount_path_status": str(readiness_packet.get("receiver_page_mount_path_status") or ""),
        "receiver_page_mount_path_ready_for_next_slice": ready,
        "target_receiver_state_readback_ready": bool(readiness_packet.get("target_receiver_state_readback_ready")),
        "visible_mount_point_ready_for_page_mount_path": bool(readiness_packet.get("visible_mount_point_ready_for_page_mount_path")),
        "receiver_state_target_key": str(readiness_packet.get("receiver_state_target_key") or ""),
        "receiver_state_message_count": int(readiness_packet.get("receiver_state_message_count") or 0),
        "mount_point_status": str(readiness_packet.get("mount_point_status") or ""),
        "metadata_only": True,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "streamlit_render_allowed": False,
        "page_mount_invoked_now": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
