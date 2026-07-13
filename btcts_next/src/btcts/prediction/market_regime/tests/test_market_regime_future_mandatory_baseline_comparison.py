# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_mandatory_baseline_comparison.py
# desc: MR-F6.1 tests for same-window mandatory simple-baseline comparison contract and metrics.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_comparison import (
    MANDATORY_BASELINE_IDS,
    MandatoryBaselineComparisonRow,
    build_mandatory_baseline_comparison,
)

CANDIDATE = "market_regime.future.transparent_baseline.shadow.v1"


def _row(*, trace: str, candidate: str, origin: str = "2026-07-14T00:00:00Z", predicted: MarketRegimeCode = MarketRegimeCode.RANGE, observed: MarketRegimeCode = MarketRegimeCode.RANGE, probability: float = 0.8, prediction_available: bool = True, observation_available: bool = True, avoidable_unknown: bool = False) -> MandatoryBaselineComparisonRow:
    probabilities = {} if not prediction_available else {
        predicted: probability,
        MarketRegimeCode.UP_TREND if predicted is not MarketRegimeCode.UP_TREND else MarketRegimeCode.RANGE: 1.0 - probability,
    }
    return MandatoryBaselineComparisonRow(
        trace_id=trace,
        candidate_id=candidate,
        prediction_origin=origin,
        evaluation_window_ref="window:mr_f6:test",
        source_snapshot_ref=f"snapshot:{origin}",
        target_horizon_sec=300,
        target_definition_version="market_regime_target.300s.v1",
        outcome_resolver_version="prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
        predicted_state=predicted if prediction_available else MarketRegimeCode.UNKNOWN,
        observed_state=observed if observation_available else MarketRegimeCode.UNKNOWN,
        probability_by_state=probabilities,
        observation_available=observation_available,
        prediction_available=prediction_available,
        avoidable_unknown=avoidable_unknown,
    )


def _complete_rows() -> list[MandatoryBaselineComparisonRow]:
    ids = (CANDIDATE,) + MANDATORY_BASELINE_IDS
    rows = []
    for index, candidate_id in enumerate(ids):
        rows.append(_row(trace=f"{index}:a", candidate=candidate_id))
        rows.append(_row(trace=f"{index}:b", candidate=candidate_id, origin="2026-07-14T00:05:00Z", predicted=MarketRegimeCode.UP_TREND, observed=MarketRegimeCode.RANGE, probability=0.7))
    return rows


def test_all_mandatory_baselines_same_window_are_comparison_ready() -> None:
    result = build_mandatory_baseline_comparison(rows=_complete_rows(), candidate_model_id=CANDIDATE)
    assert result["comparison_ready"] is True
    assert result["comparison_blockers"] == ()
    assert result["comparison_slot_count"] == 2
    assert len(result["candidate_summaries"]) == 7
    assert result["safety"]["writes_dhot"] is False
    assert result["safety"]["canonical_replacement"] is False


def test_metrics_include_required_quality_coverage_and_sequence_fields() -> None:
    rows = _complete_rows()
    result = build_mandatory_baseline_comparison(rows=rows, candidate_model_id=CANDIDATE)
    summary = result["candidate_summaries"][0]
    assert summary["accuracy"] == 0.5
    assert summary["coverage_rate"] == 1.0
    assert summary["unknown_rate"] == 0.0
    assert summary["brier_score"] is not None
    assert summary["log_loss"] is not None
    assert summary["expected_calibration_error"] is not None
    assert summary["state_churn_rate"] == 1.0
    assert "transition_detection_delay_sec" in summary
    assert "regime_duration_consistency" in summary


def test_missing_baseline_blocks_comparison() -> None:
    rows = [row for row in _complete_rows() if row.candidate_id != "simple_ma_slope"]
    result = build_mandatory_baseline_comparison(rows=rows, candidate_model_id=CANDIDATE)
    assert result["comparison_ready"] is False
    assert "mandatory_baseline_missing" in result["comparison_blockers"]
    assert result["missing_candidate_ids"] == ("simple_ma_slope",)


def test_same_window_mismatch_blocks_comparison() -> None:
    rows = _complete_rows()
    target = next(row for row in rows if row.candidate_id == "always_range" and row.prediction_origin.endswith("05:00Z"))
    rows.remove(target)
    result = build_mandatory_baseline_comparison(rows=rows, candidate_model_id=CANDIDATE)
    assert result["comparison_ready"] is False
    assert "same_window_contract_mismatch" in result["comparison_blockers"]
    assert "always_range" in result["window_mismatch_candidate_ids"]


