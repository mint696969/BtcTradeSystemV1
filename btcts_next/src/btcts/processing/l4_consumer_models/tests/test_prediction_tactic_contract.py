# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_contract.py
# desc: Verify Phase 4-A tactic proposal shared contract stays additive, set-based, and rollback-safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    ScenarioTacticCandidate,
    ScenarioTacticProposalOutput,
    TacticParameterSetRef,
    TacticReviewRecord,
)


def main() -> int:
    baseline_ref = TacticParameterSetRef(
        set_id="baseline-default",
        set_version="v1",
        profile_kind="baseline",
        comparison_group="phase4a-entry",
        is_active_candidate=True,
    )
    candidate_ref = TacticParameterSetRef(
        set_id="candidate-cautious-probe",
        set_version="v1",
        profile_kind="candidate",
        baseline_ref="baseline-default",
        overlay_refs=("caution_overlay",),
        rollback_parent_set_id="baseline-default",
        comparison_group="phase4a-entry",
        is_active_candidate=True,
        diagnostics={"owner": "test"},
    )

    tactic_candidate = ScenarioTacticCandidate(
        tactic_key="cautious_probe",
        tactic_label="cautious_probe",
        stance_bias="balanced_entry",
        readiness="watch",
        priority=20,
        parameter_set_ref=candidate_ref,
        reason_refs=(
            "scenario_switch_hint:tighten_primary_watch",
            "trace_focus:watch_bias",
        ),
        caution_flags=("high_caution",),
        invalidation_watch="active",
        switch_alignment="aligned",
        diagnostics={"source": "contract_test"},
    )

    proposal_output = ScenarioTacticProposalOutput(
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-19T12:00:00Z",
        scenario_ref="scenario:2026-04-19T12:00:00Z",
        scenario_regime="continuation",
        primary_tactic_key="cautious_probe",
        proposal_state="proposed",
        candidate_tactics=(tactic_candidate,),
        active_parameter_set_ref=candidate_ref,
        comparison_set_refs=(baseline_ref, candidate_ref),
        rollback_ready=True,
        review_needed=True,
        explanation_trace={
            "switch_reason": "tighten_primary_watch",
            "trace_focus_material": {
                "kind": "switch_reason",
                "direction": "watch_bias",
            },
        },
        diagnostics={"builder_type": "phase4a_contract_test"},
    )

    review_record = TacticReviewRecord(
        review_id="review-001",
        review_ts="2026-04-19T12:05:00Z",
        market_uid="bitflyer.spot.BTC_JPY",
        scenario_ref="scenario:2026-04-19T12:00:00Z",
        proposal_ref="proposal:2026-04-19T12:00:00Z",
        selected_tactic_key="cautious_probe",
        selected_parameter_set_ref=candidate_ref,
        decision_state="adopted",
        decision_reason="watch_bias_with_manageable_risk",
        comparison_refs=("baseline-default", "candidate-cautious-probe"),
        rollback_target_ref="baseline-default",
        operator_note="first safe slice",
        replay_followup_required=True,
        diagnostics={"review_lane": "human_gpt"},
    )

    assert baseline_ref.ref_type == "tactic_parameter_set_ref"
    assert baseline_ref.profile_kind == "baseline"
    assert candidate_ref.baseline_ref == "baseline-default"
    assert candidate_ref.overlay_refs == ("caution_overlay",)
    assert candidate_ref.rollback_parent_set_id == "baseline-default"

    assert tactic_candidate.tactic_key == "cautious_probe"
    assert tactic_candidate.readiness == "watch"
    assert tactic_candidate.priority == 20
    assert tactic_candidate.parameter_set_ref.set_id == "candidate-cautious-probe"
    assert tactic_candidate.switch_alignment == "aligned"

    assert proposal_output.proposal_type == "scenario_tactic_proposal_output"
    assert proposal_output.source_kind == "prediction_scenario_output"
    assert proposal_output.market_uid == "bitflyer.spot.BTC_JPY"
    assert proposal_output.scenario_regime == "continuation"
    assert proposal_output.primary_tactic_key == "cautious_probe"
    assert proposal_output.rollback_ready is True
    assert proposal_output.review_needed is True
    assert len(proposal_output.candidate_tactics) == 1
    assert proposal_output.comparison_set_refs[0].set_id == "baseline-default"
    assert (
        proposal_output.explanation_trace["trace_focus_material"]["direction"]
        == "watch_bias"
    )

    assert review_record.review_type == "tactic_review_record"
    assert review_record.review_id == "review-001"
    assert review_record.selected_tactic_key == "cautious_probe"
    assert review_record.selected_parameter_set_ref.set_id == "candidate-cautious-probe"
    assert review_record.decision_state == "adopted"
    assert review_record.rollback_target_ref == "baseline-default"
    assert review_record.replay_followup_required is True

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())