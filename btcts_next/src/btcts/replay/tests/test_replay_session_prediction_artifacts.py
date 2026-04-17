# path: ./btcts_next/src/btcts/replay/tests/test_replay_session_prediction_artifacts.py
# desc: Verify ReplaySession can hold additive prediction evaluation artifacts without affecting base output counters.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.replay_session import ReplaySession  # noqa: E402


def main() -> int:
    session = ReplaySession(
        name="prediction_artifact_session",
        source_paths=["D:/dummy/replay_a.jsonl"],
    )

    session.add(
        {
            "signal": "watch",
            "events": [
                {"event_name": "support_candidate"},
                {"event_name": "persistence_candidate"},
            ],
        }
    )
    session.add({"signal": None, "events": []})

    session.add_prediction_evaluation_entry(
        {
            "entry_type": "prediction_evaluation_entry",
            "regime_alignment": "partial",
        }
    )
    session.add_prediction_calibration_review(
        {
            "review_type": "prediction_calibration_review",
            "review_priority": "high",
        }
    )

    summary = session.summary()
    assert summary["name"] == "prediction_artifact_session"
    assert summary["source_paths"] == ["D:/dummy/replay_a.jsonl"]
    assert summary["processed_count"] == 2
    assert summary["signal_count"] == 1
    assert summary["event_count"] == 2
    assert summary["prediction_evaluation_entry_count"] == 1
    assert summary["prediction_calibration_review_count"] == 1

    assert len(session.output) == 2
    assert len(session.prediction_evaluation_entries) == 1
    assert len(session.prediction_calibration_reviews) == 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())