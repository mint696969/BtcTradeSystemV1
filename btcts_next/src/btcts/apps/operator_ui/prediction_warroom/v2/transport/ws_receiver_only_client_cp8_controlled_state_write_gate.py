# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp8_controlled_state_write_gate.py
# desc: PS-Q38C CP8 controlled state write gate. Enables caller-provided local state only after explicit allowance; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp8_controlled_state_write_gate.ps_q38c.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_q38c"
_SCHEMA_KIND = "warroom_v2_ws_receiver_only_client_cp8_incoming_metadata_state_schema_packet"


def build_warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_packet(
    cp8_incoming_metadata_state_schema_packet: Mapping[str, Any] | None = None,
    *,
    allow_controlled_state_write: bool = False,
    target_state_is_caller_provided: bool = False,
) -> dict[str, Any]:
    schema = dict(cp8_incoming_metadata_state_schema_packet or {})
    recognized = schema.get("packet_kind") == _SCHEMA_KIND
    ready = bool(allow_controlled_state_write and target_state_is_caller_provided and recognized and schema.get("incoming_metadata_state_schema_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_packet",
        "cp8_controlled_state_write_gate_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q38c_cp8_controlled_state_write_gate",
        "incoming_metadata_state_schema_kind_recognized": recognized,
        "target_state_is_caller_provided": bool(target_state_is_caller_provided),
        "controlled_state_write_ready": ready,
        "state_write_default_enabled": False,
        "state_write_requires_explicit_allow": True,
        "next_checkpoint": "CP8_state_append_update" if ready else "CP8_incoming_metadata_state_schema",
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
