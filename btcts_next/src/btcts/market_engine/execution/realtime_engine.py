# path: ./btcts_next/src/btcts/market_engine/execution/realtime_engine.py
# desc: Realtime execution engine that runs normalized events through shared series, orderbook, trust, and zone components.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l3_market_semantics.continuity import OrderbookEngine, SeriesEngine, TrustEngine
from btcts.processing.l3_market_semantics.zone import ZoneEngine
from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.processing.l3_market_semantics.continuity.models import SeriesState


@dataclass
class RealtimeStepResult:
    series_state: SeriesState
    book_state: BookState
    zone_metadata: dict[str, Any]
    started_new_series: bool


class RealtimeEngine:
    def __init__(self, profile: Any) -> None:
        self._profile = profile
        self._series_engine = SeriesEngine(profile)
        self._orderbook_engine = OrderbookEngine(profile)
        self._trust_engine = TrustEngine()
        self._zone_engine = ZoneEngine()

    def step(
        self,
        *,
        current_series: SeriesState | None,
        current_book: BookState | None,
        normalized_event: dict[str, Any],
    ) -> RealtimeStepResult:
        series_step = self._series_engine.advance(current_series, normalized_event)

        if series_step.boundary is not None:
            boundary_book = self._orderbook_engine.apply_boundary(current_book, series_step.series_state)
            trusted_book = self._trust_engine.apply(
                boundary_book,
                series_step.series_state,
                profile_valid=self._orderbook_engine.validate(boundary_book),
                has_anchor=boundary_book.anchor_event_id is not None,
                invalid_diff_attach=False,
            )
            zoned_book, zone_metadata = self._zone_engine.apply(
                book_state=trusted_book,
                zone_policy=self._profile.build_zone_policy(trusted_book),
            )
            return RealtimeStepResult(
                series_state=series_step.series_state,
                book_state=zoned_book,
                zone_metadata=zone_metadata,
                started_new_series=series_step.started_new_series,
            )

        updated_book = self._orderbook_engine.apply_event(
            current_book,
            normalized_event,
            series_step.series_state,
        )
        trusted_book = self._trust_engine.apply(
            updated_book,
            series_step.series_state,
            profile_valid=self._orderbook_engine.validate(updated_book),
            has_anchor=updated_book.anchor_event_id is not None,
            invalid_diff_attach=updated_book.boundary_reason.value == "invalid_diff_attach",
        )
        zoned_book, zone_metadata = self._zone_engine.apply(
            book_state=trusted_book,
            zone_policy=self._profile.build_zone_policy(trusted_book),
        )
        return RealtimeStepResult(
            series_state=series_step.series_state,
            book_state=zoned_book,
            zone_metadata=zone_metadata,
            started_new_series=series_step.started_new_series,
        )