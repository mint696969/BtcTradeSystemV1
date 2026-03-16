# path: ./btcts_next/src/btcts/collector_vnext/tradeflow/trade_events.py
# desc: Detect trade-flow based market events.

from __future__ import annotations

from typing import Dict, List


def trade_flow_events(metrics: Dict) -> List[Dict]:

    events: List[Dict] = []

    buy_volume = metrics["buy_volume"]
    sell_volume = metrics["sell_volume"]
    trade_count = metrics["trade_count"]
    delta = metrics["trade_delta"]

    if trade_count >= 20:
        events.append(
            {
                "event_name": "trade_surge",
                "trade_count": trade_count,
            }
        )

    if delta > 5:
        events.append(
            {
                "event_name": "aggressive_buy",
                "delta": delta,
                "buy_volume": buy_volume,
                "sell_volume": sell_volume,
            }
        )

    if delta < -5:
        events.append(
            {
                "event_name": "aggressive_sell",
                "delta": delta,
                "buy_volume": buy_volume,
                "sell_volume": sell_volume,
            }
        )

    return events