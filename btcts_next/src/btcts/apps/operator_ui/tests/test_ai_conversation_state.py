# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_conversation_state.py
# desc: Verify ai_conversation_state adapts shared market signal context for panel use.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.ai_conversation_state as state_mod  # noqa: E402


def main() -> int:
    original_loader = state_mod.load_market_signal_context

    try:
        state_mod.load_market_signal_context = lambda: {
            "spread": 1300.0,
            "imbalance": 0.25,
            "delta": 0.35,
            "wall_ratio": None,
            "pressure_bias": "live_orderbook",
            "event_ts": "2026-04-14T14:00:00Z",
            "regime": "trend_up",
            "best_strategy": "microstructure_v1",
            "data_source": "live_canonical",
        }

        live_state = state_mod.build_ai_conversation_state()
        assert live_state is not None
        assert set(live_state.keys()) == {
            "spread",
            "imbalance",
            "delta",
            "wall_ratio",
            "regime",
            "best_strategy",
            "pressure_bias",
            "event_ts",
            "data_source",
            "runtime_note",
        }
        assert live_state["data_source"] == "live_canonical"
        assert live_state["runtime_note"] == "live board/trade canonical"
        assert live_state["event_ts"] == "2026-04-14T14:00:00Z"
        assert live_state["pressure_bias"] == "live_orderbook"

        state_mod.load_market_signal_context = lambda: {
            "spread": 2800.0,
            "imbalance": -0.2,
            "delta": -0.3,
            "wall_ratio": -0.5,
            "pressure_bias": "sell_pressure",
            "event_ts": "2026-04-14T14:05:00Z",
            "regime": "range",
            "best_strategy": "baseline_none",
            "data_source": "replay_research",
        }

        replay_state = state_mod.build_ai_conversation_state()
        assert replay_state is not None
        assert set(replay_state.keys()) == {
            "spread",
            "imbalance",
            "delta",
            "wall_ratio",
            "regime",
            "best_strategy",
            "pressure_bias",
            "event_ts",
            "data_source",
            "runtime_note",
        }
        assert replay_state["data_source"] == "replay_research"
        assert replay_state["runtime_note"] == "fallback replay/research snapshot"
        assert replay_state["wall_ratio"] == -0.5
        assert replay_state["delta"] == -0.3

        state_mod.load_market_signal_context = lambda: None
        assert state_mod.build_ai_conversation_state() is None
    finally:
        state_mod.load_market_signal_context = original_loader

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())