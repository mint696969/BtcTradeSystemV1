# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp12_operator_approval_schema.py
# desc: PS-Q42B Operator approval schema defines explicit dry-run labels only; it returns no token, endpoint, or callable.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp12_operator_approval_schema.ps_q42b.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp12_operator_approval_schema_q42b"
_PREVIOUS_KIND = "warroom_v2_ws_receiver_only_client_cp12_danger_zone_entry_contract_packet"
_PREVIOUS_READY_KEYS = ('cp12_entry_ready',)


def build_warroom_v2_ws_receiver_only_client_cp12_operator_approval_schema_packet(
    previous_packet: Mapping[str, Any] | None = None,
    *,
    allow_operator_approval_schema: bool = False,
) -> dict[str, Any]:
    previous = dict(previous_packet or {})
    recognized = previous.get("packet_kind") == _PREVIOUS_KIND
    previous_ready = all(bool(previous.get(key)) for key in _PREVIOUS_READY_KEYS)
    ready = bool(allow_operator_approval_schema and recognized and previous_ready)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp12_operator_approval_schema_packet",
        "version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q42b_cp12_operator_approval_schema",
        "previous_kind_recognized": recognized,
        "previous_ready": previous_ready,
        "operator_approval_schema_ready": ready,
        "operator_approval_label": "DRY_RUN_OPERATOR_VISIBLE_ONLY_NO_CONNECT_NO_SEND" if ready else "not_ready",
        "next_checkpoint": "CP12_live_receiver_mode_config_schema" if ready else "previous_checkpoint",
        "cp12_is_danger_zone": True,
        "operator_facing_live_mode_dry_run_only": True,
        "live_receiver_mode_default_off": True,
        "operator_approval_label_required": True,
        "operator_facing_metadata_only": True,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "operator_live_mode_requested": False,
        "operator_live_mode_enabled": False,
        "operator_live_mode_activation_approved": False,
        "operator_activation_control_added": False,
        "operator_connect_control_added": False,
        "operator_start_control_added": False,
        "operator_stop_control_added": False,
        "operator_send_control_added": False,
        "live_receiver_mode_runtime_enabled": False,
        "live_receiver_mode_mount_requested_now": False,
        "runtime_actions_allowed_now": False,
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
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }
