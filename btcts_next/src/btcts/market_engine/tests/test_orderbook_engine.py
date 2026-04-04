# path: ./btcts_next/src/btcts/market_engine/tests/test_orderbook_engine.py
# desc: Behavior test for anchor application, diff attachment, rejection, and validation in Market Engine OrderbookEngine.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l3_market_semantics.continuity import OrderbookEngine
from btcts.processing.l3_market_semantics.continuity.models import SeriesState
from btcts.market_engine.profiles import BitflyerProfile
from btcts.market_engine.types import BoundaryReason, MarketUID, SeriesID, StreamSessionID, TrustState


def _series(
    *,
    stream_session_id: str = "bf-sess-1",
    series_id: str = "bf-sess-1:series:100",
    anchor_event_id: str | None = "bf-snap-1",
    boundary_reason: BoundaryReason = BoundaryReason.NONE,
    trust_state: TrustState = TrustState.PROVISIONAL,
) -> SeriesState:
    return SeriesState(
        market_uid=MarketUID("bitflyer.spot.BTC_JPY"),
        stream_session_id=StreamSessionID(stream_session_id),
        series_id=SeriesID(series_id),
        anchor_event_id=anchor_event_id,
        start_sequence=100,
        end_sequence=100,
        boundary_reason=boundary_reason,
        trust_state=trust_state,
        last_source_event_id=anchor_event_id,
        last_stream_event_no=1,
        boundary=None,
    )


def _snapshot_event() -> dict:
    return {
        "record_type": "market.orderbook.snapshot",
        "stream_session_id": "bf-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": 100,
        "source_event_id": "bf-snap-1",
        "collector_ts": "2026-03-16T12:00:00Z",
        "exchange_ts": "2026-03-16T12:00:00Z",
        "payload": {
            "event_type": "snapshot",
            "continuity_state": "resynced",
            "stream_event_no": 1,
            "bids": [
                {"price": 100.0, "size": 1.0},
                {"price": 99.5, "size": 2.0},
            ],
            "asks": [
                {"price": 101.0, "size": 1.5},
                {"price": 101.5, "size": 2.5},
            ],
        },
    }


def _continuous_diff_event(*, source_event_id: str = "bf-diff-1", bid_price: float = 100.5) -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "bf-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": 101,
        "source_event_id": source_event_id,
        "collector_ts": "2026-03-16T12:00:01Z",
        "exchange_ts": "2026-03-16T12:00:01Z",
        "payload": {
            "event_type": "delta",
            "continuity_state": "continuous",
            "stream_event_no": 2,
            "bids": [{"price": bid_price, "size": 0.7}],
            "asks": [],
        },
    }


def _gap_diff_event() -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "bf-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": 102,
        "source_event_id": "bf-diff-gap-1",
        "collector_ts": "2026-03-16T12:00:02Z",
        "exchange_ts": "2026-03-16T12:00:02Z",
        "payload": {
            "event_type": "delta",
            "continuity_state": "gap_detected",
            "stream_event_no": 3,
            "bids": [{"price": 100.2, "size": 0.3}],
            "asks": [],
        },
    }


def main() -> int:
    engine = OrderbookEngine(BitflyerProfile())

    empty = engine.empty_state()
    assert empty.best_bid is None
    assert empty.best_ask is None
    assert empty.spread is None
    assert empty.anchor_event_id is None
    assert empty.trust_state == TrustState.PROVISIONAL
    assert empty.boundary_reason == BoundaryReason.NONE

    anchored = engine.apply_event(
        None,
        _snapshot_event(),
        _series(anchor_event_id=None, trust_state=TrustState.PROVISIONAL),
    )
    assert anchored.best_bid == 100.0
    assert anchored.best_ask == 101.0
    assert anchored.spread == 1.0
    assert anchored.mid_price == 100.5
    assert anchored.continuity_state == "resynced"
    assert anchored.anchor_event_id == "bf-snap-1"
    assert anchored.last_source_event_id == "bf-snap-1"
    assert anchored.source_stream_session_id == "bf-sess-1"
    assert anchored.trust_state == TrustState.PROVISIONAL
    assert engine.validate(anchored) is True

    diffed = engine.apply_event(
        anchored,
        _continuous_diff_event(),
        _series(anchor_event_id="bf-snap-1", trust_state=TrustState.TRUSTED),
    )
    assert diffed.best_bid == 100.5
    assert diffed.best_ask == 101.0
    assert diffed.spread == 0.5
    assert diffed.mid_price == 100.75
    assert diffed.continuity_state == "continuous"
    assert diffed.last_source_event_id == "bf-diff-1"
    assert diffed.trust_state == TrustState.TRUSTED
    assert diffed.boundary_reason == BoundaryReason.NONE
    assert diffed.source_stream_session_id == "bf-sess-1"
    assert engine.validate(diffed) is True

    rejected_gap = engine.apply_event(
        diffed,
        _gap_diff_event(),
        _series(
            anchor_event_id="bf-snap-1",
            trust_state=TrustState.BROKEN,
            boundary_reason=BoundaryReason.GAP_DETECTED,
        ),
    )
    assert rejected_gap.boundary_reason == BoundaryReason.INVALID_DIFF_ATTACH
    assert rejected_gap.trust_state == TrustState.BROKEN
    assert rejected_gap.last_source_event_id == "bf-diff-gap-1"

    no_anchor_series = _series(anchor_event_id=None, trust_state=TrustState.PROVISIONAL)
    no_anchor_series.anchor_event_id = None
    rejected_no_anchor = engine.apply_event(
        engine.empty_state(),
        _continuous_diff_event(source_event_id="bf-diff-no-anchor"),
        no_anchor_series,
    )
    assert rejected_no_anchor.boundary_reason == BoundaryReason.INVALID_DIFF_ATTACH
    assert rejected_no_anchor.trust_state == TrustState.BROKEN
    assert rejected_no_anchor.last_source_event_id == "bf-diff-no-anchor"

    boundary_applied = engine.apply_boundary(
        diffed,
        _series(
            anchor_event_id="bf-snap-1",
            trust_state=TrustState.PROVISIONAL,
            boundary_reason=BoundaryReason.GAP_DETECTED,
        ),
    )
    assert boundary_applied.boundary_reason == BoundaryReason.GAP_DETECTED
    assert boundary_applied.trust_state == TrustState.PROVISIONAL
    assert boundary_applied.source_stream_session_id == "bf-sess-1"

    crossed = engine.empty_state()
    crossed.best_bid = 102.0
    crossed.best_ask = 101.0
    crossed.spread = -1.0
    assert engine.validate(crossed) is False

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())