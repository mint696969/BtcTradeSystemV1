# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_signal_state.py
# desc: Verify shared market signal context builder resolves live-first and replay fallback.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.market_signal_state as signal_mod  # noqa: E402


def main() -> int:
    original_latest_live_board_metrics = signal_mod.latest_live_board_metrics
    original_recent_live_tradeflow_metrics = signal_mod.recent_live_tradeflow_metrics
    original_load_latest_experiment_payload = signal_mod.load_latest_experiment_payload
    original_latest_regime_name = signal_mod.latest_regime_name
    original_latest_best_strategy_name = signal_mod.latest_best_strategy_name
    original_load_latest_replay_payload = signal_mod.load_latest_replay_payload
    original_latest_board_row = signal_mod.latest_board_row
    original_latest_trade_row = signal_mod.latest_trade_row
    original_board_signal_metrics = signal_mod.board_signal_metrics
    original_tradeflow_metrics = signal_mod.tradeflow_metrics

    try:
        signal_mod.load_latest_experiment_payload = lambda: {"kind": "experiment"}
        signal_mod.latest_regime_name = lambda _payload: "trend_up"
        signal_mod.latest_best_strategy_name = lambda _payload: "microstructure_v1"

        # live path
        signal_mod.latest_live_board_metrics = lambda: {
            "spread": 1200.0,
            "bid_depth": 4.0,
            "ask_depth": 1.0,
            "event_ts": "2026-04-14T12:00:00Z",
        }
        signal_mod.recent_live_tradeflow_metrics = lambda lines=80: {
            "delta": 0.25,
            "event_ts": "2026-04-14T12:00:01Z",
        }
        signal_mod.load_latest_replay_payload = lambda: {}
        signal_mod.latest_board_row = lambda _payload: {}
        signal_mod.latest_trade_row = lambda _payload: {}
        signal_mod.board_signal_metrics = lambda _row: {}
        signal_mod.tradeflow_metrics = lambda _row: {}

        live_state = signal_mod.load_market_signal_context()
        assert live_state is not None
        assert live_state["data_source"] == "live_canonical"
        assert set(live_state.keys()) == {
            "spread",
            "imbalance",
            "delta",
            "wall_ratio",
            "pressure_bias",
            "event_ts",
            "regime",
            "best_strategy",
            "data_source",
        }
        assert live_state["spread"] == 1200.0
        assert round(float(live_state["imbalance"]), 3) == 0.6
        assert live_state["delta"] == 0.25
        assert live_state["wall_ratio"] is None
        assert live_state["pressure_bias"] == "live_orderbook"
        assert live_state["regime"] == "trend_up"
        assert live_state["best_strategy"] == "microstructure_v1"

        # replay fallback path
        signal_mod.latest_live_board_metrics = lambda: {}
        signal_mod.recent_live_tradeflow_metrics = lambda lines=80: {}
        signal_mod.load_latest_replay_payload = lambda: {"kind": "replay"}
        signal_mod.latest_board_row = lambda _payload: {"kind": "board"}
        signal_mod.latest_trade_row = lambda _payload: {"kind": "trade"}
        signal_mod.board_signal_metrics = lambda _row: {
            "spread": 2500.0,
            "imbalance": -0.1,
            "pressure_bias": "sell_pressure",
            "wall_ratio": -0.35,
            "event_ts": "2026-04-14T12:05:00Z",
        }
        signal_mod.tradeflow_metrics = lambda _row: {
            "trade_delta": -0.45,
            "event_ts": "2026-04-14T12:05:01Z",
        }

        replay_state = signal_mod.load_market_signal_context()
        assert replay_state is not None
        assert replay_state["data_source"] == "replay_research"
        assert set(replay_state.keys()) == {
            "spread",
            "imbalance",
            "delta",
            "wall_ratio",
            "pressure_bias",
            "event_ts",
            "regime",
            "best_strategy",
            "data_source",
        }
        assert replay_state["spread"] == 2500.0
        assert replay_state["imbalance"] == -0.1
        assert replay_state["delta"] == -0.45
        assert replay_state["wall_ratio"] == -0.35
        assert replay_state["pressure_bias"] == "sell_pressure"
        assert replay_state["regime"] == "trend_up"
        assert replay_state["best_strategy"] == "microstructure_v1"
    finally:
        signal_mod.latest_live_board_metrics = original_latest_live_board_metrics
        signal_mod.recent_live_tradeflow_metrics = original_recent_live_tradeflow_metrics
        signal_mod.load_latest_experiment_payload = original_load_latest_experiment_payload
        signal_mod.latest_regime_name = original_latest_regime_name
        signal_mod.latest_best_strategy_name = original_latest_best_strategy_name
        signal_mod.load_latest_replay_payload = original_load_latest_replay_payload
        signal_mod.latest_board_row = original_latest_board_row
        signal_mod.latest_trade_row = original_latest_trade_row
        signal_mod.board_signal_metrics = original_board_signal_metrics
        signal_mod.tradeflow_metrics = original_tradeflow_metrics

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())