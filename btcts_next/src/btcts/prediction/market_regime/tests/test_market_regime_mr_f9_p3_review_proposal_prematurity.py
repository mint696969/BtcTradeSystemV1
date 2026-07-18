# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_mr_f9_p3_review_proposal_prematurity.py
# desc: MR-F9 P3 integration guards for prematurity-blocked proposal and review semantics.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_comparison import (
    MandatoryBaselineComparisonRow,
)
from btcts.prediction.market_regime.future_shadow_comparison_proposal import (
    FutureShadowProposalPolicy,
    build_future_shadow_comparison_proposal,
)
from btcts.prediction.market_regime.future_shadow_model_comparison import (
    FutureShadowCandidateIdentity,
    FutureShadowComparisonCohort,
)
from btcts.prediction.market_regime.future_shadow_review_contracts import (
    FutureShadowReviewNote,
    build_future_shadow_review_link,
    build_future_shadow_review_request,
)

ACTIVE = "active.v1"
SHADOW = "shadow.v1"


def _identities() -> tuple[FutureShadowCandidateIdentity, ...]:
    return (
        FutureShadowCandidateIdentity(
            ACTIVE,
            "model",
            "logic",
            ACTIVE,
            "target.*",
            "source.v1",
            "active",
        ),
        FutureShadowCandidateIdentity(
            SHADOW,
            "model",
            "logic",
            SHADOW,
            "target.*",
            "source.v1",
            "shadow",
        ),
    )


def _cohort() -> FutureShadowComparisonCohort:
    return FutureShadowComparisonCohort(
        "mr-f9-p3",
        "replacement-24h-window",
        "split",
        "test",
        "missing.v1",
        "all",
    )


def _row(
    candidate_id: str,
    index: int,
    *,
    prediction_available: bool = True,
    observation_available: bool = True,
) -> MandatoryBaselineComparisonRow:
    predicted = (
        MarketRegimeCode.RANGE
        if prediction_available
        else MarketRegimeCode.UNKNOWN
    )
    observed = (
        MarketRegimeCode.RANGE
        if observation_available
        else MarketRegimeCode.UNKNOWN
    )
    return MandatoryBaselineComparisonRow(
        trace_id=f"{candidate_id}:{index}",
        candidate_id=candidate_id,
        prediction_origin=f"2026-07-18T04:{index:02d}:00Z",
        evaluation_window_ref="replacement-24h-window",
        source_snapshot_ref=f"snapshot:{index}",
        target_horizon_sec=86400,
        target_definition_version="market_regime_target.86400s.v1",
        outcome_resolver_version="resolver.v1",
        predicted_state=predicted,
        observed_state=observed,
        probability_by_state={
            MarketRegimeCode.RANGE: 0.8,
            MarketRegimeCode.BREAKOUT: 0.2,
        },
        observation_available=observation_available,
        prediction_available=prediction_available,
    )


def _execution_diagnostics() -> dict:
    return {
        "artifact_kind": "future_execution_diagnostics_report",
        "origin_count": 1,
        "trace_count": 2,
        "safety": {
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }


def _outcome_diagnostics() -> dict:
    return {
        "artifact_kind": "future_outcome_persistence_diagnostics_report",
        "snapshot_count": 0,
        "receipt_count": 0,
        "trace_count": 0,
        "safety": {
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_outcome_ledger_append": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        },
    }


def _premature_proposal():
    rows = (
        _row(ACTIVE, 0),
        _row(SHADOW, 0),
    )
    return build_future_shadow_comparison_proposal(
        identities=_identities(),
        cohort=_cohort(),
        rows=rows,
        rollback_candidate_id=ACTIVE,
        policy=FutureShadowProposalPolicy(
            minimum_observed_slots=30,
            minimum_coverage_rate=0.20,
        ),
    )


def test_premature_collection_produces_insufficient_evidence_not_winner() -> None:
    proposal = _premature_proposal()

    assert proposal["proposal"]["decision"] == "insufficient_evidence"
    assert proposal["proposal"]["selected_candidate_id"] is None
    assert "minimum_observed_slots_not_met" in (
        proposal["proposal"]["comparison_blockers"]
    )
    assert proposal["proposal"]["human_approval_required"] is True
    assert proposal["proposal"]["proposal_is_not_runtime_activation"] is True
    assert proposal["safety"]["writes_dhot"] is False
    assert proposal["safety"]["auto_promotion_allowed"] is False
    assert proposal["safety"]["live_parameter_apply_allowed"] is False


def test_premature_proposal_creates_blocked_review_without_note_or_link() -> None:
    request = build_future_shadow_review_request(
        proposal=_premature_proposal(),
        execution_diagnostics=_execution_diagnostics(),
        outcome_diagnostics=_outcome_diagnostics(),
        proposal_ref="artifact:proposal:premature",
        execution_diagnostics_ref="artifact:execution:premature",
        outcome_diagnostics_ref="artifact:outcome:premature",
        review_scope_id="mr-f9:replacement-24h",
        requested_at="2026-07-18T05:00:00Z",
    )

    assert request["review_status"] == "BLOCKED_INSUFFICIENT_EVIDENCE"
    assert request["proposal_decision"] == "insufficient_evidence"
    assert request["selected_candidate_id"] is None
    assert request["review_note_required"] is False
    assert request["review_link_required"] is False
    assert request["human_approval_required"] is True
    assert request["runtime_activation_performed"] is False
    assert request["auto_promotion_allowed"] is False
    assert request["live_parameter_apply_allowed"] is False
    assert request["would_write"] is False
    assert request["safety"]["writes_dhot"] is False


def test_blocked_premature_review_cannot_receive_decision_link() -> None:
    request = build_future_shadow_review_request(
        proposal=_premature_proposal(),
        execution_diagnostics=_execution_diagnostics(),
        outcome_diagnostics=_outcome_diagnostics(),
        proposal_ref="artifact:proposal:premature",
        execution_diagnostics_ref="artifact:execution:premature",
        outcome_diagnostics_ref="artifact:outcome:premature",
        review_scope_id="mr-f9:replacement-24h",
        requested_at="2026-07-18T05:00:00Z",
    )
    note = FutureShadowReviewNote(
        note_id="review-note:premature",
        request_id=request["request_id"],
        author="operator:mint",
        recorded_at="2026-07-18T05:01:00Z",
        decision="approve",
        note_text="Premature evidence must remain blocked.",
    )

    with pytest.raises(ValueError, match="blocked_request_forbidden"):
        build_future_shadow_review_link(request=request, note=note)


def test_missing_predictions_and_observations_cannot_create_winner() -> None:
    rows = (
        _row(ACTIVE, 0, prediction_available=False),
        _row(SHADOW, 0, observation_available=False),
    )
    proposal = build_future_shadow_comparison_proposal(
        identities=_identities(),
        cohort=_cohort(),
        rows=rows,
        rollback_candidate_id=ACTIVE,
        policy=FutureShadowProposalPolicy(
            minimum_observed_slots=1,
            minimum_coverage_rate=0.20,
        ),
    )

    assert proposal["proposal"]["decision"] == "insufficient_evidence"
    assert proposal["proposal"]["selected_candidate_id"] is None
    blockers = proposal["proposal"]["comparison_blockers"]
    assert blockers
    assert any(
        item.startswith("minimum_coverage_not_met:")
        or item == "required_metric_missing"
        for item in blockers
    )