def test_unknown_and_avoidable_unknown_rates_are_separate() -> None:
    rows = _complete_rows()
    target = next(row for row in rows if row.candidate_id == "always_range" and row.prediction_origin.endswith("05:00Z"))
    rows[rows.index(target)] = _row(trace=target.trace_id, candidate=target.candidate_id, origin=target.prediction_origin, prediction_available=False, avoidable_unknown=True)
    result = build_mandatory_baseline_comparison(rows=rows, candidate_model_id=CANDIDATE)
    summary = next(item for item in result["candidate_summaries"] if item["candidate_id"] == "always_range")
    assert summary["coverage_rate"] == 0.5
    assert summary["unknown_rate"] == 0.5
    assert summary["avoidable_unknown_rate"] == 0.5


def test_contract_fails_closed_on_probability_and_target_errors() -> None:
    with pytest.raises(ValueError, match="probability_sum_invalid"):
        _row(trace="bad-prob", candidate=CANDIDATE, probability=0.7). __class__(
            trace_id="bad-prob",
            candidate_id=CANDIDATE,
            prediction_origin="2026-07-14T00:00:00Z",
            evaluation_window_ref="window",
            source_snapshot_ref="snapshot",
            target_horizon_sec=300,
            target_definition_version="market_regime_target.300s.v1",
            outcome_resolver_version="resolver",
            predicted_state=MarketRegimeCode.RANGE,
            observed_state=MarketRegimeCode.RANGE,
            probability_by_state={MarketRegimeCode.RANGE: 0.7},
            observation_available=True,
            prediction_available=True,
        )
    with pytest.raises(ValueError, match="target_definition_mismatch"):
        MandatoryBaselineComparisonRow(
            trace_id="bad-target",
            candidate_id=CANDIDATE,
            prediction_origin="2026-07-14T00:00:00Z",
            evaluation_window_ref="window",
            source_snapshot_ref="snapshot",
            target_horizon_sec=300,
            target_definition_version="market_regime_target.900s.v1",
            outcome_resolver_version="resolver",
            predicted_state=MarketRegimeCode.RANGE,
            observed_state=MarketRegimeCode.RANGE,
            probability_by_state={MarketRegimeCode.RANGE: 1.0},
            observation_available=True,
            prediction_available=True,
        )


def test_contract_rejects_unknown_probability_non_argmax_and_negative_delay() -> None:
    common = dict(
        trace_id="strict-contract",
        candidate_id=CANDIDATE,
        prediction_origin="2026-07-14T00:00:00Z",
        evaluation_window_ref="window",
        source_snapshot_ref="snapshot",
        target_horizon_sec=300,
        target_definition_version="market_regime_target.300s.v1",
        outcome_resolver_version="resolver",
        predicted_state=MarketRegimeCode.RANGE,
        observed_state=MarketRegimeCode.RANGE,
        observation_available=True,
        prediction_available=True,
    )
    with pytest.raises(ValueError, match="unknown_probability_not_allowed"):
        MandatoryBaselineComparisonRow(
            **common,
            probability_by_state={MarketRegimeCode.RANGE: 0.8, MarketRegimeCode.UNKNOWN: 0.2},
        )
    with pytest.raises(ValueError, match="predicted_state_not_argmax"):
        MandatoryBaselineComparisonRow(
            **common,
            probability_by_state={MarketRegimeCode.RANGE: 0.4, MarketRegimeCode.UP_TREND: 0.6},
        )
    with pytest.raises(ValueError, match="transition_detection_precedes_observation"):
        MandatoryBaselineComparisonRow(
            **common,
            probability_by_state={MarketRegimeCode.RANGE: 1.0},
            observed_transition_at_epoch_sec=100.0,
            detected_transition_at_epoch_sec=99.0,
        )


def test_result_is_immutable_at_public_boundaries() -> None:
    result = build_mandatory_baseline_comparison(rows=_complete_rows(), candidate_model_id=CANDIDATE)
    with pytest.raises(TypeError):
        result["comparison_ready"] = False
    with pytest.raises(TypeError):
        result["candidate_summaries"][0]["accuracy"] = 0.0
    with pytest.raises(TypeError):
        result["safety"]["writes_dhot"] = True
