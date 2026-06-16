# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_reasoning_state.py
# desc: AI reasoning panel 用の market signal state adapter.

from __future__ import annotations

from typing import TypedDict

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)


def _source_label_for_data_source(data_source: str, *, suffix: str) -> str:
    labels = {
        "execution_market_live_canonical": f"execution_market_live_canonical + {suffix}",
        "execution_market_state": f"execution_market_state + {suffix}",
        # Legacy labels kept only for compatibility with old tests/callers.
        "live_canonical": f"live_canonical + {suffix}",
        "replay_board_tradeflow": f"replay_board+tradeflow + {suffix}",
        "replay_research": f"replay_board+tradeflow + {suffix}",
    }
    if data_source == "unknown":
        return f"unknown + {suffix}"
    return labels.get(data_source, f"{data_source} + {suffix}")


class AiReasoningState(TypedDict):
    spread: float
    imbalance: float
    delta: float
    wall_ratio: float | None
    pressure_bias: str | None
    regime: str
    best_strategy: str
    source_label: str
    source: str
    data_source: str


def build_ai_reasoning_state() -> AiReasoningState | None:
    signal_state = load_market_signal_context()
    if not signal_state:
        return None

    data_source = str(signal_state.get("data_source") or "unknown")
    source_label = _source_label_for_data_source(
        data_source,
        suffix="research_experiment",
    )

    return {
        "spread": signal_state.get("spread"),
        "imbalance": signal_state.get("imbalance"),
        "delta": signal_state.get("delta"),
        "wall_ratio": signal_state.get("wall_ratio"),
        "pressure_bias": signal_state.get("pressure_bias"),
        "regime": signal_state.get("regime"),
        "best_strategy": signal_state.get("best_strategy"),
        "source_label": source_label,
        "source": source_label,
        "data_source": data_source,
    }