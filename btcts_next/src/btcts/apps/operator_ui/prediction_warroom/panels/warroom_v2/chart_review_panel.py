# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/chart_review_panel.py
# desc: WarRoom v2 chart review renderer. D-hot market snapshot and chart series are read-only; no push transport.

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from .market_chart_read_model import build_warroom_v2_market_chart_read_model
from .market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model

WARROOM_V2_CHART_REVIEW_PANEL_RENDERER_VERSION = "prediction_warroom.v2.chart_review_panel_renderer.ps_q29u.v1"
WARROOM_V2_CHART_REVIEW_SCHEMA_VERSION = "warroom_chart_review.v1"
WARROOM_V2_CHART_REVIEW_TIMEFRAMES = ("1m", "5m", "15m", "1h", "1d")


def _base_payload(timeframe: str) -> dict[str, Any]:
    selected = timeframe if timeframe in WARROOM_V2_CHART_REVIEW_TIMEFRAMES else "5m"
    return {"schema_version": WARROOM_V2_CHART_REVIEW_SCHEMA_VERSION, "exchange": "bitFlyer", "market": "BTC-FX-JPY", "timeframe": selected, "timezone": "Asia/Tokyo", "selection": {"clicked_at": None, "range_start": None, "range_end": None}, "operator_intent": "この範囲で当時の予測が妥当だったか確認したい。地合い・方向感・ボラ・反転警戒・市場間確認を見直したい。", "market_snapshot": {"ltp": None, "best_bid": None, "best_ask": None, "spread": None, "spread_bps": None, "data_age_sec": None, "data_state": "NO_DATA", "change_1m_pct": None, "change_5m_pct": None, "change_15m_pct": None, "change_1h_pct": None, "invalidation_watch": "NO_DATA"}, "range_summary": {"open": None, "high": None, "low": None, "close": None, "change_pct": None, "range_pct": None, "row_count": 0}, "prediction_context": {"snapshot_time": None, "selected_horizon": None, "items": {"地合い": None, "方向感": None, "ボラ": None, "反転警戒": None, "市場間確認": None}}, "annotations": {"predictions": [], "orderbook": [], "orders": [], "manual": []}, "safety": {"read_only": True, "display_only": True, "runtime_connected": False, "push_connected": False, "would_send_to_broker": False}}


def _apply_snapshot(payload: dict[str, Any], source: dict[str, Any]) -> None:
    raw = dict(source.get("raw_values") or {})
    if raw:
        payload["market"] = str(raw.get("market") or payload["market"])
        for key in payload["market_snapshot"]:
            if key in raw:
                payload["market_snapshot"][key] = raw.get(key)


def _markdown_packet(payload: dict[str, Any]) -> str:
    s, sel, r = payload["market_snapshot"], payload["selection"], payload["range_summary"]
    return "\n".join(["# WarRoom Chart Review Packet", "", f"schema_version: {payload['schema_version']}", f"exchange: {payload['exchange']}", f"market: {payload['market']}", f"timeframe: {payload['timeframe']}", "", "## Selection", f"clicked_at: {sel['clicked_at']}", f"range_start: {sel['range_start']}", f"range_end: {sel['range_end']}", "", "## Market Snapshot", f"ltp: {s['ltp']}", f"best_bid: {s['best_bid']}", f"best_ask: {s['best_ask']}", f"spread: {s['spread']}", f"spread_bps: {s['spread_bps']}", f"data_state: {s['data_state']}", "", "## Range Summary", f"open: {r.get('open')}", f"high: {r.get('high')}", f"low: {r.get('low')}", f"close: {r.get('close')}", f"change_pct: {r.get('change_pct')}", f"range_pct: {r.get('range_pct')}", "", "## Annotations", "predictions: []", "orderbook: []", "orders: []", "manual: []"])


def build_warroom_v2_chart_review_panel_packet(*, timeframe: str = "5m", source_packet: dict[str, Any] | None = None, chart_series_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    source, chart = dict(source_packet or {}), dict(chart_series_packet or {})
    payload = _base_payload(timeframe)
    _apply_snapshot(payload, source)
    if chart.get("range_summary"):
        payload["range_summary"] = dict(chart["range_summary"])
    chart_connected = bool(chart.get("chart_series_connected"))
    return {"ok": True, "renderer_version": WARROOM_V2_CHART_REVIEW_PANEL_RENDERER_VERSION, "schema_version": WARROOM_V2_CHART_REVIEW_SCHEMA_VERSION, "placement": "bottom_of_warroom_v2", "chart_placeholder_only": not chart_connected, "actual_chart_series_bound": chart_connected, "chart_readability_mode": "price_and_bps", "timeframes": list(WARROOM_V2_CHART_REVIEW_TIMEFRAMES), "selected_timeframe": payload["timeframe"], "annotation_layers": list(payload["annotations"].keys()), "payload": payload, "markdown_preview": _markdown_packet(payload), "json_preview": json.dumps(payload, ensure_ascii=False, indent=2), "copy_for_gpt_ready": True, "market_snapshot_source": source, "chart_series": chart, "push_ready": True, "auto_refresh_ready": True, "data_connected": bool(source.get("data_connected")), "chart_series_connected": chart_connected, "runtime_connected": False, "push_connected": False, "websocket_enabled": False, "sse_enabled": False, "display_only": True, "read_only": True, "would_send_to_broker": False}


def _render_chart_views(chart: dict[str, Any]) -> None:
    df = pd.DataFrame(chart["chart_rows"])
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    view = df.dropna(subset=["ts"]).set_index("ts")
    latest, summary = view.iloc[-1], dict(chart.get("range_summary") or {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", int(summary.get("row_count") or len(view)))
    c2.metric("Change %", "--" if summary.get("change_pct") is None else f"{float(summary['change_pct']):+.4f}%")
    c3.metric("Range %", "--" if summary.get("range_pct") is None else f"{float(summary['range_pct']):.4f}%")
    c4.metric("Spread bps", "--" if latest.get("spread_bps") is None else f"{float(latest['spread_bps']):.2f}")
    st.line_chart(view[["mid_price", "best_bid", "best_ask"]], height=260, width="stretch")
    base = float(view["mid_price"].dropna().iloc[0]) if not view["mid_price"].dropna().empty else None
    if base:
        view = view.assign(mid_change_bps=(view["mid_price"] / base - 1.0) * 10000.0)
        st.line_chart(view[["mid_change_bps", "spread_bps"]].dropna(how="all"), height=180, width="stretch")


def render_warroom_v2_chart_review_panel(*, source_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    source = source_packet if source_packet is not None else build_warroom_v2_market_snapshot_dhot_read_model()
    st.subheader("Chart Review / GPT相談パケット")
    timeframe = st.selectbox("timeframe", WARROOM_V2_CHART_REVIEW_TIMEFRAMES, index=1)
    chart = build_warroom_v2_market_chart_read_model(timeframe=str(timeframe))
    packet = build_warroom_v2_chart_review_panel_packet(timeframe=str(timeframe), source_packet=source, chart_series_packet=chart)
    if chart.get("chart_rows"):
        _render_chart_views(chart)
    else:
        st.markdown("▧ chart placeholder: market series is not available yet")
    st.caption("D-hot market chart series read-only / price + bps views / no push connection")
    st.text_area("Copy for GPT", packet["markdown_preview"] + "\n\n```json\n" + packet["json_preview"] + "\n```", height=360)
    return packet
