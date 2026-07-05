# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_strip_view.py
# desc: Thin market strip for WarRoom v2 cockpit. Shows essential manual-trade market data in one compact top row.

from __future__ import annotations

from typing import Any, Mapping

MARKET_TOP_STRIP_VERSION = "warroom_v2_market_top_strip.2026_07_05.v2_japanese"


def _rows(packet: Mapping[str, Any], widget_id: str) -> list[Mapping[str, Any]]:
    render_packets = packet.get("render_packets", {})
    widget = render_packets.get(widget_id, {}) if isinstance(render_packets, Mapping) else {}
    rows = widget.get("rows", []) if isinstance(widget, Mapping) else []
    return [row for row in rows if isinstance(row, Mapping)]


def _value(row: Mapping[str, Any]) -> Mapping[str, Any]:
    value = row.get("value", {})
    return value if isinstance(value, Mapping) else {}


def _latest_value(rows: list[Mapping[str, Any]], topic_key: str | None = None) -> Mapping[str, Any]:
    for row in reversed(rows):
        if topic_key is None or str(row.get("topic_key") or "") == topic_key:
            return _value(row)
    return {}


def _widget_state(widgets_packet: Mapping[str, Any], widget_id: str) -> str:
    render_packets = widgets_packet.get("render_packets", {})
    widget = render_packets.get(widget_id, {}) if isinstance(render_packets, Mapping) else {}
    if isinstance(widget, Mapping):
        health = widget.get("health", {})
        if isinstance(health, Mapping) and health.get("state"):
            return str(health.get("state"))
        if widget.get("freshness_label"):
            return str(widget.get("freshness_label"))
    return "not_started"


def _as_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        if isinstance(value, str) and value.strip():
            return float(value)
    except ValueError:
        return None
    return None


def _spread_bps(spread: object, bid: object, ask: object, provided: object) -> float | None:
    explicit = _as_float(provided)
    if explicit is not None:
        return explicit
    spread_f = _as_float(spread)
    bid_f = _as_float(bid)
    ask_f = _as_float(ask)
    if spread_f is None or bid_f is None or ask_f is None:
        return None
    mid = (bid_f + ask_f) / 2.0
    if mid <= 0:
        return None
    return spread_f / mid * 10_000.0


def _spread_value(spread: object, bid: object, ask: object) -> float | None:
    explicit = _as_float(spread)
    if explicit is not None:
        return explicit
    bid_f = _as_float(bid)
    ask_f = _as_float(ask)
    if bid_f is None or ask_f is None:
        return None
    return ask_f - bid_f


