# path: ./btcts_next/src/btcts/processing/l3_market_semantics/continuity/orderbook_engine.py
# desc: Continuity-aware orderbook assembly engine for anchor and diff attachment semantics.

from __future__ import annotations

from dataclasses import replace
from typing import Any

from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.processing.l3_market_semantics.continuity.models import SeriesState
from btcts.market_engine.types import BoundaryReason, TrustState


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


def _exchange_ts(event: dict[str, Any]) -> str | None:
    value = event.get("exchange_ts")
    return str(value) if value else None


def _collector_ts(event: dict[str, Any]) -> str | None:
    value = event.get("collector_ts")
    return str(value) if value else None


def _source_event_id(event: dict[str, Any]) -> str | None:
    value = event.get("source_event_id")
    return str(value) if value else None


class OrderbookEngine:
    def __init__(self, profile: Any) -> None:
        self._profile = profile

    def empty_state(self) -> BookState:
        return BookState(
            best_bid=None,
            best_ask=None,
            spread=None,
            bids_near=[],
            asks_near=[],
            bids_far=[],
            asks_far=[],
            collector_ts=None,
            exchange_ts=None,
            trust_state=TrustState.PROVISIONAL,
            boundary_reason=BoundaryReason.NONE,
            anchor_event_id=None,
            last_source_event_id=None,
            source_stream_session_id=None,
        )

    def apply_event(
        self,
        current: BookState | None,
        normalized_event: dict[str, Any],
        series_state: SeriesState,
    ) -> BookState:
        book = current or self.empty_state()

        if self._profile.is_anchor_candidate(normalized_event):
            updated = self._profile.apply_anchor(book, normalized_event)
            updated.collector_ts = _collector_ts(normalized_event)
            updated.exchange_ts = _exchange_ts(normalized_event)
            updated.anchor_event_id = _source_event_id(normalized_event)
            updated.last_source_event_id = _source_event_id(normalized_event)
            updated.source_stream_session_id = str(series_state.stream_session_id)
            updated.boundary_reason = series_state.boundary_reason
            if series_state.trust_state in {TrustState.TRUSTED, TrustState.PROVISIONAL}:
                updated.trust_state = series_state.trust_state
            return updated

        if self._profile.can_attach_diff(book, normalized_event, series_state):
            updated = self._profile.apply_diff(book, normalized_event)
            updated.collector_ts = _collector_ts(normalized_event)
            updated.exchange_ts = _exchange_ts(normalized_event)
            updated.last_source_event_id = _source_event_id(normalized_event)
            updated.source_stream_session_id = str(series_state.stream_session_id)
            updated.boundary_reason = series_state.boundary_reason
            updated.trust_state = series_state.trust_state
            return updated

        rejected = replace(book)
        rejected.collector_ts = _collector_ts(normalized_event)
        rejected.exchange_ts = _exchange_ts(normalized_event)
        rejected.last_source_event_id = _source_event_id(normalized_event)
        rejected.source_stream_session_id = str(series_state.stream_session_id)
        rejected.boundary_reason = BoundaryReason.INVALID_DIFF_ATTACH
        rejected.trust_state = TrustState.BROKEN
        return rejected

    def apply_boundary(
        self,
        current: BookState | None,
        series_state: SeriesState,
    ) -> BookState:
        book = current or self.empty_state()
        updated = replace(book)
        updated.boundary_reason = series_state.boundary_reason
        updated.trust_state = series_state.trust_state
        updated.source_stream_session_id = str(series_state.stream_session_id)
        return updated

    def validate(self, book_state: BookState) -> bool:
        return self._profile.validate_rebuild_state(book_state)