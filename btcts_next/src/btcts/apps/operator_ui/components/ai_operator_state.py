# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_state.py
# desc: AI Operator の state 組み立てを分離したデータ層。

from __future__ import annotations

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)


def analyze_operator_state() -> MarketSignalContext | None:
    signal_state = load_market_signal_context()
    if not signal_state:
        return None

    if signal_state.get("wall_ratio") is not None:
        return signal_state

    normalized: MarketSignalContext = dict(signal_state)
    normalized["wall_ratio"] = 0.0
    return normalized