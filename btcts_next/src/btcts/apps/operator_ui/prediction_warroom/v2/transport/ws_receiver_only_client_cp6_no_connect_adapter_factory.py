# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp6_no_connect_adapter_factory.py
# desc: PS-Q36T CP6 no-connect adapter factory. Builds adapter shell metadata only; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp6_no_connect_adapter_factory.ps_q36t.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_q36t"
_DESCRIPTOR_KIND = "warroom_v2_ws_receiver_only_client_cp6_redacted_connection_descriptor_packet"


def build_warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_packet(
    redacted_connection_descriptor_packet: Mapping[str, Any] | None = None,
    *,
    allow_no_connect_adapter_factory: bool = False,
) -> dict[str, Any]:
    descriptor = dict(redacted_connection_descriptor_packet or {})
    recognized = descriptor.get("packet_kind") == _DESCRIPTOR_KIND
    safe_descriptor = bool(
        recognized
        and descriptor.get("redacted_connection_descriptor_ready")
        and descriptor.get("endpoint_value_returned") is False
        and descriptor.get("token_value_returned") is False
        and descriptor.get("callable_values_returned") is False
    )
    ready = bool(allow_no_connect_adapter_factory and safe_descriptor)
    adapter_shell = {
        "adapter_kind": "receiver_only_live_no_send_adapter_shell",
        "adapter_shell_ready": True,
        "connect_callable_present": False,
        "open_socket_callable_present": False,
        "send_callable_present": False,
        "adapter_opens_socket": False,
        "adapter_sends_messages": False,
        "adapter_reads_network": False,
    } if ready else {}
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_no_connect_adapter_factory_packet",
        "no_connect_adapter_factory_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36t_cp6_no_connect_adapter_factory",
        "descriptor_kind_recognized": recognized,
        "no_connect_adapter_factory_ready": ready,
        "adapter_shell": adapter_shell,
        "adapter_factory_added": ready,
        "adapter_shell_added": ready,
        "adapter_opens_socket": False,
        "adapter_sends_messages": False,
        "adapter_reads_network": False,
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
