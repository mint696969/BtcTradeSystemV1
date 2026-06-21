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
    raised_rewrite_trace = raised_output.scenario_trace[
        "invalidation_rewrite_trace"
    ]
    assert raised_rewrite_trace["trace_type"] == (
        "prediction_invalidation_rewrite_trace"
    )
    assert raised_rewrite_trace["rewrite_state"] == "rewrite_watch"
    assert raised_rewrite_trace["rewrite_priority"] == "medium"
    assert raised_rewrite_trace["rewrite_reason"] == "tighten_primary_watch"
    assert raised_rewrite_trace["evidence_weighting_state"] == (
        "sufficient_evidence"
    )
    assert raised_rewrite_trace["replay_feedback_rewrite_effect"] == (
        "raise_rewrite_sensitivity"
    )
    assert raised_rewrite_trace["invalidation_signal_count"] == 2
    assert raised_rewrite_trace["invalidation_signal_count"] == len(
        raised_output.invalidation_signals
    )
    raised_switch_trace = raised_output.scenario_trace[
        "scenario_switch_trace"
    ]
    assert raised_switch_trace["trace_type"] == (
        "prediction_scenario_switch_trace"
    )
    assert raised_switch_trace["switch_hint"] == "tighten_primary_watch"
    assert raised_switch_trace["switch_action_family"] == "watch"
    assert raised_switch_trace["switch_urgency"] == "medium"
    assert raised_switch_trace["trace_focus_switch_alignment"] == "no_focus"
    assert raised_output.diagnostics["scenario_switch_action_family"] == "watch"
    assert raised_output.diagnostics["scenario_switch_urgency"] == "medium"
    assert raised_output.diagnostics[
        "scenario_switch_trace_focus_alignment"
    ] == "no_focus"
    raised_contract_summary = raised_output.scenario_trace[
        "trace_contract_summary"
    ]
    assert raised_contract_summary["trace_type"] == (
        "prediction_scenario_trace_contract"
    )
    assert raised_contract_summary["contract_status"] == "complete"
    assert raised_contract_summary["trace_count"] == 3
    assert raised_contract_summary["trace_names"] == (
        "evidence_weighting_trace",
        "invalidation_rewrite_trace",
        "scenario_switch_trace",
    )
    assert raised_contract_summary["missing_trace_names"] == ()
    assert raised_contract_summary["advisory_read_only"] is True
    assert raised_contract_summary["execution_surface"] == "none"
    assert raised_contract_summary["runtime_write_surface"] == "none"
    assert raised_output.diagnostics["scenario_trace_contract_status"] == (
        "complete"
    )
    assert raised_output.diagnostics["scenario_trace_contract_trace_count"] == 3
    assert raised_output.diagnostics[
        "scenario_trace_contract_advisory_read_only"
    ] is True
    raised_packet = raised_output.scenario_trace[
        "advisory_output_packet_candidate"
    ]
    assert raised_packet["trace_type"] == (
        "prediction_advisory_output_packet_candidate"
    )
    assert raised_packet["packet_status"] == "candidate_ready"
    assert raised_packet["review_priority"] == "medium"
    assert raised_packet["operator_review_required"] is True
    assert raised_packet["advisory_read_only"] is True
    assert raised_packet["non_executing"] is True
    assert raised_packet["would_send_to_broker"] is False
    assert raised_packet["would_append_ledger"] is False
    assert raised_packet["would_write_runtime_artifact"] is False
    assert raised_packet["execution_surface"] == "none"
    assert raised_packet["runtime_write_surface"] == "none"
    assert raised_output.diagnostics["advisory_output_packet_status"] == (
        "candidate_ready"
    )
    assert raised_output.diagnostics[
        "advisory_output_packet_review_priority"
    ] == "medium"
    assert raised_output.diagnostics[
        "advisory_output_packet_operator_review_required"
    ] is True
    assert raised_output.diagnostics["advisory_output_packet_read_only"] is True
    assert raised_output.diagnostics["advisory_output_packet_non_executing"] is True
    raised_handoff = raised_output.scenario_trace[
        "operator_review_handoff_shape"
    ]
    assert raised_handoff["trace_type"] == (
        "prediction_operator_review_handoff_shape"
    )
    assert raised_handoff["handoff_status"] == "ready_for_operator_review"
    assert raised_handoff["review_priority"] == "medium"
    assert raised_handoff["review_route"] == "watch_path_review"
    assert raised_handoff["manual_review_only"] is True
    assert raised_handoff["advisory_read_only"] is True
    assert raised_handoff["non_executing"] is True
    assert raised_handoff["would_send_to_broker"] is False
    assert raised_handoff["would_append_ledger"] is False
    assert raised_handoff["would_write_runtime_artifact"] is False
    assert raised_handoff["execution_surface"] == "none"
    assert raised_handoff["runtime_write_surface"] == "none"
    assert raised_output.diagnostics["operator_review_handoff_status"] == (
        "ready_for_operator_review"
    )
    assert raised_output.diagnostics["operator_review_handoff_priority"] == (
        "medium"
    )
    assert raised_output.diagnostics["operator_review_handoff_route"] == (
        "watch_path_review"
    )
    assert raised_output.diagnostics["operator_review_handoff_manual_only"] is True
    assert raised_output.diagnostics["operator_review_handoff_read_only"] is True
    assert raised_output.diagnostics["operator_review_handoff_non_executing"] is True
    raised_summary = raised_output.scenario_trace["advisory_packet_summary"]
    assert raised_summary["trace_type"] == "prediction_advisory_packet_summary"
    assert raised_summary["summary_status"] == "ready_for_operator_review"
    assert raised_summary["review_priority"] == "medium"
    assert raised_summary["review_route"] == "watch_path_review"
    assert raised_summary["next_action_label"] == "monitor_watch_path"
    assert raised_summary["next_action_family"] == "monitor"
    assert raised_summary["manual_review_only"] is True
    assert raised_summary["advisory_read_only"] is True
    assert raised_summary["non_executing"] is True
    assert raised_summary["would_send_to_broker"] is False
    assert raised_summary["would_append_ledger"] is False
    assert raised_summary["would_write_runtime_artifact"] is False
    assert raised_summary["execution_surface"] == "none"
    assert raised_summary["runtime_write_surface"] == "none"
    assert raised_output.diagnostics["advisory_packet_summary_status"] == (
        "ready_for_operator_review"
    )
    assert raised_output.diagnostics[
        "advisory_packet_summary_next_action_label"
    ] == "monitor_watch_path"
    assert raised_output.diagnostics[
        "advisory_packet_summary_next_action_family"
    ] == "monitor"
    assert raised_output.diagnostics["advisory_packet_summary_manual_only"] is True
    assert raised_output.diagnostics["advisory_packet_summary_read_only"] is True
    assert raised_output.diagnostics["advisory_packet_summary_non_executing"] is True
    raised_closeout = raised_output.scenario_trace[
        "scenario_core_closeout_candidate"
    ]
    assert raised_closeout["trace_type"] == (
        "prediction_scenario_core_closeout_candidate"
    )
    assert raised_closeout["closeout_status"] == "ready_for_thread_closeout"
    assert raised_closeout["summary_contract_status"] == "complete"
    assert raised_closeout["consolidated_trace_count"] == 7
    assert raised_closeout["source_next_action_label"] == "monitor_watch_path"
    assert raised_closeout["manual_review_only"] is True
    assert raised_closeout["advisory_read_only"] is True
    assert raised_closeout["non_executing"] is True
    assert raised_closeout["would_send_to_broker"] is False
    assert raised_closeout["would_append_ledger"] is False
    assert raised_closeout["would_write_runtime_artifact"] is False
    assert raised_closeout["execution_surface"] == "none"
    assert raised_closeout["runtime_write_surface"] == "none"
    assert raised_output.diagnostics["scenario_core_closeout_status"] == (
        "ready_for_thread_closeout"
    )
    assert raised_output.diagnostics[
        "scenario_core_closeout_summary_contract_status"
    ] == "complete"
    assert raised_output.diagnostics["scenario_core_closeout_trace_count"] == 7
    assert raised_output.diagnostics["scenario_core_closeout_read_only"] is True
    assert raised_output.diagnostics["scenario_core_closeout_non_executing"] is True
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
    assert raised_output.diagnostics["invalidation_rewrite_state"] == "rewrite_watch"
    assert raised_output.diagnostics["invalidation_rewrite_priority"] == "medium"
    assert raised_output.diagnostics[
        "invalidation_rewrite_evidence_weighting_state"
    ] == "sufficient_evidence"
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
    lowered_rewrite_trace = lowered_output.scenario_trace[
        "invalidation_rewrite_trace"
    ]
    assert lowered_rewrite_trace["rewrite_state"] == "rewrite_not_required"
    assert lowered_rewrite_trace["rewrite_priority"] == "normal"
    assert lowered_rewrite_trace["replay_feedback_rewrite_effect"] == (
        "lower_rewrite_sensitivity"
    )
    lowered_switch_trace = lowered_output.scenario_trace[
        "scenario_switch_trace"
    ]
    assert lowered_switch_trace["switch_action_family"] == "hold"
    assert lowered_switch_trace["switch_urgency"] == "normal"
    assert lowered_output.diagnostics["scenario_switch_action_family"] == "hold"
    lowered_contract_summary = lowered_output.scenario_trace[
        "trace_contract_summary"
    ]
    assert lowered_contract_summary["contract_status"] == "complete"
    assert lowered_contract_summary["trace_count"] == 3
    assert lowered_output.diagnostics["scenario_trace_contract_status"] == (
        "complete"
    )
    lowered_packet = lowered_output.scenario_trace[
        "advisory_output_packet_candidate"
    ]
    assert lowered_packet["packet_status"] == "candidate_ready"
    assert lowered_packet["review_priority"] == "normal"
    assert lowered_packet["operator_review_required"] is False
    assert lowered_packet["non_executing"] is True
    assert lowered_output.diagnostics[
        "advisory_output_packet_review_priority"
    ] == "normal"
    assert lowered_output.diagnostics[
        "advisory_output_packet_operator_review_required"
    ] is False
    lowered_handoff = lowered_output.scenario_trace[
        "operator_review_handoff_shape"
    ]
    assert lowered_handoff["handoff_status"] == "optional_operator_review"
    assert lowered_handoff["review_priority"] == "normal"
    assert lowered_handoff["review_route"] == "optional_review"
    assert lowered_handoff["manual_review_only"] is True
    assert lowered_handoff["non_executing"] is True
    assert lowered_output.diagnostics["operator_review_handoff_status"] == (
        "optional_operator_review"
    )
    assert lowered_output.diagnostics["operator_review_handoff_priority"] == (
        "normal"
    )
    assert lowered_output.diagnostics["operator_review_handoff_route"] == (
        "optional_review"
    )
    lowered_summary = lowered_output.scenario_trace["advisory_packet_summary"]
    assert lowered_summary["summary_status"] == "optional_operator_review"
    assert lowered_summary["next_action_label"] == "optional_no_action_review"
    assert lowered_summary["next_action_family"] == "optional"
    assert lowered_summary["non_executing"] is True
    assert lowered_output.diagnostics[
        "advisory_packet_summary_next_action_label"
    ] == "optional_no_action_review"
    lowered_closeout = lowered_output.scenario_trace[
        "scenario_core_closeout_candidate"
    ]
    assert lowered_closeout["closeout_status"] == "ready_for_thread_closeout"
    assert lowered_closeout["summary_contract_status"] == "complete"
    assert lowered_closeout["source_next_action_label"] == (
        "optional_no_action_review"
    )
    assert lowered_closeout["non_executing"] is True
    assert lowered_output.diagnostics["scenario_core_closeout_status"] == (
        "ready_for_thread_closeout"
    )
    assert lowered_output.diagnostics["invalidation_rewrite_state"] == (
        "rewrite_not_required"
    )
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
    transition_rewrite_trace = transition_output.scenario_trace[
        "invalidation_rewrite_trace"
    ]
    assert transition_rewrite_trace["rewrite_state"] == "rewrite_required"
    assert transition_rewrite_trace["rewrite_priority"] == "high"
    assert transition_rewrite_trace["replay_feedback_rewrite_effect"] == "neutral"
    transition_switch_trace = transition_output.scenario_trace[
        "scenario_switch_trace"
    ]
    assert transition_switch_trace["switch_action_family"] == "execute"
    assert transition_switch_trace["switch_urgency"] == "high"
    transition_contract_summary = transition_output.scenario_trace[
        "trace_contract_summary"
    ]
    assert transition_contract_summary["contract_status"] == "complete"
    assert transition_contract_summary["advisory_read_only"] is True
    transition_packet = transition_output.scenario_trace[
        "advisory_output_packet_candidate"
    ]
    assert transition_packet["review_priority"] == "high"
    assert transition_packet["operator_review_required"] is True
    assert transition_packet["would_write_runtime_artifact"] is False
    transition_handoff = transition_output.scenario_trace[
        "operator_review_handoff_shape"
    ]
    assert transition_handoff["review_priority"] == "high"
    assert transition_handoff["review_route"] == "priority_switch_review"
    assert transition_handoff["operator_review_required"] is True
    transition_summary = transition_output.scenario_trace[
        "advisory_packet_summary"
    ]
    assert transition_summary["next_action_label"] == "review_switch_plan"
    assert transition_summary["next_action_family"] == "review_switch"
    assert transition_summary["would_write_runtime_artifact"] is False
    transition_closeout = transition_output.scenario_trace[
        "scenario_core_closeout_candidate"
    ]
    assert transition_closeout["closeout_status"] == "ready_for_thread_closeout"
    assert transition_closeout["source_next_action_label"] == "review_switch_plan"
    assert transition_closeout["would_write_runtime_artifact"] is False

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
    reversal_rewrite_trace = reversal_output.scenario_trace[
        "invalidation_rewrite_trace"
    ]
    assert reversal_rewrite_trace["rewrite_state"] == "rewrite_prepared"
    assert reversal_rewrite_trace["rewrite_priority"] == "high"
    assert reversal_rewrite_trace["trace_focus_rewrite_action"] == (
        "prioritize_switch_reason_review"
    )
    assert reversal_rewrite_trace["trace_focus_material"]["direction"] == (
        "switch_bias"
    )
    reversal_switch_trace = reversal_output.scenario_trace[
        "scenario_switch_trace"
    ]
    assert reversal_switch_trace["switch_hint"] == "prepare_reversal_switch"
    assert reversal_switch_trace["switch_action_family"] == "prepare"
    assert reversal_switch_trace["switch_urgency"] == "high"
    assert reversal_switch_trace["trace_focus_switch_alignment"] == (
        "different_switch_focus"
    )
    assert reversal_switch_trace["trace_focus_material"]["direction"] == (
        "switch_bias"
    )
    assert reversal_output.diagnostics["scenario_switch_action_family"] == (
        "prepare"
    )
    assert reversal_output.diagnostics["scenario_switch_urgency"] == "high"
    assert reversal_output.diagnostics[
        "scenario_switch_trace_focus_alignment"
    ] == "different_switch_focus"
    reversal_contract_summary = reversal_output.scenario_trace[
        "trace_contract_summary"
    ]
    assert reversal_contract_summary["contract_status"] == "complete"
    assert reversal_contract_summary["trace_count"] == 3
    assert reversal_output.diagnostics["scenario_trace_contract_status"] == (
        "complete"
    )
    reversal_packet = reversal_output.scenario_trace[
        "advisory_output_packet_candidate"
    ]
    assert reversal_packet["review_priority"] == "high"
    assert reversal_packet["operator_review_required"] is True
    assert reversal_packet["advisory_read_only"] is True
    assert reversal_packet["would_send_to_broker"] is False
    assert reversal_output.diagnostics[
        "advisory_output_packet_review_priority"
    ] == "high"
    reversal_handoff = reversal_output.scenario_trace[
        "operator_review_handoff_shape"
    ]
    assert reversal_handoff["handoff_status"] == "ready_for_operator_review"
    assert reversal_handoff["review_priority"] == "high"
    assert reversal_handoff["review_route"] == "priority_switch_review"
    assert reversal_handoff["manual_review_only"] is True
    assert reversal_handoff["would_send_to_broker"] is False
    assert reversal_output.diagnostics["operator_review_handoff_route"] == (
        "priority_switch_review"
    )
    reversal_summary = reversal_output.scenario_trace[
        "advisory_packet_summary"
    ]
    assert reversal_summary["summary_status"] == "ready_for_operator_review"
    assert reversal_summary["next_action_label"] == "review_switch_plan"
    assert reversal_summary["next_action_family"] == "review_switch"
    assert reversal_summary["manual_review_only"] is True
    assert reversal_summary["would_send_to_broker"] is False
    assert reversal_output.diagnostics[
        "advisory_packet_summary_next_action_label"
    ] == "review_switch_plan"
    reversal_closeout = reversal_output.scenario_trace[
        "scenario_core_closeout_candidate"
    ]
    assert reversal_closeout["closeout_status"] == "ready_for_thread_closeout"
    assert reversal_closeout["summary_contract_status"] == "complete"
    assert reversal_closeout["source_next_action_label"] == "review_switch_plan"
    assert reversal_closeout["manual_review_only"] is True
    assert reversal_closeout["would_send_to_broker"] is False
    assert reversal_output.diagnostics["scenario_core_closeout_status"] == (
        "ready_for_thread_closeout"
    )
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