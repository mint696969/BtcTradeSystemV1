# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp8_preflight_to_state_bridge.py
# desc: PS-Q38F CP8 preflight-to-state bridge. Links CP7 completion to CP8 readback without opening sockets or receiving payloads.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp8_preflight_to_state_bridge.ps_q38f.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp8_preflight_to_state_bridge_q38f"
_CP7_KIND = "warroom_v2_ws_receiver_only_client_cp7_completion_packet"
_READBACK_KIND = "warroom_v2_ws_receiver_only_client_cp8_state_readback_packet"


def build_warroom_v2_ws_receiver_only_client_cp8_preflight_to_state_bridge_packet(
    cp7_completion_packet: Mapping[str, Any] | None = None,
    cp8_state_readback_packet: Mapping[str, Any] | None = None,
    *,
    allow_bridge: bool = False,
) -> dict[str, Any]:
    cp7 = dict(cp7_completion_packet or {})
    readback = dict(cp8_state_readback_packet or {})
    cp7_ok = cp7.get("packet_kind") == _CP7_KIND and bool(cp7.get("cp7_completed"))
    readback_ok = readback.get("packet_kind") == _READBACK_KIND and bool(readback.get("state_readback_ready"))
    ready = bool(allow_bridge and cp7_ok and readback_ok)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp8_preflight_to_state_bridge_packet",
        "cp8_preflight_to_state_bridge_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q38f_cp8_preflight_to_state_bridge",
        "cp7_completion_ready": cp7_ok,
        "state_readback_ready": readback_ok,
        "preflight_to_state_bridge_ready": ready,
        "live_incoming_state_flow_ready": ready,
        "next_checkpoint": "CP8_no_send_state_boundary_guard" if ready else "CP8_state_readback",
        "metadata_only": True,
        "read_only_or_caller_state_only": True,
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
    }
