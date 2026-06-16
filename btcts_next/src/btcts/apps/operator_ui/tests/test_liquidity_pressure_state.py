# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_liquidity_pressure_state.py
# desc: Verify liquidity_pressure_state resolves execution-market live board only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.liquidity_pressure_state as state_mod  # noqa: E402


def main() -> int:
    original_execution_market_context = state_mod.execution_market_context
    original_latest_live_board_metrics = state_mod.latest_live_board_metrics

    try:
        state_mod.execution_market_context = lambda: {
            "exchange": "bitflyer",
            "symbol_raw": "FX_BTC_JPY",
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
        }
        calls: list[tuple[str, str]] = []
        state_mod.latest_live_board_metrics = lambda **kwargs: calls.append((kwargs["exchange"], kwargs["symbol"])) or {
            "bid_depth": 5.0,
            "ask_depth": 1.0,
            "event_ts": "2026-04-14T16:00:00Z",
        }

        live_state = state_mod.build_liquidity_pressure_state()
        assert live_state is not None
        assert calls == [("bitflyer", "FX_BTC_JPY")]
        assert live_state["source_label"] == "execution_market_live_canonical"
        assert live_state["data_source"] == "execution_market_live_canonical"
        assert live_state["product_code"] == "FX_BTC_JPY"
        assert live_state["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
        assert live_state["bid_wall_size"] == 5.0
        assert live_state["ask_wall_size"] == 1.0
        assert round(float(live_state["wall_ratio"]), 3) == 0.667
        assert live_state["wall_side"] == "bid"

        state_mod.latest_live_board_metrics = lambda **kwargs: {}
        assert state_mod.build_liquidity_pressure_state() is None
    finally:
        state_mod.execution_market_context = original_execution_market_context
        state_mod.latest_live_board_metrics = original_latest_live_board_metrics

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
