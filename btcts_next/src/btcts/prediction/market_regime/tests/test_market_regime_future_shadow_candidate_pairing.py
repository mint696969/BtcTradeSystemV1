# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_candidate_pairing.py
# desc: MR-F8.3 tests for paired active/shadow forecasts generated from one immutable evidence slot.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_candidate_registry import BASELINE_CANDIDATE


def evidence() -> FutureBaselineEvidence:
    return FutureBaselineEvidence(
        origin_timestamp="2026-07-15T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=900,
        feature_snapshot_ref="snapshot:mr-f8.3",
        regime_scores={
            MarketRegimeCode.BREAKOUT: 0.44,
            MarketRegimeCode.RANGE: 0.34,
            MarketRegimeCode.UP_TREND: 0.22,
        },
        available_feature_families=("price_structure", "volatility", "liquidity", "source_quality", "microprice"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )


def test_generates_two_forecasts_from_identical_slot() -> None:
    result = build_future_shadow_candidate_pair(evidence=evidence())
    assert result["candidate_count"] == 2
    assert len(result["forecasts"]) == 2
    slots = {
        (
            row["origin_timestamp"],
            row["feature_snapshot_ref"],
            row["target_horizon_sec"],
            row["target_definition_version"],
        )
        for row in result["forecasts"]
    }
    assert len(slots) == 1
    assert result["comparison_ready_for_outcome_join"] is True


def test_preserves_parameter_identity_and_abstention_difference() -> None:
    result = build_future_shadow_candidate_pair(evidence=evidence())
    rows = {row["parameter_set_id"]: row for row in result["forecasts"]}
    assert rows["market_regime.future.transparent_baseline.params.v1"]["forecast_status"] == "FORECAST"
    assert rows["market_regime.future.transparent_baseline.params.conservative.v1"]["forecast_status"] == "ABSTAIN"


def test_single_candidate_registry_fails_closed() -> None:
    with pytest.raises(ValueError, match="registry_invalid"):
        build_future_shadow_candidate_pair(evidence=evidence(), candidates=(BASELINE_CANDIDATE,))


def test_output_is_immutable_and_never_enables_apply() -> None:
    result = build_future_shadow_candidate_pair(evidence=evidence())
    with pytest.raises(TypeError):
        result["candidate_count"] = 1
    assert result["safety"]["writes_dhot"] is False
    assert result["safety"]["parameter_auto_promotion_allowed"] is False
    assert result["safety"]["live_parameter_apply_allowed"] is False
