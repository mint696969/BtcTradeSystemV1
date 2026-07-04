# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_redacted_endpoint_descriptor.py
# desc: PS-Q37C CP7 redacted endpoint descriptor. Records configured booleans only; no endpoint/token/callable values returned.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp7_redacted_endpoint_descriptor.ps_q37c.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_q37c"
_APPROVAL_KIND = "warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_packet"


def build_warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_packet(
    cp7_dry_run_approval_gate_packet: Mapping[str, Any] | None = None,
    *,
    endpoint_configured: bool = False,
    token_configured: bool = False,
    connect_callable_configured: bool = False,
    allow_descriptor: bool = False,
) -> dict[str, Any]:
    gate = dict(cp7_dry_run_approval_gate_packet or {})
    recognized = gate.get("packet_kind") == _APPROVAL_KIND
    ready = bool(allow_descriptor and recognized and gate.get("dry_run_approval_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_redacted_endpoint_descriptor_packet",
        "cp7_redacted_endpoint_descriptor_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q37c_cp7_redacted_endpoint_descriptor",
        "approval_gate_kind_recognized": recognized,
        "redacted_endpoint_descriptor_ready": ready,
        "endpoint_configured": bool(endpoint_configured) if ready else False,
        "token_configured": bool(token_configured) if ready else False,
        "connect_callable_configured": bool(connect_callable_configured) if ready else False,
        "descriptor_kind": "redacted_configured_flags_only" if ready else "not_ready",
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
        "next_checkpoint": "CP7_adapter_interface_shape" if ready else "CP7_dry_run_approval_gate",
    }
