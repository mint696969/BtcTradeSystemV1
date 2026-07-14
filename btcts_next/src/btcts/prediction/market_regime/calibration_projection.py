# path: ./btcts_next/src/btcts/prediction/market_regime/calibration_projection.py
# desc: Pure MR-F7 projection from calibration estimates to forecast/card display contracts. No I/O or runtime fitting.

from __future__ import annotations

from dataclasses import replace
from enum import Enum
from typing import Any, Mapping

from .calibration_dataset import CalibrationSampleMaturity
from .calibration_estimator import MarketRegimeCalibrationEstimate
from .future_forecast_contract import FutureForecastStatus, MarketRegimeFutureForecast

MARKET_REGIME_CALIBRATION_PROJECTION_VERSION = "prediction.market_regime.calibration_projection.mr_f7.v1"


class CalibrationDisplayState(str, Enum):
    UNCALIBRATED = "UNCALIBRATED"
    INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"
    PROVISIONAL = "PROVISIONAL"
    CAPPED = "CAPPED"
    CALIBRATED = "CALIBRATED"


def calibration_display_state(estimate: MarketRegimeCalibrationEstimate | None) -> CalibrationDisplayState:
    if estimate is None:
        return CalibrationDisplayState.UNCALIBRATED
    if estimate.calibrated_reliability is None or estimate.maturity is CalibrationSampleMaturity.EMPTY:
        return CalibrationDisplayState.INSUFFICIENT_SAMPLE
    if estimate.cap_reasons:
        return CalibrationDisplayState.CAPPED
    if estimate.calibrated_probability_claim and estimate.maturity is CalibrationSampleMaturity.MATURE:
        return CalibrationDisplayState.CALIBRATED
    return CalibrationDisplayState.PROVISIONAL


def project_calibration_estimate_to_future_forecast(
    forecast: MarketRegimeFutureForecast,
    estimate: MarketRegimeCalibrationEstimate | None,
) -> MarketRegimeFutureForecast:
    state = calibration_display_state(estimate)
    if forecast.status is FutureForecastStatus.ABSTAIN:
        return replace(
            forecast,
            calibrated_reliability=None,
            calibration_display_confidence=None,
            calibrated_probability_claim=False,
            calibration_state=CalibrationDisplayState.UNCALIBRATED.value,
            calibration_sample_count=0,
            calibration_maturity="",
            calibration_cap_reasons=(),
            calibration_estimator_version="",
        )
    if estimate is None or estimate.calibrated_reliability is None:
        return replace(
            forecast,
            calibrated_reliability=None,
            calibration_display_confidence=None,
            calibrated_probability_claim=False,
            calibration_state=state.value,
            calibration_sample_count=0 if estimate is None else int(estimate.sample_count),
            calibration_maturity="" if estimate is None else estimate.maturity.value,
            calibration_cap_reasons=() if estimate is None else tuple(estimate.cap_reasons),
            calibration_estimator_version="" if estimate is None else estimate.estimator_version,
        )
    return replace(
        forecast,
        calibrated_reliability=float(estimate.calibrated_reliability),
        calibration_display_confidence=(
            None if estimate.display_confidence is None else float(estimate.display_confidence)
        ),
        calibrated_probability_claim=bool(estimate.calibrated_probability_claim and state is CalibrationDisplayState.CALIBRATED),
        calibration_state=state.value,
        calibration_sample_count=int(estimate.sample_count),
        calibration_maturity=estimate.maturity.value,
        calibration_cap_reasons=tuple(estimate.cap_reasons),
        calibration_estimator_version=estimate.estimator_version,
    )


def project_calibration_estimate_to_card(
    card: Mapping[str, Any],
    estimate: MarketRegimeCalibrationEstimate | None,
    *,
    replace_display_confidence: bool = False,
) -> dict[str, Any]:
    row = dict(card)
    detail = dict(row.get("detail") if isinstance(row.get("detail"), Mapping) else {})
    state = calibration_display_state(estimate)
    detail["calibration_projection_version"] = MARKET_REGIME_CALIBRATION_PROJECTION_VERSION
    detail["calibration_state"] = state.value
    detail["calibrated_probability_claim"] = False
    detail["calibrated_reliability_percent"] = None
    detail["calibration_display_confidence_percent"] = None
    detail["calibration_sample_count"] = 0
    detail["calibration_maturity"] = ""
    detail["calibration_cap_reasons"] = []
    detail["display_confidence_replaced_by_calibration"] = False
    if estimate is not None:
        detail["calibration_sample_count"] = int(estimate.sample_count)
        detail["calibration_maturity"] = estimate.maturity.value
        detail["calibration_cap_reasons"] = list(estimate.cap_reasons)
        if estimate.calibrated_reliability is not None:
            detail["calibrated_reliability_percent"] = round(float(estimate.calibrated_reliability) * 100.0, 2)
        if estimate.display_confidence is not None:
            detail["calibration_display_confidence_percent"] = round(float(estimate.display_confidence) * 100.0, 2)
        claim = bool(estimate.calibrated_probability_claim and state is CalibrationDisplayState.CALIBRATED)
        detail["calibrated_probability_claim"] = claim
        if replace_display_confidence and claim and estimate.display_confidence is not None:
            row["confidence_percent"] = round(float(estimate.display_confidence) * 100.0, 2)
            detail["display_confidence_replaced_by_calibration"] = True
    row["detail"] = detail
    return row
