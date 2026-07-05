# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/trade_strip_view.py
# desc: Thin trade/order/position/PnL strip for WarRoom v2 cockpit. Read-only until a trusted trade-state source is connected.

from __future__ import annotations

from typing import Any, Mapping

TRADE_SECOND_STRIP_VERSION = "warroom_v2_trade_second_strip.2026_07_05.v1"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_mapping(*values: object) -> Mapping[str, Any]:
    for value in values:
        if isinstance(value, Mapping) and value:
            return value
    return {}


def _as_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        if isinstance(value, str) and value.strip():
            return float(value)
    except ValueError:
        return None
    return None


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    try:
        if isinstance(value, str) and value.strip():
            return int(float(value))
    except ValueError:
        return default
    return default


def _fmt_price(value: object) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "--"
    return f"{numeric:,.0f}"


def _fmt_size(value: object) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "--"
    return f"{numeric:.4f}"


def _fmt_pnl(value: object) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "--"
    sign = "+" if numeric > 0 else ""
    return f"{sign}{numeric:,.0f}"


def _position_label(side: object, size: object) -> str:
    size_f = _as_float(size)
    if size_f is None or size_f == 0:
        return "flat"
    side_label = str(side or "position").upper()
    return f"{side_label} {_fmt_size(size)}"


def _orders_label(active_count: object, pending_count: object) -> str:
    active = _as_int(active_count, 0)
    pending = _as_int(pending_count, 0)
    if active <= 0 and pending <= 0:
        return "none"
    return f"active {active} / pending {pending}"


def _confirm_label(order_state: Mapping[str, Any]) -> str:
    for key in ("confirmed_at", "last_confirmed_at", "accepted_at", "last_order_confirmed_at"):
        value = order_state.get(key)
        if value:
            return str(value)
    return "--"


def _source_label(*sources: Mapping[str, Any]) -> str:
    for source in sources:
        value = source.get("source") or source.get("data_source") or source.get("trade_state_source")
        if value:
            return str(value)
    return "not connected"


