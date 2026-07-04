# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp6_live_adapter_contract.py
# desc: PS-Q36R CP6 live adapter contract. Defines no-connect live adapter preparation boundary; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp6_live_adapter_contract.ps_q36r.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract_q36r"
_CP5_COMPLETION_KIND = "warroom_v2_ws_receiver_only_client_cp5_completion_packet"


def build_warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract",
        "cp6_live_adapter_contract_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36r_cp6_live_adapter_contract",
        "requires_cp5_completion_packet": True,
        "schema_contract_defined": True,
        "live_adapter_contract_ready": False,
        "adapter_factory_added": False,
        "adapter_shell_added": False,
        "read_only": True,
        "metadata_only": True,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "auto_start_added": False,
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


def build_warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract_packet(
    cp5_completion_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp6_contract: bool = False,
) -> dict[str, Any]:
    cp5 = dict(cp5_completion_packet or {})
    recognized = cp5.get("packet_kind") == _CP5_COMPLETION_KIND
    ready = bool(allow_cp6_contract and recognized and cp5.get("cp5_completion_commit_ready"))
    return {
        **build_warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract_packet",
        "cp5_completion_kind_recognized": recognized,
        "cp6_live_adapter_contract_ready": ready,
        "next_checkpoint": "CP6_redacted_connection_descriptor" if ready else "CP5_completion",
    }
