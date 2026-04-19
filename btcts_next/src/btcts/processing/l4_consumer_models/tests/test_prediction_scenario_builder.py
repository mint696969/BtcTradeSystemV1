# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder.py
# desc: Verify PredictionScenarioOutput skeleton builder stays wording-free and prediction-system-input based.

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


def main() -> int:
    market_summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-17T03:20:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": "allow_structural_use",
                "interpretation_reason": "ok",
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
                "semantic_usage_contract_rows": [
                    {
                        "event_family": "wall",
                        "usage_grade": "strong",
                        "contract_source": "l3_event_usage_policy",
                        "meaning_version": "l3_event_usage_policy.v1alpha1",
                        "interpretation_bucket": "allow_structural_use",
                    }
                ],
                "orderbook_semantics_summary": {
                    "summary_slots_present": ["near_wall", "support", "persistence"],
                    "active_event_count": 1,
                    "active_event_names": ["support_candidate"],
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": True,
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 3.0,
                "preferred_row_freshness": "LIVE",
            },
        )
    )

    prediction_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=market_summary,
            liquidity_board_history={
                "history_window_sec": 90,
                "wall_persistence_bias": "bid_support",
            },
            regime_turning_point={
                "transition_sign": "weakening_continuation",
                "turning_point_risk": "medium",
            },
            replay_feedback=build_prediction_replay_feedback(
                PredictionReplayFeedbackBuildInput(
                    calibration_review={
                        "review_priority": "high",
                        "primary_focus": "confidence_downside_review",
                        "confidence_review": "lower_confidence_weight",
                        "caution_review": "raise_caution_weight",
                    },
                    evaluation_report={
                        "entry_count": 3,
                        "average_confidence_gap": -0.18,
                        "average_caution_gap": 1.0,
                    },
                )
            ),
        )
    )

    scenario_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(
            prediction_input=prediction_input,
            diagnostics={"caller": "unit_test"},
        )
    )

    assert scenario_output.prediction_type == "prediction_scenario_output"
    assert scenario_output.prediction_version == "phase3.v1alpha1"
    assert scenario_output.source_kind == "prediction_system_input"
    assert scenario_output.market_uid == "bitflyer.spot.BTC_JPY"
    assert scenario_output.event_ts == "2026-04-17T03:20:00Z"
    assert scenario_output.freshness == "LIVE"
    assert scenario_output.is_stale is False

    assert scenario_output.current_regime_state == "reversal_watch"
    assert scenario_output.current_hypothesis_health == "caution_increase"
    assert round(scenario_output.current_confidence, 2) == 0.28
    assert scenario_output.current_caution_level == "medium"

    assert len(scenario_output.outlooks) == 3
    assert scenario_output.outlooks[0].horizon == "5m"
    assert scenario_output.outlooks[0].regime_bias == "reversal_watch"
    assert scenario_output.outlooks[0].continuation_likelihood == "medium"
    assert scenario_output.outlooks[0].reversal_likelihood == "medium"
    assert scenario_output.outlooks[0].turning_point_risk == "medium"
    assert round(scenario_output.outlooks[0].confidence, 2) == 0.28
    assert round(scenario_output.outlooks[1].confidence, 2) == 0.20
    assert round(scenario_output.outlooks[2].confidence, 2) == 0.12
    assert scenario_output.outlooks[0].caution_level == "medium"
    assert scenario_output.outlooks[1].caution_level == "medium"
    assert scenario_output.outlooks[2].caution_level == "medium"

    assert scenario_output.invalidation_state == "caution_increase"
    assert scenario_output.invalidation_signals == (
        "transition_sign:weakening_continuation",
        "turning_point_risk:medium",
    )
    assert scenario_output.scenario_switch_hint == "watch_reversal_path"
    assert scenario_output.scenario_trace["trace_type"] == "prediction_scenario_trace"
    assert scenario_output.scenario_trace["trace_version"] == "phase3.v1alpha1"
    assert scenario_output.scenario_trace["regime_decision"] == (
        "transition_sign:weakening_continuation"
    )
    assert scenario_output.scenario_trace["hypothesis_health_path"] == "caution_increase"
    assert scenario_output.scenario_trace["caution_path"] == "medium"
    assert scenario_output.scenario_trace["invalidation_path"] == "caution_increase"
    assert scenario_output.scenario_trace["switch_reason"] == "watch_reversal_path"
    replay_feedback_effect = scenario_output.scenario_trace["replay_feedback_effect"]
    assert replay_feedback_effect["caution_adjustment"] == 1
    assert replay_feedback_effect["caution_policy"] == "raise_once_high_priority"
    assert replay_feedback_effect["invalidation_adjustment"] == 0
    assert replay_feedback_effect["invalidation_policy"] == "none"
    assert replay_feedback_effect["invalidation_score"] == 0.0
    assert replay_feedback_effect["scenario_trace_focus"] == "unknown"
    assert replay_feedback_effect["trace_focus_material"]["focus"] == "unknown"
    assert replay_feedback_effect["trace_focus_material"]["kind"] == "none"
    assert replay_feedback_effect["trace_focus_material"]["direction"] == "neutral"
    assert replay_feedback_effect["trace_focus_material"]["strength"] == 0.0

    assert scenario_output.evidence["market_summary_present"] is True
    assert scenario_output.evidence["health_digest_present"] is False
    assert scenario_output.evidence["liquidity_board_history_present"] is True
    assert scenario_output.evidence["regime_turning_point_present"] is True
    assert scenario_output.evidence["replay_feedback_present"] is True
    assert scenario_output.evidence["replay_feedback_summary"] == {
        "review_priority": "high",
        "primary_focus": "confidence_downside_review",
        "invalidation_review": "unknown",
        "scenario_trace_focus": "unknown",
        "entry_count": 3,
        "missed_count": 0,
        "high_priority_count": 0,
        "average_confidence_gap": -0.18,
        "average_caution_gap": 1.0,
    }
    assert scenario_output.evidence["summary_interpretation_bucket"] == "allow_structural_use"
    assert scenario_output.evidence["summary_trust_state"] == "trusted"
    assert scenario_output.evidence["transition_sign"] == "weakening_continuation"
    assert scenario_output.evidence["turning_point_risk"] == "medium"
    assert scenario_output.evidence["evidence_trace_summary"] == {
        "active_family_count": 3,
        "missing_family_count": 0,
        "caution_flag_count": 0,
        "active_families": (
            "market_summary_anchor",
            "liquidity_board_history",
            "regime_turning_point",
        ),
        "missing_families": (),
        "caution_flags": (),
        "market_summary_anchor_present": True,
    }

    assert scenario_output.evidence_trace == prediction_input.evidence_trace
    assert scenario_output.diagnostics["builder_type"] == "prediction_scenario_output"
    assert scenario_output.diagnostics["requested_horizons_count"] == 3
    assert scenario_output.diagnostics["active_family_count"] == 3
    assert scenario_output.diagnostics["missing_family_count"] == 0
    assert scenario_output.diagnostics["caution_flag_count"] == 0
    assert scenario_output.diagnostics["replay_feedback_present"] is True
    assert scenario_output.diagnostics["replay_feedback_confidence_adjustment"] == -0.11
    assert scenario_output.diagnostics["replay_feedback_caution_adjustment"] == 1
    assert scenario_output.diagnostics["replay_feedback_caution_adjustment_policy"] == (
        "raise_once_high_priority"
    )
    assert scenario_output.diagnostics["replay_feedback_invalidation_adjustment"] == 0
    assert scenario_output.diagnostics["replay_feedback_invalidation_adjustment_policy"] == (
        "none"
    )
    assert scenario_output.diagnostics["replay_feedback_invalidation_score"] == 0.0
    assert scenario_output.diagnostics["replay_feedback_scenario_trace_focus"] == "unknown"
    assert scenario_output.diagnostics["replay_feedback_trace_focus_kind"] == "none"
    assert scenario_output.diagnostics["replay_feedback_trace_focus_direction"] == "neutral"
    assert scenario_output.diagnostics["replay_feedback_trace_focus_strength"] == 0.0
    assert scenario_output.diagnostics["caller"] == "unit_test"

    blocked = build_prediction_scenario_output(PredictionScenarioBuildInput())
    assert blocked.market_uid is None
    assert blocked.event_ts is None
    assert blocked.freshness == "UNKNOWN"
    assert blocked.is_stale is None
    assert blocked.current_regime_state == "no_trade"
    assert blocked.current_hypothesis_health == "scenario_switch_required"
    assert blocked.current_confidence == 0.0
    assert blocked.current_caution_level == "blocked"
    assert blocked.outlooks == ()
    assert blocked.invalidation_state == "scenario_switch_required"
    assert blocked.invalidation_signals == ("prediction_input_absent",)
    assert blocked.scenario_switch_hint == "maintain_no_trade"
    assert blocked.evidence["market_summary_present"] is False
    assert blocked.evidence["replay_feedback_present"] is False
    assert blocked.evidence["replay_feedback_summary"] is None
    assert blocked.evidence["evidence_trace_summary"] == {
        "active_family_count": 0,
        "missing_family_count": 0,
        "caution_flag_count": 0,
        "active_families": (),
        "missing_families": (),
        "caution_flags": (),
        "market_summary_anchor_present": False,
    }
    assert blocked.diagnostics["builder_type"] == "prediction_scenario_output"
    assert blocked.diagnostics["active_family_count"] == 0
    assert blocked.diagnostics["missing_family_count"] == 0
    assert blocked.diagnostics["caution_flag_count"] == 0

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())