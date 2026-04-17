# path: ./btcts_next/src/btcts/replay/tests/test_replay_session_export.py
# desc: Verify ReplaySession can be exported through replay_export without extra caller-side plumbing.

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.replay_export import export_replay_session  # noqa: E402
from btcts.replay.replay_session import ReplaySession  # noqa: E402


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    session = ReplaySession(
        name="prediction_session_export",
        source_paths=["D:/dummy/replay_source.jsonl"],
    )
    session.add({"kind": "board", "result": {"signal": "watch", "events": []}})
    session.add_prediction_evaluation_entry(
        {
            "regime_alignment": "partial",
            "replay_priority": "high",
            "confidence_gap": -0.18,
            "caution_gap": 2,
            "confidence_gap_signal": "overstated_confidence",
            "confidence_bias_hint": "balanced",
            "caution_bias_hint": "balanced",
        }
    )
    session.add_prediction_calibration_review(
        {
            "review_type": "prediction_calibration_review",
            "review_priority": "high",
            "primary_focus": "confidence_downside_review",
            "confidence_review": "lower_confidence_weight",
            "caution_review": "raise_caution_weight",
            "invalidation_review": "raise_invalidation_sensitivity",
        }
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        exported = export_replay_session(
            session=session,
            out_root=Path(tmp_dir),
        )

        manifest = _read_json(exported["manifest_path"])
        assert manifest["name"] == "prediction_session_export"
        assert manifest["result_count"] == 1
        assert manifest["prediction_evaluation_entry_count"] == 1
        assert manifest["prediction_evaluation_report_path"]
        assert manifest["prediction_calibration_review_count"] == 1
        assert manifest["prediction_calibration_review_path"]

        replay_report = _read_json(exported["report_path"])
        assert replay_report["prediction_evaluation_summary"] == {
            "entry_count": 1,
            "matched_count": 0,
            "partial_count": 1,
            "missed_count": 0,
            "high_priority_count": 1,
            "average_confidence_gap": -0.18,
            "average_caution_gap": 2.0,
        }
        assert replay_report["prediction_calibration_review_summary"] == {
            "review_count": 1,
            "latest_review_priority": "high",
            "latest_primary_focus": "confidence_downside_review",
            "latest_confidence_review": "lower_confidence_weight",
            "latest_caution_review": "raise_caution_weight",
            "latest_invalidation_review": "raise_invalidation_sensitivity",
        }

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())