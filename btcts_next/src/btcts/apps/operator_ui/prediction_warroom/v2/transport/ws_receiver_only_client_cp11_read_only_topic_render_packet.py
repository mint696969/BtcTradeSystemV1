# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp11_read_only_topic_render_packet.py
# desc: PS-Q41E CP11 read-only topic render packet. Builds render metadata only; no Streamlit import, no callable, no controls.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp11_read_only_topic_render_packet.ps_q41e.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp11_read_only_topic_render_packet_q41e"
_ROWS_KIND = "warroom_v2_ws_receiver_only_client_cp11_topic_widget_row_shaping_packet"


def build_warroom_v2_ws_receiver_only_client_cp11_read_only_topic_render_packet(
    cp11_topic_widget_row_shaping_packet: Mapping[str, Any] | None = None,
    *,
    allow_render_packet: bool = False,
) -> dict[str, Any]:
    rows_packet = dict(cp11_topic_widget_row_shaping_packet or {})
    recognized = rows_packet.get("packet_kind") == _ROWS_KIND
    ready = bool(allow_render_packet and recognized and rows_packet.get("topic_widget_row_shaping_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp11_read_only_topic_render_packet",
        "cp11_read_only_topic_render_packet_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q41e_cp11_read_only_topic_render_packet",
        "topic_widget_row_shaping_kind_recognized": recognized,
        "read_only_topic_render_packet_ready": ready,
        "topic_widget_rows": list(rows_packet.get("topic_widget_rows", [])) if ready else [],
        "render_callable_returned": False,
        "streamlit_imported": False,
        "next_checkpoint": "CP11_default_off_topic_widget_mount_gate" if ready else "CP11_topic_widget_row_shaping",

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
