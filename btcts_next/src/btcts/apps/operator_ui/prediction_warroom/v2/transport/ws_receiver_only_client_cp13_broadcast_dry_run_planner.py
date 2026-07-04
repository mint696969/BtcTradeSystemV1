# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp13_broadcast_dry_run_planner.py
# desc: PS-Q43D Broadcast dry-run planner describes hypothetical delivery plan metadata without invoking publish, broadcast, or send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp13_broadcast_dry_run_planner.ps_q43d.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp13_broadcast_dry_run_planner_q43d"
_PREVIOUS_KIND = "warroom_v2_ws_receiver_only_client_cp13_realtime_presentation_envelope_packet"
_PREVIOUS_READY_KEYS = ('realtime_presentation_envelope_ready',)


def build_warroom_v2_ws_receiver_only_client_cp13_broadcast_dry_run_planner_packet(
    previous_packet: Mapping[str, Any] | None = None,
    *,
    allow_broadcast_dry_run_planner: bool = False,
) -> dict[str, Any]:
    previous = dict(previous_packet or {})
    recognized = previous.get("packet_kind") == _PREVIOUS_KIND
    previous_ready = all(bool(previous.get(key)) for key in _PREVIOUS_READY_KEYS)
    ready = bool(allow_broadcast_dry_run_planner and recognized and previous_ready)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp13_broadcast_dry_run_planner_packet",
        "version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q43d_cp13_broadcast_dry_run_planner",
        "previous_kind_recognized": recognized,
        "previous_ready": previous_ready,
        "broadcast_dry_run_planner_ready": ready,
        "broadcast_plan_kind": "dry_run_plan_only" if ready else "not_ready",
        "planned_delivery_targets_metadata": ["local_operator_panel"] if ready else [],
        "next_checkpoint": "CP13_rate_limit_display_guard" if ready else "previous_checkpoint",
        "cp13_is_danger_zone": True,
        "high_visibility_realtime_delivery_dry_run_only": True,
        "high_visibility_delivery_default_off": True,
        "high_visibility_metadata_only": True,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "high_visibility_delivery_enabled": False,
        "high_visibility_delivery_mount_requested_now": False,
        "realtime_animation_started": False,
        "realtime_delivery_runtime_started": False,
        "broadcast_invoked": False,
        "publish_invoked": False,
        "delivery_broadcast_control_added": False,
        "operator_broadcast_control_added": False,
        "operator_publish_control_added": False,
        "operator_delivery_control_added": False,
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
