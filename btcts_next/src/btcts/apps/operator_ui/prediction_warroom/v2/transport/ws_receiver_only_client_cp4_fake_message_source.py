# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp4_fake_message_source.py
# desc: PS-Q36D CP4 fake message source. Fixed local fake messages only; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_message_source.ps_q36d.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp4_fake_message_source_q36d"
_CONTRACT_KIND = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract_packet"


def _messages() -> list[dict[str, Any]]:
    return [
        {"topic": "fake.btc.tick", "symbol": "BTC", "sequence": 1, "price": 100.0},
        {"topic": "fake.btc.tick", "symbol": "BTC", "sequence": 2, "price": 101.5},
        {"topic": "fake.heartbeat", "symbol": "BTC", "sequence": 3, "price": 101.5},
    ]


def _summary(message: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "topic": str(message.get("topic") or ""),
        "symbol": str(message.get("symbol") or ""),
        "sequence": int(message.get("sequence") or 0),
        "payload_kind": "fake_receiver_message_metadata",
        "raw_payload_returned": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet(
    contract_packet: Mapping[str, Any] | None = None,
    *,
    allow_fake_message_source: bool = False,
) -> dict[str, Any]:
    contract = dict(contract_packet or {})
    recognized = contract.get("packet_kind") == _CONTRACT_KIND
    ready = bool(allow_fake_message_source and recognized and contract.get("cp4_fake_receive_loop_contract_ready"))
    summaries = [_summary(message) for message in _messages()] if ready else []
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet",
        "fake_message_source_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36d_cp4_fake_message_source",
        "contract_kind_recognized": recognized,
        "fake_message_source_ready": ready,
        "fake_messages_only": True,
        "message_count": len(summaries),
        "fake_message_summaries": summaries,
        "raw_payload_returned": False,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
