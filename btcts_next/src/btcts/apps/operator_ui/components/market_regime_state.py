# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_regime_state.py
# desc: Market regime panel 用の market signal state adapter.

from __future__ import annotations

from typing import TypedDict

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)


class MarketRegimeState(TypedDict):
    regime: str
    spread: float
    imbalance: float
    pressure_bias: str | None
    event_ts: str | None
    source_label: str
    data_source: str


def build_market_regime_state() -> MarketRegimeState | None:
    signal_state: MarketSignalContext | None = load_market_signal_context()
    if not signal_state:
        return None

    data_source = str(signal_state.get("data_source") or "unknown")
    source_label = (
        "live_canonical + research_experiment"
        if data_source == "live_canonical"
        else "replay_board+tradeflow + research_experiment"
    )

    return {
        "regime": signal_state.get("regime"),
        "spread": signal_state.get("spread"),
        "imbalance": signal_state.get("imbalance"),
        "pressure_bias": signal_state.get("pressure_bias"),
        "event_ts": signal_state.get("event_ts"),
        "source_label": source_label,
        "data_source": data_source,
    }