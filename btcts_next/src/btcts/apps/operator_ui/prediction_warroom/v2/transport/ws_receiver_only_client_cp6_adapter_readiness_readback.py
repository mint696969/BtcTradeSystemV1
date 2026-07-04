# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp6_adapter_readiness_readback.py
# desc: PS-Q36W CP6 adapter readiness/readback. Reads descriptor, adapter, and buffer metadata only; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp6_adapter_readiness_readback.ps_q36w.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp6_adapter_readiness_readback_q36w"
_DESCRIPTOR_KIND = "warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_packet"
_FACTORY_KIND = "warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_packet"
_BUFFER_KIND = "warroom_v2_ws_receiver_only_client_cp6_bounded_local_receive_buffer_packet"


def build_warroom_v2_ws_receiver_only_client_cp6_adapter_readiness_readback_packet(
    redacted_connection_descriptor_packet: Mapping[str, Any] | None = None,
    *,
    no_connect_adapter_factory_packet: Mapping[str, Any] | None = None,
    bounded_local_receive_buffer_packet: Mapping[str, Any] | None = None,
    allow_adapter_readiness_readback: bool = False,
) -> dict[str, Any]:
    descriptor = dict(redacted_connection_descriptor_packet or {})
    factory = dict(no_connect_adapter_factory_packet or {})
    buffer = dict(bounded_local_receive_buffer_packet or {})
    descriptor_ready = descriptor.get("packet_kind") == _DESCRIPTOR_KIND and bool(descriptor.get("redacted_connection_descriptor_ready"))
    factory_ready = factory.get("packet_kind") == _FACTORY_KIND and bool(factory.get("no_connect_adapter_factory_ready"))
    buffer_ready = buffer.get("packet_kind") == _BUFFER_KIND and bool(buffer.get("bounded_local_receive_buffer_ready"))
    ready = bool(allow_adapter_readiness_readback and descriptor_ready and factory_ready and buffer_ready)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_adapter_readiness_readback_packet",
        "adapter_readiness_readback_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36w_cp6_adapter_readiness_readback",
        "adapter_readiness_readback_ready": ready,
        "descriptor_ready": descriptor_ready,
        "adapter_shell_ready": factory_ready,
        "bounded_buffer_ready": buffer_ready,
        "buffer_count": int(buffer.get("buffer_count") or 0) if ready else 0,
        "latest_envelope": dict(buffer.get("latest_envelope") or {}) if ready else {},
        "session_state_keys_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
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
