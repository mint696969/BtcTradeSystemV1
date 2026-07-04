# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp4_close_handoff.py
# desc: PS-Q36I CP4 close handoff. Close guard marker for CP4 fake receive loop completion; no behavior change, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp4_close_handoff.ps_q36i.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp4_close_handoff_q36i"
_COMPLETION_KIND = "warroom_v2_ws_receiver_only_client_cp4_fake_receive_loop_completion_packet"


def build_warroom_v2_ws_receiver_only_client_cp4_close_handoff_packet(
    cp4_completion_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp4_close: bool = False,
) -> dict[str, Any]:
    completion = dict(cp4_completion_packet or {})
    recognized = completion.get("packet_kind") == _COMPLETION_KIND
    close_ready = bool(allow_cp4_close and recognized and completion.get("cp4_completion_commit_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp4_close_handoff_packet",
        "cp4_close_handoff_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36i_cp4_close_commit_handoff",
        "cp4_completion_kind_recognized": recognized,
        "cp4_close_ready": close_ready,
        "cp4_completed": close_ready,
        "cp4_completion_commit_ready": close_ready,
        "next_checkpoint": "CP5_message_normalizer_no_send" if close_ready else "CP4_completion_packet",
        "close_guard_required": True,
        "behavior_change_added": False,
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
