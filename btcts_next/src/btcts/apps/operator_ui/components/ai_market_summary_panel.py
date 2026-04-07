# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_market_summary_panel.py
# desc: Replay / Research artifact から市場状況を文章で要約する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
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


def _analyze_live_or_fallback():
    live_board = latest_live_board_metrics()
    live_flow = recent_live_tradeflow_metrics(lines=80)
    experiment_payload = load_latest_experiment_payload()

    fallback_regime = latest_regime_name(experiment_payload)
    fallback_best_strategy = latest_best_strategy_name(experiment_payload)

    live_spread = live_board.get("spread")
    live_delta = live_flow.get("delta")

    if live_spread is not None and live_delta is not None:
        bid_depth = live_board.get("bid_depth")
        ask_depth = live_board.get("ask_depth")

        imbalance = None
        if bid_depth is not None and ask_depth is not None:
            try:
                bid_depth_f = float(bid_depth)
                ask_depth_f = float(ask_depth)
                denom = bid_depth_f + ask_depth_f
                if denom > 0:
                    imbalance = (bid_depth_f - ask_depth_f) / denom
            except Exception:
                imbalance = None

        pressure_bias = "neutral_bias"
        if isinstance(imbalance, (int, float)):
            if imbalance > 0.2:
                pressure_bias = "buy_pressure"
            elif imbalance < -0.2:
                pressure_bias = "sell_pressure"

        return {
            "spread": float(live_spread),
            "imbalance": None if imbalance is None else float(imbalance),
            "delta": float(live_delta),
            "pressure_bias": pressure_bias,
            "regime": fallback_regime if fallback_regime != "unknown" else "live_canonical",
            "best_strategy": fallback_best_strategy,
            "source": "live_canonical + research_experiment",
        }

    replay_payload = load_latest_replay_payload()
    board = board_signal_metrics(latest_board_row(replay_payload))
    flow = tradeflow_metrics(latest_trade_row(replay_payload))

    if not board or not flow:
        return None

    return {
        "spread": board.get("spread"),
        "imbalance": board.get("imbalance"),
        "delta": flow.get("trade_delta"),
        "pressure_bias": board.get("pressure_bias"),
        "regime": latest_regime_name(experiment_payload),
        "best_strategy": latest_best_strategy_name(experiment_payload),
        "source": "replay_board+tradeflow + research_experiment",
    }


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'ai_summary_title')}")

    state = _analyze_live_or_fallback()
    if not state:
        st.warning(get_text(lang, "ai_summary_missing_data"))
        return

    summary_widget = load_market_summary_widget_model()

    spread = state.get("spread")
    imbalance = state.get("imbalance")
    pressure_bias = state.get("pressure_bias")
    delta = state.get("delta")

    regime = state.get("regime") or "unknown"
    best_strategy = state.get("best_strategy") or "-"

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
        st.markdown(f"- {get_text(lang, 'warroom_value_unknown')}")

    st.markdown(f"**{get_text(lang, 'ai_summary_outlook')}**")
    st.success(outlook)
    st.caption(
        get_text(lang, "warroom_generic_source_caption").format(
            source=state.get("source", "unknown"),
        )
    )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()