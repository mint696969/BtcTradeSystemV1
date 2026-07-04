# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate.py
# desc: WarRoom v2 receiver page-mount visible surface implementation gate. No UI implementation, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

from .ws_receiver_only_client_page_mount_path_visible_surface_proposal import WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ALLOWED_SURFACES

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_IMPLEMENTATION_GATE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate.ps_q35f.v1"


def _implementation_gate_status(*, proposal_ready: bool, valid_surface: bool, reason_present: bool, operator_scope_ack: bool) -> str:
    if not proposal_ready:
        return "receiver_page_mount_visible_surface_implementation_gate_blocked_proposal_required"
    if not valid_surface:
        return "receiver_page_mount_visible_surface_implementation_gate_blocked_invalid_surface"
    if not reason_present:
        return "receiver_page_mount_visible_surface_implementation_gate_blocked_readability_reason_required"
    if not operator_scope_ack:
        return "receiver_page_mount_visible_surface_implementation_gate_waiting_operator_scope_ack"
    return "receiver_page_mount_visible_surface_implementation_gate_ready_for_future_slice_no_implementation"


def build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "implementation_gate_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_IMPLEMENTATION_GATE_VERSION,
        "implementation_gate_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_no_ui_no_send",
        "input_pipeline": ["q35e_visible_surface_proposal"],
        "allowed_visible_surfaces": list(WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ALLOWED_SURFACES),
        "metadata_only": True,
        "read_only": True,
        "implementation_gate_only": True,
        "default_operator_scope_ack": False,
        "requires_accepted_q35e_proposal": True,
        "requires_operator_readability_reason": True,
        "requires_operator_scope_ack": True,
        "implementation_allowed_for_future_slice": False,
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


def build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_packet(
    *,
    visible_surface_proposal_packet: Mapping[str, Any] | None = None,
    operator_scope_ack: bool = False,
) -> dict[str, Any]:
    proposal = dict(visible_surface_proposal_packet or {})
    surface = str(proposal.get("proposed_visible_surface") or "")
    proposal_ready = bool(proposal.get("visible_surface_proposal_ready_for_future_slice"))
    valid_surface = surface in WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_PAGE_MOUNT_PATH_VISIBLE_SURFACE_PROPOSAL_ALLOWED_SURFACES
    reason = str(proposal.get("operator_readability_reason") or "").strip()
    reason_present = bool(reason)
    scope_ack = bool(operator_scope_ack)
    status = _implementation_gate_status(
        proposal_ready=proposal_ready,
        valid_surface=valid_surface,
        reason_present=reason_present,
        operator_scope_ack=scope_ack,
    )
    future_allowed = status == "receiver_page_mount_visible_surface_implementation_gate_ready_for_future_slice_no_implementation"
    return {
        **build_warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_page_mount_path_visible_surface_implementation_gate_packet",
        "visible_surface_proposal_packet": proposal,
        "q35e_proposal_status": str(proposal.get("visible_surface_proposal_status") or ""),
        "q35e_proposal_ready_for_future_slice": proposal_ready,
        "proposed_visible_surface": surface,
        "proposed_visible_surface_valid": valid_surface,
        "operator_readability_reason": reason,
        "operator_readability_reason_present": reason_present,
        "operator_scope_ack": scope_ack,
        "implementation_gate_status": status,
        "implementation_allowed_for_future_slice": future_allowed,
        "visible_surface_implementation_allowed_now": False,
        "visible_surface_implemented_now": False,
        "metadata_only": True,
        "read_only": True,
        "implementation_gate_only": True,
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
