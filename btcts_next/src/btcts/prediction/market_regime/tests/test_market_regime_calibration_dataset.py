# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_calibration_dataset.py
# desc: Focused MR-F7 calibration dataset/source-flag ledger/OOS split guards. Pure and read-only.

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.calibration_dataset import (  # noqa: E402
    CalibrationSampleMaturity,
    CalibrationSplitRole,
    MarketRegimeCalibrationBucketContext,
    MarketRegimeCalibrationDatasetSplit,
    MarketRegimeCalibrationMaturityPolicy,
    MarketRegimeEvidenceContribution,
    build_market_regime_calibration_observation,
    split_market_regime_calibration_observations,
)


def _outcome(
    *,
    outcome_id: str = "o1",
    generated_at: str = "2026-07-01T00:00:00Z",
    resolved_at: str | None = None,
    label: str = "hit",
) -> dict:
    resolved = resolved_at or generated_at.replace("00:00:00Z", "00:05:00Z")
    return {
        "schema_version": "market_regime_outcome.v1",
        "outcome_id": outcome_id,
        "prediction_id": f"p-{outcome_id}",
        "run_id": "run-1",
        "generated_at": generated_at,
        "resolved_at": resolved,
        "horizon_sec": 300,
        "predicted_regime_code": "RANGE",
        "observed_regime_code": "RANGE" if label == "hit" else "UP_TREND",
        "outcome_label": label,
        "confidence_percent": 65,
        "observation_source": "candle_summary",
        "observation_evaluator_version": "fixture.v1",
        "parameter_set_id": "market_regime.fixture.v1",
        "trace_part_jsonl": "prediction/market_regime/trace/part.jsonl",
    }


def _bucket() -> MarketRegimeCalibrationBucketContext:
    return MarketRegimeCalibrationBucketContext(
        horizon_key="300s",
        predicted_regime="RANGE",
        model_id="market_regime.fixture_model.v1",
        logic_version="market_regime.fixture_logic.v1",
        parameter_set_id="market_regime.fixture.v1",
        session_bucket="asia",
        volatility_bucket="normal",
        liquidity_bucket="normal",
        freshness_bucket="live",
        source_quality_bucket="trusted",
        bucket_policy_version="market_regime.fixture_bucket.v1",
    )


def _contribution(*, flag_id: str = "depth_imbalance") -> MarketRegimeEvidenceContribution:
    return MarketRegimeEvidenceContribution(
        source_id="market_regime.liquidity",
        flag_id=flag_id,
        observed_state="positive",
        supports_regime="RANGE",
        parameter_id=f"market_regime.liquidity.{flag_id}",
        parameter_version="v1",
        base_reliability=0.7,
        signed_contribution=0.2,
        final_contribution=0.18,
        source_refs=("L2/book",),
    )


def _observation(
    *,
    outcome_id: str = "o1",
    generated_at: str = "2026-07-01T00:00:00Z",
    resolved_at: str | None = None,
    label: str = "hit",
):
    return build_market_regime_calibration_observation(
        outcome_row=_outcome(
            outcome_id=outcome_id,
            generated_at=generated_at,
            resolved_at=resolved_at,
            label=label,
        ),
        bucket_context=_bucket(),
        contributions=(_contribution(), _contribution(flag_id="spread_bps")),
        model_id="market_regime.fixture_model.v1",
        logic_version="market_regime.fixture_logic.v1",
        target_definition_version="market_regime_target.300s.v1",
    )


def test_builds_source_flag_contribution_ledger_and_strict_target() -> None:
    observation = _observation()
    payload = observation.to_dict()
    assert observation.strict_target == 1.0
    assert observation.graded_target == 1.0
    assert observation.evaluable is True
    assert len(payload["contributions"]) == 2
    assert payload["contributions"][0]["source_id"] == "market_regime.liquidity"
    assert payload["contributions"][0]["flag_id"] == "depth_imbalance"
    assert payload["raw_confidence"] == pytest.approx(0.65)
    assert payload["safety_read_only"] is True


def test_partial_is_strict_miss_but_graded_half_credit() -> None:
    observation = _observation(label="partial")
    assert observation.evaluable is True
    assert observation.strict_target == 0.0
    assert observation.graded_target == 0.5


def test_unknown_is_not_silently_counted_as_miss() -> None:
    observation = _observation(label="unknown")
    assert observation.evaluable is False
    assert observation.strict_target is None
    assert observation.graded_target is None


