# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp9_visible_stream_panel_data_contract.py
# desc: PS-Q39B CP9 visible stream panel data contract. Safe display fields only; no raw payload, no endpoint/token/callable, no controls.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp9_visible_stream_panel_data_contract.ps_q39b.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp9_visible_stream_panel_data_contract_q39b"
_ENTRY_KIND = "warroom_v2_ws_receiver_only_client_cp9_entry_contract_packet"
SAFE_PANEL_FIELDS = (
    "transport_state_ja",
    "data_freshness_ja",
    "last_update_age_ja",
    "received_message_count",
    "dropped_count",
    "latest_topic",
    "latest_sequence",
    "operator_guidance_ja",
)


def build_warroom_v2_ws_receiver_only_client_cp9_visible_stream_panel_data_contract_packet(
    cp9_entry_contract_packet: Mapping[str, Any] | None = None,
    *,
    allow_data_contract: bool = False,
) -> dict[str, Any]:
    entry = dict(cp9_entry_contract_packet or {})
    recognized = entry.get("packet_kind") == _ENTRY_KIND
    ready = bool(allow_data_contract and recognized and entry.get("cp9_entry_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp9_visible_stream_panel_data_contract_packet",
        "cp9_visible_stream_panel_data_contract_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q39b_cp9_visible_stream_panel_data_contract",
        "cp9_entry_kind_recognized": recognized,
        "visible_stream_panel_data_contract_ready": ready,
        "safe_panel_fields": list(SAFE_PANEL_FIELDS) if ready else [],
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
        "next_checkpoint": "CP9_panel_row_shaping" if ready else "CP9_entry_contract",
    }
