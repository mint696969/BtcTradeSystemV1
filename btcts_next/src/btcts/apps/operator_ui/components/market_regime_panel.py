# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_regime_panel.py
# desc: Live canonical 優先、research regime 補助、replay fallback で市場レジームを表示する WarRoom パネル

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
from btcts.apps.operator_ui.components.live_bridge import latest_live_board_metrics


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

    experiment_payload = load_latest_experiment_payload()

    live_board = latest_live_board_metrics()
    board = None
    source_label = "replay_board + research_experiment"

    if live_board:
        bid_depth = live_board.get("bid_depth")
        ask_depth = live_board.get("ask_depth")
        spread = live_board.get("spread")

        imbalance = None
        pressure_bias = "neutral"

        if bid_depth is not None and ask_depth is not None:
            try:
                bid_depth_f = float(bid_depth)
                ask_depth_f = float(ask_depth)
                denom = bid_depth_f + ask_depth_f
                if denom > 0:
                    imbalance = (bid_depth_f - ask_depth_f) / denom
                    if imbalance > 0.2:
                        pressure_bias = "buy_pressure"
                    elif imbalance < -0.2:
                        pressure_bias = "sell_pressure"
            except Exception:
                imbalance = None
                pressure_bias = "neutral"

        board = {
            "spread": spread,
            "imbalance": imbalance,
            "pressure_bias": pressure_bias,
            "event_ts": live_board.get("event_ts"),
        }
        source_label = "live_canonical + research_experiment"

    if not board:
        replay_payload = load_latest_replay_payload()
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
        f"ts={board.get('event_ts')} / spread={board.get('spread')} / "
        f"imbalance={board.get('imbalance')}"
    )

    st.caption(f"source={source_label}")

    st.divider()