def test_duplicate_flag_parameter_contribution_fails_closed() -> None:
    duplicate = _contribution()
    with pytest.raises(ValueError, match="duplicate_contribution_key"):
        build_market_regime_calibration_observation(
            outcome_row=_outcome(),
            bucket_context=_bucket(),
            contributions=(duplicate, duplicate),
            model_id="market_regime.fixture_model.v1",
            logic_version="market_regime.fixture_logic.v1",
            target_definition_version="market_regime_target.300s.v1",
        )


def test_bucket_identity_mismatch_fails_closed() -> None:
    wrong = MarketRegimeCalibrationBucketContext(
        **({**_bucket().__dict__, "horizon_key": "900s"})
    )
    with pytest.raises(ValueError, match="bucket_horizon_key_mismatch"):
        build_market_regime_calibration_observation(
            outcome_row=_outcome(),
            bucket_context=wrong,
            contributions=(_contribution(),),
            model_id="market_regime.fixture_model.v1",
            logic_version="market_regime.fixture_logic.v1",
            target_definition_version="market_regime_target.300s.v1",
        )


def test_time_ordered_split_and_maturity_are_deterministic() -> None:
    observations = (
        _observation(outcome_id="test", generated_at="2026-07-03T00:00:00Z"),
        _observation(outcome_id="train", generated_at="2026-07-01T00:00:00Z"),
        _observation(outcome_id="validation", generated_at="2026-07-02T00:00:00Z"),
    )
    split = split_market_regime_calibration_observations(
        observations,
        train_end_exclusive="2026-07-02T00:00:00Z",
        validation_end_exclusive="2026-07-03T00:00:00Z",
        maturity_policy=MarketRegimeCalibrationMaturityPolicy(provisional_min_samples=2, mature_min_samples=3),
    )
    assert [row.outcome_id for row in split.train] == ["train"]
    assert [row.outcome_id for row in split.validation] == ["validation"]
    assert [row.outcome_id for row in split.test] == ["test"]
    assert split.maturity(CalibrationSplitRole.TRAIN) is CalibrationSampleMaturity.SPARSE
    assert split.to_dict()["random_split_allowed"] is False
    assert split.to_dict()["future_leakage_allowed"] is False


def test_duplicate_observation_and_non_monotonic_boundaries_fail_closed() -> None:
    row = _observation()
    with pytest.raises(ValueError, match="duplicate_observation_key"):
        split_market_regime_calibration_observations(
            (row, row),
            train_end_exclusive="2026-07-02T00:00:00Z",
            validation_end_exclusive="2026-07-03T00:00:00Z",
        )
    with pytest.raises(ValueError, match="split_boundaries_not_monotonic"):
        split_market_regime_calibration_observations(
            (row,),
            train_end_exclusive="2026-07-03T00:00:00Z",
            validation_end_exclusive="2026-07-02T00:00:00Z",
        )

def test_split_rejects_outcome_unavailable_at_train_boundary() -> None:
    leaking = _observation(
        outcome_id="leaking-train",
        generated_at="2026-07-01T23:59:00Z",
        resolved_at="2026-07-02T00:04:00Z",
    )
    with pytest.raises(ValueError, match="train_outcome_not_available_at_boundary"):
        split_market_regime_calibration_observations(
            (leaking,),
            train_end_exclusive="2026-07-02T00:00:00Z",
            validation_end_exclusive="2026-07-03T00:00:00Z",
        )


def test_split_rejects_outcome_unavailable_at_validation_boundary() -> None:
    leaking = _observation(
        outcome_id="leaking-validation",
        generated_at="2026-07-02T23:59:00Z",
        resolved_at="2026-07-03T00:04:00Z",
    )
    with pytest.raises(ValueError, match="validation_outcome_not_available_at_boundary"):
        split_market_regime_calibration_observations(
            (leaking,),
            train_end_exclusive="2026-07-02T00:00:00Z",
            validation_end_exclusive="2026-07-03T00:00:00Z",
        )

def test_split_dataclass_itself_enforces_resolution_boundaries() -> None:
    leaking = _observation(
        outcome_id="direct-leak",
        generated_at="2026-07-01T23:59:00Z",
        resolved_at="2026-07-02T00:04:00Z",
    )
    with pytest.raises(ValueError, match="train_outcome_not_available_at_boundary"):
        MarketRegimeCalibrationDatasetSplit(
            train=(leaking,),
            validation=(),
            test=(),
            train_end_exclusive="2026-07-02T00:00:00Z",
            validation_end_exclusive="2026-07-03T00:00:00Z",
        )
