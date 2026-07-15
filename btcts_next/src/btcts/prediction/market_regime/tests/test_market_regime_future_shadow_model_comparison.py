# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_model_comparison.py
# desc: MR-F8.2 tests for immutable future-shadow candidate, cohort, decision, and safety contracts.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_comparison import MandatoryBaselineComparisonRow
from btcts.prediction.market_regime.future_shadow_model_comparison import (
    FutureShadowCandidateIdentity,
    FutureShadowComparisonCohort,
    FutureShadowComparisonDecision,
    build_future_shadow_model_comparison,
)


def identity(candidate_id: str, role: str) -> FutureShadowCandidateIdentity:
    return FutureShadowCandidateIdentity(
        candidate_id=candidate_id,
        model_id="market_regime.future.transparent_baseline",
        logic_version="future_forecast.v1",
        parameter_set_id=candidate_id,
        target_definition_family="market_regime_target.*.v1",
        source_contract_version="market_regime_source_snapshot.v1",
        registry_role=role,
    )


def cohort() -> FutureShadowComparisonCohort:
    return FutureShadowComparisonCohort(
        cohort_id="mr-f8-test",
        evaluation_window_ref="window:test",
        oos_split_id="split:test:v1",
        oos_partition="test",
        missing_data_policy_version="missing_data.identical_slots.v1",
        condition_group_id="all_conditions",
    )


def row(candidate_id: str, trace_id: str, *, window: str = "window:test") -> MandatoryBaselineComparisonRow:
    return MandatoryBaselineComparisonRow(
        trace_id=trace_id,
        candidate_id=candidate_id,
        prediction_origin="2026-07-15T00:00:00Z",
        evaluation_window_ref=window,
        source_snapshot_ref="snapshot:1",
        target_horizon_sec=300,
        target_definition_version="market_regime_target.300s.v1",
        outcome_resolver_version="resolver.v1",
        predicted_state=MarketRegimeCode.RANGE,
        observed_state=MarketRegimeCode.RANGE,
        probability_by_state={
            MarketRegimeCode.RANGE: 0.7,
            MarketRegimeCode.UP_TREND: 0.1,
            MarketRegimeCode.DOWN_TREND: 0.1,
            MarketRegimeCode.HIGH_VOL_CHOP: 0.1,
        },
        observation_available=True,
        prediction_available=True,
    )


def test_builds_ready_two_candidate_comparison_without_promotion() -> None:
    result = build_future_shadow_model_comparison(
        identities=(identity("active.v1", "active"), identity("shadow.v1", "shadow")),
        cohort=cohort(),
        rows=(row("active.v1", "a"), row("shadow.v1", "b")),
        decision=FutureShadowComparisonDecision(
            decision="tie",
            selected_candidate_id=None,
            rollback_candidate_id="active.v1",
            rationale_codes=("metric_differences_below_threshold",),
        ),
    )
    assert result["comparison_ready"] is True
    assert result["candidate_count"] == 2
    assert len(result["candidate_summaries"]) == 2
    assert result["safety"]["parameter_auto_promotion_allowed"] is False
    assert result["safety"]["live_parameter_apply_allowed"] is False


def test_rejects_winner_when_cohort_slots_differ() -> None:
    with pytest.raises(ValueError, match="unready_decision_must_be_insufficient"):
        build_future_shadow_model_comparison(
            identities=(identity("active.v1", "active"), identity("shadow.v1", "shadow")),
            cohort=cohort(),
            rows=(row("active.v1", "a"),),
            decision=FutureShadowComparisonDecision(
                decision="winner",
                selected_candidate_id="active.v1",
                rollback_candidate_id="active.v1",
                rationale_codes=("coverage_superior",),
            ),
        )


def test_reports_insufficient_evidence_for_wrong_window() -> None:
    result = build_future_shadow_model_comparison(
        identities=(identity("active.v1", "active"), identity("shadow.v1", "shadow")),
        cohort=cohort(),
        rows=(row("active.v1", "a"), row("shadow.v1", "b", window="window:other")),
        decision=FutureShadowComparisonDecision(
            decision="insufficient_evidence",
            selected_candidate_id=None,
            rollback_candidate_id="active.v1",
            rationale_codes=("evaluation_window_mismatch",),
        ),
    )
    assert result["comparison_ready"] is False
    assert "evaluation_window_mismatch" in result["comparison_blockers"]


def test_decision_requires_human_gate_and_forbids_live_apply() -> None:
    with pytest.raises(ValueError, match="human_gate_required"):
        FutureShadowComparisonDecision(
            decision="tie",
            selected_candidate_id=None,
            rollback_candidate_id="active.v1",
            rationale_codes=("tie",),
            human_approval_required=False,
        )
    with pytest.raises(ValueError, match="live_apply_forbidden"):
        FutureShadowComparisonDecision(
            decision="tie",
            selected_candidate_id=None,
            rollback_candidate_id="active.v1",
            rationale_codes=("tie",),
            live_parameter_apply_allowed=True,
        )
