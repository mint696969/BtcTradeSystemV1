# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_completion.py
# desc: PS-Q37H CP7 completion packet. Closes gated receiver dry-run preflight and hands off to CP8 live incoming state flow.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp7_completion.ps_q37h.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp7_completion_q37h"
_GUARD_KIND = "warroom_v2_ws_receiver_only_client_cp7_forbidden_behavior_guard_packet"


def build_warroom_v2_ws_receiver_only_client_cp7_completion_packet(
    cp7_forbidden_behavior_guard_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp7_completion: bool = False,
) -> dict[str, Any]:
    guard = dict(cp7_forbidden_behavior_guard_packet or {})
    recognized = guard.get("packet_kind") == _GUARD_KIND
    completed = bool(allow_cp7_completion and recognized and guard.get("cp7_forbidden_behavior_guard_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_completion_packet",
        "cp7_completion_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q37h_cp7_completion_close",
        "cp7_forbidden_behavior_guard_kind_recognized": recognized,
        "cp7_completed": completed,
        "cp7_completion_commit_ready": completed,
        "next_checkpoint": "CP8_live_incoming_state_flow" if completed else "CP7_forbidden_behavior_guard",
        "real_no_send_websocket_adapter_preflight_complete": completed,
        "dry_run_preflight_ready": completed,
        "real_adapter_shape_defined": completed,
        "default_connect_enabled": False,
        "default_send_enabled": False,
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
