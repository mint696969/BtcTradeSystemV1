# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_feature_shadow_evaluation.py
# desc: MR-F6.11 tests for same-slot evaluation of all eight origin-feature shadow candidates.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_origin_feature_shadow_evaluation import (
    OriginFeatureShadowEvaluationSlot,
    build_origin_feature_shadow_evaluation,
)


def _rows() -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "time_utc": f"2026-07-13T23:{index:02d}:00Z",
            "close": 100.0 + index,
        }
        for index in range(60)
    )


def _slot(**overrides: object) -> OriginFeatureShadowEvaluationSlot:
    values = dict(
        slot_id="slot-001",
        prediction_origin="2026-07-14T00:00:00Z",
        source_snapshot_ref="snapshot-001",
        source_timestamp="2026-07-13T23:59:00Z",
        target_horizon_sec=300,
        current_state=MarketRegimeCode.RANGE,
        previous_state=MarketRegimeCode.DOWN_TREND,
        recent_return=0.01,
        realized_volatility_bps=8.0,
        current_forecast_label_selection=MarketRegimeCode.RANGE,
        candle_rows=_rows(),
        observed_state=MarketRegimeCode.UP_TREND,
        observation_available=True,
        evaluation_window_ref="window-001",
        target_definition_version="market_regime_target.300s.v1",
        outcome_resolver_version="resolver.v1",
    )
    values.update(overrides)
    return OriginFeatureShadowEvaluationSlot(**values)


def test_projects_all_eight_candidates_on_one_comparison_key() -> None:
    result = build_origin_feature_shadow_evaluation(slot=_slot())
    assert result["candidate_count"] == 8
    assert result["evaluation_ready"] is True
    assert {item["comparison_key"] for item in result["candidate_projections"]} == {result["comparison_key"]}
    assert all(len(item["baseline_predictions"]) == 6 for item in result["candidate_projections"])


def test_candidate_parameters_change_only_ma_and_volatility_baseline_inputs() -> None:
    result = build_origin_feature_shadow_evaluation(slot=_slot())
    projections = result["candidate_projections"]
    fast_ma_values = {item["calculated_features"]["fast_ma"] for item in projections}
    volatility_threshold_pairs = {
        (
            item["calculated_features"]["low_volatility_threshold_bps"],
            item["calculated_features"]["high_volatility_threshold_bps"],
        )
        for item in projections
    }
    assert len(fast_ma_values) == 4
    assert len(volatility_threshold_pairs) == 2
    common = {
        item["candidate_id"]: {
            row["baseline_id"]: row["predicted_state"]
            for row in item["baseline_predictions"]
            if row["baseline_id"] in {
                "always_range",
                "last_state_persists",
                "recent_return_sign",
                "current_forecast_label_selection",
            }
        }
        for item in projections
    }
    assert len({tuple(values.items()) for values in common.values()}) == 1


def test_hit_projection_uses_same_observed_state_without_selecting_candidate() -> None:
    result = build_origin_feature_shadow_evaluation(slot=_slot())
    assert result["observed_state"] is MarketRegimeCode.UP_TREND
    assert result["selection_performed"] is False
    assert result["selected_candidate_id"] is None
    assert all(
        row["hit"] is not None
        for item in result["candidate_projections"]
        for row in item["baseline_predictions"]
    )


def test_unavailable_observation_produces_no_hit_values() -> None:
    result = build_origin_feature_shadow_evaluation(slot=_slot(
        observed_state=MarketRegimeCode.UNKNOWN,
        observation_available=False,
    ))
    assert all(
        row["hit"] is None
        for item in result["candidate_projections"]
        for row in item["baseline_predictions"]
    )


def test_lookahead_and_target_mismatch_fail_closed() -> None:
    with pytest.raises(ValueError, match="lookahead_detected"):
        _slot(source_timestamp="2026-07-14T00:00:01Z")
    with pytest.raises(ValueError, match="target_definition_mismatch"):
        _slot(target_definition_version="market_regime_target.900s.v1")


def test_candle_time_contract_fails_closed() -> None:
    missing_time = list(_rows())
    missing_time[-1] = {"close": 159.0}
    with pytest.raises(ValueError, match="timestamp_invalid:candle_rows"):
        _slot(candle_rows=tuple(missing_time))

    with pytest.raises(ValueError, match="candle_lookahead_detected"):
        _slot(
            candle_rows=_rows(),
            source_timestamp="2026-07-13T23:58:00Z",
        )

    gap = list(_rows())
    gap[-1] = {"time_utc": "2026-07-14T00:00:00Z", "close": 159.0}
    with pytest.raises(ValueError, match="candle_gap_detected"):
        _slot(candle_rows=tuple(gap), source_timestamp="2026-07-14T00:00:00Z")

    with pytest.raises(ValueError, match="candle_rows_insufficient"):
        _slot(candle_rows=_rows()[:-1])


def test_projection_is_shadow_only_and_has_no_write_or_apply_surface() -> None:
    result = build_origin_feature_shadow_evaluation(slot=_slot())
    assert result["writes_dhot"] is False
    assert result["scheduler_enabled"] is False
    assert result["live_parameter_apply_allowed"] is False
    assert result["auto_promotion_allowed"] is False
    assert result["canonical_replacement_allowed"] is False
    assert all(item["selected_for_runtime"] is False for item in result["candidate_projections"])
