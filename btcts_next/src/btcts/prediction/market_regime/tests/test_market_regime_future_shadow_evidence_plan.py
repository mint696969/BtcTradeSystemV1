# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_evidence_plan.py
# desc: MR-F5.9 evidence-plan and canonical-migration review criteria tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_evidence_plan import (
    CanonicalMigrationReviewEvidence,
    FutureShadowFeatureAvailabilityEvidence,
    FutureShadowOutcomeCoverageEvidence,
    build_market_regime_future_shadow_evidence_plan,
)


def _feature(horizon: int) -> FutureShadowFeatureAvailabilityEvidence:
    families = ("price_structure", "volatility", "liquidity", "source_quality")
    if horizon >= 21600:
        families += ("session_context",)
    return FutureShadowFeatureAvailabilityEvidence(
        horizon_sec=horizon,
        observed_snapshot_count=10,
        available_feature_families=families,
        first_observed_at="2026-07-10T00:00:00Z",
        last_observed_at="2026-07-12T00:00:00Z",
        source_role="hot_data_root",
        source_artifact_refs=(f"prediction/features/{horizon}.jsonl",),
    )


def _coverage(candidate: str, horizon: int) -> FutureShadowOutcomeCoverageEvidence:
    return FutureShadowOutcomeCoverageEvidence(
        candidate_key=candidate,
        horizon_sec=horizon,
        total_rows=20,
        scored_rows=20,
        unresolved_rows=0,
        invalidated_rows=0,
        abstained_rows=0,
        observation_window_sec=86400,
        first_origin_at="2026-07-10T00:00:00Z",
        last_resolved_at="2026-07-11T00:00:00Z",
        evaluation_artifact_refs=(f"prediction/shadow/{candidate}/{horizon}.jsonl",),
    )


def _review(**overrides) -> CanonicalMigrationReviewEvidence:
    values = {
        "reviewer_ids": ("operator:mint",),
        "review_artifact_refs": ("docs/review/mr_f5_migration.md",),
        "current_state_behavior_unchanged": True,
        "exact_horizon_projection_verified": True,
        "legacy_fallback_removal_plan_reviewed": True,
        "rollback_plan_verified": True,
        "operator_ui_impact_reviewed": True,
        "outcome_identity_compatibility_verified": True,
        "calibrated_probability_claim_absent": True,
    }
    values.update(overrides)
    return CanonicalMigrationReviewEvidence(**values)


def test_empty_real_evidence_stays_blocked_and_legacy_records_do_not_count() -> None:
    plan = build_market_regime_future_shadow_evidence_plan(
        feature_evidence=(), outcome_coverage=(), migration_review=None,
    )
    assert plan["ready_for_family_completion_review"] is False
    assert plan["legacy_canonical_records_count_as_shadow_evidence"] is False
    assert "fewer_than_two_shadow_candidates" in plan["coverage_blockers"]
    assert "canonical_migration_review_absent" in plan["review_blockers"]


def test_complete_two_candidate_all_horizon_evidence_can_reach_review_ready() -> None:
    features = tuple(_feature(horizon) for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC)
    coverage = tuple(
        _coverage(candidate, horizon)
        for candidate in ("candidate-a", "candidate-b")
        for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC
    )
    plan = build_market_regime_future_shadow_evidence_plan(
        feature_evidence=features, outcome_coverage=coverage, migration_review=_review(),
    )
    assert plan["ready_for_family_completion_review"] is True
    assert plan["blockers"] == ()
    assert plan["candidate_count"] == 2
    assert plan["candidate_horizon_count"] == 14
    assert plan["safety"]["canonical_replacement"] is False


def test_long_horizon_requires_session_context() -> None:
    item = _feature(21600)
    bad = FutureShadowFeatureAvailabilityEvidence(
        horizon_sec=item.horizon_sec,
        observed_snapshot_count=item.observed_snapshot_count,
        available_feature_families=("price_structure", "volatility", "liquidity", "source_quality"),
        first_observed_at=item.first_observed_at,
        last_observed_at=item.last_observed_at,
        source_role=item.source_role,
        source_artifact_refs=item.source_artifact_refs,
    )
    plan = build_market_regime_future_shadow_evidence_plan(
        feature_evidence=(bad,), outcome_coverage=(), migration_review=None,
    )
    assert "required_feature_missing:21600:session_context" in plan["feature_blockers"]


