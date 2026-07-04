# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp8_state_readback.py
# desc: PS-Q38E CP8 state readback. Returns sanitized metadata state summary only; no raw payload, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp8_state_readback.ps_q38e.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp8_state_readback_q38e"
_UPDATE_KIND = "warroom_v2_ws_receiver_only_client_cp8_state_append_update_packet"


def build_warroom_v2_ws_receiver_only_client_cp8_state_readback_packet(
    target_state: Mapping[str, Any] | None = None,
    cp8_state_append_update_packet: Mapping[str, Any] | None = None,
    *,
    allow_readback: bool = False,
) -> dict[str, Any]:
    state = dict(target_state or {})
    update = dict(cp8_state_append_update_packet or {})
    recognized = update.get("packet_kind") == _UPDATE_KIND
    ready = bool(allow_readback and recognized and update.get("state_append_update_ready") and state.get("cp8_state_flow_ready"))
    recent = list(state.get("recent_incoming_metadata", []))[-5:] if ready else []
    latest = dict(state.get("latest_incoming_metadata", {})) if ready else {}
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp8_state_readback_packet",
        "cp8_state_readback_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q38e_cp8_state_readback",
        "state_append_update_kind_recognized": recognized,
        "state_readback_ready": ready,
        "latest_incoming_metadata": latest,
        "recent_incoming_metadata": recent,
        "received_message_count": int(state.get("received_message_count", 0)) if ready else 0,
        "dropped_count": int(state.get("dropped_count", 0)) if ready else 0,
        "bounded_metadata_state": True,
        "next_checkpoint": "CP8_preflight_to_state_bridge" if ready else "CP8_state_append_update",
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
