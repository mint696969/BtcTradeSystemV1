# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_dry_run_preflight.py
# desc: PS-Q37F CP7 dry-run preflight. Combines redacted descriptor and no-connect instance; no socket, no network, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp7_dry_run_preflight.ps_q37f.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp7_dry_run_preflight_q37f"
_DESCRIPTOR_KIND = "warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_packet"
_INSTANCE_KIND = "warroom_v2_ws_receiver_only_client_cp7_no_connect_adapter_instance_packet"


def build_warroom_v2_ws_receiver_only_client_cp7_dry_run_preflight_packet(
    *,
    cp7_redacted_endpoint_descriptor_packet: Mapping[str, Any] | None = None,
    cp7_no_connect_adapter_instance_packet: Mapping[str, Any] | None = None,
    allow_preflight: bool = False,
) -> dict[str, Any]:
    descriptor = dict(cp7_redacted_endpoint_descriptor_packet or {})
    instance = dict(cp7_no_connect_adapter_instance_packet or {})
    descriptor_ok = descriptor.get("packet_kind") == _DESCRIPTOR_KIND and bool(descriptor.get("redacted_endpoint_descriptor_ready"))
    instance_ok = instance.get("packet_kind") == _INSTANCE_KIND and bool(instance.get("no_connect_adapter_instance_ready"))
    ready = bool(allow_preflight and descriptor_ok and instance_ok)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_dry_run_preflight_packet",
        "cp7_dry_run_preflight_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q37f_cp7_dry_run_preflight",
        "redacted_endpoint_descriptor_ready": descriptor_ok,
        "no_connect_adapter_instance_ready": instance_ok,
        "dry_run_preflight_ready": ready,
        "real_adapter_shape_defined": bool(instance.get("adapter_interface_shape_kind_recognized")) if ready else False,
        "preflight_status": "cp7_dry_run_preflight_ready_no_connect_no_send" if ready else "cp7_dry_run_preflight_blocked",
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
        "next_checkpoint": "CP7_forbidden_behavior_guard" if ready else "CP7_no_connect_adapter_instance",
    }
