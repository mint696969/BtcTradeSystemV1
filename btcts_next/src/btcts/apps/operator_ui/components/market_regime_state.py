# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_regime_state.py
# desc: Market regime panel 用の market signal state adapter.

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
    source_label = _source_label_for_data_source(
        data_source,
        suffix="research_experiment",
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