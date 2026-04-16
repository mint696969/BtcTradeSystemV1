# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_alert_state_live_signal_context.py
# desc: Verify warroom_alert_state live path uses shared market signal context and rejects replay source.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.warroom_alert_state as alert_state  # noqa: E402


def main() -> int:
    original_loader = alert_state.load_market_signal_context
    original_latency = alert_state.recent_audit_latency

    try:
        alert_state.recent_audit_latency = lambda lines=40: 321.0

        alert_state.load_market_signal_context = lambda: {
            "spread": 1500.0,
            "imbalance": 0.25,
            "delta": 0.4,
            "wall_ratio": None,
            "pressure_bias": "live_orderbook",
            "event_ts": "2026-04-14T13:00:00Z",
            "regime": "trend_up",
            "best_strategy": "microstructure_v1",
            "data_source": "live_canonical",
        }

        live_state = alert_state.build_live_alert_state()
        assert live_state is not None
        assert set(live_state.keys()) == {
            "spread",
            "imbalance",
            "delta",
            "alert_ts",
            "regime",
            "best_strategy",
            "latency",
        }
        assert live_state["spread"] == 1500.0
        assert live_state["imbalance"] == 0.25
        assert live_state["delta"] == 0.4
        assert live_state["alert_ts"] == "2026-04-14T13:00:00Z"
        assert live_state["regime"] == "trend_up"
        assert live_state["best_strategy"] == "microstructure_v1"
        assert live_state["latency"] == 321.0

        alert_state.load_market_signal_context = lambda: {
            "spread": 2500.0,
            "imbalance": -0.1,
            "delta": -0.2,
            "wall_ratio": -0.35,
            "pressure_bias": "sell_pressure",
            "event_ts": "2026-04-14T13:05:00Z",
            "regime": "range",
            "best_strategy": "baseline_none",
            "data_source": "replay_research",
        }

        replay_state = alert_state.build_live_alert_state()
        assert replay_state is None
    finally:
        alert_state.load_market_signal_context = original_loader
        alert_state.recent_audit_latency = original_latency

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())