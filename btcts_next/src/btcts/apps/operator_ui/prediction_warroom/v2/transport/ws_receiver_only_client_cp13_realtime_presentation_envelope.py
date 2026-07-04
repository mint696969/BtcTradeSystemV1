# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp13_realtime_presentation_envelope.py
# desc: PS-Q43C Realtime presentation envelope prepares metadata-only visual payload envelopes without raw payload or runtime animation.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp13_realtime_presentation_envelope.ps_q43c.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp13_realtime_presentation_envelope_q43c"
_PREVIOUS_KIND = "warroom_v2_ws_receiver_only_client_cp13_high_visibility_delivery_policy_schema_packet"
_PREVIOUS_READY_KEYS = ('high_visibility_delivery_policy_ready',)


def build_warroom_v2_ws_receiver_only_client_cp13_realtime_presentation_envelope_packet(
    previous_packet: Mapping[str, Any] | None = None,
    *,
    allow_presentation_envelope: bool = False,
) -> dict[str, Any]:
    previous = dict(previous_packet or {})
    recognized = previous.get("packet_kind") == _PREVIOUS_KIND
    previous_ready = all(bool(previous.get(key)) for key in _PREVIOUS_READY_KEYS)
    ready = bool(allow_presentation_envelope and recognized and previous_ready)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp13_realtime_presentation_envelope_packet",
        "version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q43c_cp13_realtime_presentation_envelope",
        "previous_kind_recognized": recognized,
        "previous_ready": previous_ready,
        "realtime_presentation_envelope_ready": ready,
        "presentation_envelope_kind": "metadata_only_visual_envelope" if ready else "not_ready",
        "raw_payload_allowed_in_envelope": False,
        "next_checkpoint": "CP13_broadcast_dry_run_planner" if ready else "previous_checkpoint",
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
