# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp11_top_layout_push_widget_polish.py
# desc: WP11 WarRoom top layout polish for push widgets. Groups market status, freshness, connection health, manual decision context, and risk cues without socket/send/broker/order.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp9_warroom_page_mount import build_wp9_warroom_page_mount_packet

WP11_VERSION = "warroom.manual_trade_support.push_widgets.wp11.top_layout_polish.v1"
WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY = "warroom_push_widget_wp11_top_layout_packet"


@dataclass(frozen=True)
class TopLayoutGroup:
    group_id: str
    title: str
    priority: int
    widget_ids: tuple[str, ...]
    primary_state: str
    status_label: str
    cues: tuple[str, ...]
    read_only: bool = True
    controls_added: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["widget_ids"] = list(self.widget_ids)
        data["cues"] = list(self.cues)
        return data


def _health_state(packet: Mapping[str, Any], widget_id: str) -> str:
    render = dict(dict(packet.get("render_packets", {})).get(widget_id, {}))
    return str(render.get("freshness_label") or "unknown")


def _seq(packet: Mapping[str, Any], widget_id: str) -> int:
    render = dict(dict(packet.get("render_packets", {})).get(widget_id, {}))
    return int(render.get("sequence", 0))


def _all_live(packet: Mapping[str, Any], widget_ids: tuple[str, ...]) -> bool:
    return all(_health_state(packet, widget_id) == "live" for widget_id in widget_ids)


def build_wp11_top_layout_groups(page_packet: Mapping[str, Any]) -> tuple[TopLayoutGroup, ...]:
    market_widgets = ("market_depth_widget", "recent_trades_widget", "spread_liquidity_widget")
    connection_widgets = ("receiver_lifecycle_widget",)
    decision_widgets = ("summary_alerts_widget", "market_depth_widget", "recent_trades_widget")
    risk_widgets = ("spread_liquidity_widget", "summary_alerts_widget")
    market_state = "live" if _all_live(page_packet, market_widgets) else "attention"
    connection_state = _health_state(page_packet, "receiver_lifecycle_widget")
    decision_state = "ready" if _seq(page_packet, "summary_alerts_widget") > 0 else "not_ready"
    risk_state = "normal" if _all_live(page_packet, risk_widgets) else "review"
    return (
        TopLayoutGroup("market_status", "Market status", 10, market_widgets, market_state, "book / trades / spread", ("depth", "trades", "liquidity")),
        TopLayoutGroup("freshness_connection", "Freshness & connection", 20, connection_widgets, connection_state, "receiver heartbeat", ("lifecycle", "heartbeat", "stale guard")),
        TopLayoutGroup("manual_decision_context", "Manual decision context", 30, decision_widgets, decision_state, "summary before action", ("summary", "alerts", "operator review")),
        TopLayoutGroup("risk_cues", "Risk cues", 40, risk_widgets, risk_state, "liquidity and alert cues", ("spread", "liquidity", "alerts")),
    )


def build_wp11_top_layout_push_widget_polish_packet() -> dict[str, Any]:
    page_packet = build_wp9_warroom_page_mount_packet()
    groups = build_wp11_top_layout_groups(page_packet)
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp11_top_layout_polish_packet",
        "version": WP11_VERSION,
        "wp11_completed": True,
        "next_checkpoint": "WP12_Bottom_chart_layout",
        "top_layout_push_widget_polish_ready": True,
        "top_information_groups_ready": True,
        "market_status_group_ready": True,
        "freshness_connection_group_ready": True,
        "manual_decision_context_group_ready": True,
        "risk_cues_group_ready": True,
        "top_layout_visible_mount_ready": True,
        "top_layout_read_only_ready": True,
        "group_count": len(groups),
        "base_widget_count": int(page_packet["widget_count"]),
        "live_widget_count": int(page_packet["live_widget_count"]),
        "groups": [group.to_dict() for group in groups],
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


def render_wp11_top_layout_polish(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("WarRoom push-widget top layout: market status / freshness / manual context / risk cues")
    rendered: list[str] = []
    rows: list[dict[str, Any]] = []
    for group in packet.get("groups", []):
        if not isinstance(group, Mapping):
            continue
        rows.append({
            "group": str(group.get("title", "")),
            "state": str(group.get("primary_state", "")),
            "status": str(group.get("status_label", "")),
            "widgets": ",".join(str(item) for item in group.get("widget_ids", [])),
            "cues": ",".join(str(item) for item in group.get("cues", [])),
        })
        rendered.append(str(group.get("group_id", "")))
    if rows and hasattr(st_api, "dataframe"):
        st_api.dataframe(rows, width="stretch")
    elif rows and hasattr(st_api, "json"):
        st_api.json(rows)
    return {"ok": True, "rendered_group_ids": rendered, "rendered_group_count": len(rendered), "read_only": True, "controls_added": False}
