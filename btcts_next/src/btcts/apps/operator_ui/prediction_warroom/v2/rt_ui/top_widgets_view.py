# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/top_widgets_view.py
# desc: Compact top layout and realtime push-widget renderer. Keeps raw tables in an expander.

from __future__ import annotations

from typing import Any, Mapping


def _row_value_label(row: Mapping[str, Any]) -> str:
    value = row.get("value", {})
    if not isinstance(value, Mapping):
        return ""
    parts = [f"{key}={value[key]}" for key in sorted(value) if key not in {"raw", "raw_payload", "endpoint", "token", "callable"}]
    return ", ".join(parts)[:180]


def _safe_rows(render_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in render_packet.get("rows", []):
        if not isinstance(row, Mapping):
            continue
        rows.append({
            "topic": str(row.get("topic_key") or row.get("topic") or ""),
            "sequence": int(row.get("sequence") or 0),
            "updated_at_ms": int(row.get("updated_at_ms") or 0),
            "value": _row_value_label(row),
        })
    return rows


def render_rt_top_layout_and_widgets(top_packet: Mapping[str, Any], page_packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    groups = [group for group in top_packet.get("groups", []) if isinstance(group, Mapping)]
    render_packets = dict(page_packet.get("render_packets", {}))
    live_count = int(page_packet.get("live_widget_count") or 0)
    widget_count = int(page_packet.get("widget_count") or len(render_packets))
    st_api.caption("WarRoom push-widget top layout: live market status / freshness / manual context / risk cues")
    c1, c2, c3 = st_api.columns(3)
    c1.metric("Widgets", widget_count)
    c2.metric("Live", live_count)
    c3.metric("Groups", len(groups))
    if groups:
        st_api.dataframe([
            {
                "group": str(group.get("title") or group.get("group_id") or ""),
                "state": str(group.get("primary_state") or ""),
                "status": str(group.get("status_label") or ""),
                "widgets": ", ".join(str(item) for item in group.get("widget_ids", [])),
            }
            for group in groups
        ], width="stretch")
    widget_ids = list(page_packet.get("widget_ids") or sorted(render_packets))
    for widget_id in widget_ids:
        packet = dict(render_packets.get(str(widget_id), {}))
        if not packet:
            continue
        health = dict(packet.get("health", {})) if isinstance(packet.get("health"), Mapping) else {}
        state = str(packet.get("freshness_label") or health.get("state") or "unknown")
        title = str(packet.get("title") or widget_id)
        st_api.caption(f"{title} | {state} | seq={packet.get('sequence')} | heartbeat={health.get('heartbeat_ok', packet.get('heartbeat_ok'))}")
        rows = _safe_rows(packet)
        if rows:
            latest = rows[-1]
            st_api.markdown(f"**{latest['topic']}** — {latest['value']}")
    with st_api.expander("Raw push-widget packets", expanded=False):
        st_api.dataframe(_flatten_widget_rows(render_packets), width="stretch")
    return {"ok": True, "rendered_widget_count": len(widget_ids), "live_widget_count": live_count, "read_only": True, "controls_added": False}


def _flatten_widget_rows(render_packets: Mapping[str, Any]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    for widget_id, packet in render_packets.items():
        if not isinstance(packet, Mapping):
            continue
        for row in _safe_rows(packet):
            flat.append({"widget_id": widget_id, **row})
    return flat
