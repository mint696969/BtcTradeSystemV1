# path: ./btcts_next/src/btcts/market_engine/market_state/live_orderbook_semantics.py
# desc: Thin live adapter from current BookState to partial outward orderbook semantics summary.

from __future__ import annotations

from typing import Any

from btcts.ingestion.l2_canonical.orderbook.book_state import OrderBookState
from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.processing.l3_market_semantics.orderbook.event_enrichment import candidate_events
from btcts.processing.l3_market_semantics.orderbook.liquidity_signals import (
    liquidity_pressure_signal,
    wall_signal,
)
from btcts.processing.l3_market_semantics.orderbook.signal_events import (
    build_signal_events,
)
from btcts.processing.l3_market_semantics.orderbook.semantic_profile import (
    OrderbookSemanticProfile,
)


def _merged_bids(book_state: BookState) -> list[dict[str, Any]]:
    return list(book_state.bids_near) + list(book_state.bids_far)


def _merged_asks(book_state: BookState) -> list[dict[str, Any]]:
    return list(book_state.asks_near) + list(book_state.asks_far)


def to_orderbook_state(book_state: BookState) -> OrderBookState:
    out = OrderBookState()
    out.set_snapshot(
        _merged_bids(book_state),
        _merged_asks(book_state),
        update_ts=book_state.exchange_ts or book_state.collector_ts,
    )
    return out


def build_live_orderbook_signal(
    *,
    book_state: BookState,
    semantic_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    orderbook = to_orderbook_state(book_state)
    profile = OrderbookSemanticProfile.from_policy(
        semantic_policy,
        levels=20,
    )

    pressure = liquidity_pressure_signal(
        orderbook,
        levels=10,
        pressure_threshold=profile.pressure_threshold,
    )
    wall = wall_signal(
        orderbook,
        levels=20,
        wall_ratio_threshold=profile.wall_ratio_threshold,
        near_rank_threshold=profile.wall_near_rank_threshold,
    )

    return {
        "summary": {
            "spread": pressure.get("spread"),
            "mid": pressure.get("mid"),
            "imbalance": pressure.get("imbalance"),
            "bid_depth": pressure.get("bid_depth"),
            "ask_depth": pressure.get("ask_depth"),
        },
        "pressure": pressure,
        "wall": wall,
        "bid_pull": None,
        "ask_pull": None,
    }


def build_live_orderbook_transition_summary(
    *,
    prev_book_state: BookState | None,
    curr_book_state: BookState,
    semantic_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    prev_signal = None
    if prev_book_state is not None:
        prev_signal = build_live_orderbook_signal(
            book_state=prev_book_state,
            semantic_policy=semantic_policy,
        )

    curr_signal = build_live_orderbook_signal(
        book_state=curr_book_state,
        semantic_policy=semantic_policy,
    )
    events = build_signal_events(prev_signal, curr_signal)

    persistence = next(
        (
            {
                "event_name": str(event.get("event_name")),
                "side": event.get("side"),
            }
            for event in events
            if str(event.get("event_name"))
            in {
                "near_wall_continued",
                "support_continued",
                "resistance_continued",
            }
        ),
        None,
    )

    return {
        "prev_signal_present": prev_signal is not None,
        "persistence": persistence,
    }


def build_live_orderbook_semantics_summary(
    *,
    prev_book_state: BookState | None = None,
    book_state: BookState,
    semantic_policy: dict[str, Any] | None,
) -> tuple[str, dict[str, Any]]:
    signal = build_live_orderbook_signal(
        book_state=book_state,
        semantic_policy=semantic_policy,
    )
    transition = build_live_orderbook_transition_summary(
        prev_book_state=prev_book_state,
        curr_book_state=book_state,
        semantic_policy=semantic_policy,
    )
    events = candidate_events(signal)

    near_wall = None
    if bool((signal.get("wall") or {}).get("near_wall_detected")):
        wall = signal.get("wall") or {}
        near_wall = {
            "side": wall.get("near_strongest_side"),
            "rank": wall.get("near_strongest_rank"),
            "ratio": wall.get("near_strongest_ratio"),
        }

    support = next(
        (
            dict(event)
            for event in events
            if str(event.get("event_name")) == "support_candidate"
        ),
        None,
    )
    resistance = next(
        (
            dict(event)
            for event in events
            if str(event.get("event_name")) == "resistance_candidate"
        ),
        None,
    )

    summary = {
        "near_wall": near_wall,
        "support": support,
        "resistance": resistance,
        "persistence": transition.get("persistence"),
    }

    present_count = sum(value is not None for value in summary.values())

    contract_status = "missing"
    if present_count > 0:
        contract_status = "partial"
    if present_count >= 4:
        contract_status = "wired"

    return contract_status, summary