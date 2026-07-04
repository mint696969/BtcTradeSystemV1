# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator.py
# desc: PS-Q40E CP10 lifecycle dry-run evaluator. Evaluates reconnect/heartbeat/backpressure metadata without executing any runtime action.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator.ps_q40e.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator_q40e"
_BACKPRESSURE_KIND = "warroom_v2_ws_receiver_only_client_cp10_backpressure_policy_schema_packet"


def build_warroom_v2_ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator_packet(
    cp10_backpressure_policy_schema_packet: Mapping[str, Any] | None = None,
    observed_metadata: Mapping[str, Any] | None = None,
    *,
    allow_dry_run_evaluator: bool = False,
) -> dict[str, Any]:
    policy = dict(cp10_backpressure_policy_schema_packet or {})
    observed = dict(observed_metadata or {})
    recognized = policy.get("packet_kind") == _BACKPRESSURE_KIND
    ready = bool(allow_dry_run_evaluator and recognized and policy.get("backpressure_policy_schema_ready"))
    pending = int(observed.get("pending_message_count", 0)) if ready else 0
    stale_ms = int(observed.get("last_seen_age_ms", 0)) if ready else 0
    saturation = min(1.0, pending / max(int(policy.get("max_pending_messages_metadata", 100)), 1)) if ready else 0.0
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp10_lifecycle_dry_run_evaluator_packet",
        "cp10_lifecycle_dry_run_evaluator_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q40e_cp10_lifecycle_dry_run_evaluator",
        "backpressure_policy_kind_recognized": recognized,
        "lifecycle_dry_run_evaluator_ready": ready,
        "observed_pending_message_count": pending,
        "observed_last_seen_age_ms": stale_ms,
        "dry_run_saturation_ratio": saturation,
        "dry_run_stale_state_detected": bool(ready and stale_ms >= 15000),
        "dry_run_backpressure_warning": bool(ready and saturation >= 0.8),
        "dry_run_reconnect_recommended_metadata": bool(ready and stale_ms >= 15000),
        "dry_run_drop_policy_metadata": policy.get("drop_policy_metadata") if ready else "not_ready",
        "runtime_action_executed": False,
        "next_checkpoint": "CP10_lifecycle_state_readback" if ready else "CP10_backpressure_policy_schema",
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
