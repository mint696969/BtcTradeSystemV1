# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp6_normalized_adapter_envelope.py
# desc: PS-Q36U CP6 normalized adapter envelope. Wraps CP5 normalized metadata only; no raw payload, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp6_normalized_adapter_envelope.ps_q36u.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp6_normalized_adapter_envelope_q36u"
_FACTORY_KIND = "warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_packet"
_CP5_READBACK_KIND = "warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet"


def build_warroom_v2_ws_receiver_only_client_cp6_normalized_adapter_envelope_packet(
    no_connect_adapter_factory_packet: Mapping[str, Any] | None = None,
    *,
    cp5_normalized_state_readback_packet: Mapping[str, Any] | None = None,
    allow_adapter_envelope: bool = False,
) -> dict[str, Any]:
    factory = dict(no_connect_adapter_factory_packet or {})
    readback = dict(cp5_normalized_state_readback_packet or {})
    factory_ready = factory.get("packet_kind") == _FACTORY_KIND and bool(factory.get("no_connect_adapter_factory_ready"))
    readback_ready = readback.get("packet_kind") == _CP5_READBACK_KIND and bool(readback.get("normalized_state_readback_ready"))
    ready = bool(allow_adapter_envelope and factory_ready and readback_ready)
    latest = dict(readback.get("latest_normalized_message") or {}) if ready else {}
    envelope = {
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_adapter_envelope_metadata",
        "source_kind": str(latest.get("source_kind") or ""),
        "topic": str(latest.get("topic") or ""),
        "message_kind": str(latest.get("message_kind") or ""),
        "sequence": int(latest.get("sequence") or 0),
        "normalized_ok": bool(latest.get("normalized_ok")),
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "metadata_only": True,
    } if ready else {}
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_normalized_adapter_envelope_packet",
        "normalized_adapter_envelope_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36u_cp6_normalized_adapter_envelope",
        "adapter_envelope_ready": ready,
        "message_count": int(readback.get("message_count") or 0) if ready else 0,
        "adapter_envelope": envelope,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
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
