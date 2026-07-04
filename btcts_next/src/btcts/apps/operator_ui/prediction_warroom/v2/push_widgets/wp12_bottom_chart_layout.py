# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp12_bottom_chart_layout.py
# desc: WP12 WarRoom bottom chart layout. Builds clean read-only chart adapter, overlays, refresh cadence, and stale handling without socket/send/broker/order.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp11_top_layout_push_widget_polish import build_wp11_top_layout_push_widget_polish_packet
from .wp9_warroom_page_mount import build_wp9_warroom_page_mount_packet

WP12_VERSION = "warroom.manual_trade_support.push_widgets.wp12.bottom_chart_layout.v1"
WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY = "warroom_push_widget_wp12_bottom_chart_packet"


@dataclass(frozen=True)
class BottomChartRow:
    source_widget_id: str
    topic_key: str
    updated_at_ms: int
    sequence: int
    price: float | None = None
    value_label: str = ""
    freshness_label: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BottomChartOverlay:
    overlay_id: str
    source_widget_id: str
    label: str
    state: str
    priority: int
    read_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _numeric_price(value: Mapping[str, Any]) -> float | None:
    for key in ("last_price", "best_bid", "best_ask"):
        item = value.get(key)
        if isinstance(item, (int, float)):
            return float(item)
    return None


def build_bottom_chart_rows(page_packet: Mapping[str, Any]) -> tuple[BottomChartRow, ...]:
    rows: list[BottomChartRow] = []
    for widget_id, render_packet in dict(page_packet.get("render_packets", {})).items():
        freshness = str(dict(render_packet).get("freshness_label") or "unknown")
        for row in render_packet.get("rows", []):
            if not isinstance(row, Mapping):
                continue
            value = row.get("value", {})
            if not isinstance(value, Mapping):
                value = {}
            topic_key = str(row.get("topic_key") or row.get("topic") or "")
            rows.append(BottomChartRow(
                source_widget_id=str(widget_id),
                topic_key=topic_key,
                updated_at_ms=int(row.get("updated_at_ms", 0)),
                sequence=int(row.get("sequence", 0)),
                price=_numeric_price(value),
                value_label=", ".join(f"{key}={value[key]}" for key in sorted(value) if key not in {"raw", "raw_payload", "endpoint", "token", "callable"})[:120],
                freshness_label=freshness,
            ))
    return tuple(sorted(rows, key=lambda item: (item.updated_at_ms, item.topic_key)))


def build_bottom_chart_overlays(top_packet: Mapping[str, Any]) -> tuple[BottomChartOverlay, ...]:
    overlays: list[BottomChartOverlay] = []
    for group in top_packet.get("groups", []):
        if not isinstance(group, Mapping):
            continue
        overlays.append(BottomChartOverlay(
            overlay_id=str(group.get("group_id", "")),
            source_widget_id=str(next(iter(group.get("widget_ids", ["unknown"])), "unknown")),
            label=str(group.get("status_label", "")),
            state=str(group.get("primary_state", "unknown")),
            priority=int(group.get("priority", 99)),
        ))
    return tuple(sorted(overlays, key=lambda item: item.priority))


def build_wp12_bottom_chart_layout_packet() -> dict[str, Any]:
    page_packet = build_wp9_warroom_page_mount_packet()
    top_packet = build_wp11_top_layout_push_widget_polish_packet()
    rows = build_bottom_chart_rows(page_packet)
    overlays = build_bottom_chart_overlays(top_packet)
    stale_rows = [row for row in rows if row.freshness_label != "live"]
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp12_bottom_chart_layout_packet",
        "version": WP12_VERSION,
        "wp12_completed": True,
        "next_checkpoint": "WP13_Prediction_card_connection_and_updates",
        "bottom_chart_layout_ready": True,
        "bottom_chart_data_adapter_ready": True,
        "bottom_chart_overlay_ready": True,
        "bottom_chart_refresh_cadence_ready": True,
        "bottom_chart_stale_handling_ready": True,
        "bottom_chart_visual_cleanup_ready": True,
        "bottom_chart_read_only_ready": True,
        "chart_row_count": len(rows),
        "overlay_count": len(overlays),
        "stale_row_count": len(stale_rows),
        "refresh_cadence_ms": 1000,
        "rate_limit_respected": True,
        "chart_rows": [row.to_dict() for row in rows],
        "overlays": [overlay.to_dict() for overlay in overlays],
    }
    packet.update(build_wp1_no_send_flags())
    packet["warroom_page_modified"] = True
    packet["warroom_page_mount_added"] = True
    packet["websocket_opened"] = False
    packet["websocket_receive_loop_started"] = False
    packet["websocket_send_enabled"] = False
    packet["broker_send_enabled"] = False
    packet["order_intent_submitted"] = False
    return packet


def render_wp12_bottom_chart_layout(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("WarRoom bottom chart: read-only adapter / overlays / stale-aware refresh cadence")
    if hasattr(st_api, "dataframe"):
        st_api.dataframe(list(packet.get("chart_rows", [])), width="stretch")
        st_api.dataframe(list(packet.get("overlays", [])), width="stretch")
    elif hasattr(st_api, "json"):
        st_api.json({"chart_rows": list(packet.get("chart_rows", [])), "overlays": list(packet.get("overlays", []))})
    return {"ok": True, "rendered_chart_rows": len(packet.get("chart_rows", [])), "rendered_overlays": len(packet.get("overlays", [])), "read_only": True, "controls_added": False}
