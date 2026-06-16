# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_signal_state_adopters.py
# desc: Verify ai_operator_state and agent_state consume shared market signal context safely.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.ai_operator_state as operator_state  # noqa: E402
import btcts.apps.operator_ui.components.agent_state as agent_state  # noqa: E402


def main() -> int:
    original_operator_loader = operator_state.load_market_signal_context
    original_agent_loader = agent_state.load_market_signal_context
    original_read_recent_audit = agent_state.read_recent_audit

    live_signal_state = {
        "spread": 1000.0,
        "imbalance": 0.2,
        "delta": 0.3,
        "wall_ratio": None,
        "pressure_bias": "live_orderbook",
        "event_ts": "2026-04-14T12:10:00Z",
        "regime": "trend_up",
        "best_strategy": "microstructure_v1",
        "data_source": "live_canonical",
    }
    replay_signal_state = {
        "spread": 2200.0,
        "imbalance": -0.1,
        "delta": -0.2,
        "wall_ratio": -0.4,
        "pressure_bias": "sell_pressure",
        "event_ts": "2026-04-14T12:20:00Z",
        "regime": "range",
        "best_strategy": "baseline_none",
        "data_source": "replay_research",
    }

    try:
        operator_state.load_market_signal_context = lambda: live_signal_state
        normalized = operator_state.analyze_operator_state()
        assert normalized is not None
        assert normalized["wall_ratio"] == 0.0
        assert normalized["data_source"] == "live_canonical"

        agent_state.read_recent_audit = lambda lines=40: [{"event": "audit"}]

        agent_state.load_market_signal_context = lambda: live_signal_state
        live_agent = agent_state.analyze_agent_state()
        assert live_agent is not None
        assert set(live_agent.keys()) == {
            "audit_rows",
            "source_label",
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
        assert live_agent["source_label"] == "live_canonical + research_experiment + audit_latency"
        assert live_agent["wall_ratio"] is None
        assert live_agent["audit_rows"] == [{"event": "audit"}]

        agent_state.load_market_signal_context = lambda: replay_signal_state
        replay_agent = agent_state.analyze_agent_state()
        assert replay_agent is not None
        assert set(replay_agent.keys()) == {
            "audit_rows",
            "source_label",
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
        assert replay_agent["source_label"] == "replay_board+tradeflow + research_experiment + audit_latency"
        assert replay_agent["wall_ratio"] == -0.4
        assert replay_agent["delta"] == -0.2
    finally:
        operator_state.load_market_signal_context = original_operator_loader
        agent_state.load_market_signal_context = original_agent_loader
        agent_state.read_recent_audit = original_read_recent_audit

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())