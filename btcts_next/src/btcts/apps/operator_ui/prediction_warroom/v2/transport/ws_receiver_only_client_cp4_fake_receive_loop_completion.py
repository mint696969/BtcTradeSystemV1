# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp4_fake_receive_loop_completion.py
# desc: PS-Q36H CP4 fake receive loop completion packet. Declares fake loop complete and CP5 handoff candidate; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp4_fake_receive_loop_completion.ps_q36h.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_q36h"
_GUARD_KIND = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_no_send_guard_packet"


def build_warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_packet(
    no_send_guard_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp4_completion: bool = False,
) -> dict[str, Any]:
    guard = dict(no_send_guard_packet or {})
    recognized = guard.get("packet_kind") == _GUARD_KIND
    completed = bool(allow_cp4_completion and recognized and guard.get("no_send_guard_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_packet",
        "cp4_completion_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36h_cp4_fake_receive_loop_completion",
        "no_send_guard_kind_recognized": recognized,
        "cp4_completed": completed,
        "cp4_completion_commit_ready": completed,
        "next_checkpoint": "CP5_message_normalizer_no_send" if completed else "CP4_no_send_guard",
        "fake_receive_loop": True,
        "fake_messages_only": True,
        "raw_payload_returned": False,
        "external_network_used": False,
        "websocket_imported": False,
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