def build_trade_strip_packet(runtime_status: Mapping[str, Any], bridge_packet: Mapping[str, Any]) -> dict[str, Any]:
    trade_state = _first_mapping(
        bridge_packet.get("trade_state"),
        bridge_packet.get("read_only_trade_state"),
        bridge_packet.get("orders_positions_pnl"),
        runtime_status.get("trade_state"),
    )
    order_state = _first_mapping(trade_state.get("orders"), trade_state.get("order_state"), bridge_packet.get("order_state"))
    position_state = _first_mapping(trade_state.get("position"), trade_state.get("position_state"), bridge_packet.get("position_state"))
    pnl_state = _first_mapping(trade_state.get("pnl"), trade_state.get("pnl_state"), bridge_packet.get("pnl_state"))

    active_orders = order_state.get("active_count", order_state.get("active_orders", 0))
    pending_orders = order_state.get("pending_count", order_state.get("pending_orders", 0))
    position_size = position_state.get("size", position_state.get("position_size", 0))
    position_side = position_state.get("side", position_state.get("position_side", ""))
    entry_price = position_state.get("entry_price", position_state.get("average_price", position_state.get("avg_price")))
    mark_price = position_state.get("mark_price", position_state.get("last_price"))
    unrealized_pnl = pnl_state.get("unrealized", pnl_state.get("unrealized_pnl"))
    realized_pnl = pnl_state.get("realized", pnl_state.get("realized_pnl"))
    after_fill_pnl = pnl_state.get("after_fill", pnl_state.get("after_fill_pnl", unrealized_pnl))

    orders_connected = bool(order_state)
    positions_connected = bool(position_state)
    pnl_connected = bool(pnl_state)
    data_connected = bool(orders_connected or positions_connected or pnl_connected)
    runtime_connected = bool(runtime_status.get("receiver_runtime_started"))
    messages_applied = _as_int(bridge_packet.get("messages_applied"), 0)
    summary = (
        "read-only trade-state source connected"
        if data_connected
        else "orders / position / PnL lane is reserved and waiting for trusted read-only trade-state source"
    )

    return {
        "ok": True,
        "packet_kind": "warroom_v2_rt_trade_strip_packet",
        "version": TRADE_SECOND_STRIP_VERSION,
        "display_source": "read_only_trade_state" if data_connected else "waiting",
        "orders_connected": orders_connected,
        "positions_connected": positions_connected,
        "pnl_connected": pnl_connected,
        "trade_data_connected": data_connected,
        "active_orders": _as_int(active_orders, 0),
        "pending_orders": _as_int(pending_orders, 0),
        "last_order_id": order_state.get("last_order_id") or order_state.get("order_id"),
        "confirmed_at": _confirm_label(order_state),
        "position_side": position_side,
        "position_size": position_size,
        "entry_price": entry_price,
        "mark_price": mark_price,
        "unrealized_pnl": unrealized_pnl,
        "realized_pnl": realized_pnl,
        "after_fill_pnl": after_fill_pnl,
        "trade_state_source": _source_label(trade_state, order_state, position_state, pnl_state),
        "summary": summary,
        "runtime_connected": runtime_connected,
        "messages_applied": messages_applied,
        "read_only": True,
        "manual_trade_support": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "auto_trading_enabled": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


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


def render_trade_strip(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("Trade second strip: orders / position / confirmation / PnL / compact / read-only")
    cols = st_api.columns(8)
    _metric(cols[0], "Orders", _orders_label(packet.get("active_orders"), packet.get("pending_orders")), "未約定・待機中注文の数。未接続時は none ではなく source caption で waiting を確認します。")
    _metric(cols[1], "Confirmed", str(packet.get("confirmed_at") or "--"), "直近の注文受付・確定日時。手動判断の時刻整合に使います。")
    _metric(cols[2], "Position", _position_label(packet.get("position_side"), packet.get("position_size")), "現在建玉の方向とサイズ。未接続またはゼロなら flat と表示します。")
    _metric(cols[3], "Entry", _fmt_price(packet.get("entry_price")), "建玉の平均取得価格または約定基準価格。")
    _metric(cols[4], "Mark", _fmt_price(packet.get("mark_price")), "評価価格。未接続時は -- です。")
    _metric(cols[5], "U-PnL", _fmt_pnl(packet.get("unrealized_pnl")), "未実現損益。現在価格で評価した含み損益です。")
    _metric(cols[6], "R-PnL", _fmt_pnl(packet.get("realized_pnl")), "実現済み損益。決済済みの損益です。")
    _metric(cols[7], "After fill", _fmt_pnl(packet.get("after_fill_pnl")), "注文が約定した後の想定/反映損益。信頼できる read-only source 接続後に有効化します。")

    st_api.caption(
        " / ".join(
            [
                f"source={packet.get('trade_state_source') or 'not connected'}",
                f"orders_connected={bool(packet.get('orders_connected'))}",
                f"positions_connected={bool(packet.get('positions_connected'))}",
                f"pnl_connected={bool(packet.get('pnl_connected'))}",
                f"messages_applied={packet.get('messages_applied', 0)}",
                "broker_send_enabled=false",
                "order_intent_submitted=false",
            ]
        )
    )
    with st_api.expander("Trade second strip details", expanded=False):
        st_api.dataframe(
            [
                {"key": "last_order_id", "value": str(packet.get("last_order_id") or "--")},
                {"key": "display_source", "value": str(packet.get("display_source") or "waiting")},
                {"key": "summary", "value": str(packet.get("summary") or "")},
                {"key": "safety", "value": "read_only=true / broker_send_enabled=false / ledger_append_allowed=false / auto_trading_enabled=false"},
            ],
            width="stretch",
        )
    return {
        "ok": True,
        "trade_second_strip_version": TRADE_SECOND_STRIP_VERSION,
        "trade_strip_rendered": True,
        "compact_horizontal_strip": True,
        "tooltip_help_ready": True,
        "read_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "auto_trading_enabled": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
