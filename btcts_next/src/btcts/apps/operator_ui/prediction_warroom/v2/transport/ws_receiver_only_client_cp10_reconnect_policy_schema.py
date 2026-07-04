# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp10_reconnect_policy_schema.py
# desc: PS-Q40B CP10 reconnect policy schema. Defines dry-run reconnect metadata only; no reconnect execution, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp10_reconnect_policy_schema.ps_q40b.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp10_reconnect_policy_schema_q40b"
_ENTRY_KIND = "warroom_v2_ws_receiver_only_client_cp10_danger_zone_entry_contract_packet"


def build_warroom_v2_ws_receiver_only_client_cp10_reconnect_policy_schema_packet(
    cp10_danger_zone_entry_contract_packet: Mapping[str, Any] | None = None,
    *,
    allow_reconnect_policy_schema: bool = False,
) -> dict[str, Any]:
    entry = dict(cp10_danger_zone_entry_contract_packet or {})
    recognized = entry.get("packet_kind") == _ENTRY_KIND
    ready = bool(allow_reconnect_policy_schema and recognized and entry.get("cp10_entry_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp10_reconnect_policy_schema_packet",
        "cp10_reconnect_policy_schema_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q40b_cp10_reconnect_policy_schema",
        "cp10_entry_kind_recognized": recognized,
        "reconnect_policy_schema_ready": ready,
        "reconnect_policy_kind": "dry_run_metadata_only" if ready else "not_ready",
        "max_reconnect_attempts_metadata": 3,
        "min_reconnect_delay_ms_metadata": 250,
        "max_reconnect_delay_ms_metadata": 2000,
        "runtime_reconnect_allowed": False,
        "next_checkpoint": "CP10_heartbeat_policy_schema" if ready else "CP10_danger_zone_entry_contract",
        "cp10_is_danger_zone": True,
        "danger_zone_dry_run_only": True,
        "default_connect_enabled": False,
        "default_reconnect_enabled": False,
        "default_heartbeat_enabled": False,
        "default_backpressure_runtime_enabled": False,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "secret_exposure": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "operator_action_controls_added": False,
        "auto_start_added": False,
        "receive_loop_started": False,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_started": False,
        "connect_invoked": False,
        "reconnect_invoked": False,
        "heartbeat_sent": False,
        "heartbeat_received": False,
        "backpressure_runtime_started": False,
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
