# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp5_topic_routing_subscription_plan.py
# desc: WP5 WarRoom topic routing and subscription plan. Metadata-only subscribe intent; no socket open, subscribe invocation, send, broker, order, page mount, or prediction.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp2_widget_registry_manifest import DEFAULT_BINDINGS, DEFAULT_MANIFESTS, PushWidgetTopicBinding

WP5_VERSION = "warroom.manual_trade_support.push_widgets.wp5.topic_routing_subscription_plan.v1"


@dataclass(frozen=True)
class TopicRoutePlan:
    topic_key: str
    topic_pattern: str
    widget_id: str
    channel_group: str
    priority: int
    required: bool = True
    receive_only: bool = True
    subscribe_intent_only: bool = True
    subscribe_invoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SubscriptionPlan:
    plan_key: str
    routes: tuple[TopicRoutePlan, ...]
    default_symbol: str = "BTC_JPY"
    receive_only: bool = True
    metadata_only: bool = True
    websocket_opened: bool = False
    subscribe_invoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_key": self.plan_key,
            "default_symbol": self.default_symbol,
            "receive_only": self.receive_only,
            "metadata_only": self.metadata_only,
            "websocket_opened": self.websocket_opened,
            "subscribe_invoked": self.subscribe_invoked,
            "routes": [route.to_dict() for route in self.routes],
            "topic_keys": [route.topic_key for route in self.routes],
            "channel_groups": sorted({route.channel_group for route in self.routes}),
            "route_count": len(self.routes),
        }


def _group_for(topic_key: str) -> str:
    if topic_key.startswith("market."):
        return "market"
    if topic_key.startswith("receiver."):
        return "receiver"
    if topic_key.startswith("warroom."):
        return "warroom"
    if topic_key.startswith("prediction.family."):
        return "prediction"
    return "unknown"


def build_topic_route_plans(bindings: Iterable[PushWidgetTopicBinding] = DEFAULT_BINDINGS) -> tuple[TopicRoutePlan, ...]:
    routes: list[TopicRoutePlan] = []
    for index, binding in enumerate(bindings, start=1):
        routes.append(TopicRoutePlan(topic_key=binding.topic_key, topic_pattern=binding.topic_pattern, widget_id=binding.widget_id, channel_group=_group_for(binding.topic_key), priority=index, required=binding.required, receive_only=binding.receive_only))
    return tuple(routes)


def validate_subscription_plan(plan: SubscriptionPlan) -> dict[str, Any]:
    manifest_ids = {manifest.widget_id for manifest in DEFAULT_MANIFESTS}
    topic_keys = [route.topic_key for route in plan.routes]
    errors: list[str] = []
    if not plan.receive_only:
        errors.append("plan_not_receive_only")
    if not plan.metadata_only:
        errors.append("plan_not_metadata_only")
    if plan.websocket_opened:
        errors.append("websocket_opened")
    if plan.subscribe_invoked:
        errors.append("subscribe_invoked")
    if len(topic_keys) != len(set(topic_keys)):
        errors.append("duplicate_topic_key")
    for route in plan.routes:
        if route.widget_id not in manifest_ids:
            errors.append(f"route_widget_missing:{route.widget_id}")
        if not route.receive_only:
            errors.append(f"route_not_receive_only:{route.topic_key}")
        if not route.subscribe_intent_only:
            errors.append(f"route_not_intent_only:{route.topic_key}")
        if route.subscribe_invoked:
            errors.append(f"route_subscribe_invoked:{route.topic_key}")
        if route.channel_group == "unknown":
            errors.append(f"unknown_channel_group:{route.topic_key}")
    return {"ok": not errors, "errors": errors, "route_count": len(plan.routes), "channel_groups": sorted({route.channel_group for route in plan.routes})}


def build_wp5_subscription_plan_packet() -> dict[str, Any]:
    routes = build_topic_route_plans()
    plan = SubscriptionPlan(plan_key="warroom_push_widget_subscription_plan.v1", routes=routes)
    validation = validate_subscription_plan(plan)
    packet = {
        "ok": bool(validation["ok"]),
        "packet_kind": "warroom_push_widget_wp5_topic_routing_subscription_plan_packet",
        "version": WP5_VERSION,
        "wp5_completed": bool(validation["ok"]),
        "next_checkpoint": "WP6_Independent_widget_update_pipeline" if validation["ok"] else "WP5_topic_plan_fix",
        "topic_namespace_ready": bool(validation["ok"]),
        "topic_route_plan_ready": bool(validation["ok"]),
        "subscription_plan_ready": bool(validation["ok"]),
        "receive_only_subscription_intent_ready": bool(validation["ok"]),
        "future_topic_addition_ready": bool(validation["ok"]),
        "route_count": validation["route_count"],
        "channel_groups": validation["channel_groups"],
        "plan": plan.to_dict(),
        "validation": validation,
    }
    packet.update(build_wp1_no_send_flags())
    packet["websocket_opened"] = False
    packet["websocket_subscribe_invoked"] = False
    packet["websocket_send_enabled"] = False
    return packet
