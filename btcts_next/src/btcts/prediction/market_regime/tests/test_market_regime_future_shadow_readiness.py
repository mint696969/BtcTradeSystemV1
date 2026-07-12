# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_readiness.py
# desc: MR-F5.8 read-only projection and family-completion readiness audit tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_shadow_evaluation import build_market_regime_future_shadow_evaluation
from btcts.prediction.market_regime.future_shadow_readiness import MarketRegimeFamilyCompletionEvidence, build_market_regime_future_shadow_readiness

CHECKPOINTS = (
    "MR_F5_1_FUTURE_FORECAST_CONTRACT_AND_LEGACY_PATH_AUDIT_ACCEPTED",
    "MR_F5_2_TARGET_DEFINITION_AND_FEATURE_AVAILABILITY_ACCEPTED",
    "MR_F5_3_TRANSPARENT_BASELINE_MODEL_ACCEPTED",
    "MR_F5_4_EXPLICIT_EVIDENCE_ADAPTER_AND_SHADOW_PACKET_ACCEPTED",
    "MR_F5_5_SHADOW_TRACE_AND_OUTCOME_IDENTITY_ACCEPTED",
    "MR_F5_6_SHADOW_OUTCOME_RESOLUTION_AND_EVALUATION_ROW_ACCEPTED",
    "MR_F5_7_SHADOW_EVALUATION_AGGREGATION_AND_CANDIDATE_COMPARISON_ACCEPTED",
)


def _row(trace: str, parameter: str, status: str) -> dict:
    return {
        "schema_version": "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evaluation_row",
        "trace_id": trace,
        "target_horizon_sec": 300,
        "target_horizon_key": "300s",
        "target_definition_version": "market_regime_target.300s.v1",
        "model_id": "model.v1",
        "logic_version": "logic.v1",
        "parameter_set_id": parameter,
        "feature_snapshot_ref": f"snapshot:{trace}",
        "outcome_status": status,
        "shadow_only": True,
        "canonical_replacement": False,
        "ledger_append_allowed": False,
    }


def _summary():
    return build_market_regime_future_shadow_evaluation(rows=[
        _row("a1", "a", "CORRECT"), _row("a2", "a", "CORRECT"),
        _row("b1", "b", "CORRECT"), _row("b2", "b", "INCORRECT"),
    ], minimum_scored_samples=2)


def test_readiness_blocks_family_completion_without_real_shadow_evidence() -> None:
    readiness = build_market_regime_future_shadow_readiness(
        evaluation_summary=_summary(),
        completion_evidence=MarketRegimeFamilyCompletionEvidence(
            accepted_checkpoints=CHECKPOINTS,
            representative_feature_availability_proven=False,
            shadow_observation_window_completed=False,
            shadow_evaluation_row_count=4,
            comparison_ready=True,
        ),
    )
    assert readiness["family_ready_for_next_family"] is False
    assert "representative_feature_availability_not_proven" in readiness["blockers"]
    assert "shadow_observation_window_not_completed" in readiness["blockers"]
    assert "canonical_migration_review_not_completed" in readiness["blockers"]
    assert readiness["next_prediction_family"] == ""


def test_all_explicit_completion_evidence_can_mark_ready_but_never_promotes() -> None:
    readiness = build_market_regime_future_shadow_readiness(
        evaluation_summary=_summary(),
        completion_evidence=MarketRegimeFamilyCompletionEvidence(
            accepted_checkpoints=CHECKPOINTS,
            representative_feature_availability_proven=True,
            shadow_observation_window_completed=True,
            shadow_evaluation_row_count=4,
            comparison_ready=True,
            canonical_migration_review_completed=True,
        ),
    )
    assert readiness["family_ready_for_next_family"] is True
    assert readiness["next_prediction_family"] == "trend_bias"
    assert readiness["promotion_candidates"] == ()
    assert readiness["safety"]["parameter_auto_promotion_allowed"] is False


def test_missing_checkpoint_and_evidence_mismatch_are_explicit() -> None:
    readiness = build_market_regime_future_shadow_readiness(
        evaluation_summary=_summary(),
        completion_evidence=MarketRegimeFamilyCompletionEvidence(
            accepted_checkpoints=CHECKPOINTS[:-1],
            representative_feature_availability_proven=True,
            shadow_observation_window_completed=True,
            shadow_evaluation_row_count=3,
            comparison_ready=False,
            canonical_migration_review_completed=True,
        ),
    )
    assert readiness["missing_required_checkpoints"] == (CHECKPOINTS[-1],)
    assert "shadow_evaluation_row_count_mismatch" in readiness["blockers"]
    assert "comparison_ready_evidence_mismatch" in readiness["blockers"]


def test_invalid_completion_evidence_types_fail_closed() -> None:
    with pytest.raises(ValueError, match="future_shadow_readiness_checkpoint_invalid"):
        MarketRegimeFamilyCompletionEvidence(
            accepted_checkpoints=("",), representative_feature_availability_proven=False,
            shadow_observation_window_completed=False, shadow_evaluation_row_count=0, comparison_ready=False,
        )
    with pytest.raises(ValueError, match="future_shadow_readiness_boolean_invalid:comparison_ready"):
        MarketRegimeFamilyCompletionEvidence(
            accepted_checkpoints=CHECKPOINTS, representative_feature_availability_proven=False,
            shadow_observation_window_completed=False, shadow_evaluation_row_count=0, comparison_ready=1,
        )


def test_candidate_count_mismatch_fails_closed() -> None:
    summary = dict(_summary()); summary["candidate_count"] = 99
    with pytest.raises(ValueError, match="future_shadow_readiness_candidate_count_mismatch"):
        build_market_regime_future_shadow_readiness(
            evaluation_summary=summary,
            completion_evidence=MarketRegimeFamilyCompletionEvidence(
                accepted_checkpoints=CHECKPOINTS, representative_feature_availability_proven=False,
                shadow_observation_window_completed=False, shadow_evaluation_row_count=4, comparison_ready=True,
            ),
        )


def test_invalid_summary_safety_boundary_fails_closed() -> None:
    summary = dict(_summary())
    summary["safety"] = dict(summary["safety"])
    summary["safety"]["writes_dhot"] = True
    with pytest.raises(ValueError, match="future_shadow_readiness_safety_writes_dhot_invalid"):
        build_market_regime_future_shadow_readiness(
            evaluation_summary=summary,
            completion_evidence=MarketRegimeFamilyCompletionEvidence(
                accepted_checkpoints=CHECKPOINTS,
                representative_feature_availability_proven=False,
                shadow_observation_window_completed=False,
                shadow_evaluation_row_count=4,
                comparison_ready=True,
            ),
        )


def test_readiness_output_is_immutable_at_public_boundaries() -> None:
    readiness = build_market_regime_future_shadow_readiness(
        evaluation_summary=_summary(),
        completion_evidence=MarketRegimeFamilyCompletionEvidence(
            accepted_checkpoints=CHECKPOINTS,
            representative_feature_availability_proven=False,
            shadow_observation_window_completed=False,
            shadow_evaluation_row_count=4,
            comparison_ready=True,
        ),
    )
    with pytest.raises(TypeError): readiness["family_ready_for_next_family"] = True
    with pytest.raises(TypeError): readiness["safety"]["writes_dhot"] = True
    with pytest.raises(TypeError): readiness["candidate_projection"][0]["weighted_score"] = 0.0
