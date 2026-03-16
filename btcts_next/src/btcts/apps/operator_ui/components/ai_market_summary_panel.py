# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_market_summary_panel.py
# desc: Replay / Research artifact から市場状況を文章で要約する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_best_strategy_name,
    latest_board_row,
    latest_regime_name,
    latest_trade_row,
    load_latest_experiment_payload,
    load_latest_replay_payload,
    tradeflow_metrics,
)
from btcts.apps.operator_ui.ui_text import get_text


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'ai_summary_title')}")

    replay_payload = load_latest_replay_payload()
    experiment_payload = load_latest_experiment_payload()

    board = board_signal_metrics(latest_board_row(replay_payload))
    flow = tradeflow_metrics(latest_trade_row(replay_payload))

    if not board or not flow:
        st.warning(get_text(lang, "ai_summary_missing_data"))
        return

    spread = board.get("spread")
    imbalance = board.get("imbalance")
    pressure_bias = board.get("pressure_bias")
    delta = flow.get("trade_delta")

    regime = latest_regime_name(experiment_payload)
    best_strategy = latest_best_strategy_name(experiment_payload)

    if pressure_bias == "buy_pressure" or (isinstance(imbalance, (int, float)) and imbalance > 0.2):
        headline = get_text(lang, "ai_summary_value_buy_bias")
    elif pressure_bias == "sell_pressure" or (isinstance(imbalance, (int, float)) and imbalance < -0.2):
        headline = get_text(lang, "ai_summary_value_sell_bias")
    else:
        headline = get_text(lang, "ai_summary_value_neutral_bias")

    bullets = []

    if isinstance(spread, (int, float)):
        if spread > 7000:
            bullets.append(get_text(lang, "ai_summary_value_wide_spread"))
        elif spread < 3000:
            bullets.append(get_text(lang, "ai_summary_value_tight_spread"))

    if isinstance(delta, (int, float)):
        if delta > 0:
            bullets.append(get_text(lang, "ai_summary_value_buy_flow"))
        elif delta < 0:
            bullets.append(get_text(lang, "ai_summary_value_sell_flow"))

    bullets.append(f"regime={regime}")
    bullets.append(f"best_strategy={best_strategy}")

    if regime in {"trend_up"} and isinstance(delta, (int, float)) and delta > 0:
        outlook = get_text(lang, "ai_summary_value_long_watch")
    elif regime in {"trend_down"} and isinstance(delta, (int, float)) and delta < 0:
        outlook = get_text(lang, "ai_summary_value_short_watch")
    elif regime == "absorption_zone":
        if isinstance(delta, (int, float)) and delta < 0:
            outlook = get_text(lang, "ai_summary_value_short_watch")
        elif isinstance(delta, (int, float)) and delta > 0:
            outlook = get_text(lang, "ai_summary_value_long_watch")
        else:
            outlook = get_text(lang, "ai_summary_value_wait")
    else:
        outlook = get_text(lang, "ai_summary_value_wait")

    st.markdown(f"**{get_text(lang, 'ai_summary_headline')}**")
    st.info(headline)

    st.markdown(f"**{get_text(lang, 'ai_summary_bullets')}**")
    if bullets:
        for item in bullets:
            st.markdown(f"- {item}")
    else:
        st.markdown("-")

    st.markdown(f"**{get_text(lang, 'ai_summary_outlook')}**")
    st.success(outlook)

    st.divider()