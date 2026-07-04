# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp8_completion.py
# desc: PS-Q38H CP8 completion packet. Closes live incoming state flow and hands off to CP9 visible stream panel.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp8_completion.ps_q38h.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp8_completion_q38h"
_GUARD_KIND = "warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_packet"


def build_warroom_v2_ws_receiver_only_client_cp8_completion_packet(
    cp8_no_send_state_boundary_guard_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp8_completion: bool = False,
) -> dict[str, Any]:
    guard = dict(cp8_no_send_state_boundary_guard_packet or {})
    recognized = guard.get("packet_kind") == _GUARD_KIND
    completed = bool(allow_cp8_completion and recognized and guard.get("cp8_no_send_state_boundary_guard_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp8_completion_packet",
        "cp8_completion_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q38h_cp8_completion_close",
        "cp8_no_send_state_boundary_guard_kind_recognized": recognized,
        "cp8_completed": completed,
        "cp8_completion_commit_ready": completed,
        "next_checkpoint": "CP9_visible_stream_panel" if completed else "CP8_no_send_state_boundary_guard",
        "live_incoming_state_flow_ready": completed,
        "controlled_state_write_ready": completed,
        "state_readback_ready": completed,
        "bounded_metadata_state": True,
        "metadata_only": True,
        "read_only_or_caller_state_only": True,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "secret_exposure": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "auto_start_added": False,
        "receive_loop_started": False,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_started": False,
        "connect_invoked": False,
        "receive_invoked": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }
