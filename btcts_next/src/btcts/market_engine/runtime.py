# path: ./btcts_next/src/btcts/market_engine/runtime.py
# desc: Minimal runtime entrypoint for Market Engine realtime assembly, projection, and market_state writing.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.market_engine.assembler.core.assembler_engine import AssemblerEngine
from btcts.market_engine.assembler.profiles.bitflyer import BitflyerProfile
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
        self._profile = BitflyerProfile()
        self._engine = AssemblerEngine(self._profile)
        self._projector = MarketStateProjector()
        self._writer = MarketStateWriter()
        self._current_series = None
        self._current_book = None

    @property
    def config(self) -> MarketEngineConfig:
        return self._cfg

    def step(self, normalized_event: dict[str, Any]) -> RuntimeStepResult:
        result = self._engine.run_realtime_step(
            current_series=self._current_series,
            current_book=self._current_book,
            normalized_event=normalized_event,
        )
        self._current_series = result.series_state
        self._current_book = result.book_state

        record = self._projector.project(
            cfg=self._cfg,
            book_state=result.book_state,
            series_state=result.series_state,
            zone_metadata=result.zone_metadata,
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