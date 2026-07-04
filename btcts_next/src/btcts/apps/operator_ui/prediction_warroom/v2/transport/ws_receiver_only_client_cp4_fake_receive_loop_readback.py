# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp4_fake_receive_loop_readback.py
# desc: PS-Q36F CP4 fake receive loop readback. Reads summarized fake metadata only; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_readback.ps_q36f.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_q36f"
_STATE_RECORD_KIND = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_state_record"


def build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_packet(
    target_state: Mapping[str, Any] | None = None,
    *,
    state_write_key: str,
    allow_readback: bool = False,
) -> dict[str, Any]:
    state = dict(target_state or {})
    record = state.get(state_write_key)
    record = dict(record) if isinstance(record, Mapping) else {}
    recognized = record.get("packet_kind") == _STATE_RECORD_KIND
    ready = bool(allow_readback and recognized)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_readback_packet",
        "readback_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36f_cp4_fake_receive_loop_readback",
        "state_record_kind_recognized": recognized,
        "readback_ready": ready,
        "message_count": int(record.get("message_count") or 0) if ready else 0,
        "latest_message": dict(record.get("latest_message") or {}) if ready else {},
        "raw_payload_returned": False,
        "session_state_keys_returned": False,
        "external_network_used": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
