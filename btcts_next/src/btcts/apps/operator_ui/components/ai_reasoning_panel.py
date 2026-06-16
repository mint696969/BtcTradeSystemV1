# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_reasoning_panel.py
# desc: Replay / Research artifact を基に、AI が現在の市場解釈理由を説明する War Room パネル。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.ai_reasoning_state import (
    build_ai_reasoning_state,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_execution_market_prediction_summary_widget_model,
    load_execution_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.components.prediction_summary_presenter import (
    prediction_snapshot_lines,
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
    return build_ai_reasoning_state()


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
    summary_widget = load_execution_market_summary_widget_model()
    prediction_widget = load_execution_market_prediction_summary_widget_model()

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
    c1.metric(get_text(lang, "ai_reasoning_metric_spread"), spread_state)
    c2.metric(get_text(lang, "ai_reasoning_metric_imbalance"), imbalance_state)
    c3.metric(get_text(lang, "ai_reasoning_metric_delta"), delta_state)

    c4, c5, c6 = st.columns(3)
    c4.metric(get_text(lang, "ai_reasoning_metric_wall"), wall_state)
    c5.metric(get_text(lang, "ai_reasoning_metric_regime"), regime or "-")
    c6.metric(get_text(lang, "ai_reasoning_metric_strategy"), best_strategy or "-")

    st.markdown(f"**{get_text(lang, 'ai_reasoning_reasons')}**")
    for line in _reason_lines(lang, spread, imbalance, delta, wall_ratio, regime, best_strategy):
        st.markdown(f"- {line}")

    st.markdown(f"**{get_text(lang, 'ai_reasoning_conclusion')}**")
    st.success(_conclusion(lang, regime, imbalance, delta, wall_ratio))
    st.caption(
        get_text(lang, "warroom_generic_source_caption").format(
            source=state.get("source_label") or state.get("source", "unknown"),
        )
    )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    prediction_lines = prediction_snapshot_lines(prediction_widget)
    if prediction_lines:
        st.markdown("**Prediction snapshot**")
        for line in prediction_lines:
            st.markdown(f"- {line}")

    st.divider()