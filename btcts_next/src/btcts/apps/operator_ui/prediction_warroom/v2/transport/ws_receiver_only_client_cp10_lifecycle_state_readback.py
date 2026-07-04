# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp10_lifecycle_state_readback.py
# desc: PS-Q40F CP10 lifecycle state readback. Returns dry-run lifecycle summary metadata only; no endpoint/token/callable/raw payload.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp10_lifecycle_state_readback.ps_q40f.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp10_lifecycle_state_readback_q40f"
_EVALUATOR_KIND = "warroom_v2_ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator_packet"


def build_warroom_v2_ws_receiver_only_client_cp10_lifecycle_state_readback_packet(
    cp10_lifecycle_dry_run_evaluator_packet: Mapping[str, Any] | None = None,
    *,
    allow_state_readback: bool = False,
) -> dict[str, Any]:
    evaluator = dict(cp10_lifecycle_dry_run_evaluator_packet or {})
    recognized = evaluator.get("packet_kind") == _EVALUATOR_KIND
    ready = bool(allow_state_readback and recognized and evaluator.get("lifecycle_dry_run_evaluator_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp10_lifecycle_state_readback_packet",
        "cp10_lifecycle_state_readback_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q40f_cp10_lifecycle_state_readback",
        "lifecycle_dry_run_evaluator_kind_recognized": recognized,
        "lifecycle_state_readback_ready": ready,
        "lifecycle_summary": {
            "mode": "dry_run_no_action" if ready else "not_ready",
            "stale_state_detected": bool(evaluator.get("dry_run_stale_state_detected")) if ready else False,
            "backpressure_warning": bool(evaluator.get("dry_run_backpressure_warning")) if ready else False,
            "reconnect_recommended_metadata": bool(evaluator.get("dry_run_reconnect_recommended_metadata")) if ready else False,
        },
        "runtime_action_executed": False,
        "next_checkpoint": "CP10_danger_zone_no_action_guard" if ready else "CP10_lifecycle_dry_run_evaluator",
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
