# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_forbidden_behavior_guard.py
# desc: PS-Q37G CP7 forbidden behavior guard. Verifies no socket, no network, no send, no secrets, no broker, no prediction/classifier.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp7_forbidden_behavior_guard.ps_q37g.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp7_forbidden_behavior_guard_q37g"
_PREFLIGHT_KIND = "warroom_v2_ws_receiver_only_client_cp7_dry_run_preflight_packet"
_FORBIDDEN_TRUE_FIELDS = (
    "raw_payload_returned",
    "endpoint_value_returned",
    "token_value_returned",
    "callable_values_returned",
    "secret_exposure",
    "warroom_page_modified",
    "warroom_page_visible_ui_modified",
    "visible_controls_added",
    "auto_start_added",
    "receive_loop_started",
    "external_network_used",
    "websocket_imported",
    "socket_opened",
    "client_started",
    "connect_invoked",
    "receive_invoked",
    "client_sends_messages",
    "external_message_send_enabled",
    "broker_send_enabled",
    "would_send_to_broker",
    "order_intent_submitted",
    "ledger_append_allowed",
    "prediction_generation_invoked",
    "prediction_inference_invoked",
    "classifier_invoked",
)


def build_warroom_v2_ws_receiver_only_client_cp7_forbidden_behavior_guard_packet(
    cp7_dry_run_preflight_packet: Mapping[str, Any] | None = None,
    *,
    allow_guard: bool = False,
) -> dict[str, Any]:
    preflight = dict(cp7_dry_run_preflight_packet or {})
    recognized = preflight.get("packet_kind") == _PREFLIGHT_KIND
    failures = [field for field in _FORBIDDEN_TRUE_FIELDS if bool(preflight.get(field))]
    if preflight.get("not_sending_external_messages") is not True:
        failures.append("not_sending_external_messages")
    if preflight.get("send_disabled") is not True:
        failures.append("send_disabled")
    ready = bool(allow_guard and recognized and preflight.get("dry_run_preflight_ready") and not failures)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_forbidden_behavior_guard_packet",
        "cp7_forbidden_behavior_guard_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q37g_cp7_forbidden_behavior_guard",
        "dry_run_preflight_kind_recognized": recognized,
        "guard_failures": failures,
        "cp7_forbidden_behavior_guard_ready": ready,
        "dry_run_only": True,
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
        "next_checkpoint": "CP7_completion" if ready else "CP7_dry_run_preflight",
    }
