# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_header_state.py
# desc: Verify warroom_header_state adapts shared market signal context for header use.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.warroom_header_state as state_mod  # noqa: E402


def main() -> int:
    original_loader = state_mod.load_market_signal_context

    try:
        state_mod.load_market_signal_context = lambda: {
            "spread": 1500.0,
            "imbalance": 0.24,
            "delta": 0.33,
            "wall_ratio": None,
            "pressure_bias": "live_orderbook",
            "event_ts": "2026-04-14T14:40:00Z",
            "regime": "trend_up",
            "best_strategy": "microstructure_v1",
            "data_source": "live_canonical",
        }

        live_state = state_mod.build_warroom_header_state()
        assert live_state is not None
        assert set(live_state.keys()) == {
            "regime",
            "best_strategy",
            "spread",
            "imbalance",
            "pressure_bias",
            "wall_ratio",
            "delta",
            "source_label",
            "source",
            "data_source",
        }
        assert live_state["source_label"] == "live_canonical + research_experiment"
        assert live_state["source"] == "live_canonical + research_experiment"
        assert live_state["regime"] == "trend_up"
        assert live_state["best_strategy"] == "microstructure_v1"
        assert live_state["pressure_bias"] == "live_orderbook"
        assert live_state["wall_ratio"] is None

        state_mod.load_market_signal_context = lambda: {
            "spread": 3200.0,
            "imbalance": -0.21,
            "delta": -0.28,
            "wall_ratio": -0.42,
            "pressure_bias": "sell_pressure",
            "event_ts": "2026-04-14T14:45:00Z",
            "regime": "range",
            "best_strategy": "baseline_none",
            "data_source": "replay_research",
        }

        replay_state = state_mod.build_warroom_header_state()
        assert replay_state is not None
        assert set(replay_state.keys()) == {
            "regime",
            "best_strategy",
            "spread",
            "imbalance",
            "pressure_bias",
            "wall_ratio",
            "delta",
            "source_label",
            "source",
            "data_source",
        }
        assert replay_state["source_label"] == "replay_board+tradeflow + research_experiment"
        assert replay_state["source"] == "replay_board+tradeflow + research_experiment"
        assert replay_state["delta"] == -0.28
        assert replay_state["pressure_bias"] == "sell_pressure"
        assert replay_state["wall_ratio"] == -0.42

        state_mod.load_market_signal_context = lambda: None
        assert state_mod.build_warroom_header_state() is None
    finally:
        state_mod.load_market_signal_context = original_loader

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())