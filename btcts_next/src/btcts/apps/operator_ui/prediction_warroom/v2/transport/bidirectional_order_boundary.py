# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/bidirectional_order_boundary.py
# desc: WarRoom v2 bidirectional WebSocket and OrderIntent boundary contract. Pure design packet only; no socket, no IO, no order send.

from __future__ import annotations

from typing import Any

WARROOM_V2_BIDIRECTIONAL_ORDER_BOUNDARY_VERSION = "prediction_warroom.v2.transport.bidirectional_order_boundary.ps_q31s.v1"


def build_warroom_v2_bidirectional_order_boundary_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "boundary_version": WARROOM_V2_BIDIRECTIONAL_ORDER_BOUNDARY_VERSION,
        "contract_kind": "warroom_v2_bidirectional_websocket_order_intent_boundary",
        "websocket_direction_preferred": "bidirectional",
        "read_model_push_plane": "server_to_warroom_ui",
        "command_intent_plane": "warroom_ui_or_autotrade_to_order_intent_gateway",
        "server_to_ui_display_push": True,
        "ui_to_server_order_intent_future": True,
        "autotrade_to_order_intent_future": True,
        "human_and_autotrade_share_order_intent_gateway": True,
        "decision_sources": ["human_operator", "autotrade_logic"],
        "shared_order_intent_gateway": "btcts.autotrade.execution.intents.OrderIntent",
        "manual_order_preview_builder": "btcts.autotrade.execution.order_preview.build_bitflyer_fx_manual_order_preview",
        "autotrade_pipeline_anchor": "btcts.autotrade.pipeline.run_shadow_paper_dry_run_vertical_slice",
        "warroom_page_places_orders_directly": False,
        "warroom_widget_places_orders_directly": False,
        "widget_owns_order_logic": False,
        "order_logic_responsibility": "autotrade.execution.OrderIntent_gateway",
        "mode_switch_required": True,
        "mode_switch_mutual_exclusion_required": True,
        "idempotency_key_required": True,
        "risk_gate_required": True,
        "private_readiness_required": True,
        "order_preview_required": True,
        "ledger_required_before_broker_send": True,
        "broker_send_gate_required": True,
        "human_decision_source_only_changes_intent_origin": True,
        "autotrade_decision_source_only_changes_intent_origin": True,
        "websocket_enabled": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_bidirectional_order_boundary_flow() -> dict[str, Any]:
    return {
        "ok": True,
        "boundary_version": WARROOM_V2_BIDIRECTIONAL_ORDER_BOUNDARY_VERSION,
        "flow_kind": "warroom_v2_future_bidirectional_transport_flow",
        "display_push_flow": [
            "read_model_event_bridge",
            "websocket_display_topic_stream",
            "warroom_widget_update",
        ],
        "human_order_flow": [
            "human_operator_decision",
            "command_intent_envelope",
            "OrderIntent_gateway",
            "risk_gate",
            "private_readiness",
            "order_preview",
            "ledger_gate",
            "broker_send_gate",
        ],
        "autotrade_order_flow": [
            "autotrade_decision",
            "OrderIntent_gateway",
            "risk_gate",
            "private_readiness",
            "order_preview",
            "ledger_gate",
            "broker_send_gate",
        ],
        "shared_after_decision_source": "OrderIntent_gateway",
        "read_model_push_and_order_intent_planes_are_separate": True,
        "same_websocket_session_may_carry_both_planes_later": True,
        "same_message_schema_not_required_for_display_and_order": True,
        "display_messages_are_read_only": True,
        "order_messages_are_command_intents": True,
        "orders_directly_from_ui_forbidden": True,
        "orders_directly_from_widget_forbidden": True,
        "broker_send_disabled_in_this_slice": True,
        "websocket_enabled": False,
        "socket_opened": False,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
