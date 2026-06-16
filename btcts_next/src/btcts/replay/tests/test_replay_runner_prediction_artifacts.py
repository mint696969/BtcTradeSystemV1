# path: ./btcts_next/src/btcts/replay/tests/test_replay_runner_prediction_artifacts.py
# desc: Verify run_replay wires prediction evaluation entries into ReplaySession through the replay prediction artifact builder.

from __future__ import annotations

import sys
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
                "signal": {"state": "watch"},
                "events": [{"event_name": "resistance_candidate"}],
                "best_bid": 101.0,
                "best_ask": 103.0,
            }

        return None


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

        session = replay_runner.run_replay(
            name="runner_prediction_artifacts",
            paths=[Path("D:/dummy/replay_source.jsonl")],
        )

        summary = session.summary()
        assert summary["processed_count"] == 2
        assert summary["prediction_evaluation_entry_count"] == 1
        assert summary["prediction_calibration_review_count"] == 1
        assert summary["tactic_proposal_output_count"] == 1
        assert summary["tactic_review_record_count"] == 1
        assert summary["tactic_operation_record_count"] == 1
        assert len(session.prediction_evaluation_entries) == 1
        assert len(session.prediction_calibration_reviews) == 1
        assert len(session.tactic_proposal_outputs) == 1
        assert len(session.tactic_review_records) == 1
        assert len(session.tactic_operation_records) == 1
        assert session.prediction_evaluation_entries[0]["entry_type"] == "prediction_evaluation_entry"
        assert session.prediction_evaluation_entries[0]["realized_max_adverse_bp"] == 0.0
        assert session.prediction_evaluation_entries[0]["realized_max_favorable_bp"] == 198.02
        assert session.prediction_calibration_reviews[0]["review_type"] == "prediction_calibration_review"
        assert session.tactic_proposal_outputs[0]["proposal_type"] == (
            "scenario_tactic_proposal_output"
        )
        assert session.tactic_review_records[0]["review_type"] == "tactic_review_record"
        assert session.tactic_operation_records[0]["operation_type"] == (
            "tactic_operation_record"
        )
        assert session.tactic_operation_records[0]["operation_state"] == "propose"
    finally:
        replay_runner.JsonlReplaySource = original_source
        replay_runner.ReplayEngine = original_engine
        replay_runner.ReplayPipeline = original_pipeline
        replay_runner.create_exchange_profile = original_profile_factory

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())