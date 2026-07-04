# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp11_topic_widget_data_contract.py
# desc: PS-Q41C CP11 topic widget data contract. Safe topic widget fields only; no raw payload, no controls.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp11_topic_widget_data_contract.ps_q41c.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp11_topic_widget_data_contract_q41c"
_REGISTRY_KIND = "warroom_v2_ws_receiver_only_client_cp11_topic_registry_schema_packet"
SAFE_WIDGET_FIELDS = ("topic", "message_count", "latest_sequence", "latest_summary", "freshness_label_ja", "guidance_ja")


def build_warroom_v2_ws_receiver_only_client_cp11_topic_widget_data_contract_packet(
    cp11_topic_registry_schema_packet: Mapping[str, Any] | None = None,
    *,
    allow_data_contract: bool = False,
) -> dict[str, Any]:
    registry = dict(cp11_topic_registry_schema_packet or {})
    recognized = registry.get("packet_kind") == _REGISTRY_KIND
    ready = bool(allow_data_contract and recognized and registry.get("topic_registry_schema_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp11_topic_widget_data_contract_packet",
        "cp11_topic_widget_data_contract_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q41c_cp11_topic_widget_data_contract",
        "topic_registry_schema_kind_recognized": recognized,
        "topic_widget_data_contract_ready": ready,
        "safe_widget_fields": list(SAFE_WIDGET_FIELDS) if ready else [],
        "next_checkpoint": "CP11_topic_widget_row_shaping" if ready else "CP11_topic_registry_schema",

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
