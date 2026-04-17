# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_liquidity_board_history.py
# desc: Verify liquidity / board-history evidence builder stays shared-first and wording-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    HealthDigest,
    MarketSummaryBuildInput,
    PredictionLiquidityBoardHistoryBuildInput,
    build_market_summary,
    build_prediction_liquidity_board_history,
)


def main() -> int:
    stable_summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-17T03:50:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": "allow_structural_use",
                "interpretation_reason": "ok",
                "semantic_observer_status": "healthy",
                "semantic_usage_summary": {
                    "source_kind": "market_state_semantic_usage_summary",
                    "contract_source": "l3_event_usage_policy",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "observer_status": "healthy",
                    "active_event_count": 1,
                    "mapped_event_count": 1,
                    "unknown_event_count": 0,
                },
                "semantic_usage_contract_rows": [
                    {
                        "event_family": "wall",
                        "usage_grade": "strong",
                        "contract_source": "l3_event_usage_policy",
                        "meaning_version": "l3_event_usage_policy.v1alpha1",
                        "interpretation_bucket": "allow_structural_use",
                    }
                ],
                "orderbook_semantics_summary": {
                    "summary_slots_present": ["support", "persistence"],
                    "active_event_count": 1,
                    "active_event_names": ["support_candidate"],
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": True,
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 4.0,
                "preferred_row_freshness": "LIVE",
            },
        )
    )

    stable = build_prediction_liquidity_board_history(
        PredictionLiquidityBoardHistoryBuildInput(
            market_summary=stable_summary,
            diagnostics={"caller": "unit_test"},
        )
    )

    assert stable["evidence_type"] == "prediction_liquidity_board_history"
    assert stable["evidence_version"] == "phase3.v1alpha1"
    assert stable["source_kind"] == "market_summary_anchor"
    assert stable["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert stable["event_ts"] == "2026-04-17T03:50:00Z"
    assert stable["freshness"] == "LIVE"
    assert stable["is_stale"] is False
    assert stable["history_window_sec"] == 120
    assert stable["orderbook_active_event_count"] == 1
    assert stable["semantic_active_event_count"] == 1
    assert stable["support_present"] is True
    assert stable["resistance_present"] is False
    assert stable["persistence_present"] is True
    assert stable["persistence_observable"] is True
    assert stable["liquidity_pressure_balance"] == "bid_support"
    assert stable["wall_persistence_bias"] == "bid_support"
    assert stable["persistence_confidence"] == "high"
    assert stable["trigger_flags"] == (
        "orderbook_active_event_count:1",
        "semantic_active_event_count:1",
        "support_present",
        "persistence_present",
        "persistence_observable",
        "liquidity_balance:bid_support",
        "wall_persistence_bias:bid_support",
    )
    assert stable["diagnostics"]["builder_type"] == "prediction_liquidity_board_history"
    assert stable["diagnostics"]["caller"] == "unit_test"

    caution_summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-17T03:51:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": "allow_structural_use",
                "interpretation_reason": "ok",
                "semantic_observer_status": "healthy",
                "semantic_usage_summary": {
                    "source_kind": "market_state_semantic_usage_summary",
                    "contract_source": "l3_event_usage_policy",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "observer_status": "healthy",
                    "active_event_count": 2,
                    "mapped_event_count": 2,
                    "unknown_event_count": 0,
                },
                "semantic_usage_contract_rows": [
                    {
                        "event_family": "wall",
                        "usage_grade": "strong",
                        "contract_source": "l3_event_usage_policy",
                        "meaning_version": "l3_event_usage_policy.v1alpha1",
                        "interpretation_bucket": "allow_structural_use",
                    }
                ],
                "orderbook_semantics_summary": {
                    "summary_slots_present": ["support", "resistance"],
                    "active_event_count": 2,
                    "active_event_names": [
                        "support_candidate",
                        "resistance_candidate",
                    ],
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": False,
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 40.0,
                "preferred_row_freshness": "QUIET",
            },
        )
    )

    caution_digest = HealthDigest(
        digest_type="health_digest",
        digest_version="v1alpha1",
        source_kind="health_data_service",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-17T03:51:00Z",
        freshness="LIVE",
        is_stale=False,
        market_runtime={"interpretation_bucket": "allow_structural_use"},
        semantic_usage={"observer_status": "caution"},
        orderbook_runtime={"wiring_status": "partial"},
        diagnostics={},
    )

    caution = build_prediction_liquidity_board_history(
        PredictionLiquidityBoardHistoryBuildInput(
            market_summary=caution_summary,
            health_digest=caution_digest,
        )
    )

    assert caution["history_window_sec"] == 300
    assert caution["liquidity_pressure_balance"] == "balanced"
    assert caution["wall_persistence_bias"] == "unknown"
    assert caution["persistence_confidence"] == "low"
    assert caution["trigger_flags"] == (
        "orderbook_active_event_count:2",
        "semantic_active_event_count:2",
        "support_present",
        "resistance_present",
        "persistence_not_observable",
        "health_observer:caution",
        "liquidity_balance:balanced",
        "wall_persistence_bias:unknown",
    )

    blocked = build_prediction_liquidity_board_history(
        PredictionLiquidityBoardHistoryBuildInput()
    )
    assert blocked["market_uid"] is None
    assert blocked["event_ts"] is None
    assert blocked["freshness"] == "UNKNOWN"
    assert blocked["is_stale"] is None
    assert blocked["history_window_sec"] == 0
    assert blocked["liquidity_pressure_balance"] == "unknown"
    assert blocked["wall_persistence_bias"] == "unknown"
    assert blocked["persistence_confidence"] == "unknown"
    assert blocked["trigger_flags"] == ("market_summary_absent",)

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())