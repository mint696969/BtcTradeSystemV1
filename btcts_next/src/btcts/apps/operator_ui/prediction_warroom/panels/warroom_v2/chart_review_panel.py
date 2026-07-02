# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/chart_review_panel.py
# desc: WarRoom v2 chart review packet renderer. D-hot market snapshot is read-only; no chart data push.

from __future__ import annotations

import json
from typing import Any

import streamlit as st

from .market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model

WARROOM_V2_CHART_REVIEW_PANEL_RENDERER_VERSION = "prediction_warroom.v2.chart_review_panel_renderer.ps_q29r.v1"
WARROOM_V2_CHART_REVIEW_SCHEMA_VERSION = "warroom_chart_review.v1"
WARROOM_V2_CHART_REVIEW_TIMEFRAMES = ("1m", "5m", "15m", "1h", "1d")


def _base_payload(timeframe: str) -> dict[str, Any]:
    selected = timeframe if timeframe in WARROOM_V2_CHART_REVIEW_TIMEFRAMES else "5m"
    return {
        "schema_version": WARROOM_V2_CHART_REVIEW_SCHEMA_VERSION, "exchange": "bitFlyer", "market": "BTC-FX-JPY", "timeframe": selected, "timezone": "Asia/Tokyo",
        "selection": {"clicked_at": None, "range_start": None, "range_end": None},
        "operator_intent": "この範囲で当時の予測が妥当だったか確認したい。地合い・方向感・ボラ・反転警戒・市場間確認を見直したい。",
        "market_snapshot": {"ltp": None, "best_bid": None, "best_ask": None, "spread": None, "spread_bps": None, "data_age_sec": None, "data_state": "NO_DATA", "change_1m_pct": None, "change_5m_pct": None, "change_15m_pct": None, "change_1h_pct": None, "invalidation_watch": "NO_DATA"},
        "range_summary": {"open": None, "high": None, "low": None, "close": None, "change_pct": None, "range_pct": None, "volume": None, "volatility": None},
        "prediction_context": {"snapshot_time": None, "selected_horizon": None, "items": {"地合い": None, "方向感": None, "ボラ": None, "反転警戒": None, "市場間確認": None}},
        "annotations": {"predictions": [], "orderbook": [], "orders": [], "manual": []},
        "safety": {"read_only": True, "display_only": True, "runtime_connected": False, "push_connected": False, "would_send_to_broker": False},
    }


def _apply_snapshot(payload: dict[str, Any], source: dict[str, Any]) -> None:
    raw = dict(source.get("raw_values") or {})
    if not raw:
        return
    payload["market"] = str(raw.get("market") or payload["market"])
    for key in payload["market_snapshot"]:
        if key in raw:
            payload["market_snapshot"][key] = raw.get(key)


def _markdown_packet(payload: dict[str, Any]) -> str:
    s = payload["market_snapshot"]; sel = payload["selection"]
    return "\n".join(["# WarRoom Chart Review Packet", "", f"schema_version: {payload['schema_version']}", f"exchange: {payload['exchange']}", f"market: {payload['market']}", f"timeframe: {payload['timeframe']}", f"timezone: {payload['timezone']}", "", "## Selection", f"clicked_at: {sel['clicked_at']}", f"range_start: {sel['range_start']}", f"range_end: {sel['range_end']}", "", "## Operator Intent", payload["operator_intent"], "", "## Market Snapshot", f"ltp: {s['ltp']}", f"best_bid: {s['best_bid']}", f"best_ask: {s['best_ask']}", f"spread: {s['spread']}", f"spread_bps: {s['spread_bps']}", f"data_age_sec: {s['data_age_sec']}", f"data_state: {s['data_state']}", "", "## Annotations", "predictions: []", "orderbook: []", "orders: []", "manual: []"])


def build_warroom_v2_chart_review_panel_packet(*, timeframe: str = "5m", source_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    source = dict(source_packet or {})
    payload = _base_payload(timeframe)
    _apply_snapshot(payload, source)
    connected = bool(source.get("data_connected"))
    return {
        "ok": True, "renderer_version": WARROOM_V2_CHART_REVIEW_PANEL_RENDERER_VERSION, "schema_version": WARROOM_V2_CHART_REVIEW_SCHEMA_VERSION,
        "placement": "bottom_of_warroom_v2", "chart_placeholder_only": True, "timeframes": list(WARROOM_V2_CHART_REVIEW_TIMEFRAMES),
        "selected_timeframe": payload["timeframe"], "clicked_at_placeholder": None, "range_start_placeholder": None, "range_end_placeholder": None,
        "annotation_layers": list(payload["annotations"].keys()), "payload": payload, "markdown_preview": _markdown_packet(payload),
        "json_preview": json.dumps(payload, ensure_ascii=False, indent=2), "copy_for_gpt_ready": True, "market_snapshot_source": source,
        "push_ready": True, "auto_refresh_ready": True, "data_connected": connected, "runtime_connected": False, "push_connected": False,
        "websocket_enabled": False, "sse_enabled": False, "placeholder_only": not connected, "display_only": True, "read_only": True, "would_send_to_broker": False,
    }


def render_warroom_v2_chart_review_panel(*, source_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    source = source_packet if source_packet is not None else build_warroom_v2_market_snapshot_dhot_read_model()
    st.subheader("Chart Review / GPT相談パケット")
    timeframe = st.selectbox("timeframe", WARROOM_V2_CHART_REVIEW_TIMEFRAMES, index=1)
    packet = build_warroom_v2_chart_review_panel_packet(timeframe=str(timeframe), source_packet=source)
    st.caption("D-hot market snapshot read-only / chart series not bound / no push connection")
    st.markdown("▧ chart placeholder: clicked_at / range_start / range_end are not connected yet")
    st.text_area("Copy for GPT", packet["markdown_preview"] + "\n\n```json\n" + packet["json_preview"] + "\n```", height=360)
    return packet
