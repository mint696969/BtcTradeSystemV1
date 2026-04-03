# path: ./btcts_next/src/btcts/market_engine/execution/replay_engine.py
# desc: Replay execution engine that reuses the shared realtime flow over ordered normalized event sequences.

from __future__ import annotations

from typing import Any

from btcts.market_engine.execution.realtime_engine import RealtimeEngine, RealtimeStepResult
from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.processing.l3_market_semantics.continuity.models import SeriesState


class ReplayEngine:
    def __init__(self, profile: Any) -> None:
        self._profile = profile
        self._realtime_engine = RealtimeEngine(profile)

    def run(self, normalized_events: list[dict[str, Any]]) -> list[RealtimeStepResult]:
        results: list[RealtimeStepResult] = []
        current_series: SeriesState | None = None
        current_book: BookState | None = None

        sorted_events = sorted(
            normalized_events,
            key=lambda event: (
                str(event.get("stream_session_id") or ""),
                int(event.get("sequence_id") or 0),
            ),
        )

        for event in sorted_events:
            step = self._realtime_engine.step(
                current_series=current_series,
                current_book=current_book,
                normalized_event=event,
            )
            current_series = step.series_state
            current_book = step.book_state
            results.append(step)

        return results