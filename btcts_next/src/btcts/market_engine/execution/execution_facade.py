# path: ./btcts_next/src/btcts/market_engine/execution/execution_facade.py
# desc: Thin facade entrypoint for Market Engine execution across realtime and replay modes.

from __future__ import annotations

from typing import Any

from btcts.market_engine.execution.realtime_engine import RealtimeEngine, RealtimeStepResult
from btcts.market_engine.execution.replay_engine import ReplayEngine


class ExecutionFacade:
    def __init__(self, profile: Any) -> None:
        self._profile = profile
        self._realtime_engine = RealtimeEngine(profile)
        self._replay_engine = ReplayEngine(profile)

    def run_realtime_step(
        self,
        *,
        current_series,
        current_book,
        normalized_event: dict[str, Any],
    ) -> RealtimeStepResult:
        return self._realtime_engine.step(
            current_series=current_series,
            current_book=current_book,
            normalized_event=normalized_event,
        )

    def run_replay(
        self,
        normalized_events: list[dict[str, Any]],
    ) -> list[RealtimeStepResult]:
        return self._replay_engine.run(normalized_events)