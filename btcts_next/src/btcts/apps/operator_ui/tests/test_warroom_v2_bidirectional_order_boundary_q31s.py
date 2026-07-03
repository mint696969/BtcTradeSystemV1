# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_bidirectional_order_boundary_q31s.py
# desc: PS-Q31S guards for bidirectional WebSocket and OrderIntent boundary design. No socket and no order send.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    build_warroom_v2_bidirectional_order_boundary_contract,
    build_warroom_v2_bidirectional_order_boundary_flow,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q31S_WARROOM_V2_BIDIRECTIONAL_WEBSOCKET_AND_ORDER_INTENT_BOUNDARY_DESIGN_2026-07-03.md"
TRANSPORT_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport"


def test_q31s_contract_prefers_bidirectional_websocket_but_keeps_it_disabled_now() -> None:
    packet = build_warroom_v2_bidirectional_order_boundary_contract()
    assert packet["contract_kind"] == "warroom_v2_bidirectional_websocket_order_intent_boundary"
    assert packet["websocket_direction_preferred"] == "bidirectional"
    assert packet["server_to_ui_display_push"] is True
    assert packet["ui_to_server_order_intent_future"] is True
    assert packet["autotrade_to_order_intent_future"] is True
    assert packet["websocket_enabled"] is False
    assert packet["socket_opened"] is False
    assert packet["external_message_send_enabled"] is False


def test_q31s_human_and_autotrade_converge_at_shared_order_intent_gateway() -> None:
    packet = build_warroom_v2_bidirectional_order_boundary_contract()
    assert packet["human_and_autotrade_share_order_intent_gateway"] is True
    assert packet["decision_sources"] == ["human_operator", "autotrade_logic"]
    assert packet["shared_order_intent_gateway"] == "btcts.autotrade.execution.intents.OrderIntent"
    assert packet["human_decision_source_only_changes_intent_origin"] is True
    assert packet["autotrade_decision_source_only_changes_intent_origin"] is True
    assert packet["warroom_page_places_orders_directly"] is False
    assert packet["warroom_widget_places_orders_directly"] is False
    assert packet["widget_owns_order_logic"] is False


def test_q31s_execution_gates_are_required_before_any_future_broker_send() -> None:
    packet = build_warroom_v2_bidirectional_order_boundary_contract()
    assert packet["mode_switch_required"] is True
    assert packet["mode_switch_mutual_exclusion_required"] is True
    assert packet["idempotency_key_required"] is True
    assert packet["risk_gate_required"] is True
    assert packet["private_readiness_required"] is True
    assert packet["order_preview_required"] is True
    assert packet["ledger_required_before_broker_send"] is True
    assert packet["broker_send_gate_required"] is True
    assert packet["order_intent_submitted"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["mode_apply_allowed"] is False
    assert packet["parameter_apply_allowed"] is False


def test_q31s_flow_separates_read_model_push_plane_from_command_intent_plane() -> None:
    flow = build_warroom_v2_bidirectional_order_boundary_flow()
    assert flow["read_model_push_and_order_intent_planes_are_separate"] is True
    assert flow["same_websocket_session_may_carry_both_planes_later"] is True
    assert flow["same_message_schema_not_required_for_display_and_order"] is True
    assert flow["display_messages_are_read_only"] is True
    assert flow["order_messages_are_command_intents"] is True
    assert flow["display_push_flow"] == ["read_model_event_bridge", "websocket_display_topic_stream", "warroom_widget_update"]
    assert flow["human_order_flow"][2] == "OrderIntent_gateway"
    assert flow["autotrade_order_flow"][1] == "OrderIntent_gateway"
    assert flow["orders_directly_from_ui_forbidden"] is True
    assert flow["orders_directly_from_widget_forbidden"] is True
    assert flow["websocket_enabled"] is False
    assert flow["order_intent_submitted"] is False


def test_q31s_doc_and_transport_modules_preserve_no_side_effect_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "websocket_direction_preferred=bidirectional" in text
    assert "human_and_autotrade_share_order_intent_gateway=true" in text
    assert "order_logic_responsibility=autotrade.execution.OrderIntent_gateway" in text
    assert "not_sending_order_to_broker=true" in text
    forbidden = (
        "import streamlit",
        "from streamlit",
        "websocket.",
        "sse.",
        "send_to_broker(",
        "submit_order(",
        "append_ledger(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "run_prediction(",
        "invoke_classifier(",
        "st.write(",
        "st.metric(",
        "st.caption(",
        "D:" + chr(92),
        "E:" + chr(92),
    )
    for path in TRANSPORT_DIR.glob("*.py"):
        body = path.read_text(encoding="utf-8-sig")
        assert len(body.splitlines()) <= 220, f"transport file too large: {path}"
        for token in forbidden:
            assert token not in body, f"forbidden token {token!r} found in {path}"
