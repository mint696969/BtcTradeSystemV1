# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_signal_state.py
# desc: Verify shared market signal context builder resolves execution-market live/state only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.market_signal_state as signal_mod  # noqa: E402


def main() -> int:
    original_execution_market_context = signal_mod.execution_market_context
    original_latest_live_board_metrics = signal_mod.latest_live_board_metrics
    original_recent_live_tradeflow_metrics = signal_mod.recent_live_tradeflow_metrics
    original_load_latest_experiment_payload = signal_mod.load_latest_experiment_payload
    original_latest_regime_name = signal_mod.latest_regime_name
    original_latest_best_strategy_name = signal_mod.latest_best_strategy_name
    original_load_execution_market_overview = signal_mod.load_execution_market_overview

    try:
        signal_mod.execution_market_context = lambda: {
            "exchange": "bitflyer",
            "symbol_raw": "FX_BTC_JPY",
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
        }
        signal_mod.load_latest_experiment_payload = lambda: {"kind": "experiment"}
        signal_mod.latest_regime_name = lambda _payload: "trend_up"
        signal_mod.latest_best_strategy_name = lambda _payload: "microstructure_v1"

        calls: list[tuple[str, str]] = []
        signal_mod.latest_live_board_metrics = lambda **kwargs: calls.append((kwargs["exchange"], kwargs["symbol"])) or {
            "spread": 1200.0,
            "bid_depth": 4.0,
            "ask_depth": 1.0,
            "event_ts": "2026-04-14T12:00:00Z",
        }
        signal_mod.recent_live_tradeflow_metrics = lambda **kwargs: {
            "delta": 0.25,
            "event_ts": "2026-04-14T12:00:01Z",
        }
        signal_mod.load_execution_market_overview = lambda: (_ for _ in ()).throw(AssertionError("state fallback must not be used when FX live is complete"))

        live_state = signal_mod.load_market_signal_context()
        assert live_state is not None
        assert calls == [("bitflyer", "FX_BTC_JPY")]
        assert live_state["data_source"] == "execution_market_live_canonical"
        assert live_state["spread"] == 1200.0
        assert round(float(live_state["imbalance"]), 3) == 0.6
        assert live_state["delta"] == 0.25
        assert live_state["wall_ratio"] is None
        assert live_state["pressure_bias"] == "execution_market_live_orderbook"
        assert live_state["regime"] == "trend_up"
        assert live_state["best_strategy"] == "microstructure_v1"

        signal_mod.latest_live_board_metrics = lambda **kwargs: {}
        signal_mod.recent_live_tradeflow_metrics = lambda **kwargs: {}
        signal_mod.load_execution_market_overview = lambda: {
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "symbol_raw": "FX_BTC_JPY",
            "spread": 2500.0,
            "imbalance": -0.1,
            "trade_delta": -0.45,
            "near_zone_liquidity_summary": {
                "bid_size_total": 1.0,
                "ask_size_total": 2.0,
            },
            "collector_ts": "2026-04-14T12:05:01Z",
        }

        state_signal = signal_mod.load_market_signal_context()
        assert state_signal is not None
        assert state_signal["data_source"] == "execution_market_state"
        assert state_signal["spread"] == 2500.0
        assert state_signal["imbalance"] == -0.1
        assert state_signal["delta"] == -0.45
        assert round(float(state_signal["wall_ratio"]), 3) == -0.333
        assert state_signal["pressure_bias"] == "execution_market_state"
        assert state_signal["regime"] == "trend_up"
        assert state_signal["best_strategy"] == "microstructure_v1"
    finally:
        signal_mod.execution_market_context = original_execution_market_context
        signal_mod.latest_live_board_metrics = original_latest_live_board_metrics
        signal_mod.recent_live_tradeflow_metrics = original_recent_live_tradeflow_metrics
        signal_mod.load_latest_experiment_payload = original_load_latest_experiment_payload
        signal_mod.latest_regime_name = original_latest_regime_name
        signal_mod.latest_best_strategy_name = original_latest_best_strategy_name
        signal_mod.load_execution_market_overview = original_load_execution_market_overview

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
