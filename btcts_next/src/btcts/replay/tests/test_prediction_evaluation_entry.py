# path: ./btcts_next/src/btcts/replay/tests/test_prediction_evaluation_entry.py
# desc: Verify replay-side prediction evaluation entry stays thin and calibration-aware.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    MarketSummaryBuildInput,
    PredictionCalibrationBuildInput,
    PredictionScenarioBuildInput,
    PredictionSystemBuildInput,
    build_market_summary,
    build_prediction_calibration_hint,
    build_prediction_scenario_output,
    build_prediction_system_input,
)
from btcts.replay.prediction_evaluation_entry import (  # noqa: E402
    PredictionEvaluationBuildInput,
    build_prediction_evaluation_entry,
)
from btcts.replay.prediction_realized_outcome import (  # noqa: E402
    PredictionRealizedOutcomeBuildInput,
    build_prediction_realized_outcome,
)


def main() -> int:
    market_summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-17T04:20:00Z",
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
        )
    )
    scenario_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(
            prediction_input=prediction_input,
        )
    )
    calibration_hint = build_prediction_calibration_hint(
        PredictionCalibrationBuildInput(
            prediction_input=prediction_input,
            scenario_output=scenario_output,
        )
    )

    realized_outcome = build_prediction_realized_outcome(
        PredictionRealizedOutcomeBuildInput(
            market_uid="bitflyer.spot.BTC_JPY",
            event_ts="2026-04-17T04:20:00Z",
            realized_regime_state="transition",
            realized_confidence=0.28,
            realized_caution_level="high",
            realized_horizon="10m",
            realized_return_bp=-18.0,
            realized_max_adverse_bp=-22.0,
            realized_max_favorable_bp=6.0,
        )
    )

    entry = build_prediction_evaluation_entry(
        PredictionEvaluationBuildInput(
            scenario_output=scenario_output,
            calibration_hint=calibration_hint,
            realized_outcome=realized_outcome,
            diagnostics={"caller": "unit_test"},
        )
    )

    assert entry["entry_type"] == "prediction_evaluation_entry"
    assert entry["entry_version"] == "phase3.v1alpha1"
    assert entry["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert entry["event_ts"] == "2026-04-17T04:20:00Z"
    assert entry["predicted_regime_state"] == "reversal_watch"
    assert entry["realized_regime_state"] == "transition"
    assert entry["realized_horizon"] == "10m"
    assert entry["regime_alignment"] == "partial"
    assert entry["predicted_confidence"] == 0.46
    assert entry["realized_confidence"] == 0.28
    assert entry["realized_return_bp"] == -18.0
    assert entry["realized_max_adverse_bp"] == -22.0
    assert entry["realized_max_favorable_bp"] == 6.0
    assert entry["confidence_gap"] == -0.18
    assert entry["confidence_gap_signal"] == "overstated_confidence"
    assert entry["predicted_caution_level"] == "low"
    assert entry["predicted_invalidation_state"] == "caution_increase"
    assert entry["predicted_scenario_switch_hint"] == "watch_reversal_path"
    predicted_trace = entry["predicted_scenario_trace"]
    assert predicted_trace["trace_type"] == "prediction_scenario_trace"
    assert predicted_trace["trace_version"] == "phase3.v1alpha1"
    assert predicted_trace["regime_decision"] == (
        "transition_sign:weakening_continuation"
    )
    assert predicted_trace["hypothesis_health_path"] == "caution_increase"
    assert predicted_trace["caution_path"] == "low"
    assert predicted_trace["invalidation_path"] == "caution_increase"
    assert predicted_trace["switch_reason"] == "watch_reversal_path"

    replay_feedback_effect = predicted_trace["replay_feedback_effect"]
    assert replay_feedback_effect["caution_adjustment"] == 0
    assert replay_feedback_effect["caution_policy"] == "none"
    assert replay_feedback_effect["invalidation_adjustment"] == 0
    assert replay_feedback_effect["invalidation_policy"] == "none"
    assert replay_feedback_effect["invalidation_score"] == 0.0
    assert replay_feedback_effect["scenario_trace_focus"] == "unknown"
    assert replay_feedback_effect["trace_focus_material"] == {
        "focus": "unknown",
        "kind": "none",
        "direction": "neutral",
        "strength": 0.0,
    }
    assert entry["realized_caution_level"] == "high"
    assert entry["caution_gap"] == 2
    assert entry["confidence_bias_hint"] == "balanced"
    assert entry["caution_bias_hint"] == "balanced"
    assert entry["invalidation_sensitivity"] == "medium"
    assert entry["replay_priority"] == "high"
    assert entry["diagnostics"]["builder_type"] == "prediction_evaluation_entry"
    assert entry["diagnostics"]["scenario_output_present"] is True
    assert entry["diagnostics"]["calibration_hint_present"] is True
    assert entry["diagnostics"]["realized_outcome_present"] is True
    assert entry["diagnostics"]["caller"] == "unit_test"

    empty = build_prediction_evaluation_entry(PredictionEvaluationBuildInput())
    assert empty["entry_type"] == "prediction_evaluation_entry"
    assert empty["market_uid"] is None
    assert empty["event_ts"] is None
    assert empty["predicted_regime_state"] is None
    assert empty["realized_regime_state"] is None
    assert empty["realized_return_bp"] is None
    assert empty["realized_max_adverse_bp"] is None
    assert empty["realized_max_favorable_bp"] is None
    assert empty["regime_alignment"] == "unknown"
    assert empty["confidence_gap"] is None
    assert empty["confidence_gap_signal"] == "unknown"
    assert empty["caution_gap"] is None
    assert empty["predicted_invalidation_state"] is None
    assert empty["predicted_scenario_switch_hint"] is None
    assert empty["predicted_scenario_trace"] == {}
    assert empty["confidence_bias_hint"] == "unknown"
    assert empty["caution_bias_hint"] == "unknown"
    assert empty["invalidation_sensitivity"] == "unknown"
    assert empty["replay_priority"] == "normal"
    assert empty["diagnostics"]["builder_type"] == "prediction_evaluation_entry"
    assert empty["diagnostics"]["scenario_output_present"] is False
    assert empty["diagnostics"]["calibration_hint_present"] is False
    assert empty["diagnostics"]["realized_outcome_present"] is False

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())