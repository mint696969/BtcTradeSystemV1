# path: ./btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py
# desc: Verify replay export can add prediction evaluation aggregate artifacts without disturbing base replay export.

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.replay_export import export_replay_results  # noqa: E402


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_dir:
        exported = export_replay_results(
            name="prediction_eval_export",
            source_paths=[Path("D:/dummy/source_a.jsonl")],
            results=[
                {"kind": "board", "result": {"signal": "watch", "events": []}},
                {"kind": "trade", "microstructure": []},
            ],
            out_root=Path(tmp_dir),
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

        assert exported["session_dir"]
        assert exported["results_path"]
        assert exported["report_path"]
        assert exported["manifest_path"]
        assert exported["prediction_evaluation_report_path"]

        manifest = _read_json(exported["manifest_path"])
        assert manifest["name"] == "prediction_eval_export"
        assert manifest["result_count"] == 2
        assert manifest["prediction_evaluation_entry_count"] == 1
        assert manifest["prediction_evaluation_report_path"]

        prediction_report = _read_json(exported["prediction_evaluation_report_path"])
        assert prediction_report["name"] == "prediction_eval_export_prediction_evaluation"
        assert prediction_report["entry_type"] == "prediction_evaluation_report"
        assert prediction_report["entry_count"] == 1
        assert prediction_report["partial_count"] == 1
        assert prediction_report["high_priority_count"] == 1
        assert prediction_report["average_confidence_gap"] == -0.18
        assert prediction_report["average_caution_gap"] == 2.0

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

    with tempfile.TemporaryDirectory() as tmp_dir:
        exported = export_replay_results(
            name="prediction_eval_export_empty",
            source_paths=[Path("D:/dummy/source_b.jsonl")],
            results=[],
            out_root=Path(tmp_dir),
        )

        manifest = _read_json(exported["manifest_path"])
        assert manifest["prediction_evaluation_entry_count"] == 0
        assert manifest["prediction_evaluation_report_path"] is None
        assert exported["prediction_evaluation_report_path"] is None

        replay_report = _read_json(exported["report_path"])
        assert replay_report["prediction_evaluation_summary"] is None

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())