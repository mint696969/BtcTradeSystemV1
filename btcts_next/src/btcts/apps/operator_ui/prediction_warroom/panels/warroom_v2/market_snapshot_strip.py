# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/market_snapshot_strip.py
# desc: WarRoom v2 market snapshot strip placeholder renderer. Display-only; no live data or push transport.

from __future__ import annotations

from typing import Any

import streamlit as st

WARROOM_V2_MARKET_SNAPSHOT_STRIP_RENDERER_VERSION = "prediction_warroom.v2.market_snapshot_strip_renderer.ps_q29q.v1"

_MARKET_SNAPSHOT_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("market", "Market", "BTC-FX-JPY"),
    ("ltp", "LTP", "--"),
    ("best_bid", "Best Bid", "--"),
    ("best_ask", "Best Ask", "--"),
    ("spread", "Spread", "-- / -- bps"),
    ("data_age_sec", "Data Age", "-- sec"),
    ("data_state", "Data State", "NO_DATA"),
    ("change_1m_pct", "1m Change", "--"),
    ("change_5m_pct", "5m Change", "--"),
    ("change_15m_pct", "15m Change", "--"),
    ("change_1h_pct", "1h Change", "--"),
    ("invalidation_watch", "Invalidation Watch", "NO_DATA"),
)

_SECONDARY_READY_FIELDS = (
    "range_5m_pct",
    "range_15m_pct",
    "short_term_volatility",
    "recent_volume",
    "trade_density",
    "board_imbalance",
    "top_bid_size",
    "top_ask_size",
    "depth_0_1_pct",
    "fx_spot_basis",
    "alert_flags",
)


def build_warroom_v2_market_snapshot_strip_packet() -> dict[str, Any]:
    fields = [{"key": key, "label": label, "value": value, "placeholder_only": True} for key, label, value in _MARKET_SNAPSHOT_FIELDS]
    return {
        "ok": True,
        "renderer_version": WARROOM_V2_MARKET_SNAPSHOT_STRIP_RENDERER_VERSION,
        "placement": "above_prediction_cards",
        "market": "BTC-FX-JPY",
        "exchange": "bitFlyer",
        "field_count": len(fields),
        "fields": fields,
        "field_keys": [field["key"] for field in fields],
        "secondary_ready_fields": list(_SECONDARY_READY_FIELDS),
        "data_state": "NO_DATA",
        "invalidation_watch": "NO_DATA",
        "freshness_badge_only": True,
        "price_neutral_display": True,
        "risk_badge_or_border_only": True,
        "push_ready": True,
        "auto_refresh_ready": True,
        "data_connected": False,
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "placeholder_only": True,
        "display_only": True,
        "read_only": True,
        "would_send_to_broker": False,
    }


def render_warroom_v2_market_snapshot_strip() -> dict[str, Any]:
    packet = build_warroom_v2_market_snapshot_strip_packet()
    st.subheader("Market Snapshot / 手動トレード参考")
    st.caption("placeholder contract only / push-ready but not connected")
    columns = st.columns(4)
    for index, field in enumerate(packet["fields"]):
        with columns[index % 4]:
            st.metric(str(field["label"]), str(field["value"]))
    st.caption("push_ready=true / auto_refresh_ready=true / push_connected=false / data_connected=false")
    return packet
