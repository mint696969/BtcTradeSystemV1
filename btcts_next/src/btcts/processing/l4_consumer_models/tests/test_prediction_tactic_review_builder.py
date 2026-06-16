# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_review_builder.py
# desc: Verify Phase 4-A tactic review builder stays proposal-driven, set-based, and rollback-safe.

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
    PredictionTacticReviewBuildInput,
    build_prediction_tactic_review_record,
)


def main() -> int:
    baseline_ref = TacticParameterSetRef(
        set_id="baseline-default",
        set_version="v1",
        profile_kind="baseline",
        comparison_group="phase4a-entry",
    )
    candidate_ref = TacticParameterSetRef(
        set_id="candidate-continuation-follow",
        set_version="v2",
        profile_kind="candidate",
        baseline_ref="baseline-default",
        rollback_parent_set_id="baseline-default",
        comparison_group="phase4a-entry",
        is_active_candidate=True,
    )

    proposal_output = ScenarioTacticProposalOutput(
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-19T13:00:00Z",
        scenario_ref="bitflyer.spot.BTC_JPY@2026-04-19T13:00:00Z",
        scenario_regime="continuation",
        primary_tactic_key="continuation_follow",
        proposal_state="proposed",
        candidate_tactics=(
            ScenarioTacticCandidate(
                tactic_key="continuation_follow",
                tactic_label="continuation_follow",
                stance_bias="continuation_bias",
                readiness="ready",
                priority=10,
                parameter_set_ref=candidate_ref,
                switch_alignment="aligned",
            ),
        ),
        active_parameter_set_ref=candidate_ref,
        comparison_set_refs=(baseline_ref, candidate_ref),
        rollback_ready=True,
        review_needed=True,
        explanation_trace={
            "selection_trace": {
                "trace_type": "tactic_selection_trace",
                "primary_tactic_key": "continuation_follow",
                "scenario_present": True,
                "profile_kind": "candidate",
                "overlay_refs": ("prefer_cautious_probe",),
                "selection_bias_tags": (
                    "profile:candidate",
                    "overlay:prefer_cautious_probe",
                ),
                "promotion_gate_state": "allowed",
                "can_promote_active_tactic": True,
                "overlay_primary_ref": "prefer_cautious_probe",
                "overlay_support_tactic_keys": ("cautious_probe",),
                "overlay_application_mode": "primary_and_support",
            }
        },
        diagnostics={
            "source": "unit_test",
            "selection_trace": {
                "trace_type": "tactic_selection_trace",
                "primary_tactic_key": "continuation_follow",
                "scenario_present": True,
                "profile_kind": "candidate",
                "overlay_refs": ("prefer_cautious_probe",),
                "selection_bias_tags": (
                    "profile:candidate",
                    "overlay:prefer_cautious_probe",
                ),
                "promotion_gate_state": "allowed",
                "can_promote_active_tactic": True,
                "overlay_primary_ref": "prefer_cautious_probe",
                "overlay_support_tactic_keys": ("cautious_probe",),
                "overlay_application_mode": "primary_and_support",
            },
            "parameter_trace": {
                "active_set_id": "candidate-continuation-follow",
                "active_set_version": "v2",
                "profile_kind": "candidate",
                "baseline_ref": "baseline-default",
                "overlay_refs": (),
                "comparison_group": "phase4a-entry",
                "rollback_parent_set_id": "baseline-default",
                "rollback_target_ref": "baseline-default",
                "adoption_ready": True,
                "comparison_set_ids": (
                    "baseline-default",
                    "candidate-continuation-follow",
                ),
                "comparison_set_versions": (
                    "v1",
                    "v2",
                ),
                "comparison_profile_kinds": (
                    "baseline",
                    "candidate",
                ),
                "comparison_active_index": 1,
                "comparison_baseline_available": True,
                "comparison_relation": "candidate_vs_baseline",
                "overlay_influence": "none",
                "comparison_count": 2,
                "comparison_has_active_candidate": True,
            },
        },
    )

    review_record = build_prediction_tactic_review_record(
        PredictionTacticReviewBuildInput(
            proposal_output=proposal_output,
            review_ts="2026-04-19T13:01:00Z",
            decision_state="adopted",
            decision_reason="continuation_bias_with_low_caution",
            operator_note="first_adoption",
            diagnostics={"caller": "unit_test"},
        )
    )

    assert review_record.review_type == "tactic_review_record"
    assert review_record.review_version == "phase3.v1alpha1"
    assert review_record.review_id == (
        "bitflyer.spot.BTC_JPY@2026-04-19T13:00:00Z:"
        "continuation_follow:2026-04-19T13:01:00Z"
    )
    assert review_record.review_ts == "2026-04-19T13:01:00Z"
    assert review_record.market_uid == "bitflyer.spot.BTC_JPY"
    assert review_record.scenario_ref == "bitflyer.spot.BTC_JPY@2026-04-19T13:00:00Z"
    assert review_record.proposal_ref == (
        "proposal:bitflyer.spot.BTC_JPY@2026-04-19T13:00:00Z"
    )
    assert review_record.selected_tactic_key == "continuation_follow"
    assert (
        review_record.selected_parameter_set_ref.set_id
        == "candidate-continuation-follow"
    )
    assert review_record.decision_state == "adopted"
    assert review_record.decision_reason == "continuation_bias_with_low_caution"
    assert review_record.comparison_refs == (
        "baseline-default",
        "candidate-continuation-follow",
    )
    assert review_record.rollback_target_ref == "baseline-default"
    assert review_record.operator_note == "first_adoption"
    assert review_record.replay_followup_required is True
    assert review_record.selection_trace == {
        "trace_type": "tactic_selection_trace",
        "primary_tactic_key": "continuation_follow",
        "scenario_present": True,
        "profile_kind": "candidate",
        "overlay_refs": ("prefer_cautious_probe",),
        "selection_bias_tags": (
            "profile:candidate",
            "overlay:prefer_cautious_probe",
        ),
        "promotion_gate_state": "allowed",
        "can_promote_active_tactic": True,
        "overlay_primary_ref": "prefer_cautious_probe",
        "overlay_support_tactic_keys": ("cautious_probe",),
        "overlay_application_mode": "primary_and_support",
    }
    assert review_record.parameter_trace == {
        "active_set_id": "candidate-continuation-follow",
        "active_set_version": "v2",
        "profile_kind": "candidate",
        "baseline_ref": "baseline-default",
        "overlay_refs": (),
        "comparison_group": "phase4a-entry",
        "rollback_parent_set_id": "baseline-default",
        "rollback_target_ref": "baseline-default",
        "adoption_ready": True,
        "comparison_set_ids": (
            "baseline-default",
            "candidate-continuation-follow",
        ),
        "comparison_set_versions": (
            "v1",
            "v2",
        ),
        "comparison_profile_kinds": (
            "baseline",
            "candidate",
        ),
        "comparison_active_index": 1,
        "comparison_baseline_available": True,
        "comparison_relation": "candidate_vs_baseline",
        "overlay_influence": "none",
        "comparison_count": 2,
        "comparison_has_active_candidate": True,
    }
    assert review_record.diagnostics["builder_type"] == (
        "prediction_tactic_review_record"
    )
    assert review_record.diagnostics["proposal_present"] is True
    assert review_record.diagnostics["comparison_ref_count"] == 2
    assert review_record.diagnostics["selection_trace_present"] is True
    assert review_record.diagnostics["parameter_trace_present"] is True
    assert review_record.diagnostics["adoption_ready"] is True
    assert review_record.diagnostics["rollback_target_available"] is True
    assert (
        review_record.diagnostics["selected_set_id"]
        == "candidate-continuation-follow"
    )
    assert review_record.diagnostics["caller"] == "unit_test"

    empty_review = build_prediction_tactic_review_record(
        PredictionTacticReviewBuildInput()
    )
    assert empty_review.review_id is None
    assert empty_review.proposal_ref is None
    assert empty_review.selected_tactic_key == "observe_only"
    assert empty_review.selected_parameter_set_ref.set_id == "default"
    assert empty_review.comparison_refs == ()
    assert empty_review.rollback_target_ref is None
    assert empty_review.replay_followup_required is False
    assert empty_review.selection_trace == {}
    assert empty_review.parameter_trace == {}
    assert empty_review.diagnostics["proposal_present"] is False
    assert empty_review.diagnostics["selection_trace_present"] is False
    assert empty_review.diagnostics["parameter_trace_present"] is False

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())