# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_baseline_model.py
# desc: Pure MR-F5.3 tests for the transparent shadow future MarketRegime baseline model.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import (
    FutureBaselineEvidence,
    forecast_future_market_regime_baseline,
)
from btcts.prediction.market_regime.future_forecast_contract import FutureForecastStatus
from btcts.prediction.market_regime.transition_policy import evaluate_market_regime_transition


def _evidence(**overrides) -> FutureBaselineEvidence:
    values = {
        "origin_timestamp": "2026-07-12T00:00:00Z",
        "origin_current_state": MarketRegimeCode.LOW_VOL_COMPRESSION,
        "target_horizon_sec": 900,
        "feature_snapshot_ref": "feature_snapshot:mr_f5_3:test",
        "regime_scores": {
            MarketRegimeCode.BREAKOUT: 0.80,
            MarketRegimeCode.RANGE: 0.20,
            MarketRegimeCode.UP_TREND: 0.10,
        },
        "available_feature_families": ("price_structure", "volatility", "liquidity", "source_quality", "orderflow"),
        "source_timestamp_epoch_sec": 100.0,
        "origin_timestamp_epoch_sec": 100.0,
    }
    values.update(overrides)
    return FutureBaselineEvidence(**values)


def test_transparent_baseline_forecasts_exact_horizon_contract() -> None:
    result = forecast_future_market_regime_baseline(_evidence())
    assert result.status is FutureForecastStatus.FORECAST
    assert result.predicted_future_state is MarketRegimeCode.BREAKOUT
    assert result.target_horizon_sec == 900
    assert result.target_definition_version == "market_regime_target.900s.v1"
    assert result.metadata["shadow_only"] is True
    assert result.metadata["canonical_replacement"] is False
    assert result.calibrated_reliability is None


def test_multistep_transition_path_is_explicit_and_bounded() -> None:
    result = forecast_future_market_regime_baseline(_evidence(regime_scores={MarketRegimeCode.UP_TREND: 0.9, MarketRegimeCode.RANGE: 0.1}))
    assert tuple(step.regime for step in result.transition_path_candidate) == (MarketRegimeCode.BREAKOUT, MarketRegimeCode.UP_TREND)
    assert result.transition_path_candidate[-1].earliest_offset_sec == 900


def test_missing_required_feature_abstains() -> None:
    result = forecast_future_market_regime_baseline(_evidence(available_feature_families=("price_structure", "volatility", "source_quality")))
    assert result.status is FutureForecastStatus.ABSTAIN
    assert result.predicted_future_state is MarketRegimeCode.UNKNOWN
    assert result.abstain_reason == "required_feature_family_missing"
    assert "missing_required_feature:liquidity" in result.invalidation_conditions


def test_long_horizon_requires_session_context() -> None:
    result = forecast_future_market_regime_baseline(_evidence(target_horizon_sec=21600))
    assert result.status is FutureForecastStatus.ABSTAIN
    assert "missing_required_feature:session_context" in result.invalidation_conditions


def test_low_top_score_and_small_margin_abstain_independently() -> None:
    low_top = forecast_future_market_regime_baseline(
        _evidence(
            regime_scores={
                MarketRegimeCode.BREAKOUT: 0.2,
                MarketRegimeCode.RANGE: 0.2,
                MarketRegimeCode.UP_TREND: 0.2,
                MarketRegimeCode.DOWN_TREND: 0.2,
            }
        )
    )
    assert low_top.abstain_reason == "top_score_below_minimum"

    small_margin = forecast_future_market_regime_baseline(
        _evidence(
            regime_scores={
                MarketRegimeCode.BREAKOUT: 0.40,
                MarketRegimeCode.RANGE: 0.35,
                MarketRegimeCode.UP_TREND: 0.25,
            }
        )
    )
    assert small_margin.abstain_reason == "score_margin_below_minimum"

    one = forecast_future_market_regime_baseline(
        _evidence(regime_scores={MarketRegimeCode.BREAKOUT: 1.0})
    )
    assert one.abstain_reason == "insufficient_ranked_regime_candidates"


def test_origin_state_and_feature_family_names_fail_closed() -> None:
    with pytest.raises(ValueError, match="future_baseline_origin_current_state_invalid"):
        _evidence(origin_current_state="RANGE")
    with pytest.raises(ValueError, match="future_baseline_feature_family_invalid"):
        _evidence(available_feature_families=("price_structure", ""))


def test_future_transition_graph_matches_mr_f4_adjacency() -> None:
    regimes = tuple(MarketRegimeCode)
    for origin in regimes:
        for target in regimes:
            if target is MarketRegimeCode.UNKNOWN:
                continue
            result = evaluate_market_regime_transition(
                previous_regime=origin.value,
                candidate_regime=target.value,
                previous_state_age_sec=999999,
                candidate_score=1.0,
                runner_up_score=0.0,
                change_point_evidence_score=1.0,
            )
            direct_allowed = origin is target or bool(result["transition_allowed"])
            if origin is target:
                assert direct_allowed is True
            elif direct_allowed:
                from btcts.prediction.market_regime.future_baseline_model import _FUTURE_ALLOWED_TRANSITIONS
                assert target in _FUTURE_ALLOWED_TRANSITIONS[origin]
            else:
                from btcts.prediction.market_regime.future_baseline_model import _FUTURE_ALLOWED_TRANSITIONS
                assert target not in _FUTURE_ALLOWED_TRANSITIONS[origin]


def test_lookahead_and_invalid_scores_fail_closed() -> None:
    with pytest.raises(ValueError, match="lookahead_source_timestamp_after_origin"):
        _evidence(source_timestamp_epoch_sec=101.0)
    with pytest.raises(ValueError, match="future_baseline_regime_score_invalid"):
        _evidence(regime_scores={MarketRegimeCode.BREAKOUT: -0.1, MarketRegimeCode.RANGE: 0.2})


def test_input_mapping_is_defensively_frozen() -> None:
    scores = {MarketRegimeCode.BREAKOUT: 0.8, MarketRegimeCode.RANGE: 0.2}
    evidence = _evidence(regime_scores=scores)
    scores[MarketRegimeCode.BREAKOUT] = 0.0
    assert evidence.regime_scores[MarketRegimeCode.BREAKOUT] == 0.8
    with pytest.raises(TypeError):
        evidence.regime_scores[MarketRegimeCode.BREAKOUT] = 0.1  # type: ignore[index]
