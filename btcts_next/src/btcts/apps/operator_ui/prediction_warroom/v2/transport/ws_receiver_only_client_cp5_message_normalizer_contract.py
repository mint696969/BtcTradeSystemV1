# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp5_message_normalizer_contract.py
# desc: PS-Q36J CP5 message normalizer contract. Defines normalized metadata schema after CP4; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_contract.ps_q36j.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_q36j"
_CP4_CLOSE_KIND = "warroom_v2_ws_receiver_only_client_cp4_close_handoff_packet"


def build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract",
        "cp5_message_normalizer_contract_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36j_cp5_message_normalizer_contract",
        "requires_cp4_close_handoff_packet": True,
        "requires_allow_cp5_contract_flag": True,
        "normalized_fields": ["topic", "symbol", "sequence", "source_kind", "message_kind", "normalized_ok", "invalid_reason"],
        "schema_contract_defined": True,
        "normalizer_core_added": False,
        "state_write_added": False,
        "read_only": True,
        "metadata_only": True,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "aggregator_exports_added": False,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_packet(
    cp4_close_handoff_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp5_contract: bool = False,
) -> dict[str, Any]:
    cp4 = dict(cp4_close_handoff_packet or {})
    recognized = cp4.get("packet_kind") == _CP4_CLOSE_KIND
    ready = bool(allow_cp5_contract and recognized and cp4.get("cp4_close_ready"))
    return {
        **build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_packet",
        "cp4_close_handoff_kind_recognized": recognized,
        "cp5_message_normalizer_contract_ready": ready,
        "next_checkpoint": "CP5_normalizer_core" if ready else "CP4_close_handoff",
    }
