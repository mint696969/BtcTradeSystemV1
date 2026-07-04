# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp7_entry_contract.py
# desc: PS-Q37A CP7 entry contract. Starts gated receiver dry-run preflight only after CP6 completion; no socket, no network, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp7_entry_contract.ps_q37a.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp7_entry_contract_q37a"
_CP6_COMPLETION_KIND = "warroom_v2_ws_receiver_only_client_cp6_completion_packet"


def build_warroom_v2_ws_receiver_only_client_cp7_entry_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_entry_contract",
        "cp7_entry_contract_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q37a_cp7_entry_contract",
        "requires_cp6_completion_packet": True,
        "cp7_entry_ready": False,
        "dry_run_only": True,
        "default_connect_enabled": False,
        "default_send_enabled": False,
        "real_adapter_shape_allowed": True,
        "real_adapter_execution_allowed": False,
        "metadata_only": True,
        "read_only": True,
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


def build_warroom_v2_ws_receiver_only_client_cp7_entry_contract_packet(
    cp6_completion_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp7_entry: bool = False,
) -> dict[str, Any]:
    cp6 = dict(cp6_completion_packet or {})
    recognized = cp6.get("packet_kind") == _CP6_COMPLETION_KIND
    ready = bool(allow_cp7_entry and recognized and cp6.get("cp6_completed") and cp6.get("cp6_completion_commit_ready"))
    return {
        **build_warroom_v2_ws_receiver_only_client_cp7_entry_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp7_entry_contract_packet",
        "cp6_completion_kind_recognized": recognized,
        "cp7_entry_ready": ready,
        "next_checkpoint": "CP7_dry_run_approval_gate" if ready else "CP6_completion",
    }
