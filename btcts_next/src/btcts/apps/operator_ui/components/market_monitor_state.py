# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_monitor_state.py
# desc: Market Monitor の board/state/source 組み立てを分離したデータ層。

from __future__ import annotations

from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_overview,
    market_monitor_metrics,
)
from btcts.apps.operator_ui.market_state_service import market_state_diagnostics
from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_board_row,
    load_latest_replay_payload,
)


def analyze_market_monitor_state() -> dict | None:
    live_board = latest_live_board_metrics()
    state = load_market_overview()
    state_diag = market_state_diagnostics()
    board = {}
    source_label = "unknown"

    if live_board:
        best_bid = live_board.get("best_bid")
        best_ask = live_board.get("best_ask")
        spread = live_board.get("spread")
        bid_depth = live_board.get("bid_depth")
        ask_depth = live_board.get("ask_depth")

        imbalance = None
        if bid_depth is not None and ask_depth is not None:
            try:
                bid_depth_f = float(bid_depth)
                ask_depth_f = float(ask_depth)
                denom = bid_depth_f + ask_depth_f
                if denom > 0:
                    imbalance = (bid_depth_f - ask_depth_f) / denom
            except Exception:
                imbalance = None

        board = {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "imbalance": imbalance,
            "event_ts": live_board.get("event_ts"),
            "trust_state": None,
            "boundary_reason": None,
            "continuity_state": None,
            "interpretation_bucket": None,
            "interpretation_reason": None,
        }
        source_label = "live_canonical"

    if not board:
        board = market_monitor_metrics(state)
        source_label = "market_state_live"

    if not board:
        replay_payload = load_latest_replay_payload()
        board = board_signal_metrics(latest_board_row(replay_payload))
        source_label = "replay_board_fallback"

    if not board:
        return None

    return {
        "board": board,
        "state": state,
        "state_diag": state_diag,
        "source_label": source_label,
    }