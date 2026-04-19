# path: ./btcts_next/src/btcts/replay/tests/test_replay_runner_prediction_feedback_scenario_bridge.py
# desc: Verify run_replay output can bridge through replay feedback into shared PredictionSystemInput and ScenarioOutput.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.replay.replay_runner as replay_runner  # noqa: E402
from btcts.replay.replay_prediction_artifacts import (  # noqa: E402
    build_prediction_state_from_replay_result,
)
from btcts.replay.replay_prediction_feedback import (  # noqa: E402
    build_prediction_replay_feedback_from_session,
)


class _DummySource:
    def __init__(self, paths):
        self.paths = paths

    def load(self):
        return [
            {"seq": 1},
            {"seq": 2},
            {"seq": 3},
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

        if seq == 3:
            return {
                "record_id": "row_3",
                "record_type": "market.orderbook.diff",
                "event_ts": "2026-04-17T04:30:00Z",
                "signal": {"state": "watch"},
                "events": [{"event_name": "persistence_candidate"}],
                "best_bid": 102.0,
                "best_ask": 104.0,
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
            name="runner_prediction_feedback_scenario_bridge",
            paths=[Path("D:/dummy/replay_source.jsonl")],
        )

        replay_feedback = build_prediction_replay_feedback_from_session(session)
        assert replay_feedback is not None
        assert replay_feedback["feedback_type"] == "prediction_replay_feedback"
        assert replay_feedback["entry_count"] == 2
        assert replay_feedback["review_priority"] == "normal"

        latest_result = session.output[-1]
        prediction_state = build_prediction_state_from_replay_result(
            latest_result,
            exchange="bitflyer",
            symbol_raw="BTC_JPY",
            replay_feedback=replay_feedback,
        )

        prediction_input = prediction_state["prediction_input"]
        scenario_output = prediction_state["scenario_output"]

        assert prediction_input.evidence_bundle.external_context["replay_feedback"][
            "feedback_type"
        ] == "prediction_replay_feedback"
        assert prediction_input.evidence_bundle.external_context["replay_feedback"][
            "entry_count"
        ] == 2
        assert prediction_input.evidence_bundle.external_context["replay_feedback"][
            "primary_focus"
        ] == "stability_review"

        assert scenario_output.evidence["replay_feedback_present"] is True
        assert scenario_output.evidence["replay_feedback_summary"] == {
            "review_priority": "normal",
            "primary_focus": "stability_review",
            "invalidation_review": "keep_slow_invalidation",
            "scenario_trace_focus": "none",
            "entry_count": 2,
            "missed_count": 0,
            "high_priority_count": 0,
            "average_confidence_gap": 0.0,
            "average_caution_gap": 0.0,
        }
        assert scenario_output.diagnostics["replay_feedback_present"] is True
        assert scenario_output.diagnostics["replay_feedback_confidence_adjustment"] == 0.0
        assert scenario_output.diagnostics["replay_feedback_caution_adjustment"] == 0
        assert scenario_output.diagnostics["replay_feedback_caution_adjustment_policy"] == (
            "none"
        )
    finally:
        replay_runner.JsonlReplaySource = original_source
        replay_runner.ReplayEngine = original_engine
        replay_runner.ReplayPipeline = original_pipeline
        replay_runner.create_exchange_profile = original_profile_factory

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())