# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_regime_panel.py
# desc: Replay / Research artifact から市場レジームを表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_board_row,
    latest_regime_name,
    load_latest_experiment_payload,
    load_latest_replay_payload,
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
        "absorption_zone": "Absorption Zone",
    }
    return mapping.get(regime, regime)


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'market_regime_title')}")

    replay_payload = load_latest_replay_payload()
    experiment_payload = load_latest_experiment_payload()

    board = board_signal_metrics(latest_board_row(replay_payload))
    if not board:
        st.warning(get_text(lang, "market_regime_missing_data"))
        return

    regime = latest_regime_name(experiment_payload)
    spread_state = _spread_state(board.get("spread"), lang)
    pressure = _pressure_label(board.get("pressure_bias"), lang)

    flow_agreement = get_text(lang, "market_regime_value_mixed")
    imbalance = board.get("imbalance")
    if isinstance(imbalance, (int, float)):
        if imbalance > 0.2 and board.get("pressure_bias") == "buy_pressure":
            flow_agreement = get_text(lang, "market_regime_value_buy_confirm")
        elif imbalance < -0.2 and board.get("pressure_bias") == "sell_pressure":
            flow_agreement = get_text(lang, "market_regime_value_sell_confirm")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(get_text(lang, "market_regime_regime"), _regime_label(regime, lang))
    c2.metric(get_text(lang, "market_regime_spread_state"), spread_state)
    c3.metric(get_text(lang, "market_regime_pressure"), pressure)
    c4.metric(get_text(lang, "market_regime_flow_agreement"), flow_agreement)

    st.caption(
        f"Replay ts={board.get('event_ts')} / spread={board.get('spread')} / "
        f"imbalance={board.get('imbalance')}"
    )

    st.divider()