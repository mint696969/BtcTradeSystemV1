# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_visible_surface_proposal.py
# desc: WarRoom v2 receiver page-mount visible surface proposal packet. Proposal-only; no UI implementation, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_visible_surface_proposal.ps_q35e.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ALLOWED_SURFACES = (
    "compact_status_badge",
    "compact_status_card",
    "dismissible_operator_balloon",
)


def _proposal_status(*, q35c_ready: bool, surface: str, valid_surface: bool, operator_ack: bool) -> str:
    if not q35c_ready:
        return "receiver_page_mount_visible_surface_proposal_blocked_q35c_readback_required"
    if not surface:
        return "receiver_page_mount_visible_surface_proposal_no_surface_selected"
    if not valid_surface:
        return "receiver_page_mount_visible_surface_proposal_invalid_surface"
    if not operator_ack:
        return "receiver_page_mount_visible_surface_proposal_waiting_operator_ack"
    return "receiver_page_mount_visible_surface_proposal_accepted_for_future_slice_no_implementation"


def build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "visible_surface_proposal_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_VERSION,
        "visible_surface_proposal_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_only_no_implementation_no_send",
        "input_pipeline": ["q35d_next_boundary"],
        "allowed_visible_surfaces": list(WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ALLOWED_SURFACES),
        "proposal_only": True,
        "metadata_only": True,
        "read_only": True,
        "default_operator_proposal_ack": False,
        "visible_surface_requires_explicit_proposal": True,
        "visible_surface_requires_operator_ack": True,
        "visible_surface_implementation_allowed_now": False,
        "visible_surface_implemented_now": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "renders_badge_now": False,
        "renders_card_now": False,
        "renders_balloon_now": False,
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


def build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet(
    *,
    next_boundary_packet: Mapping[str, Any] | None = None,
    proposed_visible_surface: str = "",
    operator_readability_reason: str = "",
    operator_proposal_ack: bool = False,
) -> dict[str, Any]:
    boundary = dict(next_boundary_packet or {})
    q35c_ready = bool(boundary.get("q35c_readback_ready"))
    surface = str(proposed_visible_surface or "").strip()
    valid_surface = surface in WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ALLOWED_SURFACES
    ack = bool(operator_proposal_ack)
    status = _proposal_status(q35c_ready=q35c_ready, surface=surface, valid_surface=valid_surface, operator_ack=ack)
    proposal_ready = status == "receiver_page_mount_visible_surface_proposal_accepted_for_future_slice_no_implementation"
    return {
        **build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_proposal_packet",
        "next_boundary_packet": boundary,
        "q35c_readback_ready": q35c_ready,
        "q35d_next_boundary_status": str(boundary.get("next_boundary_status") or ""),
        "q35d_visible_surface_implementation_allowed_now": bool(boundary.get("visible_surface_implementation_allowed_now")),
        "proposed_visible_surface": surface,
        "proposed_visible_surface_valid": valid_surface,
        "operator_readability_reason": str(operator_readability_reason or ""),
        "operator_proposal_ack": ack,
        "visible_surface_proposal_status": status,
        "visible_surface_proposal_ready_for_future_slice": proposal_ready,
        "visible_surface_implementation_allowed_now": False,
        "visible_surface_implemented_now": False,
        "proposal_only": True,
        "metadata_only": True,
        "read_only": True,
        "warroom_page_modified": False,
        "visible_information_added": False,
        "visible_controls_added": False,
        "renders_badge_now": False,
        "renders_card_now": False,
        "renders_balloon_now": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "streamlit_render_allowed": False,
        "page_mount_invoked_now": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "would_send_to_broker": False,
    }
