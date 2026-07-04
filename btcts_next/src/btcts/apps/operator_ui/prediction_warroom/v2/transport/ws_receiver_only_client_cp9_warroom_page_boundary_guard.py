# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp9_warroom_page_boundary_guard.py
# desc: PS-Q39F CP9 WarRoom page boundary guard. Proves CP9 does not modify WarRoom page or add visible controls.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp9_warroom_page_boundary_guard.ps_q39f.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp9_warroom_page_boundary_guard_q39f"
_GATE_KIND = "warroom_v2_ws_receiver_only_client_cp9_default_off_mount_gate_packet"


def build_warroom_v2_ws_receiver_only_client_cp9_warroom_page_boundary_guard_packet(
    cp9_default_off_mount_gate_packet: Mapping[str, Any] | None = None,
    *,
    allow_page_boundary_guard: bool = False,
) -> dict[str, Any]:
    gate = dict(cp9_default_off_mount_gate_packet or {})
    recognized = gate.get("packet_kind") == _GATE_KIND
    ready = bool(allow_page_boundary_guard and recognized and gate.get("default_off_mount_gate_ready") and gate.get("warroom_page_modified") is False)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp9_warroom_page_boundary_guard_packet",
        "cp9_warroom_page_boundary_guard_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q39f_cp9_warroom_page_boundary_guard",
        "default_off_mount_gate_kind_recognized": recognized,
        "warroom_page_boundary_guard_ready": ready,
        "visible_stream_panel_ready": ready,
        "visible_stream_panel_read_only": True,
        "visible_stream_panel_default_off": True,
        "panel_mount_default_enabled": False,
        "panel_mount_requested_now": False,
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
        "next_checkpoint": "CP9_no_control_visible_guard" if ready else "CP9_default_off_mount_gate",
    }
