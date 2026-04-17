# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_replay_feedback_builder.py
# desc: Verify replay calibration feedback can be normalized into a shared Scenario Core input lane artifact.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    PredictionReplayFeedbackBuildInput,
    build_prediction_replay_feedback,
)


def main() -> int:
    built = build_prediction_replay_feedback(
        PredictionReplayFeedbackBuildInput(
            calibration_review={
                "review_priority": "high",
                "primary_focus": "confidence_downside_review",
                "confidence_review": "lower_confidence_weight",
                "caution_review": "raise_caution_weight",
                "invalidation_review": "raise_invalidation_sensitivity",
                "followup_actions": (
                    "schedule_replay_review",
                    "lower_confidence_weight",
                ),
            },
            evaluation_report={
                "entry_count": 3,
                "matched_count": 1,
                "partial_count": 1,
                "missed_count": 1,
                "high_priority_count": 2,
                "average_confidence_gap": -0.18,
                "average_caution_gap": 1.0,
            },
            diagnostics={"caller": "unit_test"},
        )
    )

    assert built["feedback_type"] == "prediction_replay_feedback"
    assert built["feedback_version"] == "phase3.v1alpha1"
    assert built["source_kind"] == "replay_prediction_calibration"
    assert built["review_priority"] == "high"
    assert built["primary_focus"] == "confidence_downside_review"
    assert built["confidence_review"] == "lower_confidence_weight"
    assert built["caution_review"] == "raise_caution_weight"
    assert built["invalidation_review"] == "raise_invalidation_sensitivity"
    assert built["followup_actions"] == (
        "schedule_replay_review",
        "lower_confidence_weight",
    )
    assert built["entry_count"] == 3
    assert built["matched_count"] == 1
    assert built["partial_count"] == 1
    assert built["missed_count"] == 1
    assert built["high_priority_count"] == 2
    assert built["average_confidence_gap"] == -0.18
    assert built["average_caution_gap"] == 1.0
    assert built["diagnostics"]["builder_type"] == "prediction_replay_feedback"
    assert built["diagnostics"]["calibration_review_present"] is True
    assert built["diagnostics"]["evaluation_report_present"] is True
    assert built["diagnostics"]["caller"] == "unit_test"

    empty = build_prediction_replay_feedback(
        PredictionReplayFeedbackBuildInput()
    )
    assert empty["review_priority"] == "normal"
    assert empty["primary_focus"] == "unknown"
    assert empty["entry_count"] == 0
    assert empty["average_confidence_gap"] is None
    assert empty["followup_actions"] == ()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())