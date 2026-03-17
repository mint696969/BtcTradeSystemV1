# path: ./btcts_next/src/btcts/market_engine/tests/test_replay_realtime_parity.py
# desc: Verify replay and realtime paths produce equivalent assembled state under the shared profile logic path.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.assembler.core.realtime_engine import RealtimeEngine
from btcts.market_engine.assembler.core.replay_engine import ReplayEngine
from btcts.market_engine.assembler.profiles.bitflyer import BitflyerProfile


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


def _diff_event(
    *,
    sequence_id: int,
    source_event_id: str,
    bid_price: float,
    stream_event_no: int,
    continuity_state: str = "continuous",
) -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "bf-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": sequence_id,
        "source_event_id": source_event_id,
        "collector_ts": f"2026-03-16T12:00:0{stream_event_no}Z",
        "exchange_ts": f"2026-03-16T12:00:0{stream_event_no}Z",
        "payload": {
            "event_type": "delta",
            "continuity_state": continuity_state,
            "stream_event_no": stream_event_no,
            "bids": [{"price": bid_price, "size": 0.7}],
            "asks": [],
        },
    }


def _events() -> list[dict]:
    return [
        _diff_event(sequence_id=102, source_event_id="bf-diff-2", bid_price=100.4, stream_event_no=3),
        _snapshot_event(),
        _diff_event(sequence_id=101, source_event_id="bf-diff-1", bid_price=100.5, stream_event_no=2),
    ]


def _book_fingerprint(step) -> tuple:
    book = step.book_state
    return (
        book.best_bid,
        book.best_ask,
        book.spread,
        book.mid_price,
        book.trust_state.value,
        book.boundary_reason.value,
        book.continuity_state,
        book.anchor_event_id,
        book.last_source_event_id,
        len(book.bids_near),
        len(book.asks_near),
        step.zone_metadata.get("mode"),
        step.zone_metadata.get("near_levels"),
        step.zone_metadata.get("far_levels"),
    )


def _series_fingerprint(step) -> tuple:
    series = step.series_state
    return (
        str(series.stream_session_id),
        str(series.series_id),
        series.anchor_event_id,
        series.start_sequence,
        series.end_sequence,
        series.trust_state.value,
        series.boundary_reason.value,
        series.last_source_event_id,
        series.last_stream_event_no,
    )


def main() -> int:
    profile = BitflyerProfile()

    replay = ReplayEngine(profile)
    replay_results = replay.run(_events())
    assert len(replay_results) == 3

    realtime = RealtimeEngine(profile)
    current_series = None
    current_book = None
    realtime_results = []
    for event in sorted(_events(), key=lambda x: (str(x.get("stream_session_id") or ""), int(x.get("sequence_id") or 0))):
        step = realtime.step(
            current_series=current_series,
            current_book=current_book,
            normalized_event=event,
        )
        current_series = step.series_state
        current_book = step.book_state
        realtime_results.append(step)

    assert len(realtime_results) == len(replay_results)

    for replay_step, realtime_step in zip(replay_results, realtime_results):
        assert _book_fingerprint(replay_step) == _book_fingerprint(realtime_step)
        assert _series_fingerprint(replay_step) == _series_fingerprint(realtime_step)

    final_replay = replay_results[-1]
    assert final_replay.book_state.best_bid == 100.5
    assert final_replay.book_state.best_ask == 101.0
    assert final_replay.book_state.spread == 0.5
    assert final_replay.book_state.trust_state.value == "trusted"
    assert final_replay.zone_metadata["mode"] == "hybrid"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())