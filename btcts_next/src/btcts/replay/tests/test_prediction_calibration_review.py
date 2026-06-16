# path: ./btcts_next/src/btcts/replay/tests/test_prediction_calibration_review.py
# desc: Verify prediction calibration review stays compact and review-oriented.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    PredictionCalibrationHint,
)
from btcts.replay.prediction_calibration_review import (  # noqa: E402
    PredictionCalibrationReviewBuildInput,
    build_prediction_calibration_review,
)


def main() -> int:
    review = build_prediction_calibration_review(
        PredictionCalibrationReviewBuildInput(
            calibration_hint=PredictionCalibrationHint(
                confidence_bias="slightly_overstated",
                caution_bias="understated",
                invalidation_sensitivity="slow",
                replay_priority="high",
            ),
            evaluation_report={
                "entry_count": 3,
                "missed_count": 1,
                "partial_count": 1,
                "high_priority_count": 2,
                "average_confidence_gap": -0.18,
                "average_caution_gap": 1.0,
                "scenario_trace_regime_decision_counts": {
                    "transition_sign:weakening_continuation": 2,
                    "stable_continuation": 1,
                },
                "scenario_trace_switch_reason_counts": {
                    "watch_reversal_path": 2,
                    "hold_primary": 1,
                },
            },
            diagnostics={"caller": "unit_test"},
        )
    )

    assert review["review_type"] == "prediction_calibration_review"
    assert review["review_version"] == "phase3.v1alpha1"
    assert review["review_priority"] == "high"
    assert review["primary_focus"] == "confidence_downside_review"
    assert review["confidence_review"] == "lower_confidence_weight"
    assert review["caution_review"] == "raise_caution_weight"
    assert review["invalidation_review"] == "raise_invalidation_sensitivity"
    assert review["scenario_trace_focus"] == "switch_reason:watch_reversal_path"
    assert review["followup_actions"] == (
        "schedule_replay_review",
        "confidence_downside_review",
        "lower_confidence_weight",
        "raise_caution_weight",
        "raise_invalidation_sensitivity",
        "trace_focus:switch_reason:watch_reversal_path",
    )
    assert review["diagnostics"]["builder_type"] == "prediction_calibration_review"
    assert review["diagnostics"]["calibration_hint_present"] is True
    assert review["diagnostics"]["evaluation_report_present"] is True
    assert review["diagnostics"]["report_entry_count"] == 3
    assert review["diagnostics"]["dominant_trace_regime_decision"] == (
        "transition_sign:weakening_continuation"
    )
    assert review["diagnostics"]["dominant_trace_switch_reason"] == (
        "watch_reversal_path"
    )
    assert review["diagnostics"]["caller"] == "unit_test"

    stable = build_prediction_calibration_review(
        PredictionCalibrationReviewBuildInput(
            evaluation_report={
                "entry_count": 2,
                "missed_count": 0,
                "partial_count": 0,
                "high_priority_count": 0,
                "average_confidence_gap": 0.02,
                "average_caution_gap": 0.0,
                "scenario_trace_regime_decision_counts": {
                    "stable_continuation": 2,
                },
                "scenario_trace_switch_reason_counts": {
                    "hold_primary": 2,
                },
            },
        )
    )

    assert stable["review_priority"] == "normal"
    assert stable["primary_focus"] == "stability_review"
    assert stable["confidence_review"] == "keep_confidence_weight"
    assert stable["caution_review"] == "keep_caution_weight"
    assert stable["invalidation_review"] == "keep_current_invalidation"
    assert stable["scenario_trace_focus"] == "none"
    assert stable["followup_actions"] == ("keep_current_course",)
    assert stable["diagnostics"]["dominant_trace_regime_decision"] == (
        "stable_continuation"
    )
    assert stable["diagnostics"]["dominant_trace_switch_reason"] == "hold_primary"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())