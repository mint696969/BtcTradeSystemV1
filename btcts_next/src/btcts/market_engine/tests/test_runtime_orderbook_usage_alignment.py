# path: ./btcts_next/src/btcts/market_engine/tests/test_runtime_orderbook_usage_alignment.py
# desc: Regression test for runtime ordering so orderbook active_event_contract usage_grade matches final interpretation bucket.

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.execution.realtime_engine import RealtimeStepResult
from btcts.market_engine.market_state.live_orderbook_semantics import (
    build_live_orderbook_semantics_summary,
)
from btcts.market_engine.runtime import MarketEngineRuntime
from btcts.processing.l3_market_semantics.continuity.models import BookState


def _cfg() -> MarketEngineConfig:
    return MarketEngineConfig(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        instrument_id="bitflyer.spot.BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        profile_name="bitflyer",
        near_zone_levels=2,
        far_zone_levels=2,
        replay_batch_size=1000,
        write_market_state=False,
    )


def _prev_book() -> BookState:
    return BookState(
        best_bid=100.0,
        best_ask=101.0,
        spread=1.0,
        mid_price=100.5,
        interpretation_bucket="allow_structural_use",
        bids_near=[
            {"price": 100.0, "size": 1.0},
            {"price": 99.5, "size": 2.0},
            {"price": 99.0, "size": 4.5},
        ],
        asks_near=[
            {"price": 101.0, "size": 1.0},
            {"price": 101.5, "size": 1.0},
            {"price": 102.0, "size": 1.0},
        ],
        bids_far=[],
        asks_far=[],
        collector_ts="2026-03-16T12:00:00Z",
        exchange_ts="2026-03-16T12:00:00Z",
    )


def _book() -> BookState:
    return BookState(
        best_bid=100.0,
        best_ask=101.0,
        spread=1.0,
        mid_price=100.5,
        interpretation_bucket="allow_structural_use",
        bids_near=[
            {"price": 100.0, "size": 1.0},
            {"price": 99.5, "size": 2.0},
            {"price": 99.0, "size": 5.0},
        ],
        asks_near=[
            {"price": 101.0, "size": 1.0},
            {"price": 101.5, "size": 1.0},
            {"price": 102.0, "size": 1.0},
        ],
        bids_far=[],
        asks_far=[],
        collector_ts="2026-03-16T12:00:01Z",
        exchange_ts="2026-03-16T12:00:01Z",
    )


def main() -> int:
    runtime = MarketEngineRuntime(_cfg())
    runtime._current_book = _prev_book()

    stale_book = _book()
    stale_status, stale_summary = build_live_orderbook_semantics_summary(
        prev_book_state=runtime._current_book,
        book_state=stale_book,
        semantic_policy={
            "pressure_threshold": 0.20,
            "wall_ratio_threshold": 0.30,
            "wall_near_rank_threshold": 5,
        },
    )

    fake_series = SimpleNamespace(
        series_id="series-1",
        stream_session_id="bf-sess-1",
    )

    runtime._engine.run_realtime_step = lambda **kwargs: RealtimeStepResult(
        series_state=fake_series,
        book_state=stale_book,
        zone_metadata={"mode": "hybrid"},
        started_new_series=False,
        orderbook_semantics_contract_status=stale_status,
        orderbook_semantics_summary=stale_summary,
        orderbook_persistence_observable=True,
    )

    runtime._interpretation.evaluate = lambda **kwargs: SimpleNamespace(
        bucket="observe_only",
        reason="unit_test_override",
        policy={"mode": "unit_test"},
    )

    result = runtime.step(normalized_event={})
    contracts = result.market_state.orderbook_semantics_summary.get("active_event_contracts") or []

    assert result.market_state.interpretation_bucket == "observe_only"
    assert any(str(event.get("event_name")) == "support_candidate" for event in contracts)
    assert any(
        str(event.get("event_name")) == "support_candidate"
        and str(event.get("usage_grade")) == "watch"
        for event in contracts
    )
    assert not any(
        str(event.get("event_name")) == "support_candidate"
        and str(event.get("usage_grade")) == "strong"
        for event in contracts
    )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())