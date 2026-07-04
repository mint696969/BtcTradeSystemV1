# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp11_no_control_topic_widget_guard.py
# desc: PS-Q41G CP11 no-control topic widget guard. Proves topic widgets do not subscribe, mutate filters, connect, send, or add controls.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp11_no_control_topic_widget_guard.ps_q41g.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp11_no_control_topic_widget_guard_q41g"
_GATE_KIND = "warroom_v2_ws_receiver_only_client_cp11_default_off_topic_widget_mount_gate_packet"
_FORBIDDEN_TRUE_FIELDS = (
    "topic_subscription_requested", "topic_subscribe_invoked", "topic_unsubscribe_invoked", "topic_filter_mutation_enabled", "topic_widget_controls_added",
    "raw_payload_returned", "endpoint_value_returned", "token_value_returned", "callable_values_returned", "secret_exposure",
    "warroom_page_modified", "warroom_page_visible_ui_modified", "visible_controls_added", "operator_action_controls_added", "auto_start_added",
    "receive_loop_started", "external_network_used", "websocket_imported", "socket_opened", "client_started", "connect_invoked",
    "reconnect_invoked", "heartbeat_sent", "heartbeat_received", "backpressure_runtime_started", "receive_invoked", "client_sends_messages",
    "external_message_send_enabled", "broker_send_enabled", "would_send_to_broker", "order_intent_submitted", "ledger_append_allowed",
    "prediction_generation_invoked", "prediction_inference_invoked", "classifier_invoked",
)


def build_warroom_v2_ws_receiver_only_client_cp11_no_control_topic_widget_guard_packet(
    cp11_default_off_topic_widget_mount_gate_packet: Mapping[str, Any] | None = None,
    *,
    allow_guard: bool = False,
) -> dict[str, Any]:
    gate = dict(cp11_default_off_topic_widget_mount_gate_packet or {})
    recognized = gate.get("packet_kind") == _GATE_KIND
    failures = [field for field in _FORBIDDEN_TRUE_FIELDS if bool(gate.get(field))]
    if gate.get("not_sending_external_messages") is not True:
        failures.append("not_sending_external_messages")
    if gate.get("send_disabled") is not True:
        failures.append("send_disabled")
    ready = bool(allow_guard and recognized and gate.get("default_off_topic_widget_mount_gate_ready") and not failures)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp11_no_control_topic_widget_guard_packet",
        "cp11_no_control_topic_widget_guard_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q41g_cp11_no_control_topic_widget_guard",
        "default_off_topic_widget_mount_gate_kind_recognized": recognized,
        "guard_failures": failures,
        "no_control_topic_widget_guard_ready": ready,
        "next_checkpoint": "CP11_completion" if ready else "CP11_default_off_topic_widget_mount_gate",

        "topic_widgets_read_only": True,
        "topic_widgets_default_off": True,
        "topic_widgets_metadata_only": True,
        "topic_subscription_requested": False,
        "topic_subscribe_invoked": False,
        "topic_unsubscribe_invoked": False,
        "topic_filter_mutation_enabled": False,
        "topic_widget_controls_added": False,
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
