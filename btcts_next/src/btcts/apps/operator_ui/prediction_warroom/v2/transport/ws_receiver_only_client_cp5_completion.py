# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp5_completion.py
# desc: PS-Q36Q CP5 completion packet. Declares message normalizer no-send complete after strict guard.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp5_completion.ps_q36q.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp5_completion_q36q"
_GUARD_KIND = "warroom_v2_ws_receiver_only_client_cp5_no_send_traceability_guard_packet"


def build_warroom_v2_ws_receiver_only_client_cp5_completion_packet(
    cp5_no_send_guard_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp5_completion: bool = False,
) -> dict[str, Any]:
    guard = dict(cp5_no_send_guard_packet or {})
    recognized = guard.get("packet_kind") == _GUARD_KIND
    completed = bool(allow_cp5_completion and recognized and guard.get("cp5_no_send_guard_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_completion_packet",
        "cp5_completion_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36q_cp5_completion_close",
        "cp5_no_send_guard_kind_recognized": recognized,
        "cp5_completed": completed,
        "cp5_completion_commit_ready": completed,
        "next_checkpoint": "CP6_receiver_adapter_live_no_send_preparation" if completed else "CP5_no_send_traceability_guard",
        "message_normalizer_no_send_complete": completed,
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
