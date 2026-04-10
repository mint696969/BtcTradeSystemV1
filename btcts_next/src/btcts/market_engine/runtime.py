# path: ./btcts_next/src/btcts/market_engine/runtime.py
# desc: Minimal runtime entrypoint for Market Engine realtime assembly, projection, and market_state writing.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.market_engine.execution.execution_facade import ExecutionFacade
from btcts.market_engine.market_state.live_orderbook_semantics import (
    build_live_orderbook_semantics_summary,
)
from btcts.processing.l3_market_semantics.continuity import InterpretationEngine
from btcts.market_engine.profiles import create_exchange_profile
from btcts.market_engine.config import MarketEngineConfig, load_market_engine_config
from btcts.market_engine.market_state.projector import MarketStateProjector
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.market_state.writer import MarketStateWriter


@dataclass
class RuntimeStepResult:
    market_state: MarketStateRecord
    output_path: str | None


class MarketEngineRuntime:
    def __init__(self, cfg: MarketEngineConfig | None = None) -> None:
        self._cfg = cfg or load_market_engine_config()
        self._profile = create_exchange_profile(str(self._cfg.profile_name))
        self._engine = ExecutionFacade(self._profile)
        self._interpretation = InterpretationEngine()
        self._projector = MarketStateProjector()
        self._writer = MarketStateWriter()
        self._current_series = None
        self._current_book = None

    @property
    def config(self) -> MarketEngineConfig:
        return self._cfg

    def step(self, normalized_event: dict[str, Any]) -> RuntimeStepResult:
        prev_book_for_orderbook_semantics = self._current_book

        result = self._engine.run_realtime_step(
            current_series=self._current_series,
            current_book=self._current_book,
            normalized_event=normalized_event,
        )
        interpretation = self._interpretation.evaluate(
            trust_state=result.book_state.trust_state,
            boundary_reason=result.book_state.boundary_reason,
            continuity_state=result.book_state.continuity_state,
            review_policy=self._profile.review_policy(),
        )

        result.book_state.interpretation_bucket = interpretation.bucket
        result.book_state.interpretation_reason = interpretation.reason
        result.book_state.interpretation_policy = dict(interpretation.policy)

        prev_orderbook_book = prev_book_for_orderbook_semantics
        if result.started_new_series:
            prev_orderbook_book = None

        (
            result.orderbook_semantics_contract_status,
            result.orderbook_semantics_summary,
        ) = build_live_orderbook_semantics_summary(
            prev_book_state=prev_orderbook_book,
            book_state=result.book_state,
            semantic_policy=self._profile.orderbook_semantic_policy(),
        )

        self._current_series = result.series_state
        self._current_book = result.book_state

        record = self._projector.project(
            cfg=self._cfg,
            book_state=result.book_state,
            series_state=result.series_state,
            zone_metadata=result.zone_metadata,
            orderbook_semantics_contract_status=result.orderbook_semantics_contract_status,
            orderbook_semantics_summary=result.orderbook_semantics_summary,
            orderbook_persistence_observable=result.orderbook_persistence_observable,
        )

        output_path: str | None = None
        if self._cfg.write_market_state:
            out = self._writer.write(
                cfg=self._cfg,
                state_type="market.overview",
                record=record,
            )
            output_path = str(out)

        return RuntimeStepResult(
            market_state=record,
            output_path=output_path,
        )