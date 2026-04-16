# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_summary_builder.py
# desc: Verify shared prediction summary first-slice builder stays wording-free and market_summary-anchored.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (
    HealthDigest,
    MarketSummary,
    PredictionSummaryBuildInput,
    build_prediction_summary,
)


def main() -> int:
    summary = MarketSummary(
        summary_type="market_summary",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        source_kind="market_state_preferred",
        source_series_id="bf-sess-1:series:100",
        event_ts="2026-04-15T12:00:00Z",
        age_sec=6.0,
        freshness="LIVE",
        is_stale=False,
        trust_state="trusted",
        continuity_state="continuous",
        interpretation_bucket="allow_structural_use",
        interpretation_reason="ok",
        market_state_label=None,
        participation_state=None,
        liquidity_bias=None,
        semantic_summary_source="market_state_semantic_usage_summary",
        semantic_contract_source="l3_event_usage_policy",
        semantic_meaning_version="l3_event_usage_policy.v1alpha1",
        semantic_observer_status="healthy",
        semantic_observer_present=True,
        semantic_usage_summary_present=True,
        semantic_contract_rows_present=True,
        semantic_contract_rows_count=2,
        semantic_runtime_wiring_status="wired",
        semantic_total_rows=8,
        semantic_active_event_count=2,
        semantic_mapped_event_count=2,
        semantic_unknown_event_count=0,
        semantic_event_family_distribution={"wall": 1, "support_resistance": 1},
        semantic_trust_bucket_distribution={"trusted": 2},
        semantic_interpretation_bucket_distribution={"allow_structural_use": 2},
        semantic_consumer_distribution={"ui": 2, "ai": 2},
        semantic_usage_contract_rows=[
            {
                "contract_source": "l3_event_usage_policy",
                "interpretation_bucket": "allow_structural_use",
                "meaning_version": "l3_event_usage_policy.v1alpha1",
                "event_family": "wall",
                "usage_grade": "strong",
            }
        ],
        orderbook_active_event_contracts=[
            {
                "contract_source": "l3_event_usage_policy",
                "event_name": "support_candidate",
                "event_family": "support_resistance",
                "usage_grade": "strong",
                "interpretation_bucket": "allow_structural_use",
                "meaning_version": "l3_event_usage_policy.v1alpha1",
                "confidence": 0.85,
                "trust_bucket": "trusted",
                "consumer_allowed": ["ui", "ai", "strategy"],
                "actionability": "actionable",
                "forecast_horizon_hint": "short",
                "half_life_sec": 30,
                "invalidates_on": ["series_boundary", "reanchor_required"],
                "evidence_refs": [],
                "side": "bid",
            }
        ],
        orderbook_active_event_names=["support_candidate"],
        orderbook_active_event_count=1,
        orderbook_summary_slots_present=["near_wall", "support", "persistence"],
        orderbook_summary_slots_count=3,
        orderbook_near_wall_present=True,
        orderbook_support_present=True,
        orderbook_resistance_present=False,
        orderbook_persistence_present=True,
        orderbook_wiring_status="partial",
        orderbook_contract_status_source="market_state_orderbook_contract_status",
        orderbook_persistence_observable=True,
        notable_events=["fresh_source"],
        alert_candidates=[],
        diagnostics={},
    )

    prediction = build_prediction_summary(
        PredictionSummaryBuildInput(
            market_summary=summary,
            horizon="short",
        )
    )

    assert prediction.prediction_type == "shared_prediction_summary"
    assert prediction.prediction_version == "phase3.v1alpha1"
    assert prediction.source_kind == "market_summary_anchor"
    assert prediction.market_uid == "bitflyer.spot.BTC_JPY"
    assert prediction.event_ts == "2026-04-15T12:00:00Z"
    assert prediction.freshness == "LIVE"
    assert prediction.is_stale is False
    assert prediction.horizon == "short"

    assert prediction.caution_level == "low"
    assert prediction.short_horizon_bias == "bullish"
    assert prediction.continuation_likelihood == "high"
    assert prediction.mean_reversion_likelihood == "medium"
    assert prediction.regime_transition_risk == "low"
    assert prediction.liquidity_deterioration_risk == "low"
    assert prediction.execution_feasibility_hint == "favorable"
    assert prediction.confidence == 0.75

    assert prediction.evidence["summary_source"] == "market_state_preferred"
    assert prediction.evidence["semantic_runtime_wiring_status"] == "wired"
    assert prediction.evidence["orderbook_wiring_status"] == "partial"
    assert prediction.evidence["interpretation_bucket"] == "allow_structural_use"
    assert prediction.evidence["trust_state"] == "trusted"
    assert prediction.evidence["continuity_state"] == "continuous"
    assert prediction.evidence["semantic_active_event_count"] == 2
    assert prediction.evidence["orderbook_active_event_count"] == 1
    assert prediction.evidence["orderbook_summary_slots_present"] == [
        "near_wall",
        "support",
        "persistence",
    ]
    assert prediction.evidence["orderbook_persistence_observable"] is True
    assert prediction.evidence["notable_events"] == ["fresh_source"]
    assert prediction.evidence["alert_candidates"] == []

    assert prediction.evidence["health_digest_present"] is False

    caution_digest = HealthDigest(
        digest_type="health_digest",
        digest_version="v1alpha1",
        source_kind="health_data_service",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-15T12:00:00Z",
        freshness="LIVE",
        is_stale=False,
        collector_runtime={},
        api_runtime={},
        ws_runtime={},
        market_runtime={
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "observe_only",
        },
        semantic_usage={
            "observer_status": "caution",
        },
        orderbook_runtime={
            "wiring_status": "partial",
        },
        diagnostics={},
    )

    cautioned = build_prediction_summary(
        PredictionSummaryBuildInput(
            market_summary=summary,
            health_digest=caution_digest,
            horizon="short",
        )
    )
    assert cautioned.caution_level == "medium"
    assert cautioned.evidence["health_digest_present"] is True
    assert cautioned.evidence["health_freshness"] == "LIVE"
    assert cautioned.evidence["health_is_stale"] is False
    assert cautioned.evidence["health_semantic_observer_status"] == "caution"
    assert cautioned.evidence["health_orderbook_wiring_status"] == "partial"
    assert cautioned.diagnostics["health_digest_present"] is True

    blocked = build_prediction_summary(PredictionSummaryBuildInput())
    assert blocked.market_uid is None
    assert blocked.freshness == "UNKNOWN"
    assert blocked.is_stale is None
    assert blocked.horizon == "short"
    assert blocked.caution_level == "blocked"
    assert blocked.short_horizon_bias == "unknown"
    assert blocked.continuation_likelihood == "unknown"
    assert blocked.mean_reversion_likelihood == "unknown"
    assert blocked.regime_transition_risk == "unknown"
    assert blocked.liquidity_deterioration_risk == "unknown"
    assert blocked.execution_feasibility_hint == "unknown"
    assert blocked.confidence == 0.0
    assert blocked.evidence == {}

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())