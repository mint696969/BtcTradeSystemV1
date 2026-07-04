# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp11_completion.py
# desc: PS-Q41H CP11 completion packet. Closes read-only topic widgets and hands off to CP12 operator-facing live receiver mode danger-zone.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp11_completion.ps_q41h.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp11_completion_q41h"
_GUARD_KIND = "warroom_v2_ws_receiver_only_client_cp11_no_control_topic_widget_guard_packet"


def build_warroom_v2_ws_receiver_only_client_cp11_completion_packet(
    cp11_no_control_topic_widget_guard_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp11_completion: bool = False,
) -> dict[str, Any]:
    guard = dict(cp11_no_control_topic_widget_guard_packet or {})
    recognized = guard.get("packet_kind") == _GUARD_KIND
    completed = bool(allow_cp11_completion and recognized and guard.get("no_control_topic_widget_guard_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp11_completion_packet",
        "cp11_completion_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q41h_cp11_completion_close",
        "cp11_no_control_topic_widget_guard_kind_recognized": recognized,
        "cp11_completed": completed,
        "cp11_completion_commit_ready": completed,
        "topic_widgets_ready": completed,
        "cp12_is_danger_zone": completed,
        "next_checkpoint": "CP12_operator_facing_live_receiver_mode" if completed else "CP11_no_control_topic_widget_guard",

        "topic_widgets_read_only": True,
        "topic_widgets_default_off": True,
        "topic_widgets_metadata_only": True,
        "topic_subscription_requested": False,
        "topic_subscribe_invoked": False,
        "topic_unsubscribe_invoked": False,
        "topic_filter_mutation_enabled": False,
        "topic_widget_controls_added": False,
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
