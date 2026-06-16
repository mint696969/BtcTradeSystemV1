# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_risk_monitor_state.py
# desc: Verify risk_monitor_state adapts shared market signal context for risk monitor use.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.risk_monitor_state as state_mod  # noqa: E402


def main() -> int:
    original_loader = state_mod.load_market_signal_context

    try:
        state_mod.load_market_signal_context = lambda: {
            "spread": 1600.0,
            "imbalance": 0.2,
            "delta": 0.3,
            "wall_ratio": None,
            "pressure_bias": "live_orderbook",
            "event_ts": "2026-04-14T15:00:00Z",
            "regime": "trend_up",
            "best_strategy": "microstructure_v1",
            "data_source": "live_canonical",
        }

        live_state = state_mod.build_risk_monitor_state()
        assert live_state is not None
        assert set(live_state.keys()) == {
            "spread",
            "imbalance",
            "wall_ratio",
            "delta",
            "source_label",
            "data_source",
        }
        assert live_state["source_label"] == "live_canonical + audit_latency"
        assert live_state["spread"] == 1600.0
        assert live_state["delta"] == 0.3
        assert live_state["wall_ratio"] is None

        state_mod.load_market_signal_context = lambda: {
            "spread": 3300.0,
            "imbalance": -0.22,
            "delta": -0.31,
            "wall_ratio": -0.44,
            "pressure_bias": "sell_pressure",
            "event_ts": "2026-04-14T15:05:00Z",
            "regime": "range",
            "best_strategy": "baseline_none",
            "data_source": "replay_research",
        }

        replay_state = state_mod.build_risk_monitor_state()
        assert replay_state is not None
        assert set(replay_state.keys()) == {
            "spread",
            "imbalance",
            "wall_ratio",
            "delta",
            "source_label",
            "data_source",
        }
        assert replay_state["source_label"] == "replay_board+tradeflow + audit_latency"
        assert replay_state["imbalance"] == -0.22
        assert replay_state["delta"] == -0.31
        assert replay_state["wall_ratio"] == -0.44

        state_mod.load_market_signal_context = lambda: None
        assert state_mod.build_risk_monitor_state() is None
    finally:
        state_mod.load_market_signal_context = original_loader

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())