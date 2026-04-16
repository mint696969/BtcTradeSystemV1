# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_liquidity_pressure_state.py
# desc: Verify liquidity_pressure_state resolves live-first and replay-fallback board pressure safely.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.liquidity_pressure_state as state_mod  # noqa: E402


def main() -> int:
    original_latest_live_board_metrics = state_mod.latest_live_board_metrics
    original_load_latest_replay_payload = state_mod.load_latest_replay_payload
    original_latest_board_row = state_mod.latest_board_row
    original_board_signal_metrics = state_mod.board_signal_metrics

    try:
        state_mod.latest_live_board_metrics = lambda: {
            "bid_depth": 5.0,
            "ask_depth": 1.0,
            "event_ts": "2026-04-14T16:00:00Z",
        }
        state_mod.load_latest_replay_payload = lambda: {}
        state_mod.latest_board_row = lambda _payload: {}
        state_mod.board_signal_metrics = lambda _row: {}

        live_state = state_mod.build_liquidity_pressure_state()
        assert live_state is not None
        assert live_state["source_label"] == "live_canonical"
        assert live_state["bid_wall_size"] == 5.0
        assert live_state["ask_wall_size"] == 1.0
        assert round(float(live_state["wall_ratio"]), 3) == 0.667
        assert live_state["wall_side"] == "bid"

        state_mod.latest_live_board_metrics = lambda: {}
        state_mod.load_latest_replay_payload = lambda: {"kind": "replay"}
        state_mod.latest_board_row = lambda _payload: {"kind": "board"}
        state_mod.board_signal_metrics = lambda _row: {
            "bid_wall_size": 0.8,
            "ask_wall_size": 1.6,
            "wall_ratio": -0.333,
            "wall_side": "ask",
            "event_ts": "2026-04-14T16:05:00Z",
        }

        replay_state = state_mod.build_liquidity_pressure_state()
        assert replay_state is not None
        assert replay_state["source_label"] == "replay_board_fallback"
        assert replay_state["bid_wall_size"] == 0.8
        assert replay_state["ask_wall_size"] == 1.6
        assert replay_state["wall_ratio"] == -0.333
        assert replay_state["wall_side"] == "ask"

        state_mod.board_signal_metrics = lambda _row: None
        assert state_mod.build_liquidity_pressure_state() is None
    finally:
        state_mod.latest_live_board_metrics = original_latest_live_board_metrics
        state_mod.load_latest_replay_payload = original_load_latest_replay_payload
        state_mod.latest_board_row = original_latest_board_row
        state_mod.board_signal_metrics = original_board_signal_metrics

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())