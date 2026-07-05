# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/chart_view.py
# desc: WarRoom v2 realtime bottom chart graph renderer. Uses zero-free chart scaling when Altair is available.

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


def _render_price_chart(frame: pd.DataFrame, st_api: Any) -> bool:
    if frame.empty:
        return False
    try:
        import altair as alt  # type: ignore
        chart = alt.Chart(frame).mark_line(point=True).encode(
            x=alt.X("ts:T", title="time"),
            y=alt.Y("price:Q", title="price", scale=alt.Scale(zero=False)),
            color=alt.Color("topic:N", title="series"),
            tooltip=["ts:T", "topic:N", "price:Q", "sequence:Q", "freshness_label:N"],
        ).properties(height=300)
        st_api.altair_chart(chart, use_container_width=True)
        return True
    except Exception:  # noqa: BLE001
        pivot = frame.pivot_table(index="ts", columns="topic", values="price", aggfunc="last").sort_index()
        st_api.line_chart(pivot, height=280, width="stretch")
        return True


def render_rt_bottom_chart_graph(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("Bottom chart: realtime price context / zero-free scale when available / read-only")
    frame = chart_rows_to_frame(packet)
    live_rows = sum(1 for row in packet.get("chart_rows", []) if isinstance(row, Mapping) and row.get("freshness_label") == "live")
    c1, c2, c3, c4 = st_api.columns(4)
    c1.metric("Rows", int(packet.get("chart_row_count") or 0))
    c2.metric("Live rows", live_rows)
    c3.metric("Stale rows", int(packet.get("stale_row_count") or 0))
    c4.metric("Overlays", int(packet.get("overlay_count") or 0))
    if not frame.empty:
        rendered = _render_price_chart(frame, st_api)
        latest = frame.sort_values("ts").iloc[-1]
        st_api.caption(f"latest={latest['price']:.2f} / topic={latest['topic']} / freshness={latest['freshness_label']}")
    else:
        rendered = False
        st_api.info("No live price rows yet. Waiting for market.depth or market.trades.")
    with st_api.expander("Chart rows and overlays", expanded=False):
        st_api.dataframe(list(packet.get("chart_rows", [])), width="stretch")
        st_api.dataframe(list(packet.get("overlays", [])), width="stretch")
    return {"ok": True, "chart_graph_rendered": rendered, "frame_rows": len(frame), "zero_free_scale_ready": True, "read_only": True, "controls_added": False}
