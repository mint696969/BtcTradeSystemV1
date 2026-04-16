# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_state.py
# desc: Verify market_regime_state adapts shared market signal context for regime panel use.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.market_regime_state as state_mod  # noqa: E402


def main() -> int:
    original_loader = state_mod.load_market_signal_context

    try:
        state_mod.load_market_signal_context = lambda: {
            "spread": 1700.0,
            "imbalance": 0.23,
            "delta": 0.34,
            "wall_ratio": None,
            "pressure_bias": "buy_pressure",
            "event_ts": "2026-04-14T15:20:00Z",
            "regime": "trend_up",
            "best_strategy": "microstructure_v1",
            "data_source": "live_canonical",
        }

        live_state = state_mod.build_market_regime_state()
        assert live_state is not None
        assert set(live_state.keys()) == {
            "regime",
            "spread",
            "imbalance",
            "pressure_bias",
            "event_ts",
            "source_label",
            "data_source",
        }
        assert live_state["source_label"] == "live_canonical + research_experiment"
        assert live_state["regime"] == "trend_up"
        assert live_state["spread"] == 1700.0
        assert live_state["pressure_bias"] == "buy_pressure"

        state_mod.load_market_signal_context = lambda: {
            "spread": 3400.0,
            "imbalance": -0.24,
            "delta": -0.32,
            "wall_ratio": -0.46,
            "pressure_bias": "sell_pressure",
            "event_ts": "2026-04-14T15:25:00Z",
            "regime": "range",
            "best_strategy": "baseline_none",
            "data_source": "replay_research",
        }

        replay_state = state_mod.build_market_regime_state()
        assert replay_state is not None
        assert set(replay_state.keys()) == {
            "regime",
            "spread",
            "imbalance",
            "pressure_bias",
            "event_ts",
            "source_label",
            "data_source",
        }
        assert replay_state["source_label"] == "replay_board+tradeflow + research_experiment"
        assert replay_state["regime"] == "range"
        assert replay_state["imbalance"] == -0.24
        assert replay_state["pressure_bias"] == "sell_pressure"

        state_mod.load_market_signal_context = lambda: None
        assert state_mod.build_market_regime_state() is None
    finally:
        state_mod.load_market_signal_context = original_loader

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())