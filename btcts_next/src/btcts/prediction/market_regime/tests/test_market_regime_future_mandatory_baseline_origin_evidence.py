# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_mandatory_baseline_origin_evidence.py
# desc: MR-F6.5 tests for immutable prediction-origin evidence bundles and safety guards.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_origin_evidence import (
    MarketRegimeOriginEvidence,
    build_market_regime_origin_evidence_bundle,
)


def _evidence(**overrides: object) -> MarketRegimeOriginEvidence:
    values = dict(
        prediction_origin="2026-07-14T00:00:00Z",
        prediction_origin_epoch_sec=1000.0,
        source_timestamp="2026-07-13T23:59:59Z",
        source_timestamp_epoch_sec=999.0,
        target_horizon_sec=300,
        trace_id="trace:test",
        model_id="market_regime.future.transparent_baseline.shadow.v1",
        logic_version="prediction.market_regime.future_baseline_model.mr_f5_3.v1",
        parameter_set_id="market_regime.future.transparent_baseline.params.v1",
        target_definition_version="market_regime_target.300s.v1",
        feature_snapshot_ref="market_regime_feature_snapshot:test",
        current_state=MarketRegimeCode.RANGE,
        previous_state=MarketRegimeCode.DOWN_TREND,
        regime_scores={MarketRegimeCode.RANGE: 3.0, MarketRegimeCode.UP_TREND: 1.0},
        recent_return=0.01,
        fast_ma=101.0,
        slow_ma=100.0,
        realized_volatility=0.02,
        low_volatility_threshold=0.01,
        high_volatility_threshold=0.03,
        current_forecast_label_selection=MarketRegimeCode.BREAKOUT,
    )
    values.update(overrides)
    return MarketRegimeOriginEvidence(**values)


def test_builds_complete_origin_bundle_with_normalized_probabilities() -> None:
    bundle = build_market_regime_origin_evidence_bundle(_evidence())
    assert bundle["artifact_kind"] == "future_origin_evidence_bundle"
    assert bundle["candidate_probability_by_state"] == {"RANGE": 0.75, "UP_TREND": 0.25}
    assert sum(bundle["candidate_probability_by_state"].values()) == pytest.approx(1.0)
    assert bundle["feature_snapshot"]["recent_return"] == 0.01
    assert bundle["feature_snapshot"]["fast_ma"] == 101.0
    assert bundle["write_performed"] is False


def test_unknown_score_is_excluded_and_positive_scores_are_required() -> None:
    bundle = build_market_regime_origin_evidence_bundle(_evidence(regime_scores={MarketRegimeCode.UNKNOWN: 99.0, MarketRegimeCode.RANGE: 1.0}))
    assert bundle["candidate_probability_by_state"] == {"RANGE": 1.0}
    with pytest.raises(ValueError, match="positive_score_missing"):
        _evidence(regime_scores={MarketRegimeCode.RANGE: 0.0})


def test_lookahead_target_and_threshold_errors_fail_closed() -> None:
    with pytest.raises(ValueError, match="lookahead_detected"):
        _evidence(source_timestamp_epoch_sec=1001.0)
    with pytest.raises(ValueError, match="target_definition_mismatch"):
        _evidence(target_definition_version="market_regime_target.900s.v1")
    with pytest.raises(ValueError, match="threshold_order_invalid"):
        _evidence(low_volatility_threshold=0.04, high_volatility_threshold=0.03)


def test_bundle_identity_is_deterministic_and_changes_with_trace() -> None:
    first = build_market_regime_origin_evidence_bundle(_evidence())
    second = build_market_regime_origin_evidence_bundle(_evidence())
    third = build_market_regime_origin_evidence_bundle(_evidence(trace_id="trace:other"))
    assert first["bundle_id"] == second["bundle_id"]
    assert first["bundle_id"] != third["bundle_id"]


def test_bundle_public_mappings_are_immutable() -> None:
    bundle = build_market_regime_origin_evidence_bundle(_evidence())
    with pytest.raises(TypeError):
        bundle["write_performed"] = True
    with pytest.raises(TypeError):
        bundle["feature_snapshot"]["recent_return"] = 0.0
    with pytest.raises(TypeError):
        bundle["candidate_probability_by_state"]["RANGE"] = 0.5


def test_safety_flags_block_backfill_promotion_and_live_apply() -> None:
    bundle = build_market_regime_origin_evidence_bundle(_evidence())
    assert bundle["historical_backfill_allowed"] is False
    assert bundle["scheduler_registration_allowed"] is False
    assert bundle["canonical_replacement"] is False
    assert bundle["parameter_auto_promotion_allowed"] is False
    assert bundle["live_parameter_apply_allowed"] is False