def test_coverage_requires_scored_rows_window_refs_and_all_horizons() -> None:
    row = FutureShadowOutcomeCoverageEvidence(
        candidate_key="candidate-a", horizon_sec=300, total_rows=1, scored_rows=1,
        unresolved_rows=0, invalidated_rows=0, abstained_rows=0, observation_window_sec=60,
        first_origin_at="2026-07-12T00:00:00Z", last_resolved_at="2026-07-12T00:01:00Z",
        evaluation_artifact_refs=(),
    )
    plan = build_market_regime_future_shadow_evidence_plan(
        feature_evidence=(), outcome_coverage=(row,), migration_review=None,
    )
    assert "scored_rows_below_minimum:candidate-a:300" in plan["coverage_blockers"]
    assert "observation_window_below_minimum:candidate-a:300" in plan["coverage_blockers"]
    assert "evaluation_refs_absent:candidate-a:300" in plan["coverage_blockers"]
    assert "candidate_horizon_coverage_missing:candidate-a:900" in plan["coverage_blockers"]


def test_incomplete_review_is_explicit() -> None:
    plan = build_market_regime_future_shadow_evidence_plan(
        feature_evidence=(), outcome_coverage=(), migration_review=_review(rollback_plan_verified=False),
    )
    assert "canonical_migration_review_incomplete:rollback_plan_verified" in plan["review_blockers"]


def test_temporal_and_integer_evidence_fail_closed() -> None:
    with pytest.raises(ValueError, match="future_shadow_evidence_feature_time_order_invalid"):
        FutureShadowFeatureAvailabilityEvidence(
            horizon_sec=300, observed_snapshot_count=1,
            available_feature_families=("price_structure",),
            first_observed_at="2026-07-12T00:00:00Z", last_observed_at="2026-07-11T00:00:00Z",
            source_role="hot_data_root", source_artifact_refs=("x",),
        )
    with pytest.raises(ValueError, match="future_shadow_evidence_observation_window_mismatch"):
        FutureShadowOutcomeCoverageEvidence(
            candidate_key="a", horizon_sec=300, total_rows=1, scored_rows=1,
            unresolved_rows=0, invalidated_rows=0, abstained_rows=0, observation_window_sec=60,
            first_origin_at="2026-07-12T00:00:00Z", last_resolved_at="2026-07-12T00:02:00Z",
            evaluation_artifact_refs=("x",),
        )
    with pytest.raises(ValueError, match="future_shadow_evidence_minimum_invalid"):
        build_market_regime_future_shadow_evidence_plan(
            feature_evidence=(), outcome_coverage=(), migration_review=None,
            minimum_scored_rows_per_candidate_horizon=True,
        )


def test_invalid_source_role_and_coverage_total_fail_closed() -> None:
    with pytest.raises(ValueError, match="future_shadow_evidence_source_role_invalid"):
        FutureShadowFeatureAvailabilityEvidence(
            horizon_sec=300, observed_snapshot_count=1,
            available_feature_families=("price_structure",),
            first_observed_at="2026-07-12T00:00:00Z", last_observed_at="2026-07-12T00:00:01Z", source_role="cold_data_root",
            source_artifact_refs=("x",),
        )
    with pytest.raises(ValueError, match="future_shadow_evidence_coverage_total_mismatch"):
        FutureShadowOutcomeCoverageEvidence(
            candidate_key="a", horizon_sec=300, total_rows=2, scored_rows=1,
            unresolved_rows=0, invalidated_rows=0, abstained_rows=0, observation_window_sec=1,
            first_origin_at="2026-07-12T00:00:00Z", last_resolved_at="2026-07-12T00:00:01Z", evaluation_artifact_refs=("x",),
        )


def test_plan_output_is_immutable() -> None:
    plan = build_market_regime_future_shadow_evidence_plan(
        feature_evidence=(), outcome_coverage=(), migration_review=None,
    )
    with pytest.raises(TypeError): plan["ready_for_family_completion_review"] = True
    with pytest.raises(TypeError): plan["safety"]["writes_dhot"] = True
