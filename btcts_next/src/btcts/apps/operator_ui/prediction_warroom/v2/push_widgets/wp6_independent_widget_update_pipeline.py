# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp6_independent_widget_update_pipeline.py
# desc: WP6 independent widget update pipeline. Push message to router, per-widget state, and render packets without page mount, socket, send, broker, order, or prediction.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp2_widget_registry_manifest import DEFAULT_MANIFESTS
from .wp3_per_widget_state_store import build_initial_widget_state_store
from .wp4_receive_only_push_router import route_receive_only_push_batch
from .wp5_topic_routing_subscription_plan import build_wp5_subscription_plan_packet

WP6_VERSION = "warroom.manual_trade_support.push_widgets.wp6.independent_widget_update_pipeline.v1"


@dataclass(frozen=True)
class WidgetRenderPacket:
    widget_id: str
    title: str
    render_adapter_key: str
    layout_zone: str
    sequence: int
    last_update_ms: int
    rows: tuple[Mapping[str, Any], ...]
    freshness_label: str = "updated"
    read_only: bool = True
    controls_added: bool = False
    raw_payload_rendered: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["rows"] = [dict(row) for row in self.rows]
        return data


def _manifest_by_id() -> dict[str, Any]:
    return {item.widget_id: item for item in DEFAULT_MANIFESTS}


def _rows_from_widget_state(widget: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for topic_key, snapshot in sorted(dict(widget.get("snapshots", {})).items()):
        value = dict(snapshot.get("value", {})) if isinstance(snapshot, Mapping) else {}
        rows.append({
            "topic_key": topic_key,
            "sequence": int(snapshot.get("sequence", 0)) if isinstance(snapshot, Mapping) else 0,
            "updated_at_ms": int(snapshot.get("updated_at_ms", 0)) if isinstance(snapshot, Mapping) else 0,
            "value": value,
            "raw_payload_rendered": False,
        })
    return tuple(rows)


def build_render_packets_from_store(store: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    manifests = _manifest_by_id()
    packets: dict[str, dict[str, Any]] = {}
    for widget_id, widget in dict(store.get("widgets", {})).items():
        manifest = manifests[widget_id]
        packet = WidgetRenderPacket(
            widget_id=widget_id,
            title=manifest.display_name,
            render_adapter_key=manifest.render_adapter_key,
            layout_zone=manifest.layout_zone,
            sequence=int(widget.get("sequence", 0)),
            last_update_ms=int(widget.get("last_update_ms", 0)),
            rows=_rows_from_widget_state(widget),
            freshness_label="updated" if int(widget.get("sequence", 0)) > 0 else "not_started",
        ).to_dict()
        packets[widget_id] = packet
    return packets


def run_independent_widget_update_pipeline(messages: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    store = build_initial_widget_state_store()
    plan = build_wp5_subscription_plan_packet()
    routed_store = route_receive_only_push_batch(store, messages)
    render_packets = build_render_packets_from_store(routed_store)
    updated_widget_ids = sorted([widget_id for widget_id, packet in render_packets.items() if int(packet["sequence"]) > 0])
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp6_independent_update_pipeline_packet",
        "version": WP6_VERSION,
        "wp6_completed": True,
        "next_checkpoint": "WP7_Per_widget_freshness_stale_heartbeat_error",
        "independent_widget_update_pipeline_ready": True,
        "push_to_router_to_state_to_render_ready": True,
        "render_packet_generation_ready": True,
        "per_widget_render_packet_ready": True,
        "non_blocking_widget_update_ready": True,
        "registry_driven_render_ready": True,
        "updated_widget_ids": updated_widget_ids,
        "updated_widget_count": len(updated_widget_ids),
        "render_packets": render_packets,
        "store": routed_store,
        "subscription_plan_key": plan["plan"]["plan_key"],
    }
    packet.update(build_wp1_no_send_flags())
    packet["warroom_page_mount_added"] = False
    packet["websocket_opened"] = False
    packet["websocket_receive_loop_started"] = False
    packet["websocket_send_enabled"] = False
    return packet


def build_wp6_independent_widget_update_pipeline_packet() -> dict[str, Any]:
    return run_independent_widget_update_pipeline([
        {"topic_key": "market.depth", "value": {"best_bid": 100, "best_ask": 101}, "received_at_ms": 1000, "sequence": 1},
        {"topic_key": "market.trades", "value": {"last_price": 101}, "received_at_ms": 1001, "sequence": 1},
    ])
