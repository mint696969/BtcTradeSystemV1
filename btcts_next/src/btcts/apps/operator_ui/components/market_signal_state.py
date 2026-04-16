# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_signal_state.py
# desc: Shared live/replay/research market signal context builder for AI / agent consumers.

from __future__ import annotations

from typing import Literal, TypedDict

from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
)
from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_best_strategy_name,
    latest_board_row,
    latest_regime_name,
    latest_trade_row,
    load_latest_experiment_payload,
    load_latest_replay_payload,
    tradeflow_metrics,
)


MarketSignalDataSource = Literal[
    "live_canonical",
    "replay_research",
]


class MarketSignalContext(TypedDict):
    spread: float
    imbalance: float
    delta: float
    wall_ratio: float | None
    pressure_bias: str | None
    event_ts: str | None
    regime: str
    best_strategy: str
    data_source: MarketSignalDataSource


def _depth_imbalance(bid_depth, ask_depth) -> float | None:
    if bid_depth is None or ask_depth is None:
        return None

    try:
        bid_depth_f = float(bid_depth)
        ask_depth_f = float(ask_depth)
    except Exception:
        return None

    denom = bid_depth_f + ask_depth_f
    if denom <= 0:
        return None

    return (bid_depth_f - ask_depth_f) / denom


def load_market_signal_context() -> MarketSignalContext | None:
    experiment_payload = load_latest_experiment_payload()

    fallback_regime = latest_regime_name(experiment_payload)
    fallback_best_strategy = latest_best_strategy_name(experiment_payload)

    live_board = latest_live_board_metrics()
    live_flow = recent_live_tradeflow_metrics(lines=80)

    live_spread = live_board.get("spread")
    live_delta = live_flow.get("delta")

    if live_spread is not None and live_delta is not None:
        imbalance = _depth_imbalance(
            live_board.get("bid_depth"),
            live_board.get("ask_depth"),
        )
        if imbalance is not None:
            return {
                "spread": float(live_spread),
                "imbalance": float(imbalance),
                "delta": float(live_delta),
                "wall_ratio": None,
                "pressure_bias": "live_orderbook",
                "event_ts": live_flow.get("event_ts") or live_board.get("event_ts"),
                "regime": (
                    fallback_regime
                    if fallback_regime != "unknown"
                    else "live_canonical"
                ),
                "best_strategy": fallback_best_strategy,
                "data_source": "live_canonical",
            }

    replay_payload = load_latest_replay_payload()
    board = board_signal_metrics(latest_board_row(replay_payload))
    flow = tradeflow_metrics(latest_trade_row(replay_payload))

    if not board or not flow:
        return None

    spread = board.get("spread")
    imbalance = board.get("imbalance")
    delta = flow.get("trade_delta")
    wall_ratio = board.get("wall_ratio")

    if spread is None or imbalance is None or delta is None or wall_ratio is None:
        return None

    return {
        "spread": float(spread),
        "imbalance": float(imbalance),
        "delta": float(delta),
        "wall_ratio": float(wall_ratio),
        "pressure_bias": board.get("pressure_bias"),
        "event_ts": flow.get("event_ts") or board.get("event_ts"),
        "regime": fallback_regime,
        "best_strategy": fallback_best_strategy,
        "data_source": "replay_research",
    }