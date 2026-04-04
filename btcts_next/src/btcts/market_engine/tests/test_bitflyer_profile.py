# path: ./btcts_next/src/btcts/market_engine/tests/test_bitflyer_profile.py
# desc: Behavior test for bitFlyer Market Engine profile boundary and diff-attach policy.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.processing.l3_market_semantics.continuity.models import SeriesState
from btcts.market_engine.profiles import BitflyerProfile
from btcts.market_engine.types import BoundaryReason, MarketUID, SeriesID, StreamSessionID, TrustState


def _book(*, anchor_event_id: str | None) -> BookState:
    return BookState(
        best_bid=100.0,
        best_ask=101.0,
        spread=1.0,
        bids_near=[{"price": 100.0, "size": 1.0}],
        asks_near=[{"price": 101.0, "size": 1.0}],
        bids_far=[],
        asks_far=[],
        collector_ts=None,
        exchange_ts=None,
        trust_state=TrustState.PROVISIONAL,
        boundary_reason=BoundaryReason.NONE,
        anchor_event_id=anchor_event_id,
        last_source_event_id=None,
        source_stream_session_id="bf-sess-1",
    )


def _series(*, boundary_reason: BoundaryReason = BoundaryReason.NONE, trust_state: TrustState = TrustState.PROVISIONAL) -> SeriesState:
    return SeriesState(
        market_uid=MarketUID("bitflyer.spot.BTC_JPY"),
        stream_session_id=StreamSessionID("bf-sess-1"),
        series_id=SeriesID("bf-sess-1:series:100"),
        anchor_event_id="bf-snap-1",
        start_sequence=100,
        end_sequence=100,
        boundary_reason=boundary_reason,
        trust_state=trust_state,
        last_source_event_id="bf-snap-1",
        last_stream_event_no=1,
        boundary=None,
    )


def _snapshot_event() -> dict:
    return {
        "record_type": "market.orderbook.snapshot",
        "stream_session_id": "bf-sess-1",
        "sequence_id": 100,
        "source_event_id": "bf-snap-1",
        "payload": {
            "event_type": "snapshot",
            "continuity_state": "resynced",
            "stream_event_no": 1,
            "bids": [{"price": 100.0, "size": 1.0}],
            "asks": [{"price": 101.0, "size": 1.0}],
        },
    }


def _continuous_diff_event() -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "bf-sess-1",
        "sequence_id": 101,
        "source_event_id": "bf-diff-1",
        "payload": {
            "event_type": "delta",
            "continuity_state": "continuous",
            "stream_event_no": 2,
            "bids": [{"price": 100.5, "size": 0.7}],
            "asks": [],
        },
    }


def _gap_diff_event() -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "bf-sess-1",
        "sequence_id": 102,
        "source_event_id": "bf-diff-gap-1",
        "payload": {
            "event_type": "delta",
            "continuity_state": "gap_detected",
            "stream_event_no": 3,
            "bids": [{"price": 100.2, "size": 0.3}],
            "asks": [],
        },
    }


def _stream_gap_event() -> dict:
    return {
        "record_type": "stream.gap_detected",
        "stream_session_id": "bf-sess-1",
        "sequence_id": 103,
        "source_event_id": "bf-gap-1",
        "payload": {},
    }


def main() -> int:
    profile = BitflyerProfile()

    snapshot = _snapshot_event()
    continuous_diff = _continuous_diff_event()
    gap_diff = _gap_diff_event()
    gap_event = _stream_gap_event()

    assert profile.classify_event(snapshot) == "snapshot"
    assert profile.classify_event(continuous_diff) == "diff"
    assert profile.classify_event(gap_event) == "boundary"

    assert profile.is_anchor_candidate(snapshot) is True
    assert profile.is_anchor_candidate(continuous_diff) is False

    assert profile.is_boundary_event(gap_event) is True
    assert profile.is_boundary_event(gap_diff) is True
    assert profile.boundary_reason(gap_event) == BoundaryReason.GAP_DETECTED
    assert profile.boundary_reason(gap_diff) == BoundaryReason.GAP_DETECTED

    book_without_anchor = _book(anchor_event_id=None)
    book_with_anchor = _book(anchor_event_id="bf-snap-1")

    clean_series = _series(boundary_reason=BoundaryReason.NONE, trust_state=TrustState.PROVISIONAL)
    broken_series = _series(boundary_reason=BoundaryReason.GAP_DETECTED, trust_state=TrustState.BROKEN)

    assert profile.can_attach_diff(book_without_anchor, continuous_diff, clean_series) is False
    assert profile.can_attach_diff(book_with_anchor, continuous_diff, clean_series) is True
    assert profile.can_attach_diff(book_with_anchor, gap_diff, clean_series) is False
    assert profile.can_attach_diff(book_with_anchor, continuous_diff, broken_series) is False

    anchored = profile.apply_anchor(_book(anchor_event_id=None), snapshot)
    assert anchored.best_bid == 100.0
    assert anchored.best_ask == 101.0
    assert anchored.spread == 1.0

    diffed = profile.apply_diff(anchored, continuous_diff)
    assert diffed.best_bid == 100.5
    assert diffed.best_ask == 101.0
    assert diffed.spread == 0.5

    assert profile.validate_rebuild_state(_book(anchor_event_id=None)) is True

    crossed = _book(anchor_event_id="bf-snap-1")
    crossed.best_bid = 102.0
    crossed.best_ask = 101.0
    crossed.spread = -1.0

    assert profile.validate_rebuild_state(diffed) is True
    assert profile.validate_rebuild_state(crossed) is False

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())