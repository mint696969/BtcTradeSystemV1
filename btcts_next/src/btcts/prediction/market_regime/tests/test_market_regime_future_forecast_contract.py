# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_forecast_contract.py
# desc: Pure contract tests for MR-F5.1 horizon-specific future MarketRegime forecast invariants.

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_forecast_contract import (
    FUTURE_MARKET_REGIME_HORIZONS_SEC,
    FutureForecastStatus,
    FutureTransitionStep,
    MarketRegimeFutureForecast,
    validate_future_forecast_set,
)


def _forecast(horizon_sec: int = 900) -> MarketRegimeFutureForecast:
    return MarketRegimeFutureForecast(
        origin_timestamp="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        target_horizon_sec=horizon_sec,
        predicted_future_state=MarketRegimeCode.BREAKOUT,
        status=FutureForecastStatus.FORECAST,
        transition_path_candidate=(FutureTransitionStep(MarketRegimeCode.BREAKOUT, min(horizon_sec, 300), ("compression_release",)),),
        raw_model_score_or_probability=0.61,
        feature_snapshot_ref="feature_snapshot:abc",
        model_id="market_regime_future_baseline.shadow.v1",
        logic_version="logic.v1",
        parameter_set_id="params.v1",
        target_definition_version=f"market_regime_target.{horizon_sec}s.v1",
        invalidation_conditions=("source_quality_below_minimum",),
    )


def test_enabled_future_horizons_are_exact_and_exclude_current() -> None:
    assert FUTURE_MARKET_REGIME_HORIZONS_SEC == (300, 900, 1800, 3600, 21600, 43200, 86400)
    assert 0 not in FUTURE_MARKET_REGIME_HORIZONS_SEC


def test_contract_is_immutable_and_preserves_origin_state() -> None:
    result = _forecast()
    assert result.origin_current_state is MarketRegimeCode.LOW_VOL_COMPRESSION
    with pytest.raises(FrozenInstanceError):
        result.target_horizon_sec = 300  # type: ignore[misc]


def test_unsupported_or_current_horizon_fails_closed() -> None:
    with pytest.raises(ValueError, match="unsupported_future_horizon_sec"):
        _forecast(0)
    with pytest.raises(ValueError, match="unsupported_future_horizon_sec"):
        _forecast(600)


def test_transition_terminal_state_must_match_prediction() -> None:
    with pytest.raises(ValueError, match="transition_path_terminal_state_mismatch"):
        MarketRegimeFutureForecast(
            **{**_forecast().__dict__, "transition_path_candidate": (FutureTransitionStep(MarketRegimeCode.RANGE, 300),)}
        )


def test_abstain_requires_unknown_reason_and_empty_path() -> None:
    result = MarketRegimeFutureForecast(
        **{
            **_forecast(21600).__dict__,
            "predicted_future_state": MarketRegimeCode.UNKNOWN,
            "status": FutureForecastStatus.ABSTAIN,
            "transition_path_candidate": (),
            "raw_model_score_or_probability": None,
            "abstain_reason": "long_horizon_context_insufficient",
        }
    )
    assert result.predicted_future_state is MarketRegimeCode.UNKNOWN
    with pytest.raises(ValueError, match="abstain_reason_required"):
        MarketRegimeFutureForecast(**{**result.__dict__, "abstain_reason": ""})


def test_target_definition_version_must_match_horizon() -> None:
    with pytest.raises(ValueError, match="target_definition_version_horizon_mismatch"):
        MarketRegimeFutureForecast(
            **{**_forecast(900).__dict__, "target_definition_version": "market_regime_target.300s.v1"}
        )


def test_metadata_is_defensively_frozen() -> None:
    source = {"evidence": "snapshot"}
    result = MarketRegimeFutureForecast(**{**_forecast().__dict__, "metadata": source})
    source["evidence"] = "mutated"
    assert result.metadata["evidence"] == "snapshot"
    with pytest.raises(TypeError):
        result.metadata["evidence"] = "blocked"  # type: ignore[index]


