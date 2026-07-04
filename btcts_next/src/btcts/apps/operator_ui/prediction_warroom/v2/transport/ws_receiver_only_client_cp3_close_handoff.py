# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_close_handoff.py
# desc: PS-Q36B CP3 close handoff. Declares visible readiness complete and hands off to CP4; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp3_close_handoff.ps_q36b.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp3_close_handoff_q36b"
_READBACK_KIND = "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_packet"


def build_warroom_v2_ws_receiver_only_client_cp3_close_handoff_packet(
    readback_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp3_close_handoff: bool = False,
) -> dict[str, Any]:
    readback = dict(readback_packet or {})
    recognized = readback.get("packet_kind") == _READBACK_KIND
    completed = bool(allow_cp3_close_handoff and recognized and readback.get("cp3_visible_readiness_readback_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp3_close_handoff_packet",
        "cp3_close_handoff_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36b_cp3_close_handoff",
        "readback_kind_recognized": recognized,
        "cp3_completed": completed,
        "cp4_fake_receive_loop_ready": completed,
        "next_checkpoint": "CP4_fake_receive_loop_contract" if completed else "CP3_visible_readiness_readback",
        "read_only": True,
        "metadata_only": True,
        "raw_readback_packet_returned": False,
        "visible_controls_added": False,
        "live_stream_enabled": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
