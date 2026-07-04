# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp8_entry_contract.py
# desc: PS-Q38A CP8 entry contract. Starts live incoming state flow only after CP7 completion; no socket, no network, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp8_entry_contract.ps_q38a.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp8_entry_contract_q38a"
_CP7_COMPLETION_KIND = "warroom_v2_ws_receiver_only_client_cp7_completion_packet"


def build_warroom_v2_ws_receiver_only_client_cp8_entry_contract_packet(
    cp7_completion_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp8_entry: bool = False,
) -> dict[str, Any]:
    cp7 = dict(cp7_completion_packet or {})
    recognized = cp7.get("packet_kind") == _CP7_COMPLETION_KIND
    ready = bool(allow_cp8_entry and recognized and cp7.get("cp7_completed") and cp7.get("cp7_completion_commit_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp8_entry_contract_packet",
        "cp8_entry_contract_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q38a_cp8_entry_contract",
        "requires_cp7_completion_packet": True,
        "cp7_completion_kind_recognized": recognized,
        "cp8_entry_ready": ready,
        "live_incoming_state_flow_allowed": ready,
        "controlled_state_write_default_enabled": False,
        "raw_payload_allowed": False,
        "next_checkpoint": "CP8_incoming_metadata_state_schema" if ready else "CP7_completion",
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
