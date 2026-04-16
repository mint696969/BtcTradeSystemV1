# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_conversation_state.py
# desc: AI conversation panel 用の market signal state adapter.

from __future__ import annotations

from typing import TypedDict

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)


class AiConversationState(TypedDict):
    spread: float
    imbalance: float
    delta: float
    wall_ratio: float | None
    regime: str
    best_strategy: str
    pressure_bias: str | None
    event_ts: str | None
    data_source: str
    runtime_note: str


def build_ai_conversation_state() -> AiConversationState | None:
    signal_state = load_market_signal_context()
    if not signal_state:
        return None

    data_source = str(signal_state.get("data_source") or "unknown")
    runtime_note = (
        "live board/trade canonical"
        if data_source == "live_canonical"
        else "fallback replay/research snapshot"
    )

    return {
        "spread": signal_state.get("spread"),
        "imbalance": signal_state.get("imbalance"),
        "delta": signal_state.get("delta"),
        "wall_ratio": signal_state.get("wall_ratio"),
        "regime": signal_state.get("regime"),
        "best_strategy": signal_state.get("best_strategy"),
        "pressure_bias": signal_state.get("pressure_bias"),
        "event_ts": signal_state.get("event_ts"),
        "data_source": data_source,
        "runtime_note": runtime_note,
    }