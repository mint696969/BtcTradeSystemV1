# path: ./btcts_next/src/btcts/replay/tests/test_replay_report_prediction_summary.py
# desc: Verify replay_report can carry compact prediction evaluation summary additively.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.replay_report import build_replay_report  # noqa: E402


def main() -> int:
    report = build_replay_report(
        name="prediction_summary_in_replay_report",
        source_paths=["D:/dummy/source.jsonl"],
        results=[
            {"kind": "board", "result": {"signal": "watch", "events": []}},
            {"kind": "trade", "microstructure": []},
        ],
        prediction_evaluation_entries=[
            {
                "regime_alignment": "partial",
                "replay_priority": "high",
                "confidence_gap": -0.18,
                "caution_gap": 2,
                "confidence_gap_signal": "overstated_confidence",
                "confidence_bias_hint": "balanced",
                "caution_bias_hint": "balanced",
            }
        ],
    )

    assert report["name"] == "prediction_summary_in_replay_report"
    assert report["result_count"] == 2
    assert report["board_count"] == 1
    assert report["trade_count"] == 1
    assert report["prediction_evaluation_summary"] == {
        "entry_count": 1,
        "matched_count": 0,
        "partial_count": 1,
        "missed_count": 0,
        "high_priority_count": 1,
        "average_confidence_gap": -0.18,
        "average_caution_gap": 2.0,
    }

    empty = build_replay_report(
        name="prediction_summary_in_replay_report_empty",
        source_paths=[],
        results=[],
    )
    assert empty["prediction_evaluation_summary"] is None

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())