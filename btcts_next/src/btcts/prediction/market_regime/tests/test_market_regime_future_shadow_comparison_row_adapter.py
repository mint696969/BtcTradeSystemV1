# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_comparison_row_adapter.py
# desc: MR-F8.4 tests for strict paired forecast, origin evidence, and outcome joins.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_comparison_row_adapter import build_future_shadow_comparison_rows


def evidence() -> FutureBaselineEvidence:
    return FutureBaselineEvidence(
        origin_timestamp="2026-07-15T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=900,
        feature_snapshot_ref="snapshot:mr-f8.4",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.44, MarketRegimeCode.RANGE: 0.34, MarketRegimeCode.UP_TREND: 0.22},
        available_feature_families=("price_structure", "volatility", "liquidity", "source_quality", "microprice"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )


def bundle() -> dict:
    return {
        "prediction_origin": "2026-07-15T00:00:00Z",
        "feature_snapshot_ref": "snapshot:mr-f8.4",
        "target_horizon_sec": 900,
        "target_definition_version": "market_regime_target.900s.v1",
        "candidate_probability_by_state": {"BREAKOUT": 0.44, "RANGE": 0.34, "UP_TREND": 0.22},
        "feature_snapshot": {"source_timestamp": "2026-07-14T23:59:59Z"},
    }


def outcomes(pair: dict) -> tuple[dict, ...]:
    rows = []
    for forecast in pair["forecasts"]:
        rows.append({
            "trace_id": forecast["trace_id"],
            "origin_timestamp": forecast["origin_timestamp"],
            "target_horizon_sec": forecast["target_horizon_sec"],
            "target_definition_version": forecast["target_definition_version"],
            "model_id": forecast["model_id"],
            "logic_version": forecast["logic_version"],
            "parameter_set_id": forecast["parameter_set_id"],
            "feature_snapshot_ref": forecast["feature_snapshot_ref"],
            "outcome_status": "CORRECT",
            "observed_future_state": "BREAKOUT",
        })
    return tuple(rows)


def test_builds_same_slot_rows_for_both_candidates() -> None:
    pair = build_future_shadow_candidate_pair(evidence=evidence())
    rows = build_future_shadow_comparison_rows(
        pair=pair,
        origin_evidence_bundle=bundle(),
        outcome_rows=outcomes(pair),
        evaluation_window_ref="window:mr-f8.4",
    )
    assert len(rows) == 2
    assert len({row.comparison_key for row in rows}) == 1
    assert {row.candidate_id for row in rows} == {
        "market_regime.future.transparent_baseline.params.v1",
        "market_regime.future.transparent_baseline.params.conservative.v1",
    }
    assert all(row.observation_available for row in rows)


def test_abstained_candidate_preserves_probability_but_no_prediction() -> None:
    pair = build_future_shadow_candidate_pair(evidence=evidence())
    rows = build_future_shadow_comparison_rows(
        pair=pair,
        origin_evidence_bundle=bundle(),
        outcome_rows=outcomes(pair),
        evaluation_window_ref="window:mr-f8.4",
    )
    conservative = next(row for row in rows if row.candidate_id.endswith("conservative.v1"))
    assert conservative.prediction_available is False
    assert conservative.predicted_state is MarketRegimeCode.UNKNOWN
    assert sum(conservative.probability_by_state.values()) == pytest.approx(1.0)


def test_missing_outcome_becomes_unobserved_without_inference() -> None:
    pair = build_future_shadow_candidate_pair(evidence=evidence())
    rows = build_future_shadow_comparison_rows(
        pair=pair,
        origin_evidence_bundle=bundle(),
        outcome_rows=(),
        evaluation_window_ref="window:mr-f8.4",
    )
    assert all(row.observation_available is False for row in rows)
    assert all(row.observed_state is MarketRegimeCode.UNKNOWN for row in rows)


def test_identity_mismatch_fails_closed() -> None:
    pair = build_future_shadow_candidate_pair(evidence=evidence())
    bad = list(outcomes(pair))
    bad[0] = {**bad[0], "parameter_set_id": "wrong"}
    with pytest.raises(ValueError, match="outcome_identity_mismatch"):
        build_future_shadow_comparison_rows(
            pair=pair,
            origin_evidence_bundle=bundle(),
            outcome_rows=tuple(bad),
            evaluation_window_ref="window:mr-f8.4",
        )
