# path: ./btcts_next/src/btcts/collector_vnext/orderbook/book_metrics.py
# desc: Core market microstructure metrics computed from reconstructed orderbook state.

from __future__ import annotations

from typing import Dict, Optional

from .book_state import OrderBookState


def orderbook_imbalance(book: OrderBookState, *, levels: int = 10) -> Optional[float]:
    bid_size = book.depth_size(side="bid", levels=levels)
    ask_size = book.depth_size(side="ask", levels=levels)

    total = bid_size + ask_size
    if total <= 0:
        return None

    return (bid_size - ask_size) / total


def depth_summary(book: OrderBookState, *, levels: int = 10) -> Dict[str, Optional[float]]:
    bid_size = book.depth_size(side="bid", levels=levels)
    ask_size = book.depth_size(side="ask", levels=levels)

    return {
        "levels": levels,
        "bid_depth": bid_size,
        "ask_depth": ask_size,
        "imbalance": orderbook_imbalance(book, levels=levels),
        "best_bid": book.best_bid(),
        "best_ask": book.best_ask(),
        "spread": book.spread(),
        "mid": book.mid(),
    }


def largest_wall(book: OrderBookState, *, side: str, levels: int = 20) -> Optional[Dict[str, float]]:
    if side == "bid":
        rows = book.top_bids(levels)
    elif side == "ask":
        rows = book.top_asks(levels)
    else:
        return None

    if not rows:
        return None

    best = max(rows, key=lambda row: float(row["size"]))
    return {
        "side": side,
        "price": float(best["price"]),
        "size": float(best["size"]),
    }


def wall_ratio(book: OrderBookState, *, side: str, levels: int = 20) -> Optional[float]:
    wall = largest_wall(book, side=side, levels=levels)
    if wall is None:
        return None

    total = book.depth_size(side=side, levels=levels)
    if total <= 0:
        return None

    return float(wall["size"]) / total