# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp9_default_off_mount_gate.py
# desc: PS-Q39E CP9 default-off mount gate. Prepares visible panel mount metadata while keeping mount disabled by default; no page change.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp9_default_off_mount_gate.ps_q39e.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp9_default_off_mount_gate_q39e"
_RENDER_KIND = "warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet"


def build_warroom_v2_ws_receiver_only_client_cp9_default_off_mount_gate_packet(
    cp9_read_only_render_packet: Mapping[str, Any] | None = None,
    *,
    allow_default_off_mount_gate: bool = False,
) -> dict[str, Any]:
    render = dict(cp9_read_only_render_packet or {})
    recognized = render.get("packet_kind") == _RENDER_KIND
    ready = bool(allow_default_off_mount_gate and recognized and render.get("read_only_render_packet_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp9_default_off_mount_gate_packet",
        "cp9_default_off_mount_gate_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q39e_cp9_default_off_mount_gate",
        "read_only_render_packet_kind_recognized": recognized,
        "default_off_mount_gate_ready": ready,
        "visible_stream_panel_ready": ready,
        "visible_stream_panel_read_only": True,
        "visible_stream_panel_default_off": True,
        "panel_mount_default_enabled": False,
        "panel_mount_requested_now": False,
        "panel_mount_requires_future_explicit_gate": True,
        "operator_action_controls_added": False,
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
        "next_checkpoint": "CP9_warroom_page_boundary_guard" if ready else "CP9_read_only_render_packet",
    }
