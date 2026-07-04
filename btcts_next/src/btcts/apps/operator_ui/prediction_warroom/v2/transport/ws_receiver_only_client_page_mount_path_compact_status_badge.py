# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_compact_status_badge.py
# desc: WarRoom v2 receiver page-mount compact status badge packet. Visible one-line badge only; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_compact_status_badge.ps_q35g.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_COUNT_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_compact_status_badge_readback_count.ps_q35h.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_STATUS_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_compact_status_badge_readback_status.ps_q35i.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_STATE_PRESENCE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_compact_status_badge_state_presence.ps_q35j.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_STATE_KEY = "warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_q35g"


def _badge_status(*, mount_markdown_allowed: bool, receiver_ready: bool) -> str:
    if not mount_markdown_allowed:
        return "receiver_page_mount_compact_status_badge_blocked_mount_point_required"
    if not receiver_ready:
        return "receiver_page_mount_compact_status_badge_blocked_receiver_readiness_required"
    return "receiver_page_mount_compact_status_badge_visible_one_line_no_socket_no_send"


def _readiness_packet(hidden_observation_packet: Mapping[str, Any] | None) -> Mapping[str, Any]:
    packet = dict(hidden_observation_packet or {})
    readiness = packet.get("page_mount_path_readiness_packet")
    return readiness if isinstance(readiness, Mapping) else {}


def _readback_count(hidden_observation_packet: Mapping[str, Any] | None) -> int:
    readiness = _readiness_packet(hidden_observation_packet)
    return int(readiness.get("receiver_state_message_count") or 0)


def _readback_label(hidden_observation_packet: Mapping[str, Any] | None) -> str:
    readiness = _readiness_packet(hidden_observation_packet)
    if not readiness:
        return "unknown"
    if bool(readiness.get("receiver_page_mount_path_ready_for_next_slice")):
        return "ready"
    return "blocked"


def _state_presence_label(hidden_observation_packet: Mapping[str, Any] | None) -> str:
    readiness = _readiness_packet(hidden_observation_packet)
    if not readiness:
        return "unknown"
    if bool(readiness.get("target_receiver_state_readback_ready")) or int(readiness.get("receiver_state_message_count") or 0) > 0:
        return "present"
    return "missing"


def build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "compact_status_badge_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_VERSION,
        "compact_status_badge_readback_count_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_COUNT_VERSION,
        "compact_status_badge_readback_status_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_STATUS_VERSION,
        "compact_status_badge_state_presence_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_STATE_PRESENCE_VERSION,
        "compact_status_badge_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_visible_one_line_no_socket_no_send",
        "state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_STATE_KEY,
        "selected_visible_surface": "compact_status_badge",
        "visible_surface_implemented_now": True,
        "visible_surface_implementation_allowed_now": True,
        "readback_count_display_enabled": True,
        "readback_status_display_enabled": True,
        "state_presence_display_enabled": True,
        "warroom_page_modified": True,
        "warroom_page_visible_ui_modified": True,
        "q35i_warroom_page_delta_modified": False,
        "q35i_warroom_page_visible_ui_delta_modified": False,
        "q35j_warroom_page_delta_modified": False,
        "q35j_warroom_page_visible_ui_delta_modified": False,
        "visible_information_added": True,
        "visible_controls_added": False,
        "renders_badge_now": True,
        "renders_card_now": False,
        "renders_balloon_now": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "streamlit_markdown_only": True,
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


def build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet(
    *,
    visible_mount_point_packet: Mapping[str, Any] | None = None,
    hidden_observation_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    mount = dict(visible_mount_point_packet or {})
    hidden = dict(hidden_observation_packet or {})
    mount_markdown_allowed = bool(mount.get("streamlit_markdown_allowed"))
    receiver_ready = bool(
        mount.get("status_line_visible_now")
        or mount.get("status_line_mounted_now")
        or mount.get("streamlit_markdown_allowed")
    )
    status = _badge_status(mount_markdown_allowed=mount_markdown_allowed, receiver_ready=receiver_ready)
    visible_now = status == "receiver_page_mount_compact_status_badge_visible_one_line_no_socket_no_send"
    receiver_state_message_count = _readback_count(hidden)
    readback_label = _readback_label(hidden)
    state_presence_label = _state_presence_label(hidden)
    compact_badge_markdown = ""
    if visible_now:
        compact_badge_markdown = f"`WS Receiver` mount ready · state={state_presence_label} · readback={readback_label} · msgs={receiver_state_message_count} · no socket/send"
    return {
        **build_warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_compact_status_badge_packet",
        "visible_mount_point_packet": mount,
        "hidden_observation_packet": hidden,
        "mount_point_status": str(mount.get("mount_point_status") or ""),
        "mount_markdown_allowed": mount_markdown_allowed,
        "receiver_ready": receiver_ready,
        "receiver_state_presence_label": state_presence_label,
        "receiver_readback_label": readback_label,
        "receiver_state_message_count": receiver_state_message_count,
        "compact_status_badge_status": status,
        "compact_status_badge_visible_now": visible_now,
        "compact_badge_markdown": compact_badge_markdown,
        "visible_surface_implemented_now": visible_now,
        "visible_surface_implementation_allowed_now": visible_now,
        "visible_information_added": visible_now,
        "renders_badge_now": visible_now,
        "renders_card_now": False,
        "renders_balloon_now": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "streamlit_markdown_allowed": visible_now,
        "page_mount_invoked_now": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "would_send_to_broker": False,
    }
