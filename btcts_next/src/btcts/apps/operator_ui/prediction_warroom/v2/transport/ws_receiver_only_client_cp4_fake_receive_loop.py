# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp4_fake_receive_loop.py
# desc: WarRoom v2 receiver-only CP4 fake receive loop. Local fake messages to state/readback only; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop.ps_q36c.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_q36c"
_CP3_PACKET_KIND = "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet"


def build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "cp4_fake_receive_loop_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_VERSION,
        "state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY,
        "input_pipeline": ["q35x_cp3_visible_readiness", "q36c_cp4_fake_receive_loop"],
        "requires_cp3_visible_readiness_packet": True,
        "requires_allow_fake_receive_loop_flag": True,
        "fake_receive_loop": True,
        "fake_messages_only": True,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "send_disabled": True,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "read_only_except_target_state": True,
        "metadata_only_readback": True,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "aggregator_exports_added": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def _default_messages() -> list[dict[str, Any]]:
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


def apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop(
    target_state: MutableMapping[str, Any] | None,
    *,
    cp3_visible_readiness_packet: Mapping[str, Any] | None = None,
    fake_messages: Sequence[Mapping[str, Any]] | None = None,
    allow_fake_receive_loop: bool = False,
    state_key: str = WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP4_FAKE_RECEIVE_LOOP_STATE_KEY,
) -> dict[str, Any]:
    cp3 = dict(cp3_visible_readiness_packet or {})
    cp3_ready = cp3.get("packet_kind") == _CP3_PACKET_KIND and bool(cp3.get("cp3_visible_readiness_visible_now"))
    messages = list(fake_messages) if fake_messages is not None else _default_messages()
    status = "receiver_only_client_cp4_fake_receive_loop_applied_no_send"
    if not allow_fake_receive_loop:
        status = "receiver_only_client_cp4_fake_receive_loop_blocked_allow_required"
    elif not cp3_ready:
        status = "receiver_only_client_cp4_fake_receive_loop_blocked_cp3_visible_readiness_required"
    elif target_state is None:
        status = "receiver_only_client_cp4_fake_receive_loop_blocked_target_state_required"
    applied = status == "receiver_only_client_cp4_fake_receive_loop_applied_no_send"
    summaries = [_summary(message) for message in messages]
    record = {
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_record",
        "message_count": len(summaries),
        "latest_message": summaries[-1] if summaries else {},
        "topics": sorted({item["topic"] for item in summaries if item.get("topic")}),
        "fake_messages_only": True,
        "external_network_used": False,
        "socket_opened": False,
        "send_disabled": True,
        "client_sends_messages": False,
        "raw_payload_returned": False,
    } if applied else {}
    if applied and target_state is not None:
        target_state[state_key] = record
    return {
        **build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_packet",
        "state_key": state_key,
        "cp3_visible_readiness_ready": cp3_ready,
        "allow_fake_receive_loop": bool(allow_fake_receive_loop),
        "fake_receive_loop_status": status,
        "fake_receive_loop_applied": applied,
        "target_state_mutated": applied,
        "message_count": len(summaries) if applied else 0,
        "latest_message": summaries[-1] if applied and summaries else {},
        "readback_ready": applied,
        "cp4_completed": applied,
        "cp4_completion_commit_ready": applied,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "external_network_used": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
