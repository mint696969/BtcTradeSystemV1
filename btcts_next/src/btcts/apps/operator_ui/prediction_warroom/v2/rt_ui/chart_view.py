# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/chart_view.py
# desc: WarRoom v2 realtime bottom chart graph renderer. Turns WP12 live chart rows into line charts and compact metrics.

from __future__ import annotations

import re
from typing import Any, Mapping

import pandas as pd

_PRICE_RE = re.compile(r"(?:best_ask|best_bid|last_price)=([0-9]+(?:\.[0-9]+)?)")


def chart_rows_to_frame(packet: Mapping[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in packet.get("chart_rows", []):
        if not isinstance(row, Mapping):
            continue
        price = row.get("price")
        topic = str(row.get("topic_key") or "")
        updated_at_ms = int(row.get("updated_at_ms") or 0)
        if isinstance(price, (int, float)) and updated_at_ms > 0:
            rows.append({"ts": pd.to_datetime(updated_at_ms, unit="ms", utc=True), "topic": topic, "price": float(price), "sequence": int(row.get("sequence") or 0), "freshness_label": str(row.get("freshness_label") or "")})
        label = str(row.get("value_label") or "")
        for match in _PRICE_RE.finditer(label):
            if updated_at_ms > 0:
                rows.append({"ts": pd.to_datetime(updated_at_ms, unit="ms", utc=True), "topic": f"{topic}.{match.group(0).split('=')[0]}", "price": float(match.group(1)), "sequence": int(row.get("sequence") or 0), "freshness_label": str(row.get("freshness_label") or "")})
    return pd.DataFrame(rows)


def render_rt_bottom_chart_graph(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("WarRoom bottom chart: realtime push-widget price context / read-only / stale-aware")
    frame = chart_rows_to_frame(packet)
    c1, c2, c3, c4 = st_api.columns(4)
    c1.metric("Rows", int(packet.get("chart_row_count") or 0))
    c2.metric("Live rows", sum(1 for row in packet.get("chart_rows", []) if isinstance(row, Mapping) and row.get("freshness_label") == "live"))
    c3.metric("Stale rows", int(packet.get("stale_row_count") or 0))
    c4.metric("Overlays", int(packet.get("overlay_count") or 0))
    if not frame.empty:
        pivot = frame.pivot_table(index="ts", columns="topic", values="price", aggfunc="last").sort_index()
        st_api.line_chart(pivot, height=280, width="stretch")
        latest = frame.sort_values("ts").iloc[-1]
        st_api.caption(f"latest={latest['price']:.2f} / topic={latest['topic']} / freshness={latest['freshness_label']}")
    else:
        st_api.info("No live price rows yet. Waiting for market.depth or market.trades.")
    with st_api.expander("Chart rows and overlays", expanded=False):
        st_api.dataframe(list(packet.get("chart_rows", [])), width="stretch")
        st_api.dataframe(list(packet.get("overlays", [])), width="stretch")
    return {"ok": True, "chart_graph_rendered": not frame.empty, "frame_rows": len(frame), "read_only": True, "controls_added": False}
