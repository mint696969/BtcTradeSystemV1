# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp5_topic_routing_subscription_plan.py
# desc: WP5 verifies metadata-only topic routing and subscription plan with no socket/subscribe/send side effects.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp5_topic_routing_subscription_plan import SubscriptionPlan, build_topic_route_plans, build_wp5_subscription_plan_packet, validate_subscription_plan  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP5_TOPIC_ROUTING_SUBSCRIPTION_PLAN_2026-07-05.md"


def test_wp5_packet_marks_topic_plan_ready_and_safe() -> None:
    packet = build_wp5_subscription_plan_packet()
    assert packet["wp5_completed"] is True
    assert packet["next_checkpoint"] == "WP6_Independent_widget_update_pipeline"
    assert packet["topic_namespace_ready"] is True
    assert packet["topic_route_plan_ready"] is True
    assert packet["subscription_plan_ready"] is True
    assert packet["receive_only_subscription_intent_ready"] is True
    assert packet["future_topic_addition_ready"] is True
    assert packet["route_count"] == 7
    assert set(packet["channel_groups"]) == {"market", "receiver", "warroom"}
    assert packet["plan"]["subscribe_invoked"] is False
    assert packet["websocket_opened"] is False
    assert packet["websocket_subscribe_invoked"] is False
    assert packet["websocket_send_enabled"] is False
    assert packet["broker_send_enabled"] is False
    assert "wp5_completed=true" in DOC.read_text(encoding="utf-8-sig")


def test_wp5_routes_are_receive_only_and_intent_only() -> None:
    routes = build_topic_route_plans()
    assert len(routes) == 7
    assert all(route.receive_only for route in routes)
    assert all(route.subscribe_intent_only for route in routes)
    assert not any(route.subscribe_invoked for route in routes)
    assert {route.topic_key for route in routes} >= {"market.depth", "market.trades", "warroom.alerts"}


def test_wp5_validation_rejects_subscribe_invocation() -> None:
    routes = build_topic_route_plans()
    unsafe = SubscriptionPlan("unsafe", routes=routes, subscribe_invoked=True)
    validation = validate_subscription_plan(unsafe)
    assert validation["ok"] is False
    assert "subscribe_invoked" in validation["errors"]
