# path: ./btcts_next/src/btcts/market_engine/tests/test_series_engine.py
# desc: Behavior test for series segmentation, boundary handling, and trust progression in Market Engine SeriesEngine.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.assembler.core.series_engine import SeriesEngine
from btcts.market_engine.assembler.profiles.bitflyer import BitflyerProfile
from btcts.market_engine.types import BoundaryReason, TrustState


def _snapshot_event(
    *,
    stream_session_id: str = "bf-sess-1",
    sequence_id: int = 100,
    source_event_id: str = "bf-snap-1",
    continuity_state: str = "resynced",
) -> dict:
    return {
        "record_type": "market.orderbook.snapshot",
        "stream_session_id": stream_session_id,
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": sequence_id,
        "source_event_id": source_event_id,
        "payload": {
            "event_type": "snapshot",
            "continuity_state": continuity_state,
            "stream_event_no": 1,
            "bids": [{"price": 100.0, "size": 1.0}],
            "asks": [{"price": 101.0, "size": 1.0}],
        },
    }


def _diff_event(
    *,
    stream_session_id: str = "bf-sess-1",
    sequence_id: int = 101,
    source_event_id: str = "bf-diff-1",
    continuity_state: str = "continuous",
    stream_event_no: int = 2,
) -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": stream_session_id,
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": sequence_id,
        "source_event_id": source_event_id,
        "payload": {
            "event_type": "delta",
            "continuity_state": continuity_state,
            "stream_event_no": stream_event_no,
            "bids": [{"price": 100.5, "size": 0.7}],
            "asks": [],
        },
    }


def _gap_event(
    *,
    stream_session_id: str = "bf-sess-1",
    sequence_id: int = 102,
    source_event_id: str = "bf-gap-1",
) -> dict:
    return {
        "record_type": "stream.gap_detected",
        "stream_session_id": stream_session_id,
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": sequence_id,
        "source_event_id": source_event_id,
        "payload": {},
    }


def main() -> int:
    engine = SeriesEngine(BitflyerProfile())

    step1 = engine.advance(None, _snapshot_event())
    assert step1.started_new_series is True
    assert step1.boundary is None
    assert str(step1.series_state.stream_session_id) == "bf-sess-1"
    assert str(step1.series_state.series_id) == "bf-sess-1:series:100"
    assert step1.series_state.anchor_event_id == "bf-snap-1"
    assert step1.series_state.start_sequence == 100
    assert step1.series_state.end_sequence == 100
    assert step1.series_state.trust_state == TrustState.PROVISIONAL
    assert step1.series_state.boundary_reason == BoundaryReason.NONE

    step2 = engine.advance(step1.series_state, _diff_event())
    assert step2.started_new_series is False
    assert step2.boundary is None
    assert step2.series_state.end_sequence == 101
    assert step2.series_state.last_source_event_id == "bf-diff-1"
    assert step2.series_state.last_stream_event_no == 2
    assert step2.series_state.trust_state == TrustState.TRUSTED
    assert step2.series_state.boundary_reason == BoundaryReason.NONE

    step3 = engine.advance(step2.series_state, _gap_event())
    assert step3.started_new_series is True
    assert step3.boundary is not None
    assert step3.boundary.reason == BoundaryReason.GAP_DETECTED
    assert step3.series_state.boundary_reason == BoundaryReason.GAP_DETECTED
    assert step3.series_state.trust_state == TrustState.PROVISIONAL
    assert str(step3.series_state.series_id) == "bf-sess-1:series:102"

    step4 = engine.advance(
        step3.series_state,
        _snapshot_event(
            stream_session_id="bf-sess-2",
            sequence_id=200,
            source_event_id="bf-snap-2",
            continuity_state="resynced",
        ),
    )
    assert step4.started_new_series is True
    assert step4.boundary is not None
    assert step4.boundary.reason == BoundaryReason.NEW_STREAM_SESSION
    assert str(step4.series_state.stream_session_id) == "bf-sess-2"
    assert str(step4.series_state.series_id) == "bf-sess-2:series:200"
    assert step4.series_state.anchor_event_id == "bf-snap-2"
    assert step4.series_state.trust_state == TrustState.PROVISIONAL

    step5 = engine.advance(
        step4.series_state,
        _diff_event(
            stream_session_id="bf-sess-2",
            sequence_id=201,
            source_event_id="bf-diff-2",
            continuity_state="gap_detected",
            stream_event_no=2,
        ),
    )
    assert step5.started_new_series is True
    assert step5.boundary is not None
    assert step5.boundary.reason == BoundaryReason.GAP_DETECTED
    assert step5.series_state.boundary_reason == BoundaryReason.GAP_DETECTED
    assert step5.series_state.trust_state == TrustState.PROVISIONAL

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())