# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp8_state_append_update.py
# desc: PS-Q38D CP8 state append/update. Writes sanitized metadata only to caller-provided local state; bounded and no send.

from __future__ import annotations

from typing import Any, MutableMapping, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp8_state_append_update.ps_q38d.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp8_state_append_update_q38d"
_GATE_KIND = "warroom_v2_ws_receiver_only_client_cp8_controlled_state_write_gate_packet"
_ALLOWED = ("topic", "message_kind", "received_at_ms", "sequence", "event_id", "source_label", "normalized_summary")
_MAX_RECENT = 5


def _sanitize(metadata: Mapping[str, Any]) -> dict[str, Any]:
    return {key: metadata[key] for key in _ALLOWED if key in metadata}


def apply_warroom_v2_ws_receiver_only_client_cp8_state_append_update(
    target_state: MutableMapping[str, Any],
    incoming_metadata: Mapping[str, Any] | None,
    cp8_controlled_state_write_gate_packet: Mapping[str, Any] | None = None,
    *,
    allow_state_update: bool = False,
) -> dict[str, Any]:
    gate = dict(cp8_controlled_state_write_gate_packet or {})
    recognized = gate.get("packet_kind") == _GATE_KIND
    allowed = bool(allow_state_update and recognized and gate.get("controlled_state_write_ready"))
    sanitized = _sanitize(dict(incoming_metadata or {})) if allowed else {}
    dropped_raw_payload = bool(incoming_metadata and "raw_payload" in incoming_metadata)
    if allowed:
        recent = list(target_state.get("recent_incoming_metadata", []))
        if sanitized:
            recent.append(sanitized)
        recent = recent[-_MAX_RECENT:]
        target_state["recent_incoming_metadata"] = recent
        target_state["latest_incoming_metadata"] = sanitized
        target_state["received_message_count"] = int(target_state.get("received_message_count", 0)) + (1 if sanitized else 0)
        target_state["dropped_count"] = int(target_state.get("dropped_count", 0)) + (1 if dropped_raw_payload else 0)
        target_state["cp8_state_flow_ready"] = True
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp8_state_append_update_packet",
        "cp8_state_append_update_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q38d_cp8_state_append_update",
        "controlled_state_write_gate_kind_recognized": recognized,
        "state_append_update_ready": allowed,
        "incoming_metadata_sanitized": bool(sanitized),
        "raw_payload_dropped": dropped_raw_payload,
        "latest_incoming_metadata": sanitized,
        "received_message_count": int(target_state.get("received_message_count", 0)),
        "dropped_count": int(target_state.get("dropped_count", 0)),
        "bounded_metadata_state": True,
        "next_checkpoint": "CP8_state_readback" if allowed else "CP8_controlled_state_write_gate",
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
