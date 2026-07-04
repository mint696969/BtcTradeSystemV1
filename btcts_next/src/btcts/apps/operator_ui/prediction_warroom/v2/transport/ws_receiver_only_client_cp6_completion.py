# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp6_completion.py
# desc: PS-Q36Y CP6 completion packet. Declares live no-send adapter preparation complete after no-connect/no-send guard.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp6_completion.ps_q36y.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp6_completion_q36y"
_GUARD_KIND = "warroom_v2_ws_receiver_only_client_cp6_no_connect_no_send_guard_packet"


def build_warroom_v2_ws_receiver_only_client_cp6_completion_packet(
    cp6_no_connect_no_send_guard_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp6_completion: bool = False,
) -> dict[str, Any]:
    guard = dict(cp6_no_connect_no_send_guard_packet or {})
    recognized = guard.get("packet_kind") == _GUARD_KIND
    completed = bool(allow_cp6_completion and recognized and guard.get("cp6_no_connect_no_send_guard_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_completion_packet",
        "cp6_completion_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36y_cp6_completion_close",
        "cp6_no_connect_no_send_guard_kind_recognized": recognized,
        "cp6_completed": completed,
        "cp6_completion_commit_ready": completed,
        "next_checkpoint": "CP7_gated_receiver_dry_run_preflight_no_send" if completed else "CP6_no_connect_no_send_guard",
        "live_no_send_adapter_preparation_complete": completed,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
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
