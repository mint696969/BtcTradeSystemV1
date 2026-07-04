# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp10_completion.py
# desc: PS-Q40H CP10 completion packet. Closes dry-run lifecycle policy checkpoint and hands off to CP11 topic widgets.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp10_completion.ps_q40h.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp10_completion_q40h"
_GUARD_KIND = "warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_packet"


def build_warroom_v2_ws_receiver_only_client_cp10_completion_packet(
    cp10_danger_zone_no_action_guard_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp10_completion: bool = False,
) -> dict[str, Any]:
    guard = dict(cp10_danger_zone_no_action_guard_packet or {})
    recognized = guard.get("packet_kind") == _GUARD_KIND
    completed = bool(allow_cp10_completion and recognized and guard.get("danger_zone_no_action_guard_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp10_completion_packet",
        "cp10_completion_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q40h_cp10_completion_close",
        "cp10_danger_zone_no_action_guard_kind_recognized": recognized,
        "cp10_completed": completed,
        "cp10_completion_commit_ready": completed,
        "next_checkpoint": "CP11_topic_widgets" if completed else "CP10_danger_zone_no_action_guard",
        "reconnect_policy_schema_ready": completed,
        "heartbeat_policy_schema_ready": completed,
        "backpressure_policy_schema_ready": completed,
        "lifecycle_dry_run_evaluator_ready": completed,
        "lifecycle_state_readback_ready": completed,
        "danger_zone_no_action_guard_ready": completed,
        "cp10_is_danger_zone": True,
        "danger_zone_dry_run_only": True,
        "default_connect_enabled": False,
        "default_reconnect_enabled": False,
        "default_heartbeat_enabled": False,
        "default_backpressure_runtime_enabled": False,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "secret_exposure": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "operator_action_controls_added": False,
        "auto_start_added": False,
        "receive_loop_started": False,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_started": False,
        "connect_invoked": False,
        "reconnect_invoked": False,
        "heartbeat_sent": False,
        "heartbeat_received": False,
        "backpressure_runtime_started": False,
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
