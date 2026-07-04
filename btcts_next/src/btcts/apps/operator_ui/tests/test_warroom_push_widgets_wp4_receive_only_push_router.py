# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp4_receive_only_push_router.py
# desc: WP4 verifies receive-only push router routes messages to per-widget state store without send/broker/page side effects.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp3_per_widget_state_store import build_initial_widget_state_store  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp4_receive_only_push_router import build_wp4_receive_only_push_router_packet, route_receive_only_push_batch, route_receive_only_push_message  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP4_RECEIVE_ONLY_PUSH_ROUTER_2026-07-05.md"


def test_wp4_packet_marks_receive_only_router_ready_and_safe() -> None:
    packet = build_wp4_receive_only_push_router_packet()
    assert packet["wp4_completed"] is True
    assert packet["next_checkpoint"] == "WP5_Topic_routing_and_subscription_plan"
    assert packet["receive_only_push_router_ready"] is True
    assert packet["topic_to_widget_routing_ready"] is True
    assert packet["router_to_state_store_ready"] is True
    assert packet["sample_widget_sequence"] == 1
    assert packet["sample_other_widget_sequence"] == 0
    assert packet["websocket_opened"] is False
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert packet["order_intent_submitted"] is False
    assert "wp4_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp4_routes_batch_to_independent_widgets() -> None:
    store = build_initial_widget_state_store()
    updated = route_receive_only_push_batch(store, [
        {"topic_key": "market.depth", "value": {"bid": 1}, "received_at_ms": 100, "sequence": 1},
        {"topic_key": "market.trades", "value": {"last": 2}, "received_at_ms": 101, "sequence": 1},
    ])
    assert updated["widgets"]["market_depth_widget"]["sequence"] == 1
    assert updated["widgets"]["recent_trades_widget"]["sequence"] == 1
    assert updated["widgets"]["spread_liquidity_widget"]["sequence"] == 0
    assert len(updated["router_audit"]) == 2


def test_wp4_rejects_unsafe_message_flags_without_mutating_widgets() -> None:
    store = build_initial_widget_state_store()
    updated = route_receive_only_push_message(store, {"topic_key": "market.depth", "value": {"bid": 1}, "received_at_ms": 100, "send_requested": True})
    assert updated["widgets"] == store["widgets"]
    assert updated["router_audit"][-1]["reason"] == "unsafe_message_flags"
    assert "send_requested" in updated["router_audit"][-1]["blocked"]
