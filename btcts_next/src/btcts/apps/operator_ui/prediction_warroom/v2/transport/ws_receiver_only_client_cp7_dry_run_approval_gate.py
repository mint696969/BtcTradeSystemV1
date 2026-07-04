# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_dry_run_approval_gate.py
# desc: PS-Q37B CP7 dry-run approval gate. Requires explicit label and operator ack; no secret, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp7_dry_run_approval_gate.ps_q37b.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_q37b"
REQUIRED_APPROVAL_LABEL = "APPROVE_CP7_RECEIVER_DRY_RUN_PREFLIGHT_NO_SEND"
_ENTRY_KIND = "warroom_v2_ws_receiver_only_client_cp7_entry_contract_packet"


def build_warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_packet(
    cp7_entry_contract_packet: Mapping[str, Any] | None = None,
    *,
    operator_dry_run_ack: bool = False,
    approval_label: str = "",
) -> dict[str, Any]:
    entry = dict(cp7_entry_contract_packet or {})
    recognized = entry.get("packet_kind") == _ENTRY_KIND
    label_matches = approval_label == REQUIRED_APPROVAL_LABEL
    ready = bool(recognized and entry.get("cp7_entry_ready") and operator_dry_run_ack and label_matches)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_dry_run_approval_gate_packet",
        "cp7_dry_run_approval_gate_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q37b_cp7_dry_run_approval_gate",
        "required_approval_label": REQUIRED_APPROVAL_LABEL,
        "approval_label_matches_required": label_matches,
        "operator_dry_run_ack": bool(operator_dry_run_ack),
        "cp7_entry_kind_recognized": recognized,
        "dry_run_approval_ready": ready,
        "approval_value_is_secret": False,
        "approval_token_value_returned": False,
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
        "next_checkpoint": "CP7_redacted_endpoint_descriptor" if ready else "CP7_entry_contract",
    }
