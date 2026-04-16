# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_summary_state.py
# desc: Verify prediction_summary_state builds a first-adopter state from market_summary with optional health caution input.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.prediction_summary_state as state_mod  # noqa: E402
from btcts.processing.l4_consumer_models.shared import HealthDigest, MarketSummary  # noqa: E402


def _market_summary() -> MarketSummary:
    return MarketSummary(
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
        semantic_usage_contract_rows=[],
        orderbook_active_event_contracts=[],
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


def _health_digest(observer_status: str) -> HealthDigest:
    return HealthDigest(
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
            "observer_status": observer_status,
        },
        orderbook_runtime={
            "wiring_status": "partial",
        },
        diagnostics={},
    )


def main() -> int:
    original_load_latest_market_summary = state_mod.load_latest_market_summary
    original_load_health_current_state_bundle = state_mod.load_health_current_state_bundle

    try:
        state_mod.load_latest_market_summary = lambda **_: _market_summary()
        state_mod.load_health_current_state_bundle = lambda: {
            "health_digest": _health_digest("caution")
        }

        with_health = state_mod.load_prediction_summary_state()
        assert with_health["source_label"] == "market_summary + health_digest_caution"
        assert with_health["summary_source"] == "market_summary_anchor"
        assert with_health["health_caution_used"] is True
        assert with_health["prediction"].caution_level == "medium"
        assert with_health["prediction"].evidence["health_digest_present"] is True

        state_mod.load_health_current_state_bundle = lambda: {}
        no_health = state_mod.load_prediction_summary_state(include_health_caution=True)
        assert no_health["source_label"] == "market_summary"
        assert no_health["health_caution_used"] is False
        assert no_health["prediction"].market_uid == "bitflyer.spot.BTC_JPY"
        assert no_health["prediction"].evidence["health_digest_present"] is False

        disabled_health = state_mod.load_prediction_summary_state(
            include_health_caution=False
        )
        assert disabled_health["source_label"] == "market_summary"
        assert disabled_health["health_caution_used"] is False
        assert disabled_health["prediction"].short_horizon_bias == "bullish"
    finally:
        state_mod.load_latest_market_summary = original_load_latest_market_summary
        state_mod.load_health_current_state_bundle = (
            original_load_health_current_state_bundle
        )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())