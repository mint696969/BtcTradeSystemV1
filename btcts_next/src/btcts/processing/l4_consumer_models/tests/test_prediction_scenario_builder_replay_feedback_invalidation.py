# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder_replay_feedback_invalidation.py
# desc: Verify replay feedback invalidation weighting stays adjustable and only escalates invalidation state conservatively.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    MarketSummaryBuildInput,
    PredictionReplayFeedbackBuildInput,
    PredictionScenarioBuildInput,
    PredictionSystemBuildInput,
    build_market_summary,
    build_prediction_replay_feedback,
    build_prediction_scenario_output,
    build_prediction_system_input,
)


def _build_market_summary(*, interpretation_bucket: str = "allow_structural_use") -> object:
    return build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-18T03:20:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": interpretation_bucket,
                "interpretation_reason": "unit_test",
                "semantic_observer_status": "healthy",
                "semantic_usage_summary": {
                    "source_kind": "market_state_semantic_usage_summary",
                    "contract_source": "l3_event_usage_policy",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "observer_status": "healthy",
                    "active_event_count": 1,
                    "mapped_event_count": 1,
                    "unknown_event_count": 0,
                },
                "orderbook_semantics_summary": {
                    "summary_slots_present": ["near_wall"],
                    "active_event_count": 1,
                    "active_event_names": ["support_candidate"],
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": True,
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 1.0,
                "preferred_row_freshness": "LIVE",
            },
        )
    )


def main() -> int:
    raised_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=_build_market_summary(),
            replay_feedback=build_prediction_replay_feedback(
                PredictionReplayFeedbackBuildInput(
                    calibration_review={
                        "review_priority": "high",
                        "primary_focus": "invalidation_review",
                        "invalidation_review": "raise_invalidation_sensitivity",
                    },
                    evaluation_report={
                        "entry_count": 4,
                        "missed_count": 3,
                        "high_priority_count": 3,
                    },
                )
            ),
        )
    )
    raised_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(prediction_input=raised_input)
    )

    assert raised_output.current_regime_state == "continuation"
    assert raised_output.current_hypothesis_health == "stable"
    assert raised_output.invalidation_state == "caution_increase"
    assert raised_output.scenario_switch_hint == "tighten_primary_watch"
    assert raised_output.scenario_trace["regime_decision"] == (
        "transition_sign:stable_continuation"
    )
    assert raised_output.scenario_trace["invalidation_path"] == "caution_increase"
    assert raised_output.scenario_trace["switch_reason"] == "tighten_primary_watch"
    replay_feedback_effect = raised_output.scenario_trace["replay_feedback_effect"]
    assert replay_feedback_effect["caution_adjustment"] == 0
    assert replay_feedback_effect["caution_policy"] == "none"
    assert replay_feedback_effect["invalidation_adjustment"] == 2
    assert replay_feedback_effect["invalidation_policy"] == "raise_twice"
    assert replay_feedback_effect["invalidation_score"] == 4.0
    assert replay_feedback_effect["scenario_trace_focus"] == "unknown"
    assert replay_feedback_effect["trace_focus_material"]["focus"] == "unknown"
    assert replay_feedback_effect["trace_focus_material"]["kind"] == "none"
    assert replay_feedback_effect["trace_focus_material"]["direction"] == "neutral"
    assert replay_feedback_effect["trace_focus_material"]["strength"] == 0.0
    assert "replay_feedback_invalidation:raise_twice" in raised_output.invalidation_signals
    assert raised_output.diagnostics["replay_feedback_invalidation_adjustment"] == 2
    assert raised_output.diagnostics["replay_feedback_invalidation_adjustment_policy"] == (
        "raise_twice"
    )
    assert raised_output.diagnostics["replay_feedback_invalidation_score"] == 4.0
    assert raised_output.diagnostics["replay_feedback_scenario_trace_focus"] == "unknown"
    assert raised_output.diagnostics["replay_feedback_trace_focus_kind"] == "none"
    assert raised_output.diagnostics["replay_feedback_trace_focus_direction"] == "neutral"
    assert raised_output.diagnostics["replay_feedback_trace_focus_strength"] == 0.0

    lowered_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=_build_market_summary(),
            replay_feedback=build_prediction_replay_feedback(
                PredictionReplayFeedbackBuildInput(
                    calibration_review={
                        "review_priority": "normal",
                        "primary_focus": "invalidation_review",
                        "invalidation_review": "lower_invalidation_sensitivity",
                    },
                    evaluation_report={
                        "entry_count": 4,
                        "missed_count": 0,
                        "high_priority_count": 0,
                    },
                )
            ),
        )
    )
    lowered_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(prediction_input=lowered_input)
    )

    assert lowered_output.current_regime_state == "continuation"
    assert lowered_output.current_hypothesis_health == "stable"
    assert lowered_output.invalidation_state == "stable"
    assert lowered_output.scenario_switch_hint == "hold_primary"
    assert lowered_output.diagnostics["replay_feedback_invalidation_adjustment"] == -1
    assert lowered_output.diagnostics["replay_feedback_invalidation_adjustment_policy"] == (
        "lower_once"
    )
    assert lowered_output.diagnostics["replay_feedback_invalidation_score"] == -1.0

    transition_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=_build_market_summary(
                interpretation_bucket="reanchor_required"
            ),
        )
    )
    transition_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(prediction_input=transition_input)
    )

    assert transition_output.current_regime_state == "transition"
    assert transition_output.invalidation_state == "scenario_switch_required"
    assert transition_output.scenario_switch_hint == "execute_transition_switch"
    assert transition_output.scenario_trace["regime_decision"] == "summary_reanchor_required"
    assert transition_output.scenario_trace["switch_reason"] == "execute_transition_switch"

    reversal_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=_build_market_summary(),
            regime_turning_point={
                "transition_sign": "weakening_continuation",
                "turning_point_risk": "high",
            },
            replay_feedback=build_prediction_replay_feedback(
                PredictionReplayFeedbackBuildInput(
                    calibration_review={
                        "review_priority": "high",
                        "primary_focus": "invalidation_review",
                        "invalidation_review": "raise_invalidation_sensitivity",
                        "scenario_trace_focus": "switch_reason:watch_reversal_path",
                    },
                    evaluation_report={
                        "entry_count": 4,
                        "missed_count": 3,
                        "high_priority_count": 3,
                    },
                )
            ),
        )
    )
    reversal_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(prediction_input=reversal_input)
    )

    assert reversal_output.current_regime_state == "reversal_watch"
    assert reversal_output.invalidation_state == "degraded"
    assert reversal_output.scenario_switch_hint == "prepare_reversal_switch"
    assert reversal_output.scenario_trace["replay_feedback_effect"][
        "scenario_trace_focus"
    ] == "switch_reason:watch_reversal_path"
    assert reversal_output.scenario_trace["replay_feedback_effect"][
        "trace_focus_material"
    ] == {
        "focus": "switch_reason:watch_reversal_path",
        "kind": "switch_reason",
        "direction": "switch_bias",
        "strength": 1.0,
    }
    assert reversal_output.diagnostics["replay_feedback_scenario_trace_focus"] == (
        "switch_reason:watch_reversal_path"
    )
    assert reversal_output.diagnostics["replay_feedback_trace_focus_kind"] == (
        "switch_reason"
    )
    assert reversal_output.diagnostics["replay_feedback_trace_focus_direction"] == (
        "switch_bias"
    )
    assert reversal_output.diagnostics["replay_feedback_trace_focus_strength"] == 1.0

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())