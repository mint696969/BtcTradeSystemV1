# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp8_incoming_metadata_state_schema.py
# desc: PS-Q38B CP8 incoming metadata state schema. Defines bounded metadata-only state; no raw payload, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp8_incoming_metadata_state_schema.ps_q38b.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp8_incoming_metadata_state_schema_q38b"
_ENTRY_KIND = "warroom_v2_ws_receiver_only_client_cp8_entry_contract_packet"
ALLOWED_METADATA_FIELDS = ("topic", "message_kind", "received_at_ms", "sequence", "event_id", "source_label", "normalized_summary")
MAX_RECENT_EVENTS = 5


def build_warroom_v2_ws_receiver_only_client_cp8_incoming_metadata_state_schema_packet(
    cp8_entry_contract_packet: Mapping[str, Any] | None = None,
    *,
    allow_schema: bool = False,
) -> dict[str, Any]:
    entry = dict(cp8_entry_contract_packet or {})
    recognized = entry.get("packet_kind") == _ENTRY_KIND
    ready = bool(allow_schema and recognized and entry.get("cp8_entry_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp8_incoming_metadata_state_schema_packet",
        "cp8_incoming_metadata_state_schema_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q38b_cp8_incoming_metadata_state_schema",
        "cp8_entry_kind_recognized": recognized,
        "incoming_metadata_state_schema_ready": ready,
        "allowed_metadata_fields": list(ALLOWED_METADATA_FIELDS) if ready else [],
        "max_recent_events": MAX_RECENT_EVENTS,
        "bounded_metadata_state": True,
        "raw_payload_field_allowed": False,
        "next_checkpoint": "CP8_controlled_state_write_gate" if ready else "CP8_entry_contract",
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
