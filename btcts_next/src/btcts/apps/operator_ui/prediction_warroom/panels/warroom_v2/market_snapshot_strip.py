# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/market_snapshot_strip.py
# desc: WarRoom v2 market snapshot strip renderer. Read-only D-hot binding is optional; no push transport.

from __future__ import annotations

from typing import Any

import streamlit as st

from .market_snapshot_read_model import build_warroom_v2_market_snapshot_dhot_read_model

WARROOM_V2_MARKET_SNAPSHOT_STRIP_RENDERER_VERSION = "prediction_warroom.v2.market_snapshot_strip_renderer.ps_q29r.v1"
_FIELD_ORDER: tuple[tuple[str, str, str], ...] = (
    ("market", "Market", "BTC-FX-JPY"), ("ltp", "LTP", "--"), ("best_bid", "Best Bid", "--"), ("best_ask", "Best Ask", "--"),
    ("spread", "Spread", "-- / -- bps"), ("data_age_sec", "Data Age", "-- sec"), ("data_state", "Data State", "NO_DATA"),
    ("change_1m_pct", "1m Change", "--"), ("change_5m_pct", "5m Change", "--"), ("change_15m_pct", "15m Change", "--"),
    ("change_1h_pct", "1h Change", "--"), ("invalidation_watch", "Invalidation Watch", "NO_DATA"),
)
_SECONDARY_READY_FIELDS = ("range_5m_pct", "range_15m_pct", "short_term_volatility", "recent_volume", "trade_density", "board_imbalance", "top_bid_size", "top_ask_size", "depth_0_1_pct", "fx_spot_basis", "alert_flags")


def build_warroom_v2_market_snapshot_strip_packet(*, source_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    source = dict(source_packet or {})
    display = dict(source.get("display_values") or {})
    raw = dict(source.get("raw_values") or {})
    fields = [{"key": k, "label": label, "value": display.get(k, default), "placeholder_only": not bool(source.get("data_connected"))} for k, label, default in _FIELD_ORDER]
    connected = bool(source.get("data_connected"))
    return {
        "ok": True, "renderer_version": WARROOM_V2_MARKET_SNAPSHOT_STRIP_RENDERER_VERSION, "placement": "above_prediction_cards",
        "market": display.get("market", "BTC-FX-JPY"), "exchange": "bitFlyer", "field_count": len(fields), "fields": fields,
        "field_keys": [field["key"] for field in fields], "secondary_ready_fields": list(_SECONDARY_READY_FIELDS),
        "data_state": display.get("data_state", "NO_DATA"), "invalidation_watch": display.get("invalidation_watch", "NO_DATA"),
        "market_snapshot_source": source, "raw_values": raw, "freshness_badge_only": True, "price_neutral_display": True,
        "risk_badge_or_border_only": True, "push_ready": True, "auto_refresh_ready": True, "data_connected": connected,
        "runtime_connected": False, "push_connected": False, "websocket_enabled": False, "sse_enabled": False,
        "placeholder_only": not connected, "display_only": True, "read_only": True, "would_send_to_broker": False,
    }


def render_warroom_v2_market_snapshot_strip(*, source_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    source = source_packet if source_packet is not None else build_warroom_v2_market_snapshot_dhot_read_model()
    packet = build_warroom_v2_market_snapshot_strip_packet(source_packet=source)
    st.subheader("Market Snapshot / 手動トレード参考")
    st.caption("D-hot read-only binding / push-ready but not connected" if packet["data_connected"] else "placeholder contract only / push-ready but not connected")
    columns = st.columns(4)
    for index, field in enumerate(packet["fields"]):
        with columns[index % 4]:
            st.metric(str(field["label"]), str(field["value"]))
    st.caption(f"data_connected={packet['data_connected']} / push_connected=false / runtime_connected=false")
    return packet
