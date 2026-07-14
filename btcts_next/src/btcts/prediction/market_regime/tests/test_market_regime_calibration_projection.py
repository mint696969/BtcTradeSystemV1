# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_calibration_projection.py
# desc: MR-F7 forecast/card calibration projection guards.

from __future__ import annotations

from btcts.prediction.market_regime.calibration_dataset import CalibrationSampleMaturity
from btcts.prediction.market_regime.calibration_estimator import MarketRegimeCalibrationEstimate
from btcts.prediction.market_regime.calibration_projection import (
    CalibrationDisplayState,
    calibration_display_state,
    project_calibration_estimate_to_card,
    project_calibration_estimate_to_future_forecast,
)
from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_forecast_contract import (
    FutureForecastStatus,
    FutureTransitionStep,
    MarketRegimeFutureForecast,
)


def _forecast() -> MarketRegimeFutureForecast:
    return MarketRegimeFutureForecast(
        origin_timestamp="2026-07-15T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=900,
        predicted_future_state=MarketRegimeCode.BREAKOUT,
        status=FutureForecastStatus.FORECAST,
        transition_path_candidate=(FutureTransitionStep(MarketRegimeCode.BREAKOUT, 300),),
        raw_model_score_or_probability=0.9,
        feature_snapshot_ref="feature:1",
        model_id="model.v1",
        logic_version="logic.v1",
        parameter_set_id="params.v1",
        target_definition_version="market_regime_target.900s.v1",
    )


def _estimate(*, claim: bool, maturity: CalibrationSampleMaturity, caps: tuple[str, ...] = ()) -> MarketRegimeCalibrationEstimate:
    return MarketRegimeCalibrationEstimate(
        raw_confidence=0.9,
        calibrated_reliability=0.8,
        display_confidence=0.75 if caps else 0.8,
        sample_count=120 if maturity is CalibrationSampleMaturity.MATURE else 30,
        maturity=maturity,
        matched_level="confidence",
        matched_key="90_100",
        fallback_chain=("confidence",),
        cap_reasons=caps,
        calibrated_probability_claim=claim,
    )


def test_only_mature_uncapped_estimate_becomes_calibrated_claim() -> None:
    estimate = _estimate(claim=True, maturity=CalibrationSampleMaturity.MATURE)
    projected = project_calibration_estimate_to_future_forecast(_forecast(), estimate)
    assert projected.calibration_state == CalibrationDisplayState.CALIBRATED.value
    assert projected.calibrated_probability_claim is True
    assert projected.calibrated_reliability == 0.8
    assert projected.calibration_display_confidence == 0.8


def test_capped_or_provisional_estimate_never_claims_calibrated_probability() -> None:
    capped = _estimate(claim=False, maturity=CalibrationSampleMaturity.MATURE, caps=("freshness_cap",))
    projected = project_calibration_estimate_to_future_forecast(_forecast(), capped)
    assert projected.calibration_state == CalibrationDisplayState.CAPPED.value
    assert projected.calibrated_reliability == 0.8
    assert projected.calibration_display_confidence == 0.75
    assert projected.calibrated_probability_claim is False
    provisional = _estimate(claim=False, maturity=CalibrationSampleMaturity.PROVISIONAL)
    assert calibration_display_state(provisional) is CalibrationDisplayState.PROVISIONAL


def test_card_confidence_is_not_replaced_without_explicit_mature_claim() -> None:
    card = {"confidence_percent": 90, "detail": {}}
    provisional = _estimate(claim=False, maturity=CalibrationSampleMaturity.PROVISIONAL)
    projected = project_calibration_estimate_to_card(card, provisional, replace_display_confidence=True)
    assert projected["confidence_percent"] == 90
    assert projected["detail"]["display_confidence_replaced_by_calibration"] is False


def test_card_confidence_replacement_requires_explicit_switch_and_calibrated_claim() -> None:
    card = {"confidence_percent": 90, "detail": {}}
    mature = _estimate(claim=True, maturity=CalibrationSampleMaturity.MATURE)
    shadow = project_calibration_estimate_to_card(card, mature)
    assert shadow["confidence_percent"] == 90
    replaced = project_calibration_estimate_to_card(card, mature, replace_display_confidence=True)
    assert replaced["confidence_percent"] == 80.0
    assert replaced["detail"]["calibrated_reliability_percent"] == 80.0
    assert replaced["detail"]["calibration_display_confidence_percent"] == 80.0
    assert replaced["detail"]["calibrated_probability_claim"] is True
    assert replaced["detail"]["display_confidence_replaced_by_calibration"] is True
