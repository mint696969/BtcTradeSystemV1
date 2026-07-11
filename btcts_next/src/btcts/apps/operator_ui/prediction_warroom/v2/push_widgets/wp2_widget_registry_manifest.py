# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp2_widget_registry_manifest.py
# desc: WP2 WarRoom push-widget registry and manifest. Stable manifest-driven widget catalog; no socket, page mount, send, broker, order, or prediction.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags

WP2_VERSION = "warroom.manual_trade_support.push_widgets.wp2.registry_manifest.v1"


@dataclass(frozen=True)
class PushWidgetManifest:
    widget_id: str
    display_name: str
    widget_kind: str
    topic_keys: tuple[str, ...]
    reducer_key: str
    render_adapter_key: str
    layout_zone: str
    default_order: int
    stale_after_ms: int = 5000
    heartbeat_required: bool = True
    read_only: bool = True
    mount_enabled: bool = True
    extension_tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["topic_keys"] = list(self.topic_keys)
        data["extension_tags"] = list(self.extension_tags)
        return data


@dataclass(frozen=True)
class PushWidgetTopicBinding:
    widget_id: str
    topic_key: str
    topic_pattern: str
    message_kind: str = "market_push_metadata"
    receive_only: bool = True
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_MANIFESTS: tuple[PushWidgetManifest, ...] = (
    PushWidgetManifest("market_depth_widget", "Market depth", "market_microstructure", ("market.depth",), "market_depth_reducer", "market_depth_render_packet", "core_grid", 10, extension_tags=("book", "depth")),
    PushWidgetManifest("recent_trades_widget", "Recent trades", "market_flow", ("market.trades",), "recent_trades_reducer", "recent_trades_render_packet", "core_grid", 20, extension_tags=("trades", "flow")),
    PushWidgetManifest("spread_liquidity_widget", "Spread / liquidity", "liquidity", ("market.spread", "market.liquidity"), "spread_liquidity_reducer", "spread_liquidity_render_packet", "core_grid", 30, extension_tags=("spread", "liquidity")),
    PushWidgetManifest("receiver_lifecycle_widget", "Receiver health", "receiver_lifecycle", ("receiver.lifecycle",), "receiver_lifecycle_reducer", "receiver_lifecycle_render_packet", "status_grid", 40, extension_tags=("health", "lifecycle")),
    PushWidgetManifest("summary_alerts_widget", "Summary / alerts", "summary_alerts", ("warroom.summary", "warroom.alerts"), "summary_alerts_reducer", "summary_alerts_render_packet", "status_grid", 50, extension_tags=("summary", "alerts")),
    PushWidgetManifest("market_regime_prediction_widget", "Market regime prediction", "prediction_family", ("prediction.family.market_regime",), "prediction_family_read_model_reducer", "market_regime_prediction_render_packet", "prediction_grid", 60, stale_after_ms=15000, mount_enabled=False, extension_tags=("prediction", "market_regime", "read_only", "unmounted")),
)

DEFAULT_BINDINGS: tuple[PushWidgetTopicBinding, ...] = (
    PushWidgetTopicBinding("market_depth_widget", "market.depth", "market.depth.BTC_JPY"),
    PushWidgetTopicBinding("recent_trades_widget", "market.trades", "market.trades.BTC_JPY"),
    PushWidgetTopicBinding("spread_liquidity_widget", "market.spread", "market.spread.BTC_JPY"),
    PushWidgetTopicBinding("spread_liquidity_widget", "market.liquidity", "market.liquidity.BTC_JPY"),
    PushWidgetTopicBinding("receiver_lifecycle_widget", "receiver.lifecycle", "receiver.lifecycle"),
    PushWidgetTopicBinding("summary_alerts_widget", "warroom.summary", "warroom.summary"),
    PushWidgetTopicBinding("summary_alerts_widget", "warroom.alerts", "warroom.alerts"),
    PushWidgetTopicBinding("market_regime_prediction_widget", "prediction.family.market_regime", "prediction.family.market_regime", message_kind="prediction_family_read_model"),
)


def _duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for value in values:
        if value in seen:
            dup.add(value)
        seen.add(value)
    return sorted(dup)


def validate_registry_manifest(manifests: Iterable[PushWidgetManifest], bindings: Iterable[PushWidgetTopicBinding]) -> dict[str, Any]:
    manifest_list = list(manifests)
    binding_list = list(bindings)
    widget_ids = [item.widget_id for item in manifest_list]
    binding_widget_ids = [item.widget_id for item in binding_list]
    topic_keys = [item.topic_key for item in binding_list]
    manifest_ids = set(widget_ids)
    errors: list[str] = []
    for duplicate in _duplicates(widget_ids):
        errors.append(f"duplicate_widget_id:{duplicate}")
    for duplicate in _duplicates(topic_keys):
        errors.append(f"duplicate_topic_key:{duplicate}")
    for widget_id in binding_widget_ids:
        if widget_id not in manifest_ids:
            errors.append(f"binding_without_manifest:{widget_id}")
    for manifest in manifest_list:
        if not manifest.read_only:
            errors.append(f"manifest_not_read_only:{manifest.widget_id}")
        if not manifest.topic_keys:
            errors.append(f"manifest_missing_topic:{manifest.widget_id}")
    for binding in binding_list:
        if not binding.receive_only:
            errors.append(f"binding_not_receive_only:{binding.widget_id}:{binding.topic_key}")
    return {"ok": not errors, "errors": errors, "widget_count": len(manifest_list), "topic_binding_count": len(binding_list)}


def build_wp2_registry_manifest_packet(
    manifests: Iterable[PushWidgetManifest] = DEFAULT_MANIFESTS,
    bindings: Iterable[PushWidgetTopicBinding] = DEFAULT_BINDINGS,
) -> dict[str, Any]:
    manifest_list = tuple(manifests)
    binding_list = tuple(bindings)
    validation = validate_registry_manifest(manifest_list, binding_list)
    routes = {binding.topic_key: binding.widget_id for binding in binding_list}
    packet = {
        "ok": bool(validation["ok"]),
        "packet_kind": "warroom_push_widget_wp2_registry_manifest_packet",
        "version": WP2_VERSION,
        "wp2_completed": bool(validation["ok"]),
        "next_checkpoint": "WP3_Per_widget_state_store" if validation["ok"] else "WP2_registry_manifest_fix",
        "primary_goal": "WarRoom_manual_trade_support_completion",
        "first_priority": "independent_WebSocket_push_auto_updating_widgets",
        "widget_registry_manifest_ready": bool(validation["ok"]),
        "stable_registry_ready": bool(validation["ok"]),
        "manifest_driven_widgets_ready": bool(validation["ok"]),
        "topic_bindings_ready": bool(validation["ok"]),
        "future_widget_extension_metadata_ready": bool(validation["ok"]),
        "registry_key": "warroom_push_widget_registry.v1",
        "manifests": [item.to_dict() for item in sorted(manifest_list, key=lambda item: item.default_order)],
        "topic_bindings": [item.to_dict() for item in binding_list],
        "routes_by_topic": routes,
        "layout_zones": sorted({item.layout_zone for item in manifest_list}),
        "validation": validation,
    }
    packet.update(build_wp1_no_send_flags())
    return packet
