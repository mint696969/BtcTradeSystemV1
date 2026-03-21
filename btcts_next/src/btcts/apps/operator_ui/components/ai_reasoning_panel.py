# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_reasoning_panel.py
# desc: Replay / Research artifact を基に、AI が現在の市場解釈理由を説明する War Room パネル。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
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


def _headline(lang: str, regime: str, imbalance, delta, pressure_bias: str | None) -> str:
    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            return get_text(lang, "ai_reasoning_headline_long")

    if regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            return get_text(lang, "ai_reasoning_headline_short")

    if pressure_bias == "buy_pressure":
        return get_text(lang, "ai_reasoning_headline_buy_pressure")

    if pressure_bias == "sell_pressure":
        return get_text(lang, "ai_reasoning_headline_sell_pressure")

    return get_text(lang, "ai_reasoning_headline_wait")


def _reason_lines(lang: str, spread, imbalance, delta, wall_ratio, regime: str, best_strategy: str) -> list[str]:
    lines: list[str] = []

    if isinstance(spread, (int, float)):
        if spread > 7000:
            lines.append(get_text(lang, "ai_reasoning_reason_spread_wide"))
        elif spread < 3000:
            lines.append(get_text(lang, "ai_reasoning_reason_spread_tight"))
        else:
            lines.append(get_text(lang, "ai_reasoning_reason_spread_normal"))

    if isinstance(imbalance, (int, float)):
        if imbalance > 0.2:
            lines.append(get_text(lang, "ai_reasoning_reason_bid_bias"))
        elif imbalance < -0.2:
            lines.append(get_text(lang, "ai_reasoning_reason_ask_bias"))
        else:
            lines.append(get_text(lang, "ai_reasoning_reason_balance_mixed"))

    if isinstance(delta, (int, float)):
        if delta > 0.2:
            lines.append(get_text(lang, "ai_reasoning_reason_buy_flow"))
        elif delta < -0.2:
            lines.append(get_text(lang, "ai_reasoning_reason_sell_flow"))
        else:
            lines.append(get_text(lang, "ai_reasoning_reason_flow_mixed"))

    if isinstance(wall_ratio, (int, float)):
        if wall_ratio > 0.25:
            lines.append(get_text(lang, "ai_reasoning_reason_bid_wall"))
        elif wall_ratio < -0.25:
            lines.append(get_text(lang, "ai_reasoning_reason_ask_wall"))

    lines.append(f"regime={regime}")
    lines.append(f"best_strategy={best_strategy}")

    return lines


def _conclusion(lang: str, regime: str, imbalance, delta, wall_ratio) -> str:
    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            return get_text(lang, "ai_reasoning_conclusion_long_watch")

    if regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            return get_text(lang, "ai_reasoning_conclusion_short_watch")

    if isinstance(wall_ratio, (int, float)) and abs(wall_ratio) > 0.45:
        return get_text(lang, "ai_reasoning_conclusion_wall_risk")

    return get_text(lang, "ai_reasoning_conclusion_wait")


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

        return {
            "spread": float(live_spread),
            "imbalance": None if imbalance is None else float(imbalance),
            "delta": float(live_delta),
            "wall_ratio": None,
            "pressure_bias": "live_orderbook",
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
        "wall_ratio": board.get("wall_ratio"),
        "pressure_bias": board.get("pressure_bias"),
        "regime": latest_regime_name(experiment_payload),
        "best_strategy": latest_best_strategy_name(experiment_payload),
        "source": "replay_board+tradeflow + research_experiment",
    }


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'ai_reasoning_title')}")

    state = _analyze_live_or_fallback()
    if not state:
        st.warning(get_text(lang, "ai_reasoning_missing_data"))
        return

    spread = state.get("spread")
    imbalance = state.get("imbalance")
    pressure_bias = state.get("pressure_bias")
    wall_ratio = state.get("wall_ratio")
    delta = state.get("delta")

    regime = state.get("regime") or "unknown"
    best_strategy = state.get("best_strategy") or "-"

    st.info(_headline(lang, regime, imbalance, delta, pressure_bias))

    spread_state = "-"
    if isinstance(spread, (int, float)):
        if spread > 7000:
            spread_state = "wide"
        elif spread < 3000:
            spread_state = "tight"
        else:
            spread_state = "normal"

    imbalance_state = "-"
    if isinstance(imbalance, (int, float)):
        if imbalance > 0.2:
            imbalance_state = "bid_bias"
        elif imbalance < -0.2:
            imbalance_state = "ask_bias"
        else:
            imbalance_state = "mixed"

    delta_state = "-"
    if isinstance(delta, (int, float)):
        if delta > 0.2:
            delta_state = "buy_flow"
        elif delta < -0.2:
            delta_state = "sell_flow"
        else:
            delta_state = "mixed"

    wall_state = "-"
    if isinstance(wall_ratio, (int, float)):
        if wall_ratio > 0.25:
            wall_state = "bid_wall"
        elif wall_ratio < -0.25:
            wall_state = "ask_wall"
        else:
            wall_state = "neutral"

    c1, c2, c3 = st.columns(3)
    c1.metric("spread", spread_state)
    c2.metric("imbalance", imbalance_state)
    c3.metric("delta", delta_state)

    c4, c5, c6 = st.columns(3)
    c4.metric("wall", wall_state)
    c5.metric("regime", regime or "-")
    c6.metric("strategy", best_strategy or "-")

    st.markdown(f"**{get_text(lang, 'ai_reasoning_reasons')}**")
    for line in _reason_lines(lang, spread, imbalance, delta, wall_ratio, regime, best_strategy):
        st.markdown(f"- {line}")

    st.markdown(f"**{get_text(lang, 'ai_reasoning_conclusion')}**")
    st.success(_conclusion(lang, regime, imbalance, delta, wall_ratio))
    st.caption(f"source={state.get('source', 'unknown')}")
    
    st.divider()