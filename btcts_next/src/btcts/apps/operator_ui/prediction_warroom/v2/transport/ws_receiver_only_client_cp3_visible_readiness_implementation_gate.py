# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_visible_readiness_implementation_gate.py
# desc: PS-Q35Y CP3 visible readiness implementation gate. Metadata allowlist before page surface; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness_implementation_gate.ps_q35y.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_q35y"
_PROPOSAL_KIND = "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_proposal_packet"


def build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "cp3_visible_readiness_implementation_gate_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q35y_cp3_visible_readiness_implementation_gate",
        "requires_q35x_proposal_packet": True,
        "requires_allow_implementation_gate_flag": True,
        "display_metadata_allowlist": ["receiver_visible_readiness_label", "live_stream_enabled"],
        "page_surface_not_written_here": True,
        "read_only": True,
        "metadata_only": True,
        "raw_proposal_packet_returned": False,
        "session_state_keys_returned": False,
        "visible_controls_added": False,
        "warroom_page_modified": False,
        "aggregator_exports_added": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet(
    proposal_packet: Mapping[str, Any] | None = None,
    *,
    allow_implementation_gate: bool = False,
) -> dict[str, Any]:
    proposal = dict(proposal_packet or {})
    recognized = proposal.get("packet_kind") == _PROPOSAL_KIND
    ready = bool(allow_implementation_gate and recognized and proposal.get("cp3_visible_readiness_proposal_ready"))
    return {
        **build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet",
        "allow_implementation_gate": bool(allow_implementation_gate),
        "proposal_kind_recognized": recognized,
        "cp1_completed": bool(proposal.get("cp1_completed")) if recognized else False,
        "receiver_visible_readiness_label": str(proposal.get("receiver_visible_readiness_label") or "cp1_pending") if recognized else "cp1_pending",
        "cp3_visible_readiness_implementation_gate_ready": ready,
        "display_metadata_allowed": ready,
        "visible_controls_added": False,
        "live_stream_enabled": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
    }
