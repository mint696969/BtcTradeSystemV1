# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_next_boundary.py
# desc: WarRoom v2 receiver page-mount next-boundary guard. Metadata-only; no visible UI, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_NEXT_BOUNDARY_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_next_boundary.ps_q35d.v1"


def _boundary_status(*, readback_ready: bool, visible_requested: bool, proposal_ack: bool, hidden_guard_requested: bool) -> str:
    if not readback_ready:
        return "receiver_page_mount_next_boundary_blocked_q35c_readback_required"
    if visible_requested and not proposal_ack:
        return "receiver_page_mount_next_boundary_blocked_visible_surface_proposal_required"
    if visible_requested and proposal_ack:
        return "receiver_page_mount_next_boundary_visible_surface_proposal_ready_no_implementation"
    if hidden_guard_requested:
        return "receiver_page_mount_next_boundary_hidden_guard_allowed"
    return "receiver_page_mount_next_boundary_waiting"


def build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "next_boundary_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_NEXT_BOUNDARY_VERSION,
        "next_boundary_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_default_off_no_visible_ui_no_send",
        "input_pipeline": ["q35c_hidden_observation_readback"],
        "metadata_only": True,
        "read_only": True,
        "default_visible_surface_requested": False,
        "default_operator_visible_surface_proposal_ack": False,
        "default_hidden_receiver_guard_requested": True,
        "visible_surface_requires_explicit_proposal": True,
        "visible_surface_implementation_allowed_now": False,
        "hidden_receiver_guard_can_continue": True,
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


def build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet(
    *,
    hidden_observation_readback_packet: Mapping[str, Any] | None = None,
    visible_surface_requested: bool = False,
    operator_visible_surface_proposal_ack: bool = False,
    hidden_receiver_guard_requested: bool = True,
) -> dict[str, Any]:
    readback = dict(hidden_observation_readback_packet or {})
    readback_ready = bool(readback.get("hidden_observation_readback_ready_for_next_slice"))
    visible_requested = bool(visible_surface_requested)
    proposal_ack = bool(operator_visible_surface_proposal_ack)
    hidden_requested = bool(hidden_receiver_guard_requested)
    status = _boundary_status(
        readback_ready=readback_ready,
        visible_requested=visible_requested,
        proposal_ack=proposal_ack,
        hidden_guard_requested=hidden_requested,
    )
    hidden_allowed = status == "receiver_page_mount_next_boundary_hidden_guard_allowed"
    visible_proposal_ready = status == "receiver_page_mount_next_boundary_visible_surface_proposal_ready_no_implementation"
    return {
        **build_warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_next_boundary_packet",
        "hidden_observation_readback_packet": readback,
        "q35c_readback_status": str(readback.get("hidden_observation_readback_status") or ""),
        "q35c_readback_ready": readback_ready,
        "receiver_page_mount_path_status": str(readback.get("receiver_page_mount_path_status") or ""),
        "receiver_page_mount_path_ready_for_next_slice": bool(readback.get("receiver_page_mount_path_ready_for_next_slice")),
        "visible_surface_requested": visible_requested,
        "operator_visible_surface_proposal_ack": proposal_ack,
        "hidden_receiver_guard_requested": hidden_requested,
        "next_boundary_status": status,
        "next_hidden_receiver_guard_allowed": hidden_allowed,
        "next_visible_surface_proposal_ready": visible_proposal_ready,
        "visible_surface_implementation_allowed_now": False,
        "metadata_only": True,
        "read_only": True,
        "warroom_page_modified": False,
        "visible_information_added": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "streamlit_render_allowed": False,
        "page_mount_invoked_now": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "would_send_to_broker": False,
    }
