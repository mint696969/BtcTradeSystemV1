# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp8_no_send_state_boundary_guard.py
# desc: PS-Q38G CP8 no-send state-boundary guard. Proves state flow does not leak to socket, send, UI controls, broker, prediction, or classifier.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp8_no_send_state_boundary_guard.ps_q38g.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_q38g"
_BRIDGE_KIND = "warroom_v2_ws_receiver_only_client_cp8_preflight_to_state_bridge_packet"
_FORBIDDEN_TRUE_FIELDS = (
    "raw_payload_returned", "endpoint_value_returned", "token_value_returned", "callable_values_returned", "secret_exposure",
    "warroom_page_modified", "warroom_page_visible_ui_modified", "visible_controls_added", "auto_start_added",
    "receive_loop_started", "external_network_used", "websocket_imported", "socket_opened", "client_started",
    "connect_invoked", "receive_invoked", "client_sends_messages", "external_message_send_enabled",
    "broker_send_enabled", "would_send_to_broker", "order_intent_submitted", "ledger_append_allowed",
    "prediction_generation_invoked", "prediction_inference_invoked", "classifier_invoked",
)


def build_warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_packet(
    cp8_preflight_to_state_bridge_packet: Mapping[str, Any] | None = None,
    *,
    allow_guard: bool = False,
) -> dict[str, Any]:
    bridge = dict(cp8_preflight_to_state_bridge_packet or {})
    recognized = bridge.get("packet_kind") == _BRIDGE_KIND
    failures = [field for field in _FORBIDDEN_TRUE_FIELDS if bool(bridge.get(field))]
    if bridge.get("not_sending_external_messages") is not True:
        failures.append("not_sending_external_messages")
    if bridge.get("send_disabled") is not True:
        failures.append("send_disabled")
    ready = bool(allow_guard and recognized and bridge.get("live_incoming_state_flow_ready") and not failures)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp8_no_send_state_boundary_guard_packet",
        "cp8_no_send_state_boundary_guard_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q38g_cp8_no_send_state_boundary_guard",
        "preflight_to_state_bridge_kind_recognized": recognized,
        "guard_failures": failures,
        "cp8_no_send_state_boundary_guard_ready": ready,
        "next_checkpoint": "CP8_completion" if ready else "CP8_preflight_to_state_bridge",
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
