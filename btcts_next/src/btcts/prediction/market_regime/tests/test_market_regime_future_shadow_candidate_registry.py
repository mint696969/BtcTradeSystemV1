# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_candidate_registry.py
# desc: Tests for MR-F5 operational future-shadow two-candidate registry and parameterized baseline identity.

from __future__ import annotations

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_shadow_candidate_registry import (
    BASELINE_CANDIDATE,
    CONSERVATIVE_CANDIDATE,
    build_default_future_shadow_candidate_registry,
    validate_future_shadow_candidate_registry,
)


def _evidence() -> FutureBaselineEvidence:
    return FutureBaselineEvidence(
        origin_timestamp="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=900,
        feature_snapshot_ref="snapshot:candidate-registry",
        regime_scores={
            MarketRegimeCode.BREAKOUT: 0.44,
            MarketRegimeCode.RANGE: 0.34,
            MarketRegimeCode.UP_TREND: 0.22,
        },
        available_feature_families=("price_structure", "volatility", "liquidity", "source_quality", "microprice"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )


def test_default_registry_has_exactly_two_safe_candidates() -> None:
    registry = build_default_future_shadow_candidate_registry()
    validation = validate_future_shadow_candidate_registry(registry)
    assert validation["ok"] is True
    assert validation["candidate_count"] == 2
    assert validation["live_parameter_apply_allowed"] is False
    assert registry[0].registry_state == "active"
    assert registry[1].registry_state == "shadow"


def test_candidate_parameter_set_identity_is_preserved() -> None:
    baseline = forecast_future_market_regime_baseline(_evidence(), candidate=BASELINE_CANDIDATE)
    conservative = forecast_future_market_regime_baseline(_evidence(), candidate=CONSERVATIVE_CANDIDATE)
    assert baseline.parameter_set_id == BASELINE_CANDIDATE.parameter_set_id
    assert conservative.parameter_set_id == CONSERVATIVE_CANDIDATE.parameter_set_id
    assert baseline.parameter_set_id != conservative.parameter_set_id


def test_conservative_candidate_can_abstain_when_baseline_forecasts() -> None:
    baseline = forecast_future_market_regime_baseline(_evidence(), candidate=BASELINE_CANDIDATE)
    conservative = forecast_future_market_regime_baseline(_evidence(), candidate=CONSERVATIVE_CANDIDATE)
    assert baseline.status.value == "FORECAST"
    assert conservative.status.value == "ABSTAIN"
    assert conservative.abstain_reason == "score_margin_below_minimum"
