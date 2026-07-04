# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_visible_readiness.py
# desc: PS-Q35X CP3 visible readiness proposal. Proposal metadata only; no page, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness.ps_q35x.v2"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_STATE_KEY = "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_q35x"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_SOURCE_STATE_KEY = "warroom_v2_ws_receiver_only_client_cp1_completion_source_q35x"
_CP1_COMPLETION_KIND = "warroom_v2_ws_receiver_only_client_cp1_completion_packet"


def build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "cp3_visible_readiness_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_VERSION,
        "state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_STATE_KEY,
        "source_state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_SOURCE_STATE_KEY,
        "slice": "q35x_cp3_visible_readiness_proposal",
        "proposal_only": True,
        "requires_cp1_completion_packet": True,
        "requires_allow_visible_readiness_proposal_flag": True,
        "read_only": True,
        "metadata_only": True,
        "raw_cp1_completion_packet_returned": False,
        "session_state_keys_returned": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "aggregator_exports_added": False,
        "live_stream_enabled": False,
        "fake_receive_loop_enabled": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet(
    *,
    cp1_completion_packet: Mapping[str, Any] | None = None,
    allow_visible_readiness_proposal: bool = False,
) -> dict[str, Any]:
    cp1 = dict(cp1_completion_packet or {})
    cp1_completed = cp1.get("packet_kind") == _CP1_COMPLETION_KIND and bool(cp1.get("cp1_completed"))
    ready = bool(allow_visible_readiness_proposal and cp1_completed)
    return {
        **build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_proposal_packet",
        "allow_visible_readiness_proposal": bool(allow_visible_readiness_proposal),
        "cp1_completion_present": bool(cp1_completion_packet),
        "cp1_completion_kind_recognized": cp1.get("packet_kind") == _CP1_COMPLETION_KIND,
        "cp1_completed": cp1_completed,
        "cp3_visible_readiness_proposal_ready": ready,
        "receiver_visible_readiness_label": "cp1_ready" if cp1_completed else "cp1_pending",
        "live_stream_enabled": False,
        "fake_receive_loop_enabled": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