def test_identity_and_mr_f7_calibration_guards() -> None:
    with pytest.raises(ValueError, match="required_identity_missing"):
        MarketRegimeFutureForecast(**{**_forecast().__dict__, "target_definition_version": ""})
    with pytest.raises(ValueError, match="calibrated_probability_claim_requires_reliability"):
        MarketRegimeFutureForecast(
            **{
                **_forecast().__dict__,
                "calibrated_probability_claim": True,
                "calibration_state": "CALIBRATED",
                "calibration_sample_count": 100,
                "calibration_maturity": "MATURE",
                "calibration_estimator_version": "estimator.v1",
            }
        )
    with pytest.raises(ValueError, match="calibration_estimator_version_required"):
        MarketRegimeFutureForecast(
            **{
                **_forecast().__dict__,
                "calibrated_reliability": 0.8,
                "calibration_state": "PROVISIONAL",
                "calibration_maturity": "PROVISIONAL",
            }
        )


def test_complete_set_requires_each_future_horizon_exactly_once() -> None:
    forecasts = tuple(_forecast(horizon) for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC)
    validate_future_forecast_set(forecasts)
    with pytest.raises(ValueError, match="future_horizon_coverage_mismatch"):
        validate_future_forecast_set(forecasts[:-1])
    with pytest.raises(ValueError, match="duplicate_future_horizon"):
        validate_future_forecast_set(forecasts + (forecasts[-1],))


def test_serialization_keeps_raw_score_distinct_from_calibration() -> None:
    payload = _forecast().to_dict()
    assert payload["raw_model_score_or_probability"] == 0.61
    assert payload["calibrated_reliability"] is None
    assert payload["calibration_display_confidence"] is None
    assert payload["calibrated_probability_claim"] is False


def test_display_confidence_is_distinct_and_cannot_exceed_reliability() -> None:
    valid = MarketRegimeFutureForecast(
        **{
            **_forecast().__dict__,
            "calibrated_reliability": 0.8,
            "calibration_display_confidence": 0.65,
            "calibration_state": "CAPPED",
            "calibration_sample_count": 120,
            "calibration_maturity": "MATURE",
            "calibration_cap_reasons": ("freshness_cap",),
            "calibration_estimator_version": "estimator.v1",
        }
    )
    assert valid.calibrated_reliability == 0.8
    assert valid.calibration_display_confidence == 0.65
    with pytest.raises(ValueError, match="calibration_display_confidence_exceeds_reliability"):
        MarketRegimeFutureForecast(
            **{
                **valid.__dict__,
                "calibration_display_confidence": 0.9,
            }
        )


def test_calibration_state_combinations_fail_closed() -> None:
    with pytest.raises(ValueError, match="capped_state_requires_cap_reasons"):
        MarketRegimeFutureForecast(
            **{
                **_forecast().__dict__,
                "calibrated_reliability": 0.8,
                "calibration_display_confidence": 0.7,
                "calibration_state": "CAPPED",
                "calibration_sample_count": 120,
                "calibration_maturity": "MATURE",
                "calibration_estimator_version": "estimator.v1",
            }
        )
    with pytest.raises(ValueError, match="provisional_state_requires_non_mature_sample"):
        MarketRegimeFutureForecast(
            **{
                **_forecast().__dict__,
                "calibrated_reliability": 0.8,
                "calibration_display_confidence": 0.8,
                "calibration_state": "PROVISIONAL",
                "calibration_sample_count": 120,
                "calibration_maturity": "MATURE",
                "calibration_estimator_version": "estimator.v1",
            }
        )
    with pytest.raises(ValueError, match="uncalibrated_state_disallows_calibration_values"):
        MarketRegimeFutureForecast(
            **{
                **_forecast().__dict__,
                "calibrated_reliability": 0.8,
                "calibration_display_confidence": 0.8,
                "calibration_state": "UNCALIBRATED",
                "calibration_sample_count": 120,
                "calibration_maturity": "MATURE",
                "calibration_estimator_version": "estimator.v1",
            }
        )
