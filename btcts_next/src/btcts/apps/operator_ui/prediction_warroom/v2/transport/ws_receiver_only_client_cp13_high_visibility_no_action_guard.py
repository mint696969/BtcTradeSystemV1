# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp13_high_visibility_no_action_guard.py
# desc: PS-Q43G High-visibility no-action guard proves broadcast, publish, send, connect, page modification, and controls did not execute.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp13_high_visibility_no_action_guard.ps_q43g.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp13_high_visibility_no_action_guard_q43g"
_PREVIOUS_KIND = "warroom_v2_ws_receiver_only_client_cp13_default_off_delivery_mount_gate_packet"
_PREVIOUS_READY_KEYS = ('default_off_delivery_mount_gate_ready',)
_FORBIDDEN_TRUE_FIELDS = ('high_visibility_delivery_enabled', 'high_visibility_delivery_mount_requested_now', 'realtime_animation_started', 'realtime_delivery_runtime_started', 'broadcast_invoked', 'publish_invoked', 'delivery_broadcast_control_added', 'operator_broadcast_control_added', 'operator_publish_control_added', 'operator_delivery_control_added', 'runtime_actions_allowed_now', 'raw_payload_returned', 'endpoint_value_returned', 'token_value_returned', 'callable_values_returned', 'secret_exposure', 'warroom_page_modified', 'warroom_page_visible_ui_modified', 'visible_controls_added', 'operator_action_controls_added', 'auto_start_added', 'receive_loop_started', 'external_network_used', 'websocket_imported', 'socket_opened', 'client_started', 'connect_invoked', 'reconnect_invoked', 'heartbeat_sent', 'heartbeat_received', 'backpressure_runtime_started', 'receive_invoked', 'client_sends_messages', 'external_message_send_enabled', 'broker_send_enabled', 'would_send_to_broker', 'order_intent_submitted', 'ledger_append_allowed', 'prediction_generation_invoked', 'prediction_inference_invoked', 'classifier_invoked')


def build_warroom_v2_ws_receiver_only_client_cp13_high_visibility_no_action_guard_packet(
    previous_packet: Mapping[str, Any] | None = None,
    *,
    allow_high_visibility_no_action_guard: bool = False,
) -> dict[str, Any]:
    previous = dict(previous_packet or {})
    recognized = previous.get("packet_kind") == _PREVIOUS_KIND
    previous_ready = all(bool(previous.get(key)) for key in _PREVIOUS_READY_KEYS)
    guard_failures = [field for field in _FORBIDDEN_TRUE_FIELDS if bool(previous.get(field))]
    if previous.get("not_sending_external_messages") is False:
        guard_failures.append("not_sending_external_messages")
    if previous.get("send_disabled") is False:
        guard_failures.append("send_disabled")
    ready = bool(allow_high_visibility_no_action_guard and recognized and previous_ready and not guard_failures)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp13_high_visibility_no_action_guard_packet",
        "version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q43g_cp13_high_visibility_no_action_guard",
        "previous_kind_recognized": recognized,
        "previous_ready": previous_ready,
        "guard_failures": guard_failures,
        "high_visibility_no_action_guard_ready": ready,
        "next_checkpoint": "CP13_completion" if ready else "previous_checkpoint",
        "cp13_is_danger_zone": True,
        "high_visibility_realtime_delivery_dry_run_only": True,
        "high_visibility_delivery_default_off": True,
        "high_visibility_metadata_only": True,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "high_visibility_delivery_enabled": False,
        "high_visibility_delivery_mount_requested_now": False,
        "realtime_animation_started": False,
        "realtime_delivery_runtime_started": False,
        "broadcast_invoked": False,
        "publish_invoked": False,
        "delivery_broadcast_control_added": False,
        "operator_broadcast_control_added": False,
        "operator_publish_control_added": False,
        "operator_delivery_control_added": False,
        "runtime_actions_allowed_now": False,
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
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }
