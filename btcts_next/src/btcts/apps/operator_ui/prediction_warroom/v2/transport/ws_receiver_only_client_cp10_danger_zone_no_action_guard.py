# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp10_danger_zone_no_action_guard.py
# desc: PS-Q40G CP10 danger-zone no-action guard. Proves reconnect/heartbeat/backpressure runtime actions did not execute.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp10_danger_zone_no_action_guard.ps_q40g.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_q40g"
_READBACK_KIND = "warroom_v2_ws_receiver_only_client_cp10_lifecycle_state_readback_packet"
_FORBIDDEN_TRUE_FIELDS = (
    "raw_payload_returned", "endpoint_value_returned", "token_value_returned", "callable_values_returned", "secret_exposure",
    "warroom_page_modified", "warroom_page_visible_ui_modified", "visible_controls_added", "operator_action_controls_added",
    "auto_start_added", "receive_loop_started", "external_network_used", "websocket_imported", "socket_opened", "client_started",
    "connect_invoked", "reconnect_invoked", "heartbeat_sent", "heartbeat_received", "backpressure_runtime_started",
    "receive_invoked", "client_sends_messages", "external_message_send_enabled", "broker_send_enabled", "would_send_to_broker",
    "order_intent_submitted", "ledger_append_allowed", "prediction_generation_invoked", "prediction_inference_invoked", "classifier_invoked",
    "runtime_action_executed",
)


def build_warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_packet(
    cp10_lifecycle_state_readback_packet: Mapping[str, Any] | None = None,
    *,
    allow_guard: bool = False,
) -> dict[str, Any]:
    readback = dict(cp10_lifecycle_state_readback_packet or {})
    recognized = readback.get("packet_kind") == _READBACK_KIND
    failures = [field for field in _FORBIDDEN_TRUE_FIELDS if bool(readback.get(field))]
    if readback.get("not_sending_external_messages") is not True:
        failures.append("not_sending_external_messages")
    if readback.get("send_disabled") is not True:
        failures.append("send_disabled")
    ready = bool(allow_guard and recognized and readback.get("lifecycle_state_readback_ready") and not failures)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp10_danger_zone_no_action_guard_packet",
        "cp10_danger_zone_no_action_guard_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q40g_cp10_danger_zone_no_action_guard",
        "lifecycle_state_readback_kind_recognized": recognized,
        "guard_failures": failures,
        "danger_zone_no_action_guard_ready": ready,
        "runtime_actions_allowed_now": False,
        "next_checkpoint": "CP10_completion" if ready else "CP10_lifecycle_state_readback",
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
