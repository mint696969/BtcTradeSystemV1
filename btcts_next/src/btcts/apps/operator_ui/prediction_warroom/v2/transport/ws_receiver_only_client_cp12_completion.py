# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp12_completion.py
# desc: PS-Q42H CP12 completion closes dry-run operator-facing live receiver mode and hands off to CP13 high-visibility realtime delivery danger-zone.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp12_completion.ps_q42h.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp12_completion_q42h"
_PREVIOUS_KIND = "warroom_v2_ws_receiver_only_client_cp12_operator_facing_no_action_guard_packet"
_PREVIOUS_READY_KEYS = ('operator_facing_no_action_guard_ready',)


def build_warroom_v2_ws_receiver_only_client_cp12_completion_packet(
    previous_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp12_completion: bool = False,
) -> dict[str, Any]:
    previous = dict(previous_packet or {})
    recognized = previous.get("packet_kind") == _PREVIOUS_KIND
    previous_ready = all(bool(previous.get(key)) for key in _PREVIOUS_READY_KEYS)
    ready = bool(allow_cp12_completion and recognized and previous_ready)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp12_completion_packet",
        "version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q42h_cp12_completion",
        "previous_kind_recognized": recognized,
        "previous_ready": previous_ready,
        "cp12_completed": ready,
        "cp12_completion_commit_ready": ready,
        "cp13_is_danger_zone": ready,
        "next_checkpoint": "CP13_high_visibility_realtime_delivery" if ready else "previous_checkpoint",
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
