# path: ./btcts_next/src/btcts/replay/tests/test_prediction_evaluation_report.py
# desc: Verify replay-side prediction evaluation report stays compact and aggregation-first.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.prediction_evaluation_report import (  # noqa: E402
    build_prediction_evaluation_report,
)


def main() -> int:
    report = build_prediction_evaluation_report(
        "prediction_eval_unit",
        [
            {
                "regime_alignment": "matched",
                "replay_priority": "normal",
                "confidence_gap": 0.10,
                "caution_gap": 0,
                "confidence_gap_signal": "balanced",
                "confidence_bias_hint": "balanced",
                "caution_bias_hint": "balanced",
                "predicted_scenario_trace": {
                    "regime_decision": "stable_continuation",
                    "switch_reason": "hold_primary",
                },
            },
            {
                "regime_alignment": "partial",
                "replay_priority": "high",
                "confidence_gap": -0.20,
                "caution_gap": 2,
                "confidence_gap_signal": "overstated_confidence",
                "confidence_bias_hint": "slightly_overstated",
                "caution_bias_hint": "understated",
                "predicted_scenario_trace": {
                    "regime_decision": "weakening_continuation",
                    "switch_reason": "watch_reversal_path",
                },
            },
            {
                "regime_alignment": "missed",
                "replay_priority": "high",
                "confidence_gap": 0.25,
                "caution_gap": -1,
                "confidence_gap_signal": "understated_confidence",
                "confidence_bias_hint": "understated",
                "caution_bias_hint": "balanced",
                "predicted_scenario_trace": {
                    "regime_decision": "weakening_continuation",
                    "switch_reason": "watch_reversal_path",
                },
            },
        ],
    )

    assert report["name"] == "prediction_eval_unit"
    assert report["entry_type"] == "prediction_evaluation_report"
    assert report["entry_version"] == "phase3.v1alpha1"
    assert report["entry_count"] == 3
    assert report["matched_count"] == 1
    assert report["partial_count"] == 1
    assert report["missed_count"] == 1
    assert report["high_priority_count"] == 2
    assert report["average_confidence_gap"] == 0.05
    assert report["average_caution_gap"] == 0.33
    assert report["regime_alignment_counts"] == {
        "matched": 1,
        "missed": 1,
        "partial": 1,
    }
    assert report["replay_priority_counts"] == {
        "high": 2,
        "normal": 1,
    }
    assert report["confidence_gap_signal_counts"] == {
        "balanced": 1,
        "overstated_confidence": 1,
        "understated_confidence": 1,
    }
    assert report["confidence_bias_hint_counts"] == {
        "balanced": 1,
        "slightly_overstated": 1,
        "understated": 1,
    }
    assert report["caution_bias_hint_counts"] == {
        "balanced": 2,
        "understated": 1,
    }
    assert report["scenario_trace_regime_decision_counts"] == {
        "stable_continuation": 1,
        "weakening_continuation": 2,
    }
    assert report["scenario_trace_switch_reason_counts"] == {
        "hold_primary": 1,
        "watch_reversal_path": 2,
    }

    empty = build_prediction_evaluation_report("empty_eval", [])
    assert empty["name"] == "empty_eval"
    assert empty["entry_count"] == 0
    assert empty["matched_count"] == 0
    assert empty["partial_count"] == 0
    assert empty["missed_count"] == 0
    assert empty["high_priority_count"] == 0
    assert empty["average_confidence_gap"] is None
    assert empty["average_caution_gap"] is None
    assert empty["regime_alignment_counts"] == {}
    assert empty["replay_priority_counts"] == {}
    assert empty["confidence_gap_signal_counts"] == {}
    assert empty["confidence_bias_hint_counts"] == {}
    assert empty["caution_bias_hint_counts"] == {}
    assert empty["scenario_trace_regime_decision_counts"] == {}
    assert empty["scenario_trace_switch_reason_counts"] == {}

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())