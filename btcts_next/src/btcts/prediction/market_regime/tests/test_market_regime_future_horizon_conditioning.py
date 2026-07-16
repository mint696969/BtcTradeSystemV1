# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_horizon_conditioning.py
# desc: MR-F9.18A12 guards for bounded distribution-only sequential conditioning.

from __future__ import annotations

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_forecast_contract import (
    FutureForecastStatus,
    FutureTransitionStep,
    MarketRegimeFutureForecast,
)
from btcts.prediction.market_regime.future_horizon_conditioning import condition_horizon_regime_scores


def _forecast(*, status: FutureForecastStatus, margin: float = 0.4):
    return MarketRegimeFutureForecast(
        origin_timestamp="2026-07-16T10:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=300,
        predicted_future_state=(MarketRegimeCode.UP_TREND if status is FutureForecastStatus.FORECAST else MarketRegimeCode.UNKNOWN),
        status=status,
        transition_path_candidate=(
            (FutureTransitionStep(MarketRegimeCode.BREAKOUT, 150), FutureTransitionStep(MarketRegimeCode.UP_TREND, 300))
            if status is FutureForecastStatus.FORECAST else ()
        ),
        raw_model_score_or_probability=(0.6 if status is FutureForecastStatus.FORECAST else None),
        feature_snapshot_ref="snapshot:test",
        model_id="model:test",
        logic_version="logic:test",
        parameter_set_id="params:test",
        target_definition_version="market_regime_target.300s.v1",
        abstain_reason=("score_margin_below_minimum" if status is FutureForecastStatus.ABSTAIN else ""),
        metadata={"normalized_score_margin": margin},
    )


def test_forecast_predecessor_changes_distribution_without_copying_label() -> None:
    result, diagnostics = condition_horizon_regime_scores(
        local_scores={MarketRegimeCode.RANGE: 0.6, MarketRegimeCode.DOWN_TREND: 0.4},
        predecessor_scores={MarketRegimeCode.UP_TREND: 0.8, MarketRegimeCode.RANGE: 0.2},
        predecessor_forecast=_forecast(status=FutureForecastStatus.FORECAST, margin=0.5),
        transition_prior_fraction_of_top=0.2,
    )
    assert result[MarketRegimeCode.UP_TREND] > 0.0
    assert result[MarketRegimeCode.RANGE] > 0.6
    assert diagnostics["conditioning_applied"] is True
    assert diagnostics["conditioning_weight"] == 0.1
    assert diagnostics["predecessor_label_copied"] is False
    assert diagnostics["distribution_context_only"] is True


def test_abstain_predecessor_adds_no_directional_score() -> None:
    local = {MarketRegimeCode.RANGE: 0.6, MarketRegimeCode.DOWN_TREND: 0.4}
    result, diagnostics = condition_horizon_regime_scores(
        local_scores=local,
        predecessor_scores={MarketRegimeCode.UP_TREND: 1.0},
        predecessor_forecast=_forecast(status=FutureForecastStatus.ABSTAIN),
        transition_prior_fraction_of_top=0.2,
    )
    assert dict(result) == local
    assert diagnostics["conditioning_applied"] is False
    assert diagnostics["reason"] == "predecessor_abstained"


def test_larger_predecessor_margin_has_larger_bounded_effect() -> None:
    kwargs = {
        "local_scores": {MarketRegimeCode.RANGE: 1.0},
        "predecessor_scores": {MarketRegimeCode.UP_TREND: 1.0},
        "transition_prior_fraction_of_top": 0.2,
    }
    low, low_diag = condition_horizon_regime_scores(
        predecessor_forecast=_forecast(status=FutureForecastStatus.FORECAST, margin=0.1),
        **kwargs,
    )
    high, high_diag = condition_horizon_regime_scores(
        predecessor_forecast=_forecast(status=FutureForecastStatus.FORECAST, margin=0.8),
        **kwargs,
    )
    assert high[MarketRegimeCode.UP_TREND] > low[MarketRegimeCode.UP_TREND]
    assert low_diag["conditioning_weight"] == 0.02
    assert high_diag["conditioning_weight"] == 0.16
    assert high_diag["conditioning_weight"] < 0.2
