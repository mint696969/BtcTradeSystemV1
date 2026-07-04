# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_adapter_interface_shape.py
# desc: PS-Q37D CP7 adapter interface shape. Defines metadata shape only; no import, connect, receive, socket, or send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp7_adapter_interface_shape.ps_q37d.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp7_adapter_interface_shape_q37d"
_DESCRIPTOR_KIND = "warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_packet"


def build_warroom_v2_ws_receiver_only_client_cp7_adapter_interface_shape_packet(
    cp7_redacted_endpoint_descriptor_packet: Mapping[str, Any] | None = None,
    *,
    allow_adapter_shape: bool = False,
) -> dict[str, Any]:
    descriptor = dict(cp7_redacted_endpoint_descriptor_packet or {})
    recognized = descriptor.get("packet_kind") == _DESCRIPTOR_KIND
    ready = bool(allow_adapter_shape and recognized and descriptor.get("redacted_endpoint_descriptor_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_adapter_interface_shape_packet",
        "cp7_adapter_interface_shape_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q37d_cp7_adapter_interface_shape",
        "redacted_endpoint_descriptor_kind_recognized": recognized,
        "adapter_interface_shape_ready": ready,
        "adapter_kind": "receiver_only_websocket_adapter_shape_no_connect_no_send" if ready else "not_ready",
        "defined_operations": ["configure_redacted", "dry_run_preflight", "metadata_readback"] if ready else [],
        "connect_operation_defined": False,
        "receive_operation_defined": False,
        "send_operation_defined": False,
        "connect_callable_attached": False,
        "dry_run_only": True,
        "default_connect_enabled": False,
        "default_send_enabled": False,
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
        "next_checkpoint": "CP7_no_connect_adapter_instance" if ready else "CP7_redacted_endpoint_descriptor",
    }
