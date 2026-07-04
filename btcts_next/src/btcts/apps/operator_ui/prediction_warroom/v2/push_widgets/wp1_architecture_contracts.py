# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp1_architecture_contracts.py
# desc: WP1 WarRoom push-widget architecture contracts. No socket open, no page mount, no send, no broker/order/prediction.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

WP1_VERSION = "warroom.manual_trade_support.push_widgets.wp1.architecture.v1"


@dataclass(frozen=True)
class WidgetManifestContract:
    widget_id: str
    display_name: str
    widget_kind: str
    topic_keys: tuple[str, ...]
    reducer_key: str
    render_adapter_key: str
    read_only: bool = True
    future_extension_point: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["topic_keys"] = list(self.topic_keys)
        return data


@dataclass(frozen=True)
class WidgetTopicBindingContract:
    widget_id: str
    topic_key: str
    topic_pattern: str
    receive_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WidgetStateSnapshotContract:
    widget_id: str
    topic_key: str
    sequence: int = 0
    value: Mapping[str, Any] | None = None
    stale: bool = False
    error: bool = False
    heartbeat_ok: bool = True
    raw_payload_retained: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"widget_id": self.widget_id, "topic_key": self.topic_key, "sequence": self.sequence, "value": dict(self.value or {}), "stale": self.stale, "error": self.error, "heartbeat_ok": self.heartbeat_ok, "raw_payload_retained": self.raw_payload_retained}


def build_wp1_no_send_flags() -> dict[str, Any]:
    return {
        "architecture_only": True,
        "manual_trade_support_read_only": True,
        "warroom_page_modified": False,
        "warroom_page_mount_added": False,
        "websocket_imported": False,
        "websocket_opened": False,
        "websocket_receive_loop_started": False,
        "websocket_send_enabled": False,
        "websocket_subscribe_invoked": False,
        "external_network_used": False,
        "raw_payload_rendered": False,
        "endpoint_value_rendered": False,
        "token_value_rendered": False,
        "callable_value_rendered": False,
        "secret_exposure": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "auto_trading_enabled": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def build_wp1_reference_architecture_packet() -> dict[str, Any]:
    manifests = [
        WidgetManifestContract("market_depth_widget", "Market depth", "market_microstructure", ("market.depth",), "market_depth_reducer", "market_depth_render_packet").to_dict(),
        WidgetManifestContract("recent_trades_widget", "Recent trades", "market_flow", ("market.trades",), "recent_trades_reducer", "recent_trades_render_packet").to_dict(),
    ]
    bindings = [
        WidgetTopicBindingContract("market_depth_widget", "market.depth", "market.depth.BTC_JPY").to_dict(),
        WidgetTopicBindingContract("recent_trades_widget", "market.trades", "market.trades.BTC_JPY").to_dict(),
    ]
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp1_architecture_packet",
        "version": WP1_VERSION,
        "wp1_completed": True,
        "next_checkpoint": "WP2_Widget_registry_and_manifest",
        "primary_goal": "WarRoom_manual_trade_support_completion",
        "first_priority": "independent_WebSocket_push_auto_updating_widgets",
        "widget_registry_ready": True,
        "widget_manifest_contract_ready": True,
        "topic_binding_contract_ready": True,
        "per_widget_state_contract_ready": True,
        "widget_update_reducer_contract_ready": True,
        "widget_render_packet_contract_ready": True,
        "widget_health_status_contract_ready": True,
        "push_router_contract_ready": True,
        "state_isolation_contract_ready": True,
        "future_widget_extension_contract_seeded": True,
        "registry": {"registry_key": "warroom_push_widget_registry", "manifests": manifests, "topic_bindings": bindings, "widget_count": len(manifests), "topic_binding_count": len(bindings)},
        "router": {"router_key": "warroom_receive_only_push_router", "receive_only": True, "routes_by_topic": {item["topic_key"]: item["widget_id"] for item in bindings}, "send_enabled": False},
        "state_snapshot_contract": WidgetStateSnapshotContract("market_depth_widget", "market.depth").to_dict(),
    }
    packet.update(build_wp1_no_send_flags())
    return packet


def assert_wp1_no_send(packet: Mapping[str, Any]) -> dict[str, Any]:
    blocked = [key for key, expected in build_wp1_no_send_flags().items() if expected is False and bool(packet.get(key))]
    return {"ok": not blocked, "blocked": blocked}
