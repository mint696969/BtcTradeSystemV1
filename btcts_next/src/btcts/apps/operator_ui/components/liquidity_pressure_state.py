# path: ./btcts_next/src/btcts/apps/operator_ui/components/liquidity_pressure_state.py
# desc: Liquidity pressure panel state adapter for execution-market live board only.

from __future__ import annotations

from btcts.apps.operator_ui.components.live_bridge import latest_live_board_metrics
from btcts.apps.operator_ui.components.market_state_bridge import execution_market_context


def build_liquidity_pressure_state() -> dict | None:
    ctx = execution_market_context()
    live_board = latest_live_board_metrics(
        exchange=str(ctx["exchange"]),
        symbol=str(ctx["symbol_raw"]),
    )
    if not live_board:
        return None

    bid_depth = live_board.get("bid_depth")
    ask_depth = live_board.get("ask_depth")

    wall_ratio = None
    wall_side = None

    if bid_depth is not None and ask_depth is not None:
        try:
            bid_depth_f = float(bid_depth)
            ask_depth_f = float(ask_depth)
            denom = bid_depth_f + ask_depth_f
            if denom > 0:
                wall_ratio = (bid_depth_f - ask_depth_f) / denom
                if wall_ratio > 0.05:
                    wall_side = "bid"
                elif wall_ratio < -0.05:
                    wall_side = "ask"
        except Exception:
            wall_ratio = None
            wall_side = None

    return {
        "bid_wall_size": bid_depth,
        "ask_wall_size": ask_depth,
        "wall_ratio": wall_ratio,
        "wall_side": wall_side,
        "event_ts": live_board.get("event_ts"),
        "source_label": "execution_market_live_canonical",
        "data_source": "execution_market_live_canonical",
        "product_code": ctx["product_code"],
        "market_uid": ctx["market_uid"],
    }