def build_market_strip_packet(widgets_packet: Mapping[str, Any]) -> dict[str, Any]:
    depth_rows = _rows(widgets_packet, "market_depth_widget")
    trade_rows = _rows(widgets_packet, "recent_trades_widget")
    spread_rows = _rows(widgets_packet, "spread_liquidity_widget")
    lifecycle_rows = _rows(widgets_packet, "receiver_lifecycle_widget")
    summary_rows = _rows(widgets_packet, "summary_alerts_widget")

    depth_value = _latest_value(depth_rows)
    trade_value = _latest_value(trade_rows, "market.trades")
    spread_value = _latest_value(spread_rows, "market.spread")
    liquidity_value = _latest_value(spread_rows, "market.liquidity")
    lifecycle_value = _latest_value(lifecycle_rows)
    summary_value = _latest_value(summary_rows, "warroom.summary")
    alert_value = _latest_value(summary_rows, "warroom.alerts")

    best_bid = depth_value.get("best_bid")
    best_ask = depth_value.get("best_ask")
    spread = _spread_value(spread_value.get("spread", depth_value.get("spread")), best_bid, best_ask)
    spread_bps = _spread_bps(spread, best_bid, best_ask, spread_value.get("spread_bps"))
    bid_f = _as_float(best_bid)
    ask_f = _as_float(best_ask)
    mid = ((bid_f + ask_f) / 2.0) if bid_f is not None and ask_f is not None else None

    market_states = {
        "depth": _widget_state(widgets_packet, "market_depth_widget"),
        "trades": _widget_state(widgets_packet, "recent_trades_widget"),
        "spread_liquidity": _widget_state(widgets_packet, "spread_liquidity_widget"),
        "receiver": _widget_state(widgets_packet, "receiver_lifecycle_widget"),
        "summary_alerts": _widget_state(widgets_packet, "summary_alerts_widget"),
    }
    alert_count = int(alert_value.get("alert_count") or 0) if isinstance(alert_value.get("alert_count", 0), (int, float, str)) else 0
    return {
        "ok": True,
        "packet_kind": "warroom_v2_rt_market_strip_packet",
        "version": MARKET_TOP_STRIP_VERSION,
        "display_source": widgets_packet.get("display_source", "live"),
        "symbol": depth_value.get("symbol") or spread_value.get("symbol") or liquidity_value.get("symbol") or "--",
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid_price": mid,
        "spread": spread,
        "spread_bps": spread_bps,
        "last_price": trade_value.get("last_price"),
        "last_size": trade_value.get("last_size"),
        "last_side": trade_value.get("side"),
        "liquidity_state": liquidity_value.get("liquidity_state") or liquidity_value.get("lane_state") or "--",
        "depth_score": liquidity_value.get("depth_score"),
        "bid_levels": liquidity_value.get("bid_levels"),
        "ask_levels": liquidity_value.get("ask_levels"),
        "market_uid": depth_value.get("market_uid"),
        "source": depth_value.get("source") or spread_value.get("source") or liquidity_value.get("source"),
        "receiver_status": lifecycle_value.get("status", "waiting"),
        "last_event_ts": lifecycle_value.get("last_event_ts") or summary_value.get("last_event_ts"),
        "summary": summary_value.get("summary"),
        "alert_count": alert_count,
        "highest_alert_level": alert_value.get("highest_level", "info"),
        "last_error": alert_value.get("last_error"),
        "live_widget_count": int(widgets_packet.get("live_widget_count") or 0),
        "market_states": market_states,
        "read_only": True,
        "manual_trade_support": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def _fmt_price(value: object) -> str:
    numeric = _as_float(value)
    if numeric is not None:
        return f"{numeric:,.0f}"
    return "--"


def _fmt_size(value: object) -> str:
    numeric = _as_float(value)
    if numeric is not None:
        return f"{numeric:.4f}"
    return "--"


def _fmt_bps(value: object) -> str:
    numeric = _as_float(value)
    if numeric is not None:
        return f"{numeric:.2f} bps"
    return "--"


def _side_label(value: object) -> str:
    side = str(value or "").strip().lower()
    if side == "buy":
        return "BUY"
    if side == "sell":
        return "SELL"
    return "未接続"


def _state_label(value: object) -> str:
    state = str(value or "--")
    mapping = {
        "live": "ライブ",
        "receiving": "受信中",
        "normal": "通常",
        "attention": "注意",
        "stale": "古い",
        "slow": "遅延",
        "waiting": "待機",
        "not_started": "未開始",
        "info": "情報",
        "error": "異常",
    }
    return mapping.get(state, state)


def _source_label(value: object) -> str:
    source = str(value or "")
    if source == "dhot_unified_market_state":
        return "D-hot統合市場状態"
    return source or "--"


def _receiver_label(value: object) -> str:
    status = str(value or "waiting")
    if status in {"receiving", "live"}:
        return "🟢 受信中"
    if status in {"slow", "attention", "stale"}:
        return f"🟡 {_state_label(status)}"
    if status in {"error", "failed"}:
        return f"🔴 {_state_label(status)}"
    return f"⚪ {_state_label(status)}"


def _metric(column: Any, label: str, value: str, help_text: str, *, delta: str | None = None) -> None:
    try:
        column.metric(label, value, delta=delta, help=help_text)
    except TypeError:
        if delta is not None:
            try:
                column.metric(label, value, delta=delta)
                return
            except TypeError:
                pass
        column.metric(label, value)


def _state_summary(states: Mapping[str, Any]) -> str:
    return " / ".join(f"{key}={value}" for key, value in states.items())


def render_market_strip(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("市場データ: 手動取引用の必須情報 / コンパクト表示 / 読み取り専用 / broker送信なし")
    cols = st_api.columns(8)
    _metric(cols[0], "銘柄", str(packet.get("symbol") or "--"), "取引対象。現在は Collector/D-hot 由来の市場状態を表示します。")
    _metric(cols[1], "買気配", _fmt_price(packet.get("best_bid")), "最良買い気配。成行で売る場合に近い価格の目安です。")
    _metric(cols[2], "売気配", _fmt_price(packet.get("best_ask")), "最良売り気配。成行で買う場合に近い価格の目安です。")
    _metric(cols[3], "中心値", _fmt_price(packet.get("mid_price")), "買気配と売気配の中間値。短期判断の基準線として使います。")
    _metric(cols[4], "スプレッド", _fmt_price(packet.get("spread")), "売気配 - 買気配。広がるほど約定コストと滑りリスクが上がります。", delta=_fmt_bps(packet.get("spread_bps")))
    _metric(cols[5], "直近約定", _fmt_price(packet.get("last_price")), "直近約定価格。約定ストリーム未接続時は未接続表示になります。")
    _metric(cols[6], "約定方向", f"{_side_label(packet.get('last_side'))} {_fmt_size(packet.get('last_size'))}", "直近約定の方向とサイズ。約定ストリーム未接続時は未接続表示です。")
    _metric(cols[7], "受信状態", _receiver_label(packet.get("receiver_status")), "Push/Collector からの観測状態。古い表示の時は最終観測値として扱います。")

    compact_context = " / ".join(
        [
            f"流動性={_state_label(packet.get('liquidity_state'))}",
            f"板厚スコア={packet.get('depth_score') if packet.get('depth_score') is not None else '--'}",
            f"警告={packet.get('alert_count', 0)}:{_state_label(packet.get('highest_alert_level') or 'info')}",
            f"最終更新={packet.get('last_event_ts') or '--'}",
            f"データ源={_source_label(packet.get('source'))}",
        ]
    )
    st_api.caption(compact_context)
    with st_api.expander("市場データの詳細", expanded=False):
        st_api.dataframe(
            [
                {"項目": "市場UID", "値": str(packet.get("market_uid") or "--")},
                {"項目": "買い板段数", "値": str(packet.get("bid_levels") or "--")},
                {"項目": "売り板段数", "値": str(packet.get("ask_levels") or "--")},
                {"項目": "ウィジェット状態", "値": _state_summary(packet.get("market_states", {}))},
                {"項目": "要約", "値": str(packet.get("summary") or "--")},
                {"項目": "最終エラー", "値": str(packet.get("last_error") or "--")},
                {"項目": "安全境界", "値": "read_only=true / broker_send_enabled=false / prediction_invoked=false / classifier_invoked=false"},
            ],
            width="stretch",
        )
    return {
        "ok": True,
        "market_top_strip_version": MARKET_TOP_STRIP_VERSION,
        "market_strip_rendered": True,
        "compact_horizontal_strip": True,
        "tooltip_help_ready": True,
        "read_only": True,
        "broker_send_enabled": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
