# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_no_connect_adapter_instance.py
# desc: PS-Q37E CP7 no-connect adapter instance metadata. Creates no runtime client and opens no socket.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp7_no_connect_adapter_instance.ps_q37e.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp7_no_connect_adapter_instance_q37e"
_SHAPE_KIND = "warroom_v2_ws_receiver_only_client_cp7_adapter_interface_shape_packet"


def build_warroom_v2_ws_receiver_only_client_cp7_no_connect_adapter_instance_packet(
    cp7_adapter_interface_shape_packet: Mapping[str, Any] | None = None,
    *,
    allow_no_connect_instance: bool = False,
) -> dict[str, Any]:
    shape = dict(cp7_adapter_interface_shape_packet or {})
    recognized = shape.get("packet_kind") == _SHAPE_KIND
    ready = bool(allow_no_connect_instance and recognized and shape.get("adapter_interface_shape_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_no_connect_adapter_instance_packet",
        "cp7_no_connect_adapter_instance_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q37e_cp7_no_connect_adapter_instance",
        "adapter_interface_shape_kind_recognized": recognized,
        "no_connect_adapter_instance_ready": ready,
        "adapter_instance_kind": "metadata_only_no_connect_adapter_instance" if ready else "not_ready",
        "runtime_adapter_object_created": False,
        "runtime_client_object_created": False,
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
        "next_checkpoint": "CP7_dry_run_preflight" if ready else "CP7_adapter_interface_shape",
    }
