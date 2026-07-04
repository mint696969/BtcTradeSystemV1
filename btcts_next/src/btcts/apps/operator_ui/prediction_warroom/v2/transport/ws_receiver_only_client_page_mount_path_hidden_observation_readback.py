# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_hidden_observation_readback.py
# desc: WarRoom v2 receiver page-mount hidden observation readback diagnostics. Pure read-only helper; no UI, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_page_mount_path_hidden_observation import WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_READBACK_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_hidden_observation_readback.ps_q35c.v1"


def _readback_status(*, present: bool, value_is_mapping: bool, readiness_present: bool) -> str:
    if not present:
        return "receiver_page_mount_hidden_observation_readback_missing"
    if not value_is_mapping:
        return "receiver_page_mount_hidden_observation_readback_invalid_value"
    if not readiness_present:
        return "receiver_page_mount_hidden_observation_readback_present_without_readiness_packet"
    return "receiver_page_mount_hidden_observation_readback_present"


def build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "hidden_observation_readback_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_READBACK_VERSION,
        "hidden_observation_readback_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_default_off_no_visible_ui_no_send",
        "source_state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY,
        "input_pipeline": ["q35b_hidden_observation_session_state"],
        "read_only": True,
        "metadata_only": True,
        "hidden_readback_diagnostic": True,
        "default_status": "receiver_page_mount_hidden_observation_readback_missing",
        "ready_status": "receiver_page_mount_hidden_observation_readback_present",
        "warroom_page_modified": False,
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


def build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet(
    session_state: Mapping[str, Any] | None = None,
    *,
    state_key: str = WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_HIDDEN_OBSERVATION_STATE_KEY,
) -> dict[str, Any]:
    state = session_state or {}
    present = state_key in state
    value = state.get(state_key)
    value_is_mapping = isinstance(value, Mapping)
    observation_packet = dict(value) if value_is_mapping else {}
    readiness_value = observation_packet.get("page_mount_path_readiness_packet") if observation_packet else None
    readiness_present = isinstance(readiness_value, Mapping)
    readiness_packet = dict(readiness_value) if readiness_present else {}
    status = _readback_status(present=present, value_is_mapping=value_is_mapping, readiness_present=readiness_present)
    ready = status == "receiver_page_mount_hidden_observation_readback_present"
    return {
        **build_warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_hidden_observation_readback_packet",
        "state_key": state_key,
        "hidden_observation_present": present,
        "hidden_observation_value_is_mapping": value_is_mapping,
        "hidden_observation_value_kind": type(value).__name__ if present else "",
        "page_mount_path_readiness_packet_present": readiness_present,
        "hidden_observation_readback_status": status,
        "hidden_observation_readback_ready_for_next_slice": ready,
        "hidden_observation_packet": observation_packet,
        "page_mount_path_readiness_packet": readiness_packet,
        "receiver_page_mount_path_status": str(observation_packet.get("receiver_page_mount_path_status") or readiness_packet.get("receiver_page_mount_path_status") or ""),
        "receiver_page_mount_path_ready_for_next_slice": bool(observation_packet.get("receiver_page_mount_path_ready_for_next_slice") or readiness_packet.get("receiver_page_mount_path_ready_for_next_slice")),
        "target_receiver_state_readback_ready": bool(observation_packet.get("target_receiver_state_readback_ready") or readiness_packet.get("target_receiver_state_readback_ready")),
        "visible_mount_point_ready_for_page_mount_path": bool(observation_packet.get("visible_mount_point_ready_for_page_mount_path") or readiness_packet.get("visible_mount_point_ready_for_page_mount_path")),
        "receiver_state_target_key": str(observation_packet.get("receiver_state_target_key") or readiness_packet.get("receiver_state_target_key") or ""),
        "receiver_state_message_count": int(observation_packet.get("receiver_state_message_count") or readiness_packet.get("receiver_state_message_count") or 0),
        "mount_point_status": str(observation_packet.get("mount_point_status") or readiness_packet.get("mount_point_status") or ""),
        "read_only": True,
        "metadata_only": True,
        "warroom_page_modified": False,
        "visible_information_added": False,
        "streamlit_render_allowed": False,
        "page_mount_invoked_now": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "would_send_to_broker": False,
    }
