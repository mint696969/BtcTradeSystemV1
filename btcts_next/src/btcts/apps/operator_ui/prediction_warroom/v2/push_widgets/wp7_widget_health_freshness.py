# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp7_widget_health_freshness.py
# desc: WP7 per-widget freshness/stale/heartbeat/error health layer. No page mount, socket, send, broker, order, ledger, or prediction.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp2_widget_registry_manifest import DEFAULT_MANIFESTS
from .wp6_independent_widget_update_pipeline import run_independent_widget_update_pipeline

WP7_VERSION = "warroom.manual_trade_support.push_widgets.wp7.widget_health_freshness.v1"


@dataclass(frozen=True)
class WidgetHealthPacket:
    widget_id: str
    state: str
    last_update_ms: int
    age_ms: int | None
    stale: bool
    slow: bool
    error: bool
    heartbeat_ok: bool
    last_sequence: int
    stale_after_ms: int
    slow_after_ms: int
    read_only: bool = True
    runtime_action_requested: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _manifest_by_id() -> dict[str, Any]:
    return {manifest.widget_id: manifest for manifest in DEFAULT_MANIFESTS}


def _state_for(sequence: int, age_ms: int | None, stale: bool, slow: bool, error: bool, heartbeat_ok: bool) -> str:
    if error:
        return "error"
    if stale:
        return "stale"
    if not heartbeat_ok:
        return "heartbeat_missing"
    if slow:
        return "slow"
    if sequence > 0:
        return "live"
    return "not_started"


def build_widget_health_packets(render_packets: Mapping[str, Mapping[str, Any]], *, now_ms: int, errors_by_widget: Mapping[str, str] | None = None) -> dict[str, dict[str, Any]]:
    manifests = _manifest_by_id()
    errors = dict(errors_by_widget or {})
    health: dict[str, dict[str, Any]] = {}
    for widget_id, render_packet in dict(render_packets).items():
        manifest = manifests[widget_id]
        sequence = int(render_packet.get("sequence", 0))
        last_update_ms = int(render_packet.get("last_update_ms", 0))
        age_ms = None if sequence <= 0 or last_update_ms <= 0 else max(0, int(now_ms) - last_update_ms)
        stale = bool(age_ms is not None and age_ms > int(manifest.stale_after_ms))
        slow_after_ms = max(1, int(manifest.stale_after_ms // 2))
        slow = bool(age_ms is not None and age_ms > slow_after_ms and not stale)
        error = widget_id in errors
        heartbeat_ok = not bool(manifest.heartbeat_required and stale)
        state = _state_for(sequence, age_ms, stale, slow, error, heartbeat_ok)
        health[widget_id] = WidgetHealthPacket(
            widget_id=widget_id,
            state=state,
            last_update_ms=last_update_ms,
            age_ms=age_ms,
            stale=stale,
            slow=slow,
            error=error,
            heartbeat_ok=heartbeat_ok,
            last_sequence=sequence,
            stale_after_ms=int(manifest.stale_after_ms),
            slow_after_ms=slow_after_ms,
        ).to_dict()
        if error:
            health[widget_id]["error_reason"] = errors[widget_id]
    return health


def attach_widget_health(render_packets: Mapping[str, Mapping[str, Any]], health_packets: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    enriched: dict[str, dict[str, Any]] = {}
    for widget_id, packet in dict(render_packets).items():
        next_packet = dict(packet)
        health = dict(health_packets[widget_id])
        next_packet["health"] = health
        next_packet["freshness_label"] = str(health["state"])
        next_packet["stale"] = bool(health["stale"])
        next_packet["error"] = bool(health["error"])
        next_packet["heartbeat_ok"] = bool(health["heartbeat_ok"])
        next_packet["controls_added"] = False
        next_packet["read_only"] = True
        enriched[widget_id] = next_packet
    return enriched


def run_widget_health_freshness_pipeline(messages: list[Mapping[str, Any]], *, now_ms: int, errors_by_widget: Mapping[str, str] | None = None) -> dict[str, Any]:
    base = run_independent_widget_update_pipeline(messages)
    health = build_widget_health_packets(base["render_packets"], now_ms=now_ms, errors_by_widget=errors_by_widget)
    enriched = attach_widget_health(base["render_packets"], health)
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp7_health_freshness_packet",
        "version": WP7_VERSION,
        "wp7_completed": True,
        "next_checkpoint": "WP8_First_real_push_widget_set",
        "per_widget_freshness_ready": True,
        "per_widget_stale_ready": True,
        "per_widget_heartbeat_ready": True,
        "per_widget_error_ready": True,
        "per_widget_slow_ready": True,
        "health_enriched_render_packets_ready": True,
        "health_isolation_ready": True,
        "health_packets": health,
        "render_packets": enriched,
        "updated_widget_ids": base["updated_widget_ids"],
    }
    packet.update(build_wp1_no_send_flags())
    packet["warroom_page_mount_added"] = False
    packet["websocket_opened"] = False
    packet["websocket_receive_loop_started"] = False
    packet["websocket_send_enabled"] = False
    return packet


def build_wp7_widget_health_freshness_packet() -> dict[str, Any]:
    return run_widget_health_freshness_pipeline([
        {"topic_key": "market.depth", "value": {"best_bid": 100}, "received_at_ms": 1000, "sequence": 1},
        {"topic_key": "market.trades", "value": {"last_price": 101}, "received_at_ms": 5900, "sequence": 1},
    ], now_ms=6200)
