# path: ./btcts_next/src/btcts/collector_vnext/tradeflow/trade_metrics.py
# desc: Compute trade flow metrics from aggregated trades.

from __future__ import annotations

from typing import Dict, List


def trade_metrics(trades: List[Dict]) -> Dict:

    buy_volume = 0.0
    sell_volume = 0.0
    trade_count = len(trades)

    price_sum = 0.0

    for t in trades:

        size = float(t.get("size", 0))
        price = float(t.get("price", 0))
        side = t.get("side")

        price_sum += price

        if side == "buy":
            buy_volume += size
        else:
            sell_volume += size

    avg_price = None
    if trade_count > 0:
        avg_price = price_sum / trade_count

    delta = buy_volume - sell_volume

    return {
        "trade_count": trade_count,
        "buy_volume": buy_volume,
        "sell_volume": sell_volume,
        "trade_delta": delta,
        "avg_price": avg_price,
    }