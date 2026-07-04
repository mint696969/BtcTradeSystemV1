# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp4_fake_receive_loop.py
# desc: PS-Q36C CP4 fake receive loop contract. Contract only; no source/write/readback/completion, no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop.ps_q36c.v2"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_q36c"
_CP3_HANDOFF_KIND = "warroom_v2_ws_receiver_only_client_cp3_close_handoff_packet"


def build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "cp4_fake_receive_loop_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_VERSION,
        "state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY,
        "slice": "q36c_cp4_fake_receive_loop_contract",
        "contract_only": True,
        "fake_receive_loop_contract_defined": True,
        "fake_messages_only": True,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "send_disabled": True,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "raw_payload_returned": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "aggregator_exports_added": False,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract_packet(
    cp3_handoff_packet: Mapping[str, Any] | None = None,
    *,
    allow_fake_receive_loop_contract: bool = False,
) -> dict[str, Any]:
    handoff = dict(cp3_handoff_packet or {})
    recognized = handoff.get("packet_kind") == _CP3_HANDOFF_KIND
    ready = bool(allow_fake_receive_loop_contract and recognized and handoff.get("cp4_fake_receive_loop_ready"))
    return {
        **build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract_packet",
        "cp3_handoff_kind_recognized": recognized,
        "cp4_fake_receive_loop_contract_ready": ready,
        "fake_receive_loop_enabled": ready,
        "fake_messages_only": True,
        "external_network_used": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
    }
