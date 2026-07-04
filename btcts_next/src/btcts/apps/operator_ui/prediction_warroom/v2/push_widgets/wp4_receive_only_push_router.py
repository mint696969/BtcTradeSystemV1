# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp4_receive_only_push_router.py
# desc: WP4 receive-only push router. Routes push-shaped messages to per-widget state store without opening sockets, sending, broker, order, page mount, or prediction.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp3_per_widget_state_store import apply_widget_state_update, build_initial_widget_state_store

WP4_VERSION = "warroom.manual_trade_support.push_widgets.wp4.receive_only_push_router.v1"
UNSAFE_MESSAGE_FLAGS = (
    "send_requested",
    "publish_requested",
    "broker_send_requested",
    "order_requested",
    "ledger_append_requested",
    "prediction_requested",
    "classifier_requested",
)


@dataclass(frozen=True)
class ReceiveOnlyPushMessage:
    topic_key: str
    value: Mapping[str, Any]
    received_at_ms: int
    sequence: int | None = None
    message_kind: str = "market_push_metadata"
    receive_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["value"] = dict(self.value)
        return data


def _blocked_message_flags(message: Mapping[str, Any]) -> list[str]:
    return [key for key in UNSAFE_MESSAGE_FLAGS if bool(message.get(key))]


def route_receive_only_push_message(store: Mapping[str, Any], message: Mapping[str, Any]) -> dict[str, Any]:
    blocked = _blocked_message_flags(message)
    if blocked:
        new_store = dict(store)
        audit = list(new_store.get("router_audit", []))
        audit.append({"routed": False, "reason": "unsafe_message_flags", "blocked": blocked})
        new_store["router_audit"] = audit
        return new_store
    topic_key = str(message.get("topic_key", ""))
    value = message.get("value", {})
    if not isinstance(value, Mapping):
        value = {"value": value}
    updated = apply_widget_state_update(
        store,
        topic_key=topic_key,
        value=value,
        updated_at_ms=int(message.get("received_at_ms", 0)),
        sequence=message.get("sequence"),
    )
    audit = list(updated.get("router_audit", []))
    audit.append({"routed": topic_key in dict(store.get("routes_by_topic", {})), "topic_key": topic_key, "receive_only": True})
    updated["router_audit"] = audit[-64:]
    updated["receive_only_router_used"] = True
    updated["router_send_enabled"] = False
    return updated


def route_receive_only_push_batch(store: Mapping[str, Any], messages: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    current: Mapping[str, Any] = store
    for message in messages:
        current = route_receive_only_push_message(current, message)
    return dict(current)


def build_wp4_receive_only_push_router_packet() -> dict[str, Any]:
    store = build_initial_widget_state_store()
    sample = ReceiveOnlyPushMessage(topic_key="market.depth", value={"best_bid": 100, "best_ask": 101}, received_at_ms=1000, sequence=1).to_dict()
    routed = route_receive_only_push_message(store, sample)
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp4_receive_only_push_router_packet",
        "version": WP4_VERSION,
        "wp4_completed": True,
        "next_checkpoint": "WP5_Topic_routing_and_subscription_plan",
        "receive_only_push_router_ready": True,
        "push_message_contract_ready": True,
        "topic_to_widget_routing_ready": True,
        "router_to_state_store_ready": True,
        "unsafe_message_flag_guard_ready": True,
        "unknown_topic_passthrough_guard_ready": True,
        "router_audit_ready": True,
        "sample_widget_sequence": routed["widgets"]["market_depth_widget"]["sequence"],
        "sample_other_widget_sequence": routed["widgets"]["recent_trades_widget"]["sequence"],
        "routed_store": routed,
    }
    packet.update(build_wp1_no_send_flags())
    packet["websocket_receive_loop_started"] = False
    packet["websocket_opened"] = False
    packet["websocket_send_enabled"] = False
    return packet
