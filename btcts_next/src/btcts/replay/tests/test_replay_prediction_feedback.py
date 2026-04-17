# path: ./btcts_next/src/btcts/replay/tests/test_replay_prediction_feedback.py
# desc: Verify replay-side helper bridges replay prediction artifacts into shared replay feedback.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.replay_prediction_feedback import (  # noqa: E402
    build_prediction_replay_feedback_from_artifacts,
)
from btcts.replay.replay_session import ReplaySession  # noqa: E402
from btcts.replay.replay_prediction_feedback import (  # noqa: E402
    build_prediction_replay_feedback_from_session,
)


def main() -> int:
    built = build_prediction_replay_feedback_from_artifacts(
        name="artifact_bridge_test",
        prediction_evaluation_entries=[
            {
                "regime_alignment": "matched",
                "replay_priority": "high",
                "confidence_gap": -0.30,
                "caution_gap": 2,
                "confidence_gap_signal": "overstated_confidence",
                "confidence_bias_hint": "balanced",
                "caution_bias_hint": "balanced",
            },
            {
                "regime_alignment": "partial",
                "replay_priority": "normal",
                "confidence_gap": -0.10,
                "caution_gap": 1,
                "confidence_gap_signal": "balanced",
                "confidence_bias_hint": "balanced",
                "caution_bias_hint": "balanced",
            },
        ],
        prediction_calibration_review={
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
        diagnostics={"caller": "unit_test"},
    )

    assert built["feedback_type"] == "prediction_replay_feedback"
    assert built["source_kind"] == "replay_session_prediction_feedback"
    assert built["review_priority"] == "high"
    assert built["primary_focus"] == "confidence_downside_review"
    assert built["entry_count"] == 2
    assert built["matched_count"] == 1
    assert built["partial_count"] == 1
    assert built["missed_count"] == 0
    assert built["high_priority_count"] == 1
    assert built["average_confidence_gap"] == -0.2
    assert built["average_caution_gap"] == 1.5
    assert built["followup_actions"] == (
        "schedule_replay_review",
        "lower_confidence_weight",
    )
    assert built["diagnostics"]["builder_type"] == "replay_prediction_feedback"
    assert built["diagnostics"]["session_name"] == "artifact_bridge_test"
    assert built["diagnostics"]["caller"] == "unit_test"

    session = ReplaySession(
        name="session_bridge_test",
        source_paths=["D:/dummy/a.jsonl"],
    )
    session.add_prediction_evaluation_entry(
        {
            "regime_alignment": "missed",
            "replay_priority": "high",
            "confidence_gap": -0.25,
            "caution_gap": 2,
            "confidence_gap_signal": "overstated_confidence",
            "confidence_bias_hint": "balanced",
            "caution_bias_hint": "balanced",
        }
    )
    session.add_prediction_calibration_review(
        {
            "review_priority": "high",
            "primary_focus": "confidence_downside_review",
            "confidence_review": "lower_confidence_weight",
            "caution_review": "raise_caution_weight",
            "invalidation_review": "raise_invalidation_sensitivity",
            "followup_actions": ("schedule_replay_review",),
        }
    )

    bridged = build_prediction_replay_feedback_from_session(session)
    assert bridged is not None
    assert bridged["entry_count"] == 1
    assert bridged["missed_count"] == 1
    assert bridged["review_priority"] == "high"
    assert bridged["primary_focus"] == "confidence_downside_review"
    assert bridged["diagnostics"]["prediction_evaluation_entry_count"] == 1
    assert bridged["diagnostics"]["prediction_calibration_review_count"] == 1

    empty_session = ReplaySession(name="empty", source_paths=[])
    assert build_prediction_replay_feedback_from_session(empty_session) is None

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())