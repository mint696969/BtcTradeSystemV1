# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_trade_flow_state.py
# desc: Verify trade_flow_state resolves execution-market live tradeflow only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.trade_flow_state as state_mod  # noqa: E402


def main() -> int:
    original_execution_market_context = state_mod.execution_market_context
    original_recent_live_tradeflow_metrics = state_mod.recent_live_tradeflow_metrics

    try:
        state_mod.execution_market_context = lambda: {
            "exchange": "bitflyer",
            "symbol_raw": "FX_BTC_JPY",
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
        }
        calls: list[tuple[str, str]] = []
        state_mod.recent_live_tradeflow_metrics = lambda **kwargs: calls.append((kwargs["exchange"], kwargs["symbol"])) or {
            "buy_size": 1.25,
            "sell_size": 0.75,
            "delta": 0.5,
            "trade_count": 42,
            "event_ts": "2026-04-14T15:40:00Z",
        }

        live_state = state_mod.build_trade_flow_state()
        assert live_state is not None
        assert calls == [("bitflyer", "FX_BTC_JPY")]
        assert live_state["source_label"] == "execution_market_live_canonical"
        assert live_state["data_source"] == "execution_market_live_canonical"
        assert live_state["product_code"] == "FX_BTC_JPY"
        assert live_state["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
        assert live_state["buy_volume"] == 1.25
        assert live_state["sell_volume"] == 0.75
        assert live_state["trade_delta"] == 0.5
        assert live_state["trade_count"] == 42
        assert live_state["micro_event_names"] == []

        state_mod.recent_live_tradeflow_metrics = lambda **kwargs: {}
        assert state_mod.build_trade_flow_state() is None
    finally:
        state_mod.execution_market_context = original_execution_market_context
        state_mod.recent_live_tradeflow_metrics = original_recent_live_tradeflow_metrics

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
