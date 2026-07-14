# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_calibration_estimator.py
# desc: Focused MR-F7 hierarchical calibration, caps, and diagnostics guards.

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.calibration_dataset import (  # noqa: E402
    CalibrationSplitRole,
    MarketRegimeCalibrationBucketContext,
    MarketRegimeCalibrationDatasetSplit,
    MarketRegimeCalibrationMaturityPolicy,
    build_market_regime_calibration_observation,
)
from btcts.prediction.market_regime.calibration_estimator import (  # noqa: E402
    MarketRegimeConfidenceCapPolicy,
    MarketRegimeHierarchicalCalibrator,
    build_market_regime_calibration_diagnostics,
    evaluate_market_regime_calibrator_oos,
)


def _row(
    idx: int,
    *,
    label: str,
    freshness: str = "live",
    quality: str = "trusted",
    horizon_sec: int = 300,
    confidence_percent: float = 90,
):
    generated = f"2026-07-01T00:{idx:02d}:00Z"
    resolved = f"2026-07-01T00:{idx:02d}:30Z"
    bucket = MarketRegimeCalibrationBucketContext(
        horizon_key=f"{horizon_sec}s",
        predicted_regime="RANGE",
        model_id="model.v1",
        logic_version="logic.v1",
        parameter_set_id="params.v1",
        session_bucket="asia",
        volatility_bucket="normal",
        liquidity_bucket="normal",
        freshness_bucket=freshness,
        source_quality_bucket=quality,
        bucket_policy_version="bucket.v1",
    )
    return build_market_regime_calibration_observation(
        outcome_row={
            "schema_version": "market_regime_outcome.v1",
            "outcome_id": f"o-{idx}-{freshness}-{quality}-{horizon_sec}",
            "prediction_id": f"p-{idx}",
            "run_id": "run",
            "generated_at": generated,
            "resolved_at": resolved,
            "horizon_sec": horizon_sec,
            "predicted_regime_code": "RANGE",
            "observed_regime_code": "RANGE" if label == "hit" else "UP_TREND",
            "outcome_label": label,
            "confidence_percent": confidence_percent,
            "observation_source": "fixture",
            "observation_evaluator_version": "fixture.v1",
            "parameter_set_id": "params.v1",
        },
        bucket_context=bucket,
        contributions=(),
        model_id="model.v1",
        logic_version="logic.v1",
        target_definition_version="target.v1",
    )


def test_beta_binomial_shrinkage_avoids_extreme_small_sample_claim() -> None:
    calibrator = MarketRegimeHierarchicalCalibrator(
        prior_mean=0.5,
        prior_strength=20,
        maturity_policy=MarketRegimeCalibrationMaturityPolicy(provisional_min_samples=2, mature_min_samples=4),
    ).fit((_row(1, label="hit"),))
    estimate = calibrator.estimate(_row(2, label="hit"))
    assert estimate.calibrated_reliability == pytest.approx(11 / 21)
    assert estimate.calibrated_probability_claim is False
    assert "sparse_sample_cap" in estimate.cap_reasons


def test_hierarchical_fallback_uses_coarser_bucket() -> None:
    train = tuple(_row(i, label="hit" if i < 3 else "miss") for i in range(4))
    calibrator = MarketRegimeHierarchicalCalibrator(
        maturity_policy=MarketRegimeCalibrationMaturityPolicy(provisional_min_samples=2, mature_min_samples=4)
    ).fit(train)
    query = _row(10, label="hit", freshness="stale")
    estimate = calibrator.estimate(query)
    assert estimate.matched_level != "none"
    assert estimate.sample_count >= 4
    assert "freshness_cap" in estimate.cap_reasons
    assert estimate.display_confidence <= 0.60


def test_quality_long_horizon_and_provisional_caps_are_explained() -> None:
    train = tuple(_row(i, label="hit", quality="degraded", horizon_sec=14_400) for i in range(3))
    calibrator = MarketRegimeHierarchicalCalibrator(
        maturity_policy=MarketRegimeCalibrationMaturityPolicy(provisional_min_samples=2, mature_min_samples=10),
        cap_policy=MarketRegimeConfidenceCapPolicy(),
    ).fit(train)
    estimate = calibrator.estimate(_row(20, label="hit", quality="degraded", horizon_sec=14_400))
    assert set(estimate.cap_reasons) >= {"source_quality_cap", "long_horizon_cap", "provisional_sample_cap"}
    assert estimate.display_confidence <= 0.65
    assert estimate.calibrated_probability_claim is False


def test_empty_fit_returns_explicit_insufficient_sample() -> None:
    estimate = MarketRegimeHierarchicalCalibrator().fit(()).estimate(_row(1, label="hit"))
    assert estimate.calibrated_reliability is None
    assert estimate.display_confidence is None
    assert estimate.cap_reasons == ("insufficient_sample",)


