# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_mandatory_baseline_artifact_adapter.py
# desc: MR-F6.4 tests for fail-closed adaptation of accepted MR-F5 operational evidence.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_artifact_adapter import adapt_mr_f5_evidence_batch

PARAMETER_SET = "market_regime.future.transparent_baseline.params.v1"
TRACE = "market_regime_future_trace:test"
FEATURE_REF = "market_regime_feature_snapshot:test"


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "trace_id": TRACE,
        "model_id": "market_regime.future.transparent_baseline.shadow.v1",
        "parameter_set_id": PARAMETER_SET,
        "origin_timestamp": "2026-07-12T16:54:42Z",
        "feature_snapshot_ref": FEATURE_REF,
        "target_horizon_sec": 300,
        "target_definition_version": "market_regime_target.300s.v1",
        "schema_version": "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
        "forecast_status": "FORECAST",
        "predicted_future_state": "RANGE",
        "observed_future_state": "LOW_VOL_COMPRESSION",
    }
    row.update(overrides)
    return row


def _batch(rows: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "artifact_kind": "future_shadow_evidence_batch",
        "canonical_isolated": True,
        "append_only": True,
        "rows": rows if rows is not None else [_row()],
    }


def _feature(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_timestamp": "2026-07-12T16:54:41Z",
        "current_state": "RANGE",
        "previous_state": "DOWN_TREND",
        "recent_return": 0.01,
        "fast_ma": 101.0,
        "slow_ma": 100.0,
        "realized_volatility": 0.02,
        "low_volatility_threshold": 0.01,
        "high_volatility_threshold": 0.03,
        "current_forecast_label_selection": "BREAKOUT",
    }
    payload.update(overrides)
    return payload


def _probabilities() -> dict[str, float]:
    return {"RANGE": 0.8, "UP_TREND": 0.2}


def test_real_mr_f5_shape_without_enrichment_fails_closed_with_explicit_blockers() -> None:
    result = adapt_mr_f5_evidence_batch(
        batch=_batch(),
        evaluation_window_ref="accepted-mr-f5-window",
        accepted_parameter_set_id=PARAMETER_SET,
    )
    assert result["adaptation_ready"] is False
    assert result["adapted_slot_count"] == 0
    assert result["blocker_counts"]["candidate_probability_by_trace_missing"] == 1
    assert result["blocker_counts"]["feature_snapshot_payload_missing"] == 1
    assert result["safety"]["writes_dhot"] is False


def test_complete_enrichment_produces_one_normalized_slot() -> None:
    result = adapt_mr_f5_evidence_batch(
        batch=_batch(),
        evaluation_window_ref="accepted-mr-f5-window",
        accepted_parameter_set_id=PARAMETER_SET,
        feature_snapshots={FEATURE_REF: _feature()},
        candidate_probabilities_by_trace={TRACE: _probabilities()},
    )
    assert result["adaptation_ready"] is True
    assert result["adapted_slot_count"] == 1
    slot = result["slots"][0]
    assert slot.candidate_trace_id == TRACE
    assert slot.current_state is MarketRegimeCode.RANGE
    assert slot.observed_state is MarketRegimeCode.LOW_VOL_COMPRESSION
    assert slot.source_timestamp_epoch_sec < slot.prediction_origin_epoch_sec


def test_only_accepted_parameter_set_is_selected() -> None:
    other = _row(trace_id="other", parameter_set_id="other-parameter-set")
    result = adapt_mr_f5_evidence_batch(
        batch=_batch([_row(), other]),
        evaluation_window_ref="window",
        accepted_parameter_set_id=PARAMETER_SET,
        feature_snapshots={FEATURE_REF: _feature()},
        candidate_probabilities_by_trace={TRACE: _probabilities()},
    )
    assert result["input_row_count"] == 2
    assert result["accepted_parameter_set_row_count"] == 1
    assert result["adapted_slot_count"] == 1


def test_missing_feature_field_is_reported_not_invented() -> None:
    feature = _feature()
    del feature["fast_ma"]
    result = adapt_mr_f5_evidence_batch(
        batch=_batch(),
        evaluation_window_ref="window",
        accepted_parameter_set_id=PARAMETER_SET,
        feature_snapshots={FEATURE_REF: feature},
        candidate_probabilities_by_trace={TRACE: _probabilities()},
    )
    assert result["adaptation_ready"] is False
    assert result["blocker_counts"]["feature_snapshot_field_missing:fast_ma"] == 1


def test_unsafe_or_wrong_artifact_is_rejected() -> None:
    with pytest.raises(ValueError, match="artifact_kind_invalid"):
        adapt_mr_f5_evidence_batch(
            batch={**_batch(), "artifact_kind": "other"},
            evaluation_window_ref="window",
            accepted_parameter_set_id=PARAMETER_SET,
        )
    with pytest.raises(ValueError, match="safety_contract_invalid"):
        adapt_mr_f5_evidence_batch(
            batch={**_batch(), "canonical_isolated": False},
            evaluation_window_ref="window",
            accepted_parameter_set_id=PARAMETER_SET,
        )


def test_adapter_result_is_immutable() -> None:
    result = adapt_mr_f5_evidence_batch(
        batch=_batch(),
        evaluation_window_ref="window",
        accepted_parameter_set_id=PARAMETER_SET,
    )
    with pytest.raises(TypeError):
        result["adaptation_ready"] = True
    with pytest.raises(TypeError):
        result["blocker_counts"]["x"] = 1
