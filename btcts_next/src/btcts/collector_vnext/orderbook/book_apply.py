# path: ./btcts_next/src/btcts/collector_vnext/orderbook/book_apply.py
# desc: Apply orderbook delta updates to OrderBookState.

from __future__ import annotations

from .book_state import OrderBookState


def apply_delta(book: OrderBookState, bids, asks):

    if bids:

        for r in bids:

            price = float(r["price"])
            size = float(r["size"])

            if size == 0:
                book.bids.pop(price, None)
            else:
                book.bids[price] = size

    if asks:

        for r in asks:

            price = float(r["price"])
            size = float(r["size"])

            if size == 0:
                book.asks.pop(price, None)
            else:
                book.asks[price] = size