# path: ./btcts_next/src/btcts/market_engine/tests/test_foundation_flow.py
# desc: Small foundation-flow test for Market Engine series, orderbook, trust, and zone components.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l3_market_semantics.continuity import OrderbookEngine, SeriesEngine, TrustEngine
from btcts.processing.l3_market_semantics.zone import ZoneEngine
from btcts.market_engine.assembler.models.book_state import BookState
from btcts.market_engine.assembler.models.series_state import SeriesState
from btcts.market_engine.types import BoundaryReason, TrustState


class DummyProfile:
    profile_name = "dummy"

    def classify_event(self, normalized_event: dict) -> str:
        payload = normalized_event.get("payload", {})
        return str(payload.get("event_type") or "unknown")

    def message_family(self, normalized_event: dict) -> str:
        return normalized_event.get("record_type", "unknown")

    def is_boundary_event(self, normalized_event: dict) -> bool:
        return normalized_event.get("record_type") == "stream.gap_detected"

    def boundary_reason(self, normalized_event: dict) -> BoundaryReason:
        if normalized_event.get("record_type") == "stream.gap_detected":
            return BoundaryReason.GAP_DETECTED
        return BoundaryReason.NONE

    def is_anchor_candidate(self, normalized_event: dict) -> bool:
        return normalized_event.get("record_type") == "market.orderbook.snapshot"

    def can_attach_diff(
        self,
        book_state: BookState,
        normalized_event: dict,
        series_state: SeriesState,
    ) -> bool:
        return (
            normalized_event.get("record_type") == "market.orderbook.diff"
            and book_state.anchor_event_id is not None
            and series_state.trust_state != TrustState.BROKEN
        )

    def apply_anchor(self, book_state: BookState, normalized_event: dict) -> BookState:
        payload = normalized_event["payload"]
        book_state.bids_near = list(payload.get("bids", []))
        book_state.asks_near = list(payload.get("asks", []))
        book_state.bids_far = []
        book_state.asks_far = []
        book_state.best_bid = payload["bids"][0]["price"] if payload.get("bids") else None
        book_state.best_ask = payload["asks"][0]["price"] if payload.get("asks") else None
        if book_state.best_bid is not None and book_state.best_ask is not None:
            book_state.spread = book_state.best_ask - book_state.best_bid
        else:
            book_state.spread = None
        return book_state

    def apply_diff(self, book_state: BookState, normalized_event: dict) -> BookState:
        payload = normalized_event["payload"]
        if payload.get("bids"):
            book_state.bids_near = list(payload["bids"]) + list(book_state.bids_near)
            book_state.best_bid = book_state.bids_near[0]["price"]
        if payload.get("asks"):
            book_state.asks_near = list(payload["asks"]) + list(book_state.asks_near)
            book_state.best_ask = book_state.asks_near[0]["price"]
        if book_state.best_bid is not None and book_state.best_ask is not None:
            book_state.spread = book_state.best_ask - book_state.best_bid
        else:
            book_state.spread = None
        return book_state

    def build_zone_policy(self, book_state: BookState) -> dict:
        return {"near_levels": 2, "far_levels": 2}

    def validate_rebuild_state(self, book_state: BookState) -> bool:
        return book_state.best_bid is not None and book_state.best_ask is not None


def _snapshot_event() -> dict:
    return {
        "record_type": "market.orderbook.snapshot",
        "stream_session_id": "sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "sequence_id": 10,
        "source_event_id": "snap-1",
        "collector_ts": "2026-03-16T10:00:00Z",
        "exchange_ts": "2026-03-16T10:00:00Z",
        "payload": {
            "event_type": "snapshot",
            "continuity_state": "resynced",
            "stream_event_no": 1,
            "bids": [{"price": 100.0, "size": 1.0}, {"price": 99.0, "size": 2.0}],
            "asks": [{"price": 101.0, "size": 1.5}, {"price": 102.0, "size": 2.5}],
        },
    }


def _diff_event() -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "sequence_id": 11,
        "source_event_id": "diff-1",
        "collector_ts": "2026-03-16T10:00:01Z",
        "exchange_ts": "2026-03-16T10:00:01Z",
        "payload": {
            "event_type": "delta",
            "continuity_state": "continuous",
            "stream_event_no": 2,
            "bids": [{"price": 100.5, "size": 0.7}],
            "asks": [],
        },
    }


def _gap_event() -> dict:
    return {
        "record_type": "stream.gap_detected",
        "stream_session_id": "sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "sequence_id": 12,
        "source_event_id": "gap-1",
        "payload": {},
    }


def main() -> int:
    profile = DummyProfile()
    series_engine = SeriesEngine(profile)
    orderbook_engine = OrderbookEngine(profile)
    trust_engine = TrustEngine()
    zone_engine = ZoneEngine()

    snapshot = _snapshot_event()
    diff = _diff_event()
    gap = _gap_event()

    step1 = series_engine.advance(None, snapshot)
    assert step1.started_new_series is True
    assert step1.series_state.anchor_event_id == "snap-1"

    book = orderbook_engine.apply_event(None, snapshot, step1.series_state)
    assert book.best_bid == 100.0
    assert book.best_ask == 101.0
    assert book.spread == 1.0

    trusted = trust_engine.apply(
        book,
        step1.series_state,
        profile_valid=orderbook_engine.validate(book),
        has_anchor=True,
    )
    assert trusted.trust_state == TrustState.PROVISIONAL

    step2 = series_engine.advance(step1.series_state, diff)
    assert step2.started_new_series is False
    assert step2.series_state.last_source_event_id == "diff-1"

    book2 = orderbook_engine.apply_event(book, diff, step2.series_state)
    assert book2.best_bid == 100.5

    trusted2 = trust_engine.apply(
        book2,
        step2.series_state,
        profile_valid=orderbook_engine.validate(book2),
        has_anchor=True,
    )
    assert trusted2.trust_state == TrustState.TRUSTED

    zoned, metadata = zone_engine.apply(
        book_state=book2,
        zone_policy=profile.build_zone_policy(book2),
    )
    assert metadata["mode"] == "hybrid"
    assert metadata["near_levels"] == 2
    assert metadata["density_difference_visible"] is True
    assert len(zoned.bids_near) <= 2

    step3 = series_engine.advance(step2.series_state, gap)
    assert step3.started_new_series is True
    assert step3.boundary is not None
    assert step3.boundary.reason == BoundaryReason.GAP_DETECTED

    broken = trust_engine.apply(
        book2,
        step3.series_state,
        profile_valid=True,
        has_anchor=False,
        invalid_diff_attach=False,
    )
    assert broken.trust_state == TrustState.PROVISIONAL

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())