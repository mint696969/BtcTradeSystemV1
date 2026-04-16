# path: ./btcts_next/src/btcts/apps/operator_ui/components/liquidity_pressure_state.py
# desc: Liquidity pressure panel 用の live-first / replay-fallback board state adapter.

from __future__ import annotations

from btcts.apps.operator_ui.components.live_bridge import latest_live_board_metrics
from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_board_row,
    load_latest_replay_payload,
)


def build_liquidity_pressure_state() -> dict | None:
    live_board = latest_live_board_metrics()
    if live_board:
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
            "source_label": "live_canonical",
            "data_source": "live_canonical",
        }

    replay_payload = load_latest_replay_payload()
    board = board_signal_metrics(latest_board_row(replay_payload))
    if not board:
        return None

    return {
        "bid_wall_size": board.get("bid_wall_size"),
        "ask_wall_size": board.get("ask_wall_size"),
        "wall_ratio": board.get("wall_ratio"),
        "wall_side": board.get("wall_side"),
        "event_ts": board.get("event_ts"),
        "source_label": "replay_board_fallback",
        "data_source": "replay_board_fallback",
    }