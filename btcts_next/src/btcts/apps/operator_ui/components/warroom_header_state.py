# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_header_state.py
# desc: War Room header 用の market signal state adapter.

from __future__ import annotations

from typing import TypedDict

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_prediction_summary_widget_model,
)


class WarroomHeaderState(TypedDict):
    regime: str
    best_strategy: str
    spread: float
    imbalance: float
    pressure_bias: str | None
    wall_ratio: float | None
    delta: float
    source_label: str
    source: str
    data_source: str
    prediction_bias: str
    prediction_caution: str
    prediction_switch_hint: str
    prediction_trace_summary: str


def build_warroom_header_state() -> WarroomHeaderState | None:
    signal_state = load_market_signal_context()
    if not signal_state:
        return None

    prediction_widget = load_prediction_summary_widget_model()

    data_source = str(signal_state.get("data_source") or "unknown")
    source_label = (
        "live_canonical + research_experiment"
        if data_source == "live_canonical"
        else "replay_board+tradeflow + research_experiment"
    )

    return {
        "regime": signal_state.get("regime"),
        "best_strategy": signal_state.get("best_strategy"),
        "spread": signal_state.get("spread"),
        "imbalance": signal_state.get("imbalance"),
        "pressure_bias": signal_state.get("pressure_bias"),
        "wall_ratio": signal_state.get("wall_ratio"),
        "delta": signal_state.get("delta"),
        "source_label": source_label,
        "source": source_label,
        "data_source": data_source,
        "prediction_bias": prediction_widget.short_horizon_bias_key,
        "prediction_caution": prediction_widget.caution_level_key,
        "prediction_switch_hint": prediction_widget.scenario_switch_hint_key,
        "prediction_trace_summary": prediction_widget.trace_summary_key,
    }