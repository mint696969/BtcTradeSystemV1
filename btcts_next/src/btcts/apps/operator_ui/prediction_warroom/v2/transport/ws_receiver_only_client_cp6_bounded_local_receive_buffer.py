# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp6_bounded_local_receive_buffer.py
# desc: PS-Q36V CP6 bounded local receive buffer metadata. Local buffer metadata only; no receive loop, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping, Sequence

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp6_bounded_local_receive_buffer.ps_q36v.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp6_bounded_local_receive_buffer_q36v"
_ENVELOPE_KIND = "warroom_v2_ws_receiver_only_client_cp6_normalized_adapter_envelope_packet"


def build_warroom_v2_ws_receiver_only_client_cp6_bounded_local_receive_buffer_packet(
    normalized_adapter_envelope_packet: Mapping[str, Any] | None = None,
    *,
    existing_envelopes: Sequence[Mapping[str, Any]] | None = None,
    max_buffer_size: int = 5,
    allow_bounded_buffer: bool = False,
) -> dict[str, Any]:
    envelope_packet = dict(normalized_adapter_envelope_packet or {})
    recognized = envelope_packet.get("packet_kind") == _ENVELOPE_KIND
    ready = bool(allow_bounded_buffer and recognized and envelope_packet.get("adapter_envelope_ready"))
    incoming = dict(envelope_packet.get("adapter_envelope") or {}) if ready else {}
    current = [dict(item) for item in list(existing_envelopes or []) if isinstance(item, Mapping)]
    bounded = (current + ([incoming] if incoming else []))[-max(1, int(max_buffer_size)):] if ready else []
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_bounded_local_receive_buffer_packet",
        "bounded_local_receive_buffer_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36v_cp6_bounded_local_receive_buffer",
        "adapter_envelope_kind_recognized": recognized,
        "bounded_local_receive_buffer_ready": ready,
        "max_buffer_size": max(1, int(max_buffer_size)),
        "buffer_count": len(bounded),
        "latest_envelope": bounded[-1] if bounded else {},
        "bounded_envelopes": bounded,
        "receive_loop_started": False,
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
