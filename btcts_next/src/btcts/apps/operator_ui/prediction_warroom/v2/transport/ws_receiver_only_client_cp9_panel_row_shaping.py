# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp9_panel_row_shaping.py
# desc: PS-Q39C CP9 panel row shaping. Converts CP8 readback metadata into safe read-only display rows; no raw payload, no controls.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp9_panel_row_shaping.ps_q39c.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp9_panel_row_shaping_q39c"
_CONTRACT_KIND = "warroom_v2_ws_receiver_only_client_cp9_visible_stream_panel_data_contract_packet"
_READBACK_KIND = "warroom_v2_ws_receiver_only_client_cp8_state_readback_packet"


def _shape_row(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "topic": str(item.get("topic", "")),
        "message_kind": str(item.get("message_kind", "metadata")),
        "sequence": item.get("sequence"),
        "source_label": str(item.get("source_label", "sanitized_state")),
        "summary": str(item.get("normalized_summary", "metadata-only event")),
    }


def build_warroom_v2_ws_receiver_only_client_cp9_panel_row_shaping_packet(
    cp9_visible_stream_panel_data_contract_packet: Mapping[str, Any] | None = None,
    cp8_state_readback_packet: Mapping[str, Any] | None = None,
    *,
    allow_row_shaping: bool = False,
) -> dict[str, Any]:
    contract = dict(cp9_visible_stream_panel_data_contract_packet or {})
    readback = dict(cp8_state_readback_packet or {})
    contract_ok = contract.get("packet_kind") == _CONTRACT_KIND and bool(contract.get("visible_stream_panel_data_contract_ready"))
    readback_ok = readback.get("packet_kind") == _READBACK_KIND and bool(readback.get("state_readback_ready"))
    rows = [_shape_row(item) for item in list(readback.get("recent_incoming_metadata", []))[:5]] if allow_row_shaping and contract_ok and readback_ok else []
    ready = bool(allow_row_shaping and contract_ok and readback_ok)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp9_panel_row_shaping_packet",
        "cp9_panel_row_shaping_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q39c_cp9_panel_row_shaping",
        "data_contract_ready": contract_ok,
        "state_readback_ready": readback_ok,
        "panel_row_shaping_ready": ready,
        "panel_rows": rows,
        "panel_row_count": len(rows),
        "panel_rows_metadata_only": True,
        "visible_stream_panel_read_only": True,
        "visible_stream_panel_default_off": True,
        "panel_mount_default_enabled": False,
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
        "next_checkpoint": "CP9_read_only_render_packet" if ready else "CP9_visible_stream_panel_data_contract",
    }
