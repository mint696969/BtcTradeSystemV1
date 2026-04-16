# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_signal_state.py
# desc: AI signal panel 用の market signal state adapter.

from __future__ import annotations

from typing import TypedDict

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)


class AiSignalState(TypedDict):
    spread: float
    imbalance: float
    delta: float
    regime: str
    best_strategy: str
    replay_ts: str | None
    source_label: str
    data_source: str


def build_ai_signal_state() -> AiSignalState | None:
    signal_state = load_market_signal_context()
    if not signal_state:
        return None

    data_source = str(signal_state.get("data_source") or "unknown")
    source_label = (
        "live_canonical + research_experiment"
        if data_source == "live_canonical"
        else "replay_board+tradeflow + research_experiment"
    )

    return {
        "spread": signal_state.get("spread"),
        "imbalance": signal_state.get("imbalance"),
        "delta": signal_state.get("delta"),
        "regime": signal_state.get("regime"),
        "best_strategy": signal_state.get("best_strategy"),
        "replay_ts": signal_state.get("event_ts"),
        "source_label": source_label,
        "data_source": data_source,
    }