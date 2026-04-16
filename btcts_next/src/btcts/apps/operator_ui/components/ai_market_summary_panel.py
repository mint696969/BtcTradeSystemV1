# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_market_summary_panel.py
# desc: Replay / Research artifact から市場状況を文章で要約する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.ai_market_summary_state import (
    build_ai_market_summary_state,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
    load_prediction_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.components.prediction_summary_presenter import (
    prediction_snapshot_lines,
)
from btcts.apps.operator_ui.ui_text import get_text


def _analyze_live_or_fallback():
    return build_ai_market_summary_state()


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'ai_summary_title')}")

    state = _analyze_live_or_fallback()
    if not state:
        st.warning(get_text(lang, "ai_summary_missing_data"))
        return

    summary_widget = load_market_summary_widget_model()
    prediction_widget = load_prediction_summary_widget_model()

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