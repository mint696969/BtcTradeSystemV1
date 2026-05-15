# path: ./btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py
# desc: Verify run_and_export_replay carries prediction evaluation artifacts through session export actual path.

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.replay.replay_runner as replay_runner  # noqa: E402


class _DummySource:
    def __init__(self, paths):
        self.paths = paths

    def load(self):
        return [
            {"seq": 1},
            {"seq": 2},
        ]


class _DummyEngine:
    def __init__(self, records, clock=None):
        self._records = list(records)
        self._index = 0

    def has_next(self):
        return self._index < len(self._records)

    def next_event(self):
        if not self.has_next():
            return None
        item = self._records[self._index]
        self._index += 1
        return item


class _DummyPipeline:
    def __init__(self, exchange_profile=None):
        self.exchange_profile = exchange_profile

    def process_record(self, record):
        seq = int(record.get("seq") or 0)

        if seq == 1:
            return {
                "record_id": "row_1",
                "record_type": "market.orderbook.snapshot",
                "event_ts": "2026-04-17T04:20:00Z",
                "kind": "board",
                "result": {
                    "signal": "watch",
                    "events": [
                        {
                            "event_name": "support_candidate",
                            "event_family": "support_resistance",
                            "usage_grade": "strong",
                            "interpretation_bucket": "allow_structural_use",
                        }
                    ],
                },
                "signal": {"state": "watch"},
                "events": [{"event_name": "support_candidate"}],
                "best_bid": 100.0,
                "best_ask": 102.0,
            }

        if seq == 2:
            return {
                "record_id": "row_2",
                "record_type": "market.orderbook.diff",
                "event_ts": "2026-04-17T04:25:00Z",
                "kind": "board",
                "result": {
                    "signal": "watch",
                    "events": [
                        {
                            "event_name": "resistance_candidate",
                            "event_family": "support_resistance",
                            "usage_grade": "watch",
                            "interpretation_bucket": "observe_only",
                        }
                    ],
                },
                "signal": {"state": "watch"},
                "events": [{"event_name": "resistance_candidate"}],
                "best_bid": 101.0,
                "best_ask": 103.0,
            }

        return None


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    original_source = replay_runner.JsonlReplaySource
    original_engine = replay_runner.ReplayEngine
    original_pipeline = replay_runner.ReplayPipeline
    original_profile_factory = replay_runner.create_exchange_profile

    try:
        replay_runner.JsonlReplaySource = _DummySource
        replay_runner.ReplayEngine = _DummyEngine
        replay_runner.ReplayPipeline = _DummyPipeline
        replay_runner.create_exchange_profile = lambda profile_name: {
            "profile_name": profile_name
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            session, artifacts = replay_runner.run_and_export_replay(
                name="runner_export_prediction_artifacts",
                paths=[Path("D:/dummy/replay_source.jsonl")],
                out_root=Path(tmp_dir),
            )

            summary = session.summary()
            assert summary["processed_count"] == 2
            assert summary["prediction_evaluation_entry_count"] == 1
            assert summary["prediction_calibration_review_count"] == 1

            assert artifacts["prediction_evaluation_report_path"]
            assert artifacts["prediction_calibration_review_path"]
            manifest = _read_json(artifacts["manifest_path"])
            replay_report = _read_json(artifacts["report_path"])
            prediction_report = _read_json(artifacts["prediction_evaluation_report_path"])
            calibration_review = _read_json(artifacts["prediction_calibration_review_path"])

            assert manifest["prediction_evaluation_entry_count"] == 1
            assert manifest["prediction_evaluation_report_path"]
            assert manifest["prediction_calibration_review_count"] == 1
            assert manifest["prediction_calibration_review_path"]

            assert replay_report["signal_count"] == 2
            assert replay_report["event_name_counts"] == {
                "resistance_candidate": 1,
                "support_candidate": 1,
            }
            assert replay_report["prediction_evaluation_summary"] is not None
            assert replay_report["prediction_evaluation_summary"]["entry_count"] == 1
            assert replay_report["prediction_calibration_review_summary"] is not None
            assert replay_report["prediction_calibration_review_summary"]["review_count"] == 1

            assert prediction_report["entry_type"] == "prediction_evaluation_report"
            assert prediction_report["entry_count"] == 1
            assert calibration_review["review_type"] == "prediction_calibration_review"
    finally:
        replay_runner.JsonlReplaySource = original_source
        replay_runner.ReplayEngine = original_engine
        replay_runner.ReplayPipeline = original_pipeline
        replay_runner.create_exchange_profile = original_profile_factory

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())