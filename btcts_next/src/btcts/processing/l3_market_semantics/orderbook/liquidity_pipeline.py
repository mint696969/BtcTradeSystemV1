# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_pipeline.py
# desc: Build orderbook liquidity semantic payloads from reconstructed book state.

from __future__ import annotations

from typing import Dict, Optional

from btcts.ingestion.l2_canonical import OrderBookRebuilder, OrderBookState
from btcts.processing.features.orderbook.book_features import depth_summary

from .liquidity_signals import liquidity_pressure_signal, liquidity_pull_signal, wall_signal
from .semantic_profile import OrderbookSemanticProfile


def _normalize_board_event(event: Dict) -> Dict:
    return {
        "event_type": event.get("event_type"),
        "bids": event.get("bids", []),
        "asks": event.get("asks", []),
        "mid_price": event.get("mid_price"),
    }


def build_liquidity_payload(
    rebuilder: OrderBookRebuilder,
    canonical_event: Dict,
    *,
    levels: int = 10,
    wall_levels: int = 20,
    semantic_policy: Optional[Dict] = None,
) -> Optional[Dict]:
    normalized = _normalize_board_event(canonical_event)
    profile = OrderbookSemanticProfile.from_policy(
        semantic_policy,
        levels=levels,
    )

    prev_book: Optional[OrderBookState] = None
    if rebuilder.snapshot_loaded:
        prev_book = rebuilder.book.clone()

    rebuilder.apply_event(normalized)

    if not rebuilder.snapshot_loaded:
        return None

    curr_book = rebuilder.book

    summary = depth_summary(curr_book, levels=levels)
    pressure = liquidity_pressure_signal(
        curr_book,
        levels=levels,
        pressure_threshold=profile.pressure_threshold,
    )
    wall = wall_signal(
        curr_book,
        levels=wall_levels,
        wall_ratio_threshold=profile.wall_ratio_threshold,
        near_rank_threshold=profile.wall_near_rank_threshold,
    )

    bid_pull = None
    ask_pull = None
    if prev_book is not None:
        bid_pull = liquidity_pull_signal(
            prev_book,
            curr_book,
            side="bid",
            levels=levels,
            pull_threshold=profile.pull_threshold,
            near_levels=profile.pull_near_levels,
            strong_pull_threshold=profile.strong_pull_threshold,
        )
        ask_pull = liquidity_pull_signal(
            prev_book,
            curr_book,
            side="ask",
            levels=levels,
            pull_threshold=profile.pull_threshold,
            near_levels=profile.pull_near_levels,
            strong_pull_threshold=profile.strong_pull_threshold,
        )

    return {
        "event_type": canonical_event.get("event_type"),
        "rebuild_ready": rebuilder.snapshot_loaded,
        "semantic_policy": profile.to_policy(),
        "best_bid": curr_book.best_bid(),
        "best_ask": curr_book.best_ask(),
        "spread": curr_book.spread(),
        "mid": curr_book.mid(),
        "summary": summary,
        "pressure": pressure,
        "wall": wall,
        "bid_pull": bid_pull,
        "ask_pull": ask_pull,
    }