# path: ./btcts_next/src/btcts/apps/operator_ui/components/risk_monitor_state.py
# desc: Risk monitor panel 用の market signal state adapter.

from __future__ import annotations

from typing import TypedDict

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)


class RiskMonitorState(TypedDict):
    spread: float
    imbalance: float
    wall_ratio: float | None
    delta: float
    source_label: str
    data_source: str


def build_risk_monitor_state() -> RiskMonitorState | None:
    signal_state: MarketSignalContext | None = load_market_signal_context()
    if not signal_state:
        return None

    data_source = str(signal_state.get("data_source") or "unknown")
    source_label = (
        "live_canonical + audit_latency"
        if data_source == "live_canonical"
        else "replay_board+tradeflow + audit_latency"
    )

    return {
        "spread": signal_state.get("spread"),
        "imbalance": signal_state.get("imbalance"),
        "wall_ratio": signal_state.get("wall_ratio"),
        "delta": signal_state.get("delta"),
        "source_label": source_label,
        "data_source": data_source,
    }