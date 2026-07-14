# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_feature_shadow_ranking.py
# desc: MR-F6.13 tests for explicit evidence sufficiency and tie-preserving deterministic shadow ranking.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_origin_feature_shadow_aggregation import build_origin_feature_shadow_aggregation
from btcts.prediction.market_regime.future_origin_feature_shadow_evaluation import OriginFeatureShadowEvaluationSlot, build_origin_feature_shadow_evaluation
from btcts.prediction.market_regime.future_origin_feature_shadow_ranking import (
    OriginFeatureShadowRankingPolicy,
    build_origin_feature_shadow_ranking,
)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _evaluation(index: int, observed_state: MarketRegimeCode):
    origin = datetime(2026, 7, 14, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=5 * index)
    start = origin - timedelta(minutes=60)
    rows = tuple({"time_utc": _iso(start + timedelta(minutes=row)), "close": 100.0 + row} for row in range(60))
    slot = OriginFeatureShadowEvaluationSlot(
        slot_id=f"slot-{index}", prediction_origin=_iso(origin), source_snapshot_ref=f"snapshot-{index}",
        source_timestamp=_iso(origin - timedelta(minutes=1)), target_horizon_sec=300,
        current_state=MarketRegimeCode.RANGE, previous_state=MarketRegimeCode.DOWN_TREND,
        recent_return=0.01, realized_volatility_bps=8.0,
        current_forecast_label_selection=MarketRegimeCode.RANGE, candle_rows=rows,
        observed_state=observed_state, observation_available=True,
        evaluation_window_ref="window-001", target_definition_version="market_regime_target.300s.v1",
        outcome_resolver_version="resolver.v1",
    )
    return build_origin_feature_shadow_evaluation(slot=slot)


def _aggregation(slot_count: int = 4):
    states = (MarketRegimeCode.RANGE, MarketRegimeCode.UP_TREND, MarketRegimeCode.DOWN_TREND, MarketRegimeCode.RANGE)
    return build_origin_feature_shadow_aggregation(evaluations=tuple(
        _evaluation(index, states[index % len(states)]) for index in range(slot_count)
    ))


def _policy(**overrides: object) -> OriginFeatureShadowRankingPolicy:
    values = dict(
        policy_id="fixture.explicit.v1",
        minimum_evaluation_slots=4,
        minimum_observed_slots_per_baseline=4,
        minimum_scored_slots_per_baseline=4,
        minimum_coverage_rate=1.0,
    )
    values.update(overrides)
    return OriginFeatureShadowRankingPolicy(**values)


def test_explicit_policy_is_required_and_sensitive_baselines_only() -> None:
    result = build_origin_feature_shadow_ranking(aggregation=_aggregation(), policy=_policy())
    assert result["ranking_scope"] == ("simple_ma_slope", "simple_volatility_threshold")
    assert result["ranking_policy"]["policy_id"] == "fixture.explicit.v1"
    assert all(len(item["sensitive_baseline_summaries"]) == 2 for item in result["candidate_projections"])


def test_sufficient_candidates_are_ranked_without_declaring_winner() -> None:
    result = build_origin_feature_shadow_ranking(aggregation=_aggregation(), policy=_policy())
    assert result["comparison_ready"] is True
    assert result["evidence_sufficient_candidate_count"] == 8
    assert result["ranking_performed"] is True
    assert result["winner_declared"] is False
    assert result["selection_performed"] is False
    assert result["selected_candidate_id"] is None
    assert result["promotion_candidates"] == ()


def test_metric_ties_remain_grouped_and_candidate_id_is_only_display_order() -> None:
    result = build_origin_feature_shadow_ranking(aggregation=_aggregation(), policy=_policy())
    assert any(group["tie"] is True for group in result["ranked_metric_groups"])
    for group in result["ranked_metric_groups"]:
        assert group["candidate_ids"] == tuple(sorted(group["candidate_ids"]))
        assert group["selection_allowed"] is False


def test_insufficient_evidence_blocks_ranking() -> None:
    result = build_origin_feature_shadow_ranking(
        aggregation=_aggregation(slot_count=3),
        policy=_policy(),
    )
    assert result["comparison_ready"] is False
    assert result["ranking_performed"] is False
    assert result["evidence_sufficient_candidate_count"] == 0
    assert result["comparison_blockers"] == ("no_candidate_meets_evidence_sufficiency",)
    assert all("minimum_evaluation_slots_not_met" in item["evidence_blockers"] for item in result["candidate_projections"])


def test_policy_rejects_implicit_or_diluted_baseline_scope() -> None:
    with pytest.raises(ValueError, match="baseline_scope_invalid"):
        _policy(required_baseline_ids=("always_range", "simple_ma_slope"))
    with pytest.raises(ValueError, match="coverage_invalid"):
        _policy(minimum_coverage_rate=1.1)
    with pytest.raises(ValueError, match="scored_exceeds_observed"):
        _policy(minimum_observed_slots_per_baseline=3, minimum_scored_slots_per_baseline=4)


def test_tampered_summary_arithmetic_or_registry_fails_closed() -> None:
    aggregation = dict(_aggregation())
    rows = list(aggregation["pair_summaries"])
    rows[0] = dict(rows[0], accuracy=1.0)
    aggregation["pair_summaries"] = tuple(rows)
    with pytest.raises(ValueError, match="metric_mismatch:accuracy"):
        build_origin_feature_shadow_ranking(aggregation=aggregation, policy=_policy())

    aggregation = dict(_aggregation())
    rows = list(aggregation["pair_summaries"])
    rows[0] = dict(rows[0], unknown_count=999)
    aggregation["pair_summaries"] = tuple(rows)
    with pytest.raises(ValueError, match="unknown_count_mismatch"):
        build_origin_feature_shadow_ranking(aggregation=aggregation, policy=_policy())

    aggregation = dict(_aggregation())
    candidate_ids = list(aggregation["candidate_ids"])
    candidate_ids[0] = "unknown"
    aggregation["candidate_ids"] = tuple(candidate_ids)
    with pytest.raises(ValueError, match="candidate_registry_not_canonical"):
        build_origin_feature_shadow_ranking(aggregation=aggregation, policy=_policy())


def test_unsafe_or_preselected_aggregation_fails_closed() -> None:
    aggregation = dict(_aggregation())
    aggregation["selection_performed"] = True
    with pytest.raises(ValueError, match="selected_input_not_allowed"):
        build_origin_feature_shadow_ranking(aggregation=aggregation, policy=_policy())
    aggregation = dict(_aggregation())
    aggregation["live_parameter_apply_allowed"] = True
    with pytest.raises(ValueError, match="unsafe_input_flag:live_parameter_apply_allowed"):
        build_origin_feature_shadow_ranking(aggregation=aggregation, policy=_policy())