def test_diagnostics_report_calibration_and_high_confidence_misses() -> None:
    rows = tuple(_row(i, label="hit" if i in {0, 1} else "miss") for i in range(4))
    calibrator = MarketRegimeHierarchicalCalibrator(
        prior_mean=0.8,
        prior_strength=100,
        maturity_policy=MarketRegimeCalibrationMaturityPolicy(provisional_min_samples=1, mature_min_samples=2),
    ).fit(rows)
    estimates = tuple(calibrator.estimate(row) for row in rows)
    diagnostics = build_market_regime_calibration_diagnostics(rows, estimates, high_confidence_threshold=0.75)
    assert diagnostics.sample_count == 4
    assert diagnostics.brier_score is not None
    assert diagnostics.log_loss is not None
    assert diagnostics.expected_calibration_error is not None
    assert diagnostics.high_confidence_miss_count >= 1
    assert diagnostics.overconfidence_gap is not None
    assert diagnostics.coverage is not None


def test_diagnostics_length_mismatch_fails_closed() -> None:
    with pytest.raises(ValueError, match="observation_estimate_length_mismatch"):
        build_market_regime_calibration_diagnostics((_row(1, label="hit"),), ())

def test_low_confidence_is_not_implicitly_abstention() -> None:
    row = _row(1, label="miss")
    calibrator = MarketRegimeHierarchicalCalibrator(
        prior_mean=0.2,
        prior_strength=100,
        maturity_policy=MarketRegimeCalibrationMaturityPolicy(provisional_min_samples=1, mature_min_samples=2),
    ).fit((row, _row(2, label="miss")))
    estimate = calibrator.estimate(row)
    assert estimate.display_confidence is not None
    assert estimate.display_confidence < 0.5
    diagnostics = build_market_regime_calibration_diagnostics(
        (row,),
        (estimate,),
        abstention_flags=(False,),
        evaluation_role=CalibrationSplitRole.TEST,
    )
    assert diagnostics.abstention_count == 0
    assert diagnostics.unscored_count == 0
    assert diagnostics.coverage == 1.0


def test_explicit_abstention_is_separate_from_unscored() -> None:
    row = _row(1, label="hit")
    estimate = MarketRegimeHierarchicalCalibrator().fit(()).estimate(row)
    diagnostics = build_market_regime_calibration_diagnostics(
        (row, row),
        (estimate, estimate),
        abstention_flags=(True, False),
        evaluation_role=CalibrationSplitRole.TEST,
    )
    assert diagnostics.abstention_count == 1
    assert diagnostics.unscored_count == 1
    assert diagnostics.sample_count == 0


def test_in_sample_diagnostics_fail_closed() -> None:
    row = _row(1, label="hit")
    estimate = MarketRegimeHierarchicalCalibrator().fit((row,)).estimate(row)
    with pytest.raises(ValueError, match="in_sample_diagnostics_not_allowed"):
        build_market_regime_calibration_diagnostics(
            (row,),
            (estimate,),
            evaluation_role=CalibrationSplitRole.TRAIN,
        )


def test_oos_helper_fits_train_and_scores_validation_only() -> None:
    train = tuple(_row(i, label="hit") for i in range(4))
    validation = (_row(10, label="miss"),)
    split = MarketRegimeCalibrationDatasetSplit(
        train=train,
        validation=validation,
        test=(),
        train_end_exclusive="2026-07-01T00:05:00Z",
        validation_end_exclusive="2026-07-01T00:20:00Z",
        maturity_policy=MarketRegimeCalibrationMaturityPolicy(provisional_min_samples=2, mature_min_samples=4),
    )
    estimates, diagnostics = evaluate_market_regime_calibrator_oos(
        split,
        role=CalibrationSplitRole.VALIDATION,
    )
    assert len(estimates) == 1
    assert diagnostics.sample_count == 1
    assert diagnostics.evaluation_role == "VALIDATION"
    with pytest.raises(ValueError, match="oos_role_must_be_validation_or_test"):
        evaluate_market_regime_calibrator_oos(split, role=CalibrationSplitRole.TRAIN)

def test_calibration_is_conditioned_on_raw_confidence_bucket() -> None:
    low_train = tuple(
        _row(i, label="miss", confidence_percent=55)
        for i in range(4)
    )
    high_train = tuple(
        _row(i + 10, label="hit", confidence_percent=90)
        for i in range(4)
    )
    calibrator = MarketRegimeHierarchicalCalibrator(
        prior_mean=0.5,
        prior_strength=2,
        maturity_policy=MarketRegimeCalibrationMaturityPolicy(
            provisional_min_samples=2,
            mature_min_samples=4,
        ),
    ).fit(low_train + high_train)

    low_estimate = calibrator.estimate(
        _row(30, label="miss", confidence_percent=55)
    )
    high_estimate = calibrator.estimate(
        _row(31, label="hit", confidence_percent=90)
    )

    assert low_estimate.matched_level.endswith("confidence")
    assert high_estimate.matched_level.endswith("confidence")
    assert low_estimate.calibrated_reliability is not None
    assert high_estimate.calibrated_reliability is not None
    assert low_estimate.calibrated_reliability < high_estimate.calibrated_reliability
