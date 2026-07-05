# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/trade_strip_view.py
# desc: Thin trade/order/position/PnL strip placeholder. Read-only and safe until real order state is connected.

from __future__ import annotations

from typing import Any, Mapping


def build_trade_strip_packet(runtime_status: Mapping[str, Any], bridge_packet: Mapping[str, Any]) -> dict[str, Any]:
    return {"ok": True, "packet_kind": "warroom_v2_rt_trade_strip_packet", "display_source": "waiting", "orders_connected": False, "positions_connected": False, "pnl_connected": False, "read_only": True, "broker_send_enabled": False, "order_intent_submitted": False, "ledger_append_allowed": False, "summary": "orders / position / PnL lane is reserved and waiting for read-only trade-state source", "runtime_connected": bool(runtime_status.get("receiver_runtime_started")), "messages_applied": int(bridge_packet.get("messages_applied") or 0)}


def render_trade_strip(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    st_api.caption("Trade strip: orders / position / after-fill PnL / read-only / no broker action")
    c1, c2, c3, c4 = st_api.columns(4)
    c1.metric("Orders", "waiting")
    c2.metric("Position", "waiting")
    c3.metric("PnL after fill", "waiting")
    c4.metric("Action", "read-only")
    st_api.caption(str(packet.get("summary") or ""))
    return {"ok": True, "trade_strip_rendered": True, "read_only": True, "broker_send_enabled": False, "order_intent_submitted": False}
