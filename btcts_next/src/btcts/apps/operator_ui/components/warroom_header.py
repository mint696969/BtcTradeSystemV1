# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py
# desc: Replay / Research artifact を要約し、War Room 冒頭に現在の戦況サマリーを表示するヘッダーパネル。

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


def _spread_state(spread: float | None, lang: str) -> str:
    if spread is None:
        return get_text(lang, "warroom_value_unknown")

    if spread >= 7000:
        return get_text(lang, "warroom_value_wide")

    if spread <= 3000:
        return get_text(lang, "warroom_value_tight")

    return get_text(lang, "warroom_value_normal")


def _pressure_label(pressure_bias: str | None, lang: str) -> str:
    if pressure_bias == "buy_pressure":
        return get_text(lang, "warroom_value_buy")
    if pressure_bias == "sell_pressure":
        return get_text(lang, "warroom_value_sell")
    return get_text(lang, "warroom_value_neutral")


def _risk_level(spread, imbalance, delta, wall_ratio):
    score = 0

    if isinstance(spread, (int, float)):
        if spread > 7000:
            score += 2
        elif spread > 4500:
            score += 1

    if isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if (imbalance > 0.2 and delta < 0) or (imbalance < -0.2 and delta > 0):
            score += 2

    if isinstance(wall_ratio, (int, float)):
        if abs(wall_ratio) > 0.45:
            score += 2
        elif abs(wall_ratio) > 0.25:
            score += 1

    if score >= 4:
        return "HIGH"
    if score >= 2:
        return "MEDIUM"
    return "LOW"


def _risk_label(level: str, lang: str) -> str:
    mapping = {
        "LOW": get_text(lang, "warroom_value_low"),
        "MEDIUM": get_text(lang, "warroom_value_medium"),
        "HIGH": get_text(lang, "warroom_value_high"),
    }
    return mapping.get(level, level)


def _ai_decision(regime: str, imbalance, delta, lang: str) -> str:
    decision = get_text(lang, "warroom_value_wait")

    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            decision = get_text(lang, "warroom_value_long_bias")

    elif regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            decision = get_text(lang, "warroom_value_short_bias")

    return decision


def _regime_label(regime: str, lang: str) -> str:
    mapping = {
        "range": get_text(lang, "warroom_value_range"),
        "trend_up": get_text(lang, "warroom_value_trend"),
        "trend_down": get_text(lang, "warroom_value_trend"),
        "liquidity_vacuum": get_text(lang, "warroom_value_liquidity_vacuum"),
        "absorption_zone": get_text(lang, "warroom_value_absorption"),
    }
    return mapping.get(regime, regime or get_text(lang, "warroom_value_unknown"))


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'warroom_header_title')}")

    replay_payload = load_latest_replay_payload()
    experiment_payload = load_latest_experiment_payload()

    board = board_signal_metrics(latest_board_row(replay_payload))
    flow = tradeflow_metrics(latest_trade_row(replay_payload))

    if not board or not flow:
        st.warning(get_text(lang, "warroom_header_missing_data"))
        return

    regime = latest_regime_name(experiment_payload)
    best_strategy = latest_best_strategy_name(experiment_payload)

    spread = board.get("spread")
    imbalance = board.get("imbalance")
    pressure_bias = board.get("pressure_bias")
    wall_ratio = board.get("wall_ratio")
    delta = flow.get("trade_delta")

    spread_state = _spread_state(spread, lang)
    pressure = _pressure_label(pressure_bias, lang)
    risk_level = _risk_level(spread, imbalance, delta, wall_ratio)
    risk_label = _risk_label(risk_level, lang)
    ai_decision = _ai_decision(regime, imbalance, delta, lang)

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(get_text(lang, "warroom_header_regime"), _regime_label(regime, lang))
    c2.metric(get_text(lang, "warroom_header_spread_state"), spread_state)
    c3.metric(get_text(lang, "warroom_header_pressure"), pressure)
    c4.metric(
        get_text(lang, "warroom_header_trade_flow"),
        "-" if delta is None else round(float(delta), 4),
    )
    c5.metric(get_text(lang, "warroom_header_ai_decision"), ai_decision)
    c6.metric(get_text(lang, "warroom_header_risk"), risk_label)

    st.caption(
        f"best_strategy={best_strategy} / "
        f"spread={spread} / imbalance={imbalance} / wall_ratio={wall_ratio}"
    )

    st.divider()