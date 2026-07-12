# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_evaluation.py
# desc: MR-F5.7 pure aggregation and human-gated candidate comparison tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_shadow_evaluation import build_market_regime_future_shadow_evaluation


def _row(*, trace: str, parameter: str, status: str, horizon: int = 300, model: str = "model.v1", logic: str = "logic.v1") -> dict:
    return {
        "schema_version": "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evaluation_row",
        "trace_id": trace,
        "target_horizon_sec": horizon,
        "target_horizon_key": f"{horizon}s",
        "target_definition_version": f"market_regime_target.{horizon}s.v1",
        "model_id": model,
        "logic_version": logic,
        "parameter_set_id": parameter,
        "feature_snapshot_ref": f"snapshot:{trace}",
        "outcome_status": status,
        "shadow_only": True,
        "canonical_replacement": False,
        "ledger_append_allowed": False,
    }


def test_aggregation_separates_scored_and_unscored_states() -> None:
    summary = build_market_regime_future_shadow_evaluation(rows=[
        _row(trace="a1", parameter="a", status="CORRECT"),
        _row(trace="a2", parameter="a", status="PARTIAL"),
        _row(trace="a3", parameter="a", status="INCORRECT"),
        _row(trace="a4", parameter="a", status="UNRESOLVED"),
        _row(trace="a5", parameter="a", status="INVALIDATED"),
        _row(trace="a6", parameter="a", status="ABSTAINED"),
    ], minimum_scored_samples=3)
    row = summary["candidate_summaries"][0]
    assert row["total_rows"] == 6
    assert row["scored_rows"] == 3
    assert row["weighted_score"] == 0.5
    assert row["unresolved_rows"] == 1
    assert row["invalidated_rows"] == 1
    assert row["abstained_rows"] == 1


def test_two_comparable_candidates_are_ranked_without_promotion() -> None:
    rows = [
        _row(trace="a1", parameter="a", status="CORRECT"),
        _row(trace="a2", parameter="a", status="CORRECT"),
        _row(trace="b1", parameter="b", status="CORRECT"),
        _row(trace="b2", parameter="b", status="INCORRECT"),
    ]
    summary = build_market_regime_future_shadow_evaluation(rows=rows, minimum_scored_samples=2)
    assert summary["comparison_ready"] is True
    assert summary["recommendations"][0]["candidate_key"].endswith("|a")
    assert summary["promotion_candidates"] == ()
    assert all(item["human_gate_required"] is True for item in summary["recommendations"])
    assert all(item["auto_promotion_allowed"] is False for item in summary["recommendations"])


def test_mismatched_horizon_coverage_blocks_comparison() -> None:
    summary = build_market_regime_future_shadow_evaluation(rows=[
        _row(trace="a1", parameter="a", status="CORRECT", horizon=300),
        _row(trace="b1", parameter="b", status="CORRECT", horizon=900),
    ], minimum_scored_samples=1)
    assert summary["comparison_ready"] is False
    assert summary["comparison_blockers"] == ("candidate_horizon_coverage_mismatch",)


def test_insufficient_sample_blocks_comparison() -> None:
    summary = build_market_regime_future_shadow_evaluation(rows=[
        _row(trace="a1", parameter="a", status="CORRECT"),
        _row(trace="b1", parameter="b", status="CORRECT"),
    ], minimum_scored_samples=2)
    assert summary["comparison_ready"] is False
    assert summary["comparison_blockers"] == ("fewer_than_two_candidates_with_minimum_scored_samples",)
    assert all(item["recommendation"] == "keep_collecting" for item in summary["recommendations"])


def test_horizon_views_keep_candidate_identity() -> None:
    summary = build_market_regime_future_shadow_evaluation(rows=[
        _row(trace="a300", parameter="a", status="CORRECT", horizon=300),
        _row(trace="a900", parameter="a", status="PARTIAL", horizon=900),
    ], minimum_scored_samples=1)
    by_horizon = {row["target_horizon_key"]: row for row in summary["by_candidate_horizon"]}
    assert by_horizon["300s"]["weighted_score"] == 1.0
    assert by_horizon["900s"]["weighted_score"] == 0.5
    assert by_horizon["300s"]["parameter_set_id"] == "a"


def test_schema_and_target_identity_mismatch_fail_closed() -> None:
    row = _row(trace="id", parameter="a", status="CORRECT")
    bad_schema = dict(row); bad_schema["schema_version"] = "wrong"
    with pytest.raises(ValueError, match="future_shadow_evaluation_schema_version_invalid"):
        build_market_regime_future_shadow_evaluation(rows=[bad_schema], minimum_scored_samples=1)
    bad_target = dict(row); bad_target["target_definition_version"] = "market_regime_target.900s.v1"
    with pytest.raises(ValueError, match="future_shadow_evaluation_target_definition_mismatch"):
        build_market_regime_future_shadow_evaluation(rows=[bad_target], minimum_scored_samples=1)


def test_duplicate_trace_or_invalid_safety_boundary_fails_closed() -> None:
    row = _row(trace="dup", parameter="a", status="CORRECT")
    with pytest.raises(ValueError, match="future_shadow_evaluation_duplicate_trace_id"):
        build_market_regime_future_shadow_evaluation(rows=[row, row], minimum_scored_samples=1)
    bad = dict(row); bad["ledger_append_allowed"] = True
    with pytest.raises(ValueError, match="future_shadow_evaluation_ledger_boundary_invalid"):
        build_market_regime_future_shadow_evaluation(rows=[bad], minimum_scored_samples=1)


def test_summary_is_deeply_immutable_at_public_boundaries() -> None:
    summary = build_market_regime_future_shadow_evaluation(rows=[_row(trace="a1", parameter="a", status="CORRECT")], minimum_scored_samples=1)
    with pytest.raises(TypeError): summary["comparison_ready"] = True
    with pytest.raises(TypeError): summary["safety"]["writes_dhot"] = True
    with pytest.raises(TypeError): summary["candidate_summaries"][0]["weighted_score"] = 0.0
