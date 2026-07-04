# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp11_topic_widget_row_shaping.py
# desc: PS-Q41D CP11 topic widget row shaping. Groups CP9 render rows by safe topic; metadata-only and no control.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp11_topic_widget_row_shaping.ps_q41d.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp11_topic_widget_row_shaping_q41d"
_CONTRACT_KIND = "warroom_v2_ws_receiver_only_client_cp11_topic_widget_data_contract_packet"
_CP9_RENDER_KIND = "warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet"


def _shape_topic_rows(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        topic = str(row.get("topic", "summary") or "summary")
        item = grouped.setdefault(topic, {"topic": topic, "message_count": 0, "latest_sequence": None, "latest_summary": "metadata-only", "freshness_label_ja": "表示準備", "guidance_ja": "read-only"})
        item["message_count"] += 1
        item["latest_sequence"] = row.get("sequence", item["latest_sequence"])
        item["latest_summary"] = str(row.get("summary", item["latest_summary"]))
    return list(grouped.values())[:6]


def build_warroom_v2_ws_receiver_only_client_cp11_topic_widget_row_shaping_packet(
    cp11_topic_widget_data_contract_packet: Mapping[str, Any] | None = None,
    cp9_read_only_render_packet: Mapping[str, Any] | None = None,
    *,
    allow_row_shaping: bool = False,
) -> dict[str, Any]:
    contract = dict(cp11_topic_widget_data_contract_packet or {})
    render = dict(cp9_read_only_render_packet or {})
    contract_ok = contract.get("packet_kind") == _CONTRACT_KIND and bool(contract.get("topic_widget_data_contract_ready"))
    render_ok = render.get("packet_kind") == _CP9_RENDER_KIND and bool(render.get("read_only_render_packet_ready"))
    ready = bool(allow_row_shaping and contract_ok and render_ok)
    rows = _shape_topic_rows(list(render.get("render_rows", []))) if ready else []
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp11_topic_widget_row_shaping_packet",
        "cp11_topic_widget_row_shaping_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q41d_cp11_topic_widget_row_shaping",
        "topic_widget_data_contract_ready": contract_ok,
        "cp9_render_packet_ready": render_ok,
        "topic_widget_row_shaping_ready": ready,
        "topic_widget_rows": rows,
        "topic_widget_row_count": len(rows),
        "next_checkpoint": "CP11_read_only_topic_render_packet" if ready else "CP11_topic_widget_data_contract",

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
