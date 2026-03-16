# path: ./btcts_next/src/btcts/collector_vnext/orderbook/book_state.py
# desc: In-memory orderbook state representation with helper methods for analytics.

from __future__ import annotations

from typing import Dict, List, Optional


class OrderBookState:
    def __init__(self):
        self.bids: Dict[float, float] = {}
        self.asks: Dict[float, float] = {}
        self.last_update_ts: Optional[str] = None

    def clone(self) -> "OrderBookState":
        other = OrderBookState()
        other.bids = dict(self.bids)
        other.asks = dict(self.asks)
        other.last_update_ts = self.last_update_ts
        return other

    def clear(self) -> None:
        self.bids.clear()
        self.asks.clear()
        self.last_update_ts = None

    def set_snapshot(self, bids, asks, *, update_ts: Optional[str] = None) -> None:
        self.clear()

        for row in bids or []:
            self.bids[float(row["price"])] = float(row["size"])

        for row in asks or []:
            self.asks[float(row["price"])] = float(row["size"])

        self.last_update_ts = update_ts

    def best_bid(self) -> Optional[float]:
        if not self.bids:
            return None
        return max(self.bids.keys())

    def best_ask(self) -> Optional[float]:
        if not self.asks:
            return None
        return min(self.asks.keys())

    def spread(self) -> Optional[float]:
        bid = self.best_bid()
        ask = self.best_ask()
        if bid is None or ask is None:
            return None
        return ask - bid

    def mid(self) -> Optional[float]:
        bid = self.best_bid()
        ask = self.best_ask()
        if bid is None or ask is None:
            return None
        return (bid + ask) / 2.0

    def sorted_bids(self) -> List[Dict[str, float]]:
        return [
            {"price": price, "size": self.bids[price]}
            for price in sorted(self.bids.keys(), reverse=True)
        ]

    def sorted_asks(self) -> List[Dict[str, float]]:
        return [
            {"price": price, "size": self.asks[price]}
            for price in sorted(self.asks.keys())
        ]

    def top_bids(self, depth: int = 10) -> List[Dict[str, float]]:
        return self.sorted_bids()[: max(depth, 0)]

    def top_asks(self, depth: int = 10) -> List[Dict[str, float]]:
        return self.sorted_asks()[: max(depth, 0)]

    def depth_size(self, *, side: str, levels: int = 10) -> float:
        if side == "bid":
            rows = self.top_bids(levels)
        elif side == "ask":
            rows = self.top_asks(levels)
        else:
            return 0.0

        return sum(float(row["size"]) for row in rows)

    def level_count(self, *, side: str) -> int:
        if side == "bid":
            return len(self.bids)
        if side == "ask":
            return len(self.asks)
        return 0