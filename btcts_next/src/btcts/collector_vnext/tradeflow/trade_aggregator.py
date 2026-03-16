# path: ./btcts_next/src/btcts/collector_vnext/tradeflow/trade_aggregator.py
# desc: Aggregate trades into time-window buckets.

from __future__ import annotations

from typing import Dict, List


class TradeAggregator:

    def __init__(self, window_size: float = 1.0):
        self.window_size = window_size
        self.buffer: List[Dict] = []

    def add_trade(self, trade: Dict) -> None:
        self.buffer.append(trade)

    def flush(self) -> List[Dict]:
        trades = self.buffer
        self.buffer = []
        return trades