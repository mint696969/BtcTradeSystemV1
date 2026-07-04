# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp11_topic_registry_schema.py
# desc: PS-Q41B CP11 topic registry schema. Defines safe display topics only; no subscription, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp11_topic_registry_schema.ps_q41b.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp11_topic_registry_schema_q41b"
_ENTRY_KIND = "warroom_v2_ws_receiver_only_client_cp11_entry_contract_packet"
SAFE_TOPICS = ("book", "trades", "lifecycle", "summary")


def build_warroom_v2_ws_receiver_only_client_cp11_topic_registry_schema_packet(
    cp11_entry_contract_packet: Mapping[str, Any] | None = None,
    *,
    allow_topic_registry_schema: bool = False,
) -> dict[str, Any]:
    entry = dict(cp11_entry_contract_packet or {})
    recognized = entry.get("packet_kind") == _ENTRY_KIND
    ready = bool(allow_topic_registry_schema and recognized and entry.get("cp11_entry_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp11_topic_registry_schema_packet",
        "cp11_topic_registry_schema_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q41b_cp11_topic_registry_schema",
        "cp11_entry_kind_recognized": recognized,
        "topic_registry_schema_ready": ready,
        "safe_topics": list(SAFE_TOPICS) if ready else [],
        "topic_registry_source": "static_metadata_only",
        "next_checkpoint": "CP11_topic_widget_data_contract" if ready else "CP11_entry_contract",

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
