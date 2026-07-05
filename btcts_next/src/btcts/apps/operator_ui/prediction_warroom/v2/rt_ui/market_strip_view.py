# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_strip_view.py
# desc: Thin market strip for WarRoom v2 cockpit. Extracts live bid/ask/spread/freshness from RT widget packets.

from __future__ import annotations

from typing import Any, Mapping


def _rows(packet: Mapping[str, Any], widget_id: str) -> list[Mapping[str, Any]]:
    render_packets = packet.get("render_packets", {})
    widget = render_packets.get(widget_id, {}) if isinstance(render_packets, Mapping) else {}
    rows = widget.get("rows", []) if isinstance(widget, Mapping) else []
    return [row for row in rows if isinstance(row, Mapping)]


def _value(row: Mapping[str, Any]) -> Mapping[str, Any]:
    value = row.get("value", {})
    return value if isinstance(value, Mapping) else {}


def build_market_strip_packet(widgets_packet: Mapping[str, Any]) -> dict[str, Any]:
    depth_rows = _rows(widgets_packet, "market_depth_widget")
    spread_rows = _rows(widgets_packet, "spread_liquidity_widget")
    lifecycle_rows = _rows(widgets_packet, "receiver_lifecycle_widget")
    depth_value = _value(depth_rows[-1]) if depth_rows else {}
    spread_value = next((_value(row) for row in reversed(spread_rows) if str(row.get("topic_key")) == "market.spread"), {})
    lifecycle_value = _value(lifecycle_rows[-1]) if lifecycle_rows else {}
    best_bid = depth_value.get("best_bid")
    best_ask = depth_value.get("best_ask")
    spread = spread_value.get("spread", depth_value.get("spread"))
    spread_bps = spread_value.get("spread_bps")
    return {
        "ok": True,
        "packet_kind": "warroom_v2_rt_market_strip_packet",
        "display_source": widgets_packet.get("display_source", "live"),
        "symbol": depth_value.get("symbol") or spread_value.get("symbol") or "--",
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": spread,
        "spread_bps": spread_bps,
        "market_uid": depth_value.get("market_uid"),
        "source": depth_value.get("source") or spread_value.get("source"),
        "receiver_status": lifecycle_value.get("status", "waiting"),
        "last_event_ts": lifecycle_value.get("last_event_ts"),
        "live_widget_count": int(widgets_packet.get("live_widget_count") or 0),
        "read_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def _fmt_price(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):,.0f}"
    return "--"


def _fmt_bps(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.2f} bps"
    return "--"


def render_market_strip(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("Market strip: D-hot live market state / read-only / no broker action")
    cols = st_api.columns(6)
    cols[0].metric("Symbol", str(packet.get("symbol") or "--"))
    cols[1].metric("Best Bid", _fmt_price(packet.get("best_bid")))
    cols[2].metric("Best Ask", _fmt_price(packet.get("best_ask")))
    cols[3].metric("Spread", _fmt_price(packet.get("spread")))
    cols[4].metric("Spread bps", _fmt_bps(packet.get("spread_bps")))
    cols[5].metric("Receiver", str(packet.get("receiver_status") or "waiting"))
    st_api.caption(f"source={packet.get('source') or '--'} / last_event_ts={packet.get('last_event_ts') or '--'} / live_widgets={packet.get('live_widget_count', 0)}")
    return {"ok": True, "market_strip_rendered": True, "read_only": True, "broker_send_enabled": False}
