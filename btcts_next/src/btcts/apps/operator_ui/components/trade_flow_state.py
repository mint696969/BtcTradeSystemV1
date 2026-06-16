# path: ./btcts_next/src/btcts/apps/operator_ui/components/trade_flow_state.py
# desc: Trade flow monitor state adapter for execution-market live tradeflow only.

from __future__ import annotations

from btcts.apps.operator_ui.components.live_bridge import (
    recent_live_tradeflow_metrics,
)
from btcts.apps.operator_ui.components.market_state_bridge import execution_market_context


def build_trade_flow_state() -> dict | None:
    ctx = execution_market_context()
    live_flow = recent_live_tradeflow_metrics(
        exchange=str(ctx["exchange"]),
        symbol=str(ctx["symbol_raw"]),
        lines=80,
    )
    if not live_flow:
        return None

    return {
        "buy_volume": live_flow.get("buy_size"),
        "sell_volume": live_flow.get("sell_size"),
        "trade_delta": live_flow.get("delta"),
        "trade_count": live_flow.get("trade_count"),
        "event_ts": live_flow.get("event_ts"),
        "micro_event_names": [],
        "source_label": "execution_market_live_canonical",
        "data_source": "execution_market_live_canonical",
        "product_code": ctx["product_code"],
        "market_uid": ctx["market_uid"],
    }
