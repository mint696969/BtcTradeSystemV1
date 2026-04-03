# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_pipeline.py
# desc: Build orderbook liquidity semantic payloads from reconstructed book state.

from __future__ import annotations

from typing import Dict, Optional

from btcts.ingestion.l2_canonical.orderbook.book_rebuilder import OrderBookRebuilder
from btcts.ingestion.l2_canonical.orderbook.book_state import OrderBookState
from btcts.processing.features.orderbook.book_features import depth_summary

from .liquidity_signals import liquidity_pressure_signal, liquidity_pull_signal, wall_signal


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
) -> Optional[Dict]:
    normalized = _normalize_board_event(canonical_event)

    prev_book: Optional[OrderBookState] = None
    if rebuilder.snapshot_loaded:
        prev_book = rebuilder.book.clone()

    rebuilder.apply_event(normalized)

    if not rebuilder.snapshot_loaded:
        return None

    curr_book = rebuilder.book

    summary = depth_summary(curr_book, levels=levels)
    pressure = liquidity_pressure_signal(curr_book, levels=levels)
    wall = wall_signal(curr_book, levels=wall_levels)

    bid_pull = None
    ask_pull = None
    if prev_book is not None:
        bid_pull = liquidity_pull_signal(prev_book, curr_book, side="bid", levels=levels)
        ask_pull = liquidity_pull_signal(prev_book, curr_book, side="ask", levels=levels)

    return {
        "event_type": canonical_event.get("event_type"),
        "rebuild_ready": rebuilder.snapshot_loaded,
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