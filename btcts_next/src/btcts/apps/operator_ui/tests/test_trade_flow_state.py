# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_trade_flow_state.py
# desc: Verify trade_flow_state resolves live-first and replay-fallback tradeflow safely.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.trade_flow_state as state_mod  # noqa: E402


def main() -> int:
    original_recent_live_tradeflow_metrics = state_mod.recent_live_tradeflow_metrics
    original_load_latest_replay_payload = state_mod.load_latest_replay_payload
    original_latest_trade_row = state_mod.latest_trade_row
    original_tradeflow_metrics = state_mod.tradeflow_metrics

    try:
        state_mod.recent_live_tradeflow_metrics = lambda lines=80: {
            "buy_size": 1.25,
            "sell_size": 0.75,
            "delta": 0.5,
            "trade_count": 42,
            "event_ts": "2026-04-14T15:40:00Z",
        }
        state_mod.load_latest_replay_payload = lambda: {}
        state_mod.latest_trade_row = lambda _payload: {}
        state_mod.tradeflow_metrics = lambda _row: {}

        live_state = state_mod.build_trade_flow_state()
        assert live_state is not None
        assert live_state["source_label"] == "live_canonical"
        assert live_state["buy_volume"] == 1.25
        assert live_state["sell_volume"] == 0.75
        assert live_state["trade_delta"] == 0.5
        assert live_state["trade_count"] == 42
        assert live_state["micro_event_names"] == []

        state_mod.recent_live_tradeflow_metrics = lambda lines=80: {}
        state_mod.load_latest_replay_payload = lambda: {"kind": "replay"}
        state_mod.latest_trade_row = lambda _payload: {"kind": "trade"}
        state_mod.tradeflow_metrics = lambda _row: {
            "event_ts": "2026-04-14T15:45:00Z",
            "trade_count": 18,
            "buy_volume": 0.4,
            "sell_volume": 0.9,
            "trade_delta": -0.5,
            "avg_price": 123.0,
            "micro_event_names": ["absorption"],
        }

        replay_state = state_mod.build_trade_flow_state()
        assert replay_state is not None
        assert replay_state["source_label"] == "replay_tradeflow"
        assert replay_state["buy_volume"] == 0.4
        assert replay_state["sell_volume"] == 0.9
        assert replay_state["trade_delta"] == -0.5
        assert replay_state["trade_count"] == 18
        assert replay_state["micro_event_names"] == ["absorption"]

        state_mod.tradeflow_metrics = lambda _row: None
        assert state_mod.build_trade_flow_state() is None
    finally:
        state_mod.recent_live_tradeflow_metrics = original_recent_live_tradeflow_metrics
        state_mod.load_latest_replay_payload = original_load_latest_replay_payload
        state_mod.latest_trade_row = original_latest_trade_row
        state_mod.tradeflow_metrics = original_tradeflow_metrics

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())