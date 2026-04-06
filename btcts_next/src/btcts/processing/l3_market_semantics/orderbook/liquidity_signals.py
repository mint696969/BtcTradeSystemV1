# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_signals.py
# desc: Liquidity signal extraction from reconstructed orderbook state and state transitions.

from __future__ import annotations

from typing import Dict, Optional

from btcts.ingestion.l2_canonical.orderbook.book_state import OrderBookState
from btcts.processing.features.orderbook.book_features import depth_summary, largest_wall, wall_ratio


def _top_side_rows(book: OrderBookState, *, side: str, levels: int) -> list[dict[str, float]]:
    if side == "bid":
        return book.top_bids(levels)
    if side == "ask":
        return book.top_asks(levels)
    return []


def _wall_rank_and_distance(
    book: OrderBookState,
    *,
    side: str,
    wall_price: float | None,
    levels: int,
) -> tuple[int | None, float | None]:
    if wall_price is None:
        return None, None

    rows = _top_side_rows(book, side=side, levels=levels)
    if not rows:
        return None, None

    best_price = rows[0]["price"]
    for idx, row in enumerate(rows, start=1):
        if float(row["price"]) != float(wall_price):
            continue

        if side == "bid":
            distance_from_best = max(float(best_price) - float(wall_price), 0.0)
        else:
            distance_from_best = max(float(wall_price) - float(best_price), 0.0)

        return idx, distance_from_best

    return None, None


def _largest_wall_in_rank_window(
    book: OrderBookState,
    *,
    side: str,
    levels: int,
    rank_limit: int,
) -> Optional[Dict[str, float]]:
    rows = _top_side_rows(book, side=side, levels=levels)
    if not rows:
        return None

    rank_limit = max(1, min(rank_limit, len(rows)))
    limited_rows = rows[:rank_limit]
    if not limited_rows:
        return None

    best = max(limited_rows, key=lambda row: float(row["size"]))
    return {
        "side": side,
        "price": float(best["price"]),
        "size": float(best["size"]),
    }


def _wall_ratio_for_window(
    book: OrderBookState,
    *,
    wall: Optional[Dict[str, float]],
    side: str,
    denominator_levels: int,
) -> Optional[float]:
    if wall is None:
        return None

    total = book.depth_size(side=side, levels=denominator_levels)
    if total <= 0:
        return None

    return float(wall["size"]) / total


def liquidity_pressure_signal(
    book: OrderBookState,
    *,
    levels: int = 10,
    pressure_threshold: float = 0.20,
) -> Dict[str, Optional[float | str]]:
    summary = depth_summary(book, levels=levels)
    imbalance = summary["imbalance"]

    bias = "neutral"
    if imbalance is not None:
        if imbalance >= pressure_threshold:
            bias = "buy_pressure"
        elif imbalance <= -pressure_threshold:
            bias = "sell_pressure"

    return {
        "signal": "liquidity_pressure",
        "bias": bias,
        "levels": levels,
        "pressure_threshold": pressure_threshold,
        "imbalance": imbalance,
        "bid_depth": summary["bid_depth"],
        "ask_depth": summary["ask_depth"],
        "spread": summary["spread"],
        "mid": summary["mid"],
    }


def wall_signal(
    book: OrderBookState,
    *,
    levels: int = 20,
    wall_ratio_threshold: float = 0.30,
    near_rank_threshold: int = 3,
) -> Dict[str, Optional[float | str | bool]]:
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

    bid_wall_price = None if bid_wall is None else float(bid_wall["price"])
    ask_wall_price = None if ask_wall is None else float(ask_wall["price"])

    strongest_wall_price = None
    if strongest_side == "bid":
        strongest_wall_price = bid_wall_price
    elif strongest_side == "ask":
        strongest_wall_price = ask_wall_price

    strongest_rank, strongest_distance_from_best = _wall_rank_and_distance(
        book,
        side=str(strongest_side or ""),
        wall_price=strongest_wall_price,
        levels=levels,
    )

    strongest_is_near = bool(
        strongest_rank is not None and strongest_rank <= near_rank_threshold
    )

    near_depth_levels = max(1, min(near_rank_threshold, levels))

    near_bid_wall = _largest_wall_in_rank_window(
        book,
        side="bid",
        levels=levels,
        rank_limit=near_depth_levels,
    )
    near_ask_wall = _largest_wall_in_rank_window(
        book,
        side="ask",
        levels=levels,
        rank_limit=near_depth_levels,
    )

    near_bid_ratio = _wall_ratio_for_window(
        book,
        wall=near_bid_wall,
        side="bid",
        denominator_levels=levels,
    )
    near_ask_ratio = _wall_ratio_for_window(
        book,
        wall=near_ask_wall,
        side="ask",
        denominator_levels=levels,
    )

    near_strongest_side = None
    near_strongest_ratio = None

    if near_bid_ratio is not None and near_ask_ratio is not None:
        if near_bid_ratio >= near_ask_ratio:
            near_strongest_side = "bid"
            near_strongest_ratio = near_bid_ratio
        else:
            near_strongest_side = "ask"
            near_strongest_ratio = near_ask_ratio
    elif near_bid_ratio is not None:
        near_strongest_side = "bid"
        near_strongest_ratio = near_bid_ratio
    elif near_ask_ratio is not None:
        near_strongest_side = "ask"
        near_strongest_ratio = near_ask_ratio

    near_wall_detected = bool(
        near_strongest_ratio is not None and near_strongest_ratio >= wall_ratio_threshold
    )

    near_bid_wall_price = None if near_bid_wall is None else float(near_bid_wall["price"])
    near_ask_wall_price = None if near_ask_wall is None else float(near_ask_wall["price"])

    near_strongest_wall_price = None
    if near_strongest_side == "bid":
        near_strongest_wall_price = near_bid_wall_price
    elif near_strongest_side == "ask":
        near_strongest_wall_price = near_ask_wall_price

    near_strongest_rank, near_strongest_distance_from_best = _wall_rank_and_distance(
        book,
        side=str(near_strongest_side or ""),
        wall_price=near_strongest_wall_price,
        levels=levels,
    )

    return {
        "signal": "wall",
        "levels": levels,
        "wall_ratio_threshold": wall_ratio_threshold,
        "near_rank_threshold": near_rank_threshold,
        "near_depth_levels": near_depth_levels,
        "wall_detected": wall_detected,
        "strongest_side": strongest_side,
        "strongest_ratio": strongest_ratio,
        "strongest_rank": strongest_rank,
        "strongest_distance_from_best": strongest_distance_from_best,
        "strongest_is_near": strongest_is_near,
        "bid_wall_price": bid_wall_price,
        "bid_wall_size": None if bid_wall is None else bid_wall["size"],
        "ask_wall_price": ask_wall_price,
        "ask_wall_size": None if ask_wall is None else ask_wall["size"],
        "near_wall_detected": near_wall_detected,
        "near_strongest_side": near_strongest_side,
        "near_strongest_ratio": near_strongest_ratio,
        "near_strongest_rank": near_strongest_rank,
        "near_strongest_distance_from_best": near_strongest_distance_from_best,
        "near_bid_wall_price": near_bid_wall_price,
        "near_bid_wall_size": None if near_bid_wall is None else near_bid_wall["size"],
        "near_ask_wall_price": near_ask_wall_price,
        "near_ask_wall_size": None if near_ask_wall is None else near_ask_wall["size"],
    }


def liquidity_pull_signal(
    prev_book: OrderBookState,
    curr_book: OrderBookState,
    *,
    side: str,
    levels: int = 10,
    pull_threshold: float = 0.20,
    near_levels: int = 3,
    strong_pull_threshold: float = 0.40,
) -> Dict[str, Optional[float | str | bool]]:
    prev_depth = prev_book.depth_size(side=side, levels=levels)
    curr_depth = curr_book.depth_size(side=side, levels=levels)

    removed = max(prev_depth - curr_depth, 0.0)
    ratio = None
    if prev_depth > 0:
        ratio = removed / prev_depth

    near_depth_levels = max(1, min(near_levels, levels))
    prev_near_depth = prev_book.depth_size(side=side, levels=near_depth_levels)
    curr_near_depth = curr_book.depth_size(side=side, levels=near_depth_levels)

    near_removed = max(prev_near_depth - curr_near_depth, 0.0)
    near_ratio = None
    if prev_near_depth > 0:
        near_ratio = near_removed / prev_near_depth

    prev_rows = _top_side_rows(prev_book, side=side, levels=near_depth_levels)
    curr_rows = _top_side_rows(curr_book, side=side, levels=near_depth_levels)

    best_price_before = prev_rows[0]["price"] if prev_rows else None
    best_price_after = curr_rows[0]["price"] if curr_rows else None
    best_price_changed = best_price_before != best_price_after

    signal_name = f"{side}_liquidity_pull"
    detected = bool(ratio is not None and ratio >= pull_threshold)

    pull_strength = "none"
    if detected:
        if (
            (ratio is not None and ratio >= strong_pull_threshold)
            or (near_ratio is not None and near_ratio >= strong_pull_threshold)
        ):
            pull_strength = "strong"
        else:
            pull_strength = "moderate"

    return {
        "signal": signal_name,
        "side": side,
        "levels": levels,
        "near_levels": near_depth_levels,
        "pull_threshold": pull_threshold,
        "strong_pull_threshold": strong_pull_threshold,
        "detected": detected,
        "pull_strength": pull_strength,
        "prev_depth": prev_depth,
        "curr_depth": curr_depth,
        "removed_depth": removed,
        "removed_ratio": ratio,
        "prev_near_depth": prev_near_depth,
        "curr_near_depth": curr_near_depth,
        "near_removed_depth": near_removed,
        "near_removed_ratio": near_ratio,
        "best_price_before": best_price_before,
        "best_price_after": best_price_after,
        "best_price_changed": best_price_changed,
    }