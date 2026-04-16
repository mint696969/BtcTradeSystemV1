# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_timeline_state.py
# desc: Verify warroom_timeline_state resolves live-first and replay-fallback timeline safely.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.warroom_timeline_state as state_mod  # noqa: E402


def main() -> int:
    original_latest_live_board_metrics = state_mod.latest_live_board_metrics
    original_recent_live_tradeflow_metrics = state_mod.recent_live_tradeflow_metrics
    original_load_latest_experiment_payload = state_mod.load_latest_experiment_payload
    original_load_latest_replay_payload = state_mod.load_latest_replay_payload
    original_latest_regime_name = state_mod.latest_regime_name
    original_replay_tail_rows = state_mod.replay_tail_rows
    original_board_signal_metrics = state_mod.board_signal_metrics
    original_tradeflow_metrics = state_mod.tradeflow_metrics

    try:
        state_mod.load_latest_experiment_payload = lambda: {"kind": "experiment"}
        state_mod.load_latest_replay_payload = lambda: {"kind": "replay"}
        state_mod.latest_regime_name = lambda _payload: "trend_up"

        state_mod.latest_live_board_metrics = lambda: {
            "spread": 1500.0,
            "bid_depth": 4.0,
            "ask_depth": 1.0,
            "event_ts": "2026-04-14T16:20:00Z",
        }
        state_mod.recent_live_tradeflow_metrics = lambda lines=80: {
            "delta": 0.3,
            "event_ts": "2026-04-14T16:20:01Z",
        }
        state_mod.replay_tail_rows = lambda _payload, limit=20: []
        state_mod.board_signal_metrics = lambda _row: {}
        state_mod.tradeflow_metrics = lambda _row: {}

        live_state = state_mod.build_warroom_timeline_state(lang="en")
        assert live_state["timeline_is_live"] is True
        assert len(live_state["timeline"]) == 4

        state_mod.latest_live_board_metrics = lambda: {}
        state_mod.recent_live_tradeflow_metrics = lambda lines=80: {}
        state_mod.replay_tail_rows = lambda _payload, limit=20: [
            {"kind": "board", "event_ts": "2026-04-14T16:25:00Z"},
            {"kind": "trade", "event_ts": "2026-04-14T16:25:01Z"},
        ]
        state_mod.board_signal_metrics = lambda _row: {
            "spread": 3200.0,
            "imbalance": -0.25,
            "pressure_bias": "sell_pressure",
        }
        state_mod.tradeflow_metrics = lambda _row: {
            "trade_delta": -0.4,
        }

        replay_state = state_mod.build_warroom_timeline_state(lang="en")
        assert replay_state["timeline_is_live"] is False
        assert len(replay_state["timeline"]) >= 1

        state_mod.replay_tail_rows = lambda _payload, limit=20: []
        empty_state = state_mod.build_warroom_timeline_state(lang="en")
        assert empty_state["timeline_is_live"] is False
        assert empty_state["timeline"] == []
    finally:
        state_mod.latest_live_board_metrics = original_latest_live_board_metrics
        state_mod.recent_live_tradeflow_metrics = original_recent_live_tradeflow_metrics
        state_mod.load_latest_experiment_payload = original_load_latest_experiment_payload
        state_mod.load_latest_replay_payload = original_load_latest_replay_payload
        state_mod.latest_regime_name = original_latest_regime_name
        state_mod.replay_tail_rows = original_replay_tail_rows
        state_mod.board_signal_metrics = original_board_signal_metrics
        state_mod.tradeflow_metrics = original_tradeflow_metrics

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())