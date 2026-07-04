# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp6_redacted_connection_descriptor.py
# desc: PS-Q36S CP6 redacted connection descriptor. Returns descriptor metadata only; no endpoint, token, callable, socket, or send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp6_redacted_connection_descriptor.ps_q36s.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_q36s"
_CONTRACT_KIND = "warroom_v2_ws_receiver_only_client_cp6_live_adapter_contract_packet"


def build_warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_packet(
    cp6_contract_packet: Mapping[str, Any] | None = None,
    *,
    allow_descriptor: bool = False,
) -> dict[str, Any]:
    contract = dict(cp6_contract_packet or {})
    recognized = contract.get("packet_kind") == _CONTRACT_KIND
    ready = bool(allow_descriptor and recognized and contract.get("cp6_live_adapter_contract_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_packet",
        "redacted_connection_descriptor_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36s_cp6_redacted_connection_descriptor",
        "contract_kind_recognized": recognized,
        "redacted_connection_descriptor_ready": ready,
        "descriptor_kind": "receiver_only_live_no_send_redacted_descriptor" if ready else "not_ready",
        "endpoint_configured": ready,
        "token_configured": ready,
        "connect_callable_configured": ready,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "secret_exposure": False,
        "raw_payload_returned": False,
        "metadata_only": True,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
