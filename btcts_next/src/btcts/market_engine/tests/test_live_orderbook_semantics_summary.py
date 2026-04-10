# path: ./btcts_next/src/btcts/market_engine/tests/test_live_orderbook_semantics_summary.py
# desc: Minimal contract test for live partial orderbook semantics summary.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.market_state.live_orderbook_semantics import (
    build_live_orderbook_semantics_summary,
)
from btcts.processing.l3_market_semantics.continuity.models import BookState


def _prev_book() -> BookState:
    return BookState(
        best_bid=100.0,
        best_ask=101.0,
        spread=1.0,
        mid_price=100.5,
        interpretation_bucket="allow_structural_use",
        bids_near=[
            {"price": 100.0, "size": 1.0},
            {"price": 99.5, "size": 2.0},
            {"price": 99.0, "size": 4.5},
        ],
        asks_near=[
            {"price": 101.0, "size": 1.0},
            {"price": 101.5, "size": 1.0},
            {"price": 102.0, "size": 1.0},
        ],
        bids_far=[],
        asks_far=[],
    )


def _book() -> BookState:
    return BookState(
        best_bid=100.0,
        best_ask=101.0,
        spread=1.0,
        mid_price=100.5,
        interpretation_bucket="allow_structural_use",
        bids_near=[
            {"price": 100.0, "size": 1.0},
            {"price": 99.5, "size": 2.0},
            {"price": 99.0, "size": 5.0},
        ],
        asks_near=[
            {"price": 101.0, "size": 1.0},
            {"price": 101.5, "size": 1.0},
            {"price": 102.0, "size": 1.0},
        ],
        bids_far=[],
        asks_far=[],
    )


def _flat_book() -> BookState:
    return BookState(
        best_bid=100.0,
        best_ask=101.0,
        spread=1.0,
        mid_price=100.5,
        interpretation_bucket="allow_structural_use",
        bids_near=[
            {"price": 100.0, "size": 1.0},
            {"price": 99.5, "size": 1.0},
            {"price": 99.0, "size": 1.0},
        ],
        asks_near=[
            {"price": 101.0, "size": 1.0},
            {"price": 101.5, "size": 1.0},
            {"price": 102.0, "size": 1.0},
        ],
        bids_far=[],
        asks_far=[],
    )


def main() -> int:
    status, summary = build_live_orderbook_semantics_summary(
        prev_book_state=_prev_book(),
        book_state=_book(),
        semantic_policy={
            "pressure_threshold": 0.20,
            "wall_ratio_threshold": 0.30,
            "wall_near_rank_threshold": 5,
        },
    )

    assert status == "partial"
    assert summary["near_wall"] is not None
    assert summary["near_wall"]["side"] == "bid"
    assert summary["support"] is not None
    assert summary["support"]["event_name"] == "support_candidate"
    assert summary["resistance"] is None
    assert summary["persistence"] is not None
    assert summary["persistence"]["event_name"] in {
        "near_wall_continued",
        "support_continued",
    }
    assert summary["active_event_count"] == len(summary["active_event_names"])
    assert "support_candidate" in summary["active_event_names"]
    assert isinstance(summary["active_event_contracts"], list)
    assert any(
        str(event.get("event_name")) == "support_candidate"
        and str(event.get("event_family")) == "support_resistance"
        and str(event.get("usage_grade")) == "strong"
        for event in summary["active_event_contracts"]
    )

    flat_status, flat_summary = build_live_orderbook_semantics_summary(
        prev_book_state=None,
        book_state=_flat_book(),
        semantic_policy={
            "pressure_threshold": 0.20,
            "wall_ratio_threshold": 0.60,
            "wall_near_rank_threshold": 5,
        },
    )

    assert flat_status == "partial"
    assert flat_summary["near_wall"] is None
    assert flat_summary["support"] is None
    assert flat_summary["resistance"] is None
    assert flat_summary["persistence"] is None
    assert flat_summary["active_event_count"] == 0
    assert flat_summary["active_event_names"] == []
    assert flat_summary["active_event_contracts"] == []

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())