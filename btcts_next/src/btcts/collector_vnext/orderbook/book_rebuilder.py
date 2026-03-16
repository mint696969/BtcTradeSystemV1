# path: ./btcts_next/src/btcts/collector_vnext/orderbook/book_rebuilder.py
# desc: Rebuild orderbook state from snapshot + deltas.

from __future__ import annotations

from typing import Dict

from .book_state import OrderBookState
from .book_apply import apply_delta


class OrderBookRebuilder:

    def __init__(self):

        self.book = OrderBookState()

        self.snapshot_loaded = False

    def apply_event(self, event: Dict):

        event_type = event.get("event_type")

        bids = event.get("bids")
        asks = event.get("asks")

        if event_type == "snapshot":

            self.book.set_snapshot(bids, asks)
            self.snapshot_loaded = True
            return

        if event_type == "delta":

            if not self.snapshot_loaded:
                return

            apply_delta(self.book, bids, asks)

    def best_bid(self):

        return self.book.best_bid()

    def best_ask(self):

        return self.book.best_ask()