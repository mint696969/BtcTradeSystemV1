# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp9_warroom_page_mount.py
# desc: WP9 WarRoom page mount adapter for push widgets. Uses WP8 render packets; no socket open, send, broker, order, ledger, or prediction.

from __future__ import annotations

from typing import Any, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp8_first_real_push_widget_set import build_wp8_first_real_push_widget_set_packet

WP9_VERSION = "warroom.manual_trade_support.push_widgets.wp9.page_mount.v1"
WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY = "warroom_push_widget_wp9_page_mount_packet"


def build_wp9_warroom_page_mount_packet() -> dict[str, Any]:
    source = build_wp8_first_real_push_widget_set_packet()
    render_packets = dict(source["render_packets"])
    widget_ids = list(source["widget_ids"])
    packet = {
        "ok": True,
        "packet_kind": "warroom_push_widget_wp9_page_mount_packet",
        "version": WP9_VERSION,
        "wp9_completed": True,
        "next_checkpoint": "WP10_Widget_extension_contract",
        "warroom_page_mount_ready": True,
        "warroom_page_modified": True,
        "warroom_page_mount_added": True,
        "push_widget_grid_mount_ready": True,
        "registry_driven_page_mount_ready": True,
        "render_packets_read_only_ready": True,
        "health_visible_per_widget_ready": True,
        "future_widget_mount_extension_ready": True,
        "widget_count": len(widget_ids),
        "render_packet_count": len(render_packets),
        "live_widget_count": int(source["live_widget_count"]),
        "widget_ids": widget_ids,
        "render_packets": render_packets,
    }
    packet.update(build_wp1_no_send_flags())
    packet["warroom_page_modified"] = True
    packet["warroom_page_mount_added"] = True
    packet["streamlit_render_adapter_used"] = True
    packet["websocket_opened"] = False
    packet["websocket_receive_loop_started"] = False
    packet["websocket_send_enabled"] = False
    packet["broker_send_enabled"] = False
    packet["order_intent_submitted"] = False
    return packet


def _safe_rows(render_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in render_packet.get("rows", []):
        if not isinstance(row, Mapping):
            continue
        value = dict(row.get("value", {})) if isinstance(row.get("value", {}), Mapping) else {}
        rows.append({
            "topic": str(row.get("topic_key", "")),
            "sequence": int(row.get("sequence", 0)),
            "updated_at_ms": int(row.get("updated_at_ms", 0)),
            "value": value,
        })
    return rows


def render_wp9_push_widget_mount(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    render_packets = dict(packet.get("render_packets", {}))
    st_api.caption("WarRoom push widgets: receive-only / read-only / no broker / no order")
    rendered: list[str] = []
    for widget_id in packet.get("widget_ids", []):
        render_packet = dict(render_packets[str(widget_id)])
        title = str(render_packet.get("title") or widget_id)
        health = dict(render_packet.get("health", {})) if isinstance(render_packet.get("health"), Mapping) else {}
        st_api.caption(f"{title} | {render_packet.get('freshness_label')} | seq={render_packet.get('sequence')} | heartbeat={health.get('heartbeat_ok')}")
        rows = _safe_rows(render_packet)
        if rows and hasattr(st_api, "dataframe"):
            st_api.dataframe(rows, width="stretch")
        elif rows and hasattr(st_api, "json"):
            st_api.json(rows)
        rendered.append(str(widget_id))
    return {"ok": True, "rendered_widget_ids": rendered, "rendered_widget_count": len(rendered), "read_only": True, "controls_added": False}
