# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp4_fake_receive_loop_state_write.py
# desc: PS-Q36E CP4 fake receive loop state write. Writes summarized fake metadata to target state only; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_state_write.ps_q36e.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_write_q36e"
_SOURCE_KIND = "warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet"


def apply_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_write(
    target_state: MutableMapping[str, Any] | None,
    *,
    fake_message_source_packet: Mapping[str, Any] | None = None,
    allow_state_write: bool = False,
    state_key: str = STATE_KEY,
) -> dict[str, Any]:
    source = dict(fake_message_source_packet or {})
    recognized = source.get("packet_kind") == _SOURCE_KIND
    summaries = list(source.get("fake_message_summaries") or []) if recognized else []
    ready = bool(allow_state_write and recognized and source.get("fake_message_source_ready") and target_state is not None)
    record = {
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_record",
        "message_count": len(summaries),
        "latest_message": summaries[-1] if summaries else {},
        "topics": sorted({str(item.get("topic") or "") for item in summaries if item.get("topic")}),
        "fake_messages_only": True,
        "raw_payload_returned": False,
        "external_network_used": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "send_disabled": True,
    } if ready else {}
    if ready and target_state is not None:
        target_state[state_key] = record
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_write_packet",
        "state_write_version": VERSION,
        "state_key": state_key,
        "slice": "q36e_cp4_fake_receive_loop_state_write",
        "source_kind_recognized": recognized,
        "state_write_ready": ready,
        "target_state_mutated": ready,
        "message_count": len(summaries) if ready else 0,
        "latest_message": summaries[-1] if ready and summaries else {},
        "raw_payload_returned": False,
        "external_network_used": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
