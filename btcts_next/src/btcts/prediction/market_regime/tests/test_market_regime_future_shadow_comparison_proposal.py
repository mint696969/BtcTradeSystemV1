# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_comparison_proposal.py
# desc: MR-F8.5 tests for multi-slot summaries and human-gated winner/tie/insufficient proposals.

from __future__ import annotations

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_mandatory_baseline_comparison import MandatoryBaselineComparisonRow
from btcts.prediction.market_regime.future_shadow_comparison_proposal import (
    FutureShadowProposalPolicy,
    build_future_shadow_comparison_proposal,
)
from btcts.prediction.market_regime.future_shadow_model_comparison import (
    FutureShadowCandidateIdentity,
    FutureShadowComparisonCohort,
)

ACTIVE = "active.v1"
SHADOW = "shadow.v1"


def identities() -> tuple[FutureShadowCandidateIdentity, ...]:
    return (
        FutureShadowCandidateIdentity(ACTIVE, "model", "logic", ACTIVE, "target.*", "source.v1", "active"),
        FutureShadowCandidateIdentity(SHADOW, "model", "logic", SHADOW, "target.*", "source.v1", "shadow"),
    )


def cohort() -> FutureShadowComparisonCohort:
    return FutureShadowComparisonCohort("cohort", "window", "split", "test", "missing.v1", "all")


def row(candidate: str, index: int, predicted: MarketRegimeCode, observed: MarketRegimeCode, available: bool = True) -> MandatoryBaselineComparisonRow:
    probabilities = {MarketRegimeCode.RANGE: 0.8, MarketRegimeCode.BREAKOUT: 0.2}
    if predicted is MarketRegimeCode.BREAKOUT:
        probabilities = {MarketRegimeCode.RANGE: 0.2, MarketRegimeCode.BREAKOUT: 0.8}
    return MandatoryBaselineComparisonRow(
        trace_id=f"{candidate}:{index}", candidate_id=candidate,
        prediction_origin=f"2026-07-15T00:{index:02d}:00Z", evaluation_window_ref="window",
        source_snapshot_ref=f"snapshot:{index}", target_horizon_sec=300,
        target_definition_version="market_regime_target.300s.v1", outcome_resolver_version="resolver.v1",
        predicted_state=predicted if available else MarketRegimeCode.UNKNOWN,
        observed_state=observed, probability_by_state=probabilities,
        observation_available=True, prediction_available=available,
    )


def test_proposes_shadow_winner_when_material_gain_and_risk_ok() -> None:
    rows = []
    for index in range(4):
        observed = MarketRegimeCode.BREAKOUT
        rows.extend((row(ACTIVE, index, MarketRegimeCode.RANGE, observed), row(SHADOW, index, observed, observed)))
    result = build_future_shadow_comparison_proposal(
        identities=identities(), cohort=cohort(), rows=rows, rollback_candidate_id=ACTIVE,
        policy=FutureShadowProposalPolicy(minimum_observed_slots=4, minimum_accuracy_delta=0.1),
    )
    assert result["proposal"]["decision"] == "winner"
    assert result["proposal"]["selected_candidate_id"] == SHADOW
    assert result["proposal"]["human_approval_required"] is True
    assert result["safety"]["auto_promotion_allowed"] is False


def test_low_sample_is_insufficient() -> None:
    rows = (row(ACTIVE, 0, MarketRegimeCode.RANGE, MarketRegimeCode.RANGE), row(SHADOW, 0, MarketRegimeCode.RANGE, MarketRegimeCode.RANGE))
    result = build_future_shadow_comparison_proposal(
        identities=identities(), cohort=cohort(), rows=rows, rollback_candidate_id=ACTIVE,
        policy=FutureShadowProposalPolicy(minimum_observed_slots=2),
    )
    assert result["proposal"]["decision"] == "insufficient_evidence"
    assert "minimum_observed_slots_not_met" in result["proposal"]["comparison_blockers"]


def test_small_delta_is_tie() -> None:
    rows = []
    for index in range(4):
        observed = MarketRegimeCode.RANGE
        rows.extend((row(ACTIVE, index, observed, observed), row(SHADOW, index, observed, observed)))
    result = build_future_shadow_comparison_proposal(
        identities=identities(), cohort=cohort(), rows=rows, rollback_candidate_id=ACTIVE,
        policy=FutureShadowProposalPolicy(minimum_observed_slots=4),
    )
    assert result["proposal"]["decision"] == "tie"
    assert result["proposal"]["selected_candidate_id"] is None


def test_condition_summary_keeps_same_human_gate() -> None:
    rows = tuple(
        item for index in range(2)
        for item in (row(ACTIVE, index, MarketRegimeCode.RANGE, MarketRegimeCode.RANGE), row(SHADOW, index, MarketRegimeCode.RANGE, MarketRegimeCode.RANGE))
    )
    result = build_future_shadow_comparison_proposal(
        identities=identities(), cohort=cohort(), rows=rows, rollback_candidate_id=ACTIVE,
        policy=FutureShadowProposalPolicy(minimum_observed_slots=2),
        condition_rows={"short_horizon": rows},
    )
    assert len(result["condition_summaries"]) == 1
    assert result["condition_summaries"][0]["decision"]["human_approval_required"] is True
