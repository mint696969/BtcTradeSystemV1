# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_mandatory_baseline_runner.py
# desc: MR-F6.3 tests for same-slot candidate and mandatory baseline comparison projection.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_runner import (
    MandatoryBaselineEvaluationSlot,
    build_rows_for_mandatory_baseline_slot,
    run_mandatory_baseline_comparison,
)

CANDIDATE = "market_regime.future.transparent_baseline.shadow.v1"


def _slot(**overrides: object) -> MandatoryBaselineEvaluationSlot:
    values = dict(
        slot_id="slot-1",
        candidate_trace_id="candidate-trace-1",
        candidate_model_id=CANDIDATE,
        prediction_origin="2026-07-14T00:00:00Z",
        prediction_origin_epoch_sec=1000.0,
        evaluation_window_ref="window:accepted-mr-f5",
        source_snapshot_ref="snapshot:1",
        source_timestamp_epoch_sec=999.0,
        target_horizon_sec=300,
        target_definition_version="market_regime_target.300s.v1",
        outcome_resolver_version="prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
        candidate_predicted_state=MarketRegimeCode.RANGE,
        candidate_probability_by_state={MarketRegimeCode.RANGE: 0.8, MarketRegimeCode.UP_TREND: 0.2},
        candidate_prediction_available=True,
        observed_state=MarketRegimeCode.RANGE,
        observation_available=True,
        current_state=MarketRegimeCode.RANGE,
        previous_state=MarketRegimeCode.DOWN_TREND,
        recent_return=0.01,
        fast_ma=101.0,
        slow_ma=100.0,
        realized_volatility=0.02,
        low_volatility_threshold=0.01,
        high_volatility_threshold=0.03,
        current_forecast_label_selection=MarketRegimeCode.BREAKOUT,
    )
    values.update(overrides)
    return MandatoryBaselineEvaluationSlot(**values)


def test_one_slot_generates_candidate_plus_six_baseline_rows() -> None:
    rows = build_rows_for_mandatory_baseline_slot(_slot())
    assert len(rows) == 7
    assert rows[0].candidate_id == CANDIDATE
    assert {row.candidate_id for row in rows[1:]} == {
        "always_range",
        "last_state_persists",
        "recent_return_sign",
        "simple_ma_slope",
        "simple_volatility_threshold",
        "current_forecast_label_selection",
    }
    assert len({row.comparison_key for row in rows}) == 1


def test_multiple_slots_run_as_comparison_ready_same_window() -> None:
    result = run_mandatory_baseline_comparison(
        slots=(
            _slot(),
            _slot(
                slot_id="slot-2",
                candidate_trace_id="candidate-trace-2",
                prediction_origin="2026-07-14T00:05:00Z",
                prediction_origin_epoch_sec=1300.0,
                source_snapshot_ref="snapshot:2",
                source_timestamp_epoch_sec=1299.0,
                observed_state=MarketRegimeCode.DOWN_TREND,
            ),
        ),
        candidate_model_id=CANDIDATE,
    )
    assert result["comparison_ready"] is True
    assert result["input_slot_count"] == 2
    assert result["generated_row_count"] == 14
    assert result["rows_per_slot"] == 7
    assert result["comparison_slot_count"] == 2


def test_missing_optional_evidence_keeps_same_slot_with_baseline_abstain() -> None:
    rows = build_rows_for_mandatory_baseline_slot(_slot(recent_return=None))
    target = next(row for row in rows if row.candidate_id == "recent_return_sign")
    assert target.prediction_available is False
    assert target.predicted_state is MarketRegimeCode.UNKNOWN
    result = run_mandatory_baseline_comparison(slots=(_slot(recent_return=None),), candidate_model_id=CANDIDATE)
    assert result["comparison_ready"] is True
    summary = next(item for item in result["candidate_summaries"] if item["candidate_id"] == "recent_return_sign")
    assert summary["coverage_rate"] == 0.0
    assert summary["unknown_rate"] == 1.0


def test_candidate_contract_is_validated_by_shared_comparison_row() -> None:
    with pytest.raises(ValueError, match="probability_sum_invalid"):
        build_rows_for_mandatory_baseline_slot(_slot(candidate_probability_by_state={MarketRegimeCode.RANGE: 0.8}))


def test_slot_rejects_lookahead_and_target_mismatch() -> None:
    with pytest.raises(ValueError, match="lookahead_detected"):
        _slot(source_timestamp_epoch_sec=1001.0)
    with pytest.raises(ValueError, match="target_definition_mismatch"):
        _slot(target_definition_version="market_regime_target.900s.v1")


def test_runner_rejects_duplicate_slot_and_candidate_mismatch() -> None:
    with pytest.raises(ValueError, match="duplicate_slot_id"):
        run_mandatory_baseline_comparison(slots=(_slot(), _slot(candidate_trace_id="other")), candidate_model_id=CANDIDATE)
    with pytest.raises(ValueError, match="candidate_model_mismatch"):
        run_mandatory_baseline_comparison(slots=(_slot(),), candidate_model_id="other-model")


def test_runner_result_is_immutable() -> None:
    result = run_mandatory_baseline_comparison(slots=(_slot(),), candidate_model_id=CANDIDATE)
    with pytest.raises(TypeError):
        result["comparison_ready"] = False
