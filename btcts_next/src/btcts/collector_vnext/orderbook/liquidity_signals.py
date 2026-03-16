# path: ./btcts_next/src/btcts/collector_vnext/orderbook/liquidity_signals.py
# desc: Liquidity signal extraction from reconstructed orderbook state and state transitions.

from __future__ import annotations

from typing import Dict, Optional

from .book_metrics import depth_summary, largest_wall, wall_ratio
from .book_state import OrderBookState


def liquidity_pressure_signal(book: OrderBookState, *, levels: int = 10) -> Dict[str, Optional[float | str]]:
    summary = depth_summary(book, levels=levels)
    imbalance = summary["imbalance"]

    bias = "neutral"
    if imbalance is not None:
        if imbalance >= 0.20:
            bias = "buy_pressure"
        elif imbalance <= -0.20:
            bias = "sell_pressure"

    return {
        "signal": "liquidity_pressure",
        "bias": bias,
        "levels": levels,
        "imbalance": imbalance,
        "bid_depth": summary["bid_depth"],
        "ask_depth": summary["ask_depth"],
        "spread": summary["spread"],
        "mid": summary["mid"],
    }


def wall_signal(book: OrderBookState, *, levels: int = 20, wall_ratio_threshold: float = 0.30) -> Dict[str, Optional[float | str | bool]]:
    bid_wall = largest_wall(book, side="bid", levels=levels)
    ask_wall = largest_wall(book, side="ask", levels=levels)

    bid_ratio = wall_ratio(book, side="bid", levels=levels)
    ask_ratio = wall_ratio(book, side="ask", levels=levels)

    strongest_side = None
    strongest_ratio = None

    if bid_ratio is not None and ask_ratio is not None:
        if bid_ratio >= ask_ratio:
            strongest_side = "bid"
            strongest_ratio = bid_ratio
        else:
            strongest_side = "ask"
            strongest_ratio = ask_ratio
    elif bid_ratio is not None:
        strongest_side = "bid"
        strongest_ratio = bid_ratio
    elif ask_ratio is not None:
        strongest_side = "ask"
        strongest_ratio = ask_ratio

    wall_detected = bool(strongest_ratio is not None and strongest_ratio >= wall_ratio_threshold)

    return {
        "signal": "wall",
        "levels": levels,
        "wall_detected": wall_detected,
        "strongest_side": strongest_side,
        "strongest_ratio": strongest_ratio,
        "bid_wall_price": None if bid_wall is None else bid_wall["price"],
        "bid_wall_size": None if bid_wall is None else bid_wall["size"],
        "ask_wall_price": None if ask_wall is None else ask_wall["price"],
        "ask_wall_size": None if ask_wall is None else ask_wall["size"],
    }


def liquidity_pull_signal(
    prev_book: OrderBookState,
    curr_book: OrderBookState,
    *,
    side: str,
    levels: int = 10,
    pull_threshold: float = 0.20,
) -> Dict[str, Optional[float | str | bool]]:
    prev_depth = prev_book.depth_size(side=side, levels=levels)
    curr_depth = curr_book.depth_size(side=side, levels=levels)

    removed = max(prev_depth - curr_depth, 0.0)
    ratio = None
    if prev_depth > 0:
        ratio = removed / prev_depth

    signal_name = f"{side}_liquidity_pull"
    detected = bool(ratio is not None and ratio >= pull_threshold)

    return {
        "signal": signal_name,
        "side": side,
        "levels": levels,
        "detected": detected,
        "prev_depth": prev_depth,
        "curr_depth": curr_depth,
        "removed_depth": removed,
        "removed_ratio": ratio,
    }