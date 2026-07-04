# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp3_per_widget_state_store.py
# desc: WP3 WarRoom per-widget state store. Independent immutable updates; no socket, page mount, send, broker, order, or prediction.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp2_widget_registry_manifest import build_wp2_registry_manifest_packet

WP3_VERSION = "warroom.manual_trade_support.push_widgets.wp3.per_widget_state_store.v1"
BUFFER_LIMIT = 32


@dataclass(frozen=True)
class WidgetStateSnapshot:
    widget_id: str
    topic_key: str
    sequence: int = 0
    updated_at_ms: int = 0
    value: Mapping[str, Any] | None = None
    stale: bool = False
    error: bool = False
    heartbeat_ok: bool = True
    raw_payload_retained: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["value"] = dict(self.value or {})
        return data


def _empty_widget_state(widget_id: str, topic_keys: list[str]) -> dict[str, Any]:
    return {
        "widget_id": widget_id,
        "sequence": 0,
        "last_update_ms": 0,
        "topic_keys": list(topic_keys),
        "snapshots": {key: WidgetStateSnapshot(widget_id, key).to_dict() for key in topic_keys},
        "buffer": [],
        "stale": False,
        "error": False,
        "heartbeat_ok": True,
        "isolated": True,
        "bounded_buffer_limit": BUFFER_LIMIT,
    }


def build_initial_widget_state_store() -> dict[str, Any]:
    registry = build_wp2_registry_manifest_packet()
    widgets = {item["widget_id"]: _empty_widget_state(item["widget_id"], item["topic_keys"]) for item in registry["manifests"]}
    return {
        "ok": True,
        "store_version": WP3_VERSION,
        "wp3_state_store_ready": True,
        "registry_key": registry["registry_key"],
        "routes_by_topic": dict(registry["routes_by_topic"]),
        "widgets": widgets,
        "unknown_topic_errors": [],
        "state_isolation_enforced": True,
        "immutable_update_required": True,
        "bounded_buffers_ready": True,
        "raw_payload_retained": False,
    }


def _sanitize_value(value: Mapping[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, item in value.items():
        if key in {"raw", "raw_payload", "endpoint", "token", "callable"}:
            continue
        if isinstance(item, (str, int, float, bool)) or item is None:
            clean[str(key)] = item
        elif isinstance(item, (list, tuple)):
            clean[str(key)] = list(item[:20])
        elif isinstance(item, Mapping):
            clean[str(key)] = {str(k): v for k, v in list(item.items())[:20] if isinstance(v, (str, int, float, bool)) or v is None}
        else:
            clean[str(key)] = repr(item)
    return clean


def apply_widget_state_update(store: Mapping[str, Any], *, topic_key: str, value: Mapping[str, Any], updated_at_ms: int, sequence: int | None = None) -> dict[str, Any]:
    routes = dict(store.get("routes_by_topic", {}))
    widgets = {key: dict(item) for key, item in dict(store.get("widgets", {})).items()}
    errors = list(store.get("unknown_topic_errors", []))
    if topic_key not in routes:
        errors.append({"topic_key": topic_key, "reason": "unknown_topic"})
        new_store = dict(store)
        new_store["widgets"] = widgets
        new_store["unknown_topic_errors"] = errors
        return new_store
    widget_id = routes[topic_key]
    widget = dict(widgets[widget_id])
    next_sequence = int(sequence if sequence is not None else widget.get("sequence", 0) + 1)
    snapshot = WidgetStateSnapshot(widget_id=widget_id, topic_key=topic_key, sequence=next_sequence, updated_at_ms=int(updated_at_ms), value=_sanitize_value(value)).to_dict()
    snapshots = dict(widget.get("snapshots", {}))
    snapshots[topic_key] = snapshot
    buffer = list(widget.get("buffer", []))
    buffer.append({"topic_key": topic_key, "sequence": next_sequence, "updated_at_ms": int(updated_at_ms)})
    widget.update({"sequence": next_sequence, "last_update_ms": int(updated_at_ms), "snapshots": snapshots, "buffer": buffer[-BUFFER_LIMIT:], "stale": False, "error": False, "heartbeat_ok": True})
    widgets[widget_id] = widget
    new_store = dict(store)
    new_store["widgets"] = widgets
    new_store["unknown_topic_errors"] = errors
    return new_store


def build_wp3_state_store_packet() -> dict[str, Any]:
    store = build_initial_widget_state_store()
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp3_state_store_packet",
        "version": WP3_VERSION,
        "wp3_completed": True,
        "next_checkpoint": "WP4_Receive_only_WebSocket_push_router",
        "per_widget_state_store_ready": True,
        "independent_widget_state_ready": True,
        "immutable_update_ready": True,
        "bounded_buffers_ready": True,
        "unknown_topic_guard_ready": True,
        "raw_payload_drop_ready": True,
        "widget_count": len(store["widgets"]),
        "store": store,
    }
    packet.update(build_wp1_no_send_flags())
    return packet
