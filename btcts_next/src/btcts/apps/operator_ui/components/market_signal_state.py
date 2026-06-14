# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_signal_state.py
# desc: Shared execution-market signal context builder for AI / agent consumers.

from __future__ import annotations

from typing import Literal, TypedDict

from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    execution_market_context,
    load_execution_market_overview,
)
from btcts.apps.operator_ui.components.research_bridge import (
    latest_best_strategy_name,
    latest_regime_name,
    load_latest_experiment_payload,
)


MarketSignalDataSource = Literal[
    "execution_market_live_canonical",
    "execution_market_state",
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


def _market_state_wall_ratio(state: dict) -> float | None:
    near = state.get("near_zone_liquidity_summary") or {}
    try:
        bid_depth = float(near.get("bid_size_total"))
        ask_depth = float(near.get("ask_size_total"))
        denom = bid_depth + ask_depth
        if denom > 0:
            return (bid_depth - ask_depth) / denom
    except Exception:
        return None
    return None


def load_market_signal_context() -> MarketSignalContext | None:
    experiment_payload = load_latest_experiment_payload()

    fallback_regime = latest_regime_name(experiment_payload)
    fallback_best_strategy = latest_best_strategy_name(experiment_payload)

    ctx = execution_market_context()
    live_board = latest_live_board_metrics(
        exchange=str(ctx["exchange"]),
        symbol=str(ctx["symbol_raw"]),
    )
    live_flow = recent_live_tradeflow_metrics(
        exchange=str(ctx["exchange"]),
        symbol=str(ctx["symbol_raw"]),
        lines=80,
    )

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
                "pressure_bias": "execution_market_live_orderbook",
                "event_ts": live_flow.get("event_ts") or live_board.get("event_ts"),
                "regime": (
                    fallback_regime
                    if fallback_regime != "unknown"
                    else "execution_market_live_canonical"
                ),
                "best_strategy": fallback_best_strategy,
                "data_source": "execution_market_live_canonical",
            }

    # Current WarRoom decision material must not silently fall back to replay/spot.
    # If live canonical FX board/trades are incomplete, use only the configured
    # execution-market market_state. If that is missing/incomplete, return no data.
    state = load_execution_market_overview()
    if not state:
        return None

    spread = state.get("spread")
    imbalance = state.get("imbalance")
    delta = state.get("trade_delta")

    if spread is None or imbalance is None or delta is None:
        return None

    return {
        "spread": float(spread),
        "imbalance": float(imbalance),
        "delta": float(delta),
        "wall_ratio": _market_state_wall_ratio(state),
        "pressure_bias": "execution_market_state",
        "event_ts": state.get("exchange_ts") or state.get("collector_ts"),
        "regime": fallback_regime,
        "best_strategy": fallback_best_strategy,
        "data_source": "execution_market_state",
    }
