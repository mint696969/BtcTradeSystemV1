# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_feature_shadow_aggregation.py
# desc: MR-F6.12 tests for multi-slot candidate-by-baseline coverage and accuracy aggregation.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_origin_feature_shadow_aggregation import (
    build_origin_feature_shadow_aggregation,
)
from btcts.prediction.market_regime.future_origin_feature_shadow_evaluation import (
    OriginFeatureShadowEvaluationSlot,
    build_origin_feature_shadow_evaluation,
)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _rows(origin: datetime) -> tuple[dict[str, object], ...]:
    start = origin - timedelta(minutes=60)
    return tuple({
        "time_utc": _iso(start + timedelta(minutes=index)),
        "close": 100.0 + index,
    } for index in range(60))


def _evaluation(
    *,
    index: int,
    observed_state: MarketRegimeCode,
    observation_available: bool = True,
    evaluation_window_ref: str = "window-001",
    target_horizon_sec: int = 300,
):
    origin = datetime(2026, 7, 14, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=5 * index)
    slot = OriginFeatureShadowEvaluationSlot(
        slot_id=f"slot-{index:03d}",
        prediction_origin=_iso(origin),
        source_snapshot_ref=f"snapshot-{index:03d}",
        source_timestamp=_iso(origin - timedelta(minutes=1)),
        target_horizon_sec=target_horizon_sec,
        current_state=MarketRegimeCode.RANGE,
        previous_state=MarketRegimeCode.DOWN_TREND,
        recent_return=0.01,
        realized_volatility_bps=8.0,
        current_forecast_label_selection=MarketRegimeCode.RANGE,
        candle_rows=_rows(origin),
        observed_state=observed_state,
        observation_available=observation_available,
        evaluation_window_ref=evaluation_window_ref,
        target_definition_version=f"market_regime_target.{target_horizon_sec}s.v1",
        outcome_resolver_version="resolver.v1",
    )
    return build_origin_feature_shadow_evaluation(slot=slot)


def test_aggregates_eight_candidates_by_six_baselines_across_slots() -> None:
    result = build_origin_feature_shadow_aggregation(evaluations=(
        _evaluation(index=0, observed_state=MarketRegimeCode.RANGE),
        _evaluation(index=1, observed_state=MarketRegimeCode.UP_TREND),
    ))
    assert result["evaluation_slot_count"] == 2
    assert result["candidate_count"] == 8
    assert result["baseline_count"] == 6
    assert result["candidate_baseline_pair_count"] == 48
    assert len(result["pair_summaries"]) == 48
    assert all(item["slot_count"] == 2 for item in result["pair_summaries"])


def test_pair_metrics_report_coverage_accuracy_and_unknown_rate() -> None:
    result = build_origin_feature_shadow_aggregation(evaluations=(
        _evaluation(index=0, observed_state=MarketRegimeCode.RANGE),
        _evaluation(index=1, observed_state=MarketRegimeCode.UP_TREND),
        _evaluation(index=2, observed_state=MarketRegimeCode.UNKNOWN, observation_available=False),
    ))
    summary = next(item for item in result["pair_summaries"] if item["baseline_id"] == "always_range")
    assert summary["slot_count"] == 3
    assert summary["observed_slot_count"] == 2
    assert summary["scored_slot_count"] == 2
    assert summary["hit_count"] == 1
    assert summary["coverage_rate"] == 1.0
    assert summary["accuracy"] == 0.5
    assert summary["unknown_rate"] == 0.0


def test_mixed_window_or_horizon_contract_fails_closed() -> None:
    with pytest.raises(ValueError, match="mixed_comparison_contract"):
        build_origin_feature_shadow_aggregation(evaluations=(
            _evaluation(index=0, observed_state=MarketRegimeCode.RANGE),
            _evaluation(index=1, observed_state=MarketRegimeCode.RANGE, evaluation_window_ref="window-002"),
        ))
    with pytest.raises(ValueError, match="mixed_comparison_contract"):
        build_origin_feature_shadow_aggregation(evaluations=(
            _evaluation(index=0, observed_state=MarketRegimeCode.RANGE),
            _evaluation(index=1, observed_state=MarketRegimeCode.RANGE, target_horizon_sec=900),
        ))


def test_duplicate_slot_and_duplicate_comparison_key_fail_closed() -> None:
    evaluation = _evaluation(index=0, observed_state=MarketRegimeCode.RANGE)
    with pytest.raises(ValueError, match="duplicate_slot_id"):
        build_origin_feature_shadow_aggregation(evaluations=(evaluation, evaluation))

    duplicate_key = dict(_evaluation(index=1, observed_state=MarketRegimeCode.RANGE))
    duplicate_key["slot_id"] = "different-slot"
    duplicate_key["comparison_key"] = evaluation["comparison_key"]
    duplicate_key["candidate_projections"] = tuple(
        dict(item, comparison_key=evaluation["comparison_key"])
        for item in duplicate_key["candidate_projections"]
    )
    with pytest.raises(ValueError, match="duplicate_comparison_key"):
        build_origin_feature_shadow_aggregation(evaluations=(evaluation, duplicate_key))


def test_candidate_or_baseline_matrix_tamper_fails_closed() -> None:
    evaluation = dict(_evaluation(index=0, observed_state=MarketRegimeCode.RANGE))
    projections = list(evaluation["candidate_projections"])
    bad_projection = dict(projections[0])
    bad_predictions = list(bad_projection["baseline_predictions"])
    bad_predictions[0] = dict(bad_predictions[0], baseline_id="wrong")
    bad_projection["baseline_predictions"] = tuple(bad_predictions)
    projections[0] = bad_projection
    evaluation["candidate_projections"] = tuple(projections)
    with pytest.raises(ValueError, match="baseline_order_or_identity_mismatch"):
        build_origin_feature_shadow_aggregation(evaluations=(evaluation,))


def test_observation_hit_and_shadow_flag_tamper_fail_closed() -> None:
    evaluation = dict(_evaluation(index=0, observed_state=MarketRegimeCode.RANGE))
    evaluation["observation_available"] = "false"
    with pytest.raises(ValueError, match="observation_availability_invalid"):
        build_origin_feature_shadow_aggregation(evaluations=(evaluation,))

    evaluation = dict(_evaluation(index=0, observed_state=MarketRegimeCode.RANGE))
    projections = list(evaluation["candidate_projections"])
    projection = dict(projections[0])
    predictions = list(projection["baseline_predictions"])
    predictions[0] = dict(predictions[0], hit=not predictions[0]["hit"])
    projection["baseline_predictions"] = tuple(predictions)
    projections[0] = projection
    evaluation["candidate_projections"] = tuple(projections)
    with pytest.raises(ValueError, match="hit_mismatch"):
        build_origin_feature_shadow_aggregation(evaluations=(evaluation,))

    evaluation = dict(_evaluation(index=0, observed_state=MarketRegimeCode.RANGE))
    projections = list(evaluation["candidate_projections"])
    projections[0] = dict(projections[0], selected_for_runtime=True)
    evaluation["candidate_projections"] = tuple(projections)
    with pytest.raises(ValueError, match="unsafe_projection_flag:selected_for_runtime"):
        build_origin_feature_shadow_aggregation(evaluations=(evaluation,))


def test_candidate_parameter_identity_tamper_fails_closed() -> None:
    evaluation = dict(_evaluation(index=0, observed_state=MarketRegimeCode.RANGE))
    projections = list(evaluation["candidate_projections"])
    projections[0] = dict(projections[0], parameter_set_id="wrong")
    evaluation["candidate_projections"] = tuple(projections)
    with pytest.raises(ValueError, match="parameter_set_identity_mismatch"):
        build_origin_feature_shadow_aggregation(evaluations=(evaluation,))

    evaluation = dict(_evaluation(index=0, observed_state=MarketRegimeCode.RANGE))
    projections = list(evaluation["candidate_projections"])
    projection = dict(projections[0])
    projection["calculated_features"] = dict(
        projection["calculated_features"],
        fast_ma_window_rows=999,
    )
    projections[0] = projection
    evaluation["candidate_projections"] = tuple(projections)
    with pytest.raises(ValueError, match="calculated_feature_contract_mismatch:fast_ma_window_rows"):
        build_origin_feature_shadow_aggregation(evaluations=(evaluation,))


def test_aggregation_never_ranks_selects_or_applies() -> None:
    result = build_origin_feature_shadow_aggregation(evaluations=(
        _evaluation(index=0, observed_state=MarketRegimeCode.RANGE),
        _evaluation(index=1, observed_state=MarketRegimeCode.UP_TREND),
    ))
    assert result["aggregation_ready"] is True
    assert result["ranking_performed"] is False
    assert result["selection_performed"] is False
    assert result["selected_candidate_id"] is None
    assert result["writes_dhot"] is False
    assert result["scheduler_enabled"] is False
    assert result["live_parameter_apply_allowed"] is False
    assert result["auto_promotion_allowed"] is False
    assert result["canonical_replacement_allowed"] is False
