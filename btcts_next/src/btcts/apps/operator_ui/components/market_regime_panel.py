# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_regime_panel.py
# desc: Live canonical 優先、research regime 補助、replay fallback で市場レジームを表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.market_regime_state import (
    build_market_regime_state,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_execution_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.ui_text import get_text


def _spread_state(spread: float | None, lang: str) -> str:
    if spread is None:
        return get_text(lang, "market_regime_value_normal")

    if spread >= 7000:
        return get_text(lang, "market_regime_value_wide")

    if spread <= 3000:
        return get_text(lang, "market_regime_value_tight")

    return get_text(lang, "market_regime_value_normal")


def _pressure_label(bias: str | None, lang: str) -> str:
    if bias == "buy_pressure":
        return get_text(lang, "market_regime_value_buy")
    if bias == "sell_pressure":
        return get_text(lang, "market_regime_value_sell")
    return get_text(lang, "market_regime_value_neutral")


def _regime_label(regime: str, lang: str) -> str:
    mapping = {
        "range": get_text(lang, "market_regime_value_range"),
        "trend_up": get_text(lang, "market_regime_value_trend"),
        "trend_down": get_text(lang, "market_regime_value_trend"),
        "liquidity_vacuum": get_text(lang, "market_regime_value_liquidity_vacuum"),
        "sweep_risk": get_text(lang, "market_regime_value_volatility_expansion"),
        "absorption_zone": get_text(lang, "warroom_value_absorption"),
    }
    return mapping.get(regime, regime)


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'market_regime_title')}")

    state = build_market_regime_state()
    if not state:
        st.warning(get_text(lang, "market_regime_missing_data"))
        return

    regime = str(state.get("regime") or "unknown")
    spread = state.get("spread")
    imbalance = state.get("imbalance")
    pressure_bias = state.get("pressure_bias")
    event_ts = state.get("event_ts")
    source_label = str(state.get("source_label") or "unknown")

    summary_widget = load_execution_market_summary_widget_model()
    spread_state = _spread_state(spread, lang)
    pressure = _pressure_label(pressure_bias, lang)

    flow_agreement = get_text(lang, "market_regime_value_mixed")
    if isinstance(imbalance, (int, float)):
        if imbalance > 0.2 and pressure_bias == "buy_pressure":
            flow_agreement = get_text(lang, "market_regime_value_buy_confirm")
        elif imbalance < -0.2 and pressure_bias == "sell_pressure":
            flow_agreement = get_text(lang, "market_regime_value_sell_confirm")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(get_text(lang, "market_regime_regime"), _regime_label(regime, lang))
    c2.metric(get_text(lang, "market_regime_spread_state"), spread_state)
    c3.metric(get_text(lang, "market_regime_pressure"), pressure)
    c4.metric(get_text(lang, "market_regime_flow_agreement"), flow_agreement)

    st.caption(
        f"ts={event_ts} / spread={spread} / "
        f"imbalance={imbalance}"
    )

    st.caption(f"source={source_label}")

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()