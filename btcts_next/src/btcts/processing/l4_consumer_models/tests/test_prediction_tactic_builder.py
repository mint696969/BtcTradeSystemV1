# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_builder.py
# desc: Verify Phase 4-A tactic proposal builder stays scenario-driven, set-based, and rollback-safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    PredictionScenarioOutput,
    PredictionTacticBuildInput,
    TacticParameterSetRef,
    build_prediction_tactic_proposal_output,
)


def main() -> int:
    active_parameter_set_ref = TacticParameterSetRef(
        set_id="candidate-reversal-watch",
        set_version="v2",
        profile_kind="candidate",
        baseline_ref="baseline-default",
        overlay_refs=("reversal_watch_overlay",),
        rollback_parent_set_id="baseline-default",
        comparison_group="phase4a-entry",
        is_active_candidate=True,
    )

    scenario_output = PredictionScenarioOutput(
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-19T12:30:00Z",
        current_regime_state="reversal_watch",
        current_hypothesis_health="caution_increase",
        current_confidence=0.31,
        current_caution_level="medium",
        invalidation_state="caution_increase",
        scenario_switch_hint="prepare_reversal_switch",
        scenario_trace={
            "trace_type": "prediction_scenario_trace",
            "replay_feedback_effect": {
                "scenario_trace_focus": "switch_reason:prepare_reversal_switch"
            },
        },
        diagnostics={"source": "unit_test"},
    )

    proposal_output = build_prediction_tactic_proposal_output(
        PredictionTacticBuildInput(
            scenario_output=scenario_output,
            active_parameter_set_ref=active_parameter_set_ref,
            diagnostics={"caller": "unit_test"},
        )
    )

    assert proposal_output.proposal_type == "scenario_tactic_proposal_output"
    assert proposal_output.source_kind == "prediction_scenario_output"
    assert proposal_output.market_uid == "bitflyer.spot.BTC_JPY"
    assert proposal_output.event_ts == "2026-04-19T12:30:00Z"
    assert proposal_output.scenario_ref == (
        "bitflyer.spot.BTC_JPY@2026-04-19T12:30:00Z"
    )
    assert proposal_output.scenario_regime == "reversal_watch"
    assert proposal_output.primary_tactic_key == "reversal_prepare"
    assert proposal_output.proposal_state == "proposed"
    assert proposal_output.rollback_ready is True
    assert proposal_output.review_needed is True

    assert proposal_output.active_parameter_set_ref.set_id == "candidate-reversal-watch"
    assert len(proposal_output.comparison_set_refs) == 2
    assert proposal_output.comparison_set_refs[0].set_id == "baseline-default"
    assert proposal_output.comparison_set_refs[1].set_id == "candidate-reversal-watch"

    assert len(proposal_output.candidate_tactics) == 2
    assert proposal_output.candidate_tactics[0].tactic_key == "reversal_prepare"
    assert proposal_output.candidate_tactics[0].switch_alignment == "aligned"
    assert proposal_output.candidate_tactics[0].reason_refs == (
        "scenario_regime:reversal_watch",
        "scenario_switch_hint:prepare_reversal_switch",
        "invalidation_state:caution_increase",
        "primary_tactic:reversal_prepare",
        "scenario_trace_focus:switch_reason:prepare_reversal_switch",
    )
    assert proposal_output.candidate_tactics[1].tactic_key == "observe_only"
    assert proposal_output.candidate_tactics[1].switch_alignment == "fallback"

    assert proposal_output.explanation_trace["trace_type"] == (
        "scenario_tactic_explanation_trace"
    )
    assert proposal_output.explanation_trace["primary_tactic_key"] == "reversal_prepare"
    assert proposal_output.explanation_trace["scenario_regime"] == "reversal_watch"
    assert proposal_output.explanation_trace["scenario_switch_hint"] == (
        "prepare_reversal_switch"
    )
    assert proposal_output.explanation_trace["scenario_trace_focus"] == (
        "switch_reason:prepare_reversal_switch"
    )

    assert proposal_output.diagnostics["builder_type"] == (
        "prediction_tactic_proposal_output"
    )
    assert proposal_output.diagnostics["scenario_present"] is True
    assert proposal_output.diagnostics["candidate_count"] == 2
    assert proposal_output.diagnostics["comparison_set_count"] == 2
    assert proposal_output.diagnostics["adoption_ready"] is True
    assert proposal_output.diagnostics["rollback_target_available"] is True
    assert (
        proposal_output.diagnostics["selected_set_id"]
        == "candidate-reversal-watch"
    )
    assert proposal_output.diagnostics["parameter_trace"]["profile_kind"] == "candidate"
    assert proposal_output.diagnostics["parameter_trace"]["overlay_refs"] == (
        "reversal_watch_overlay",
    )
    assert proposal_output.diagnostics["parameter_trace"][
        "comparison_profile_kinds"
    ] == ("baseline", "candidate")
    assert proposal_output.diagnostics["parameter_trace"][
        "comparison_active_index"
    ] == 1
    assert proposal_output.diagnostics["parameter_trace"][
        "comparison_baseline_available"
    ] is True
    assert proposal_output.diagnostics["parameter_trace"][
        "comparison_relation"
    ] == "candidate_vs_baseline"
    assert proposal_output.diagnostics["parameter_trace"][
        "overlay_influence"
    ] == "overlay_bias"
    assert proposal_output.diagnostics["selection_trace"]["trace_type"] == (
        "tactic_selection_trace"
    )
    assert proposal_output.diagnostics["selection_trace"]["profile_kind"] == "candidate"
    assert proposal_output.diagnostics["selection_trace"]["overlay_refs"] == (
        "reversal_watch_overlay",
    )
    assert proposal_output.explanation_trace["selection_trace"]["primary_tactic_key"] == (
        "reversal_prepare"
    )
    assert proposal_output.explanation_trace["selection_trace"]["scenario_regime"] == (
        "reversal_watch"
    )
    assert proposal_output.diagnostics["caller"] == "unit_test"

    defensive_parameter_set_ref = TacticParameterSetRef(
        set_id="candidate-defensive-profile",
        set_version="v1",
        profile_kind="defensive",
        baseline_ref="baseline-default",
        overlay_refs=("prefer_cautious_probe",),
        rollback_parent_set_id="baseline-default",
        comparison_group="phase4a-entry",
        is_active_candidate=True,
    )
    defensive_scenario_output = PredictionScenarioOutput(
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-19T12:40:00Z",
        current_regime_state="continuation",
        current_hypothesis_health="caution_increase",
        current_confidence=0.48,
        current_caution_level="medium",
        invalidation_state="caution_increase",
        scenario_switch_hint="hold_primary",
    )
    defensive_proposal = build_prediction_tactic_proposal_output(
        PredictionTacticBuildInput(
            scenario_output=defensive_scenario_output,
            active_parameter_set_ref=defensive_parameter_set_ref,
        )
    )

    assert defensive_proposal.primary_tactic_key == "defensive_reduce_risk"
    assert defensive_proposal.candidate_tactics[0].tactic_key == (
        "defensive_reduce_risk"
    )
    assert defensive_proposal.diagnostics["adoption_ready"] is True
    assert defensive_proposal.diagnostics["rollback_target_available"] is True
    assert defensive_proposal.diagnostics["parameter_trace"]["profile_kind"] == (
        "defensive"
    )
    assert defensive_proposal.diagnostics["parameter_trace"]["overlay_refs"] == (
        "prefer_cautious_probe",
    )
    assert defensive_proposal.diagnostics["selection_trace"]["profile_kind"] == (
        "defensive"
    )
    assert defensive_proposal.diagnostics["selection_trace"]["selection_bias_tags"] == (
        "profile:defensive",
        "overlay:prefer_cautious_probe",
    )
    assert defensive_proposal.explanation_trace["selection_trace"]["primary_tactic_key"] == (
        "defensive_reduce_risk"
    )

    blocked = build_prediction_tactic_proposal_output(PredictionTacticBuildInput())
    assert blocked.primary_tactic_key == "maintain_no_trade"
    assert blocked.proposal_state == "blocked"
    assert blocked.market_uid is None
    assert blocked.scenario_ref is None
    assert blocked.candidate_tactics[0].tactic_key == "maintain_no_trade"
    assert blocked.explanation_trace["scenario_present"] is False
    assert blocked.diagnostics["scenario_present"] is False
    assert blocked.diagnostics["adoption_ready"] is False
    assert blocked.diagnostics["rollback_target_available"] is False
    assert blocked.diagnostics["selected_set_id"] == "global_phase4a_default"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())