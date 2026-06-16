# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_signal_panel.py
# desc: Replay / Research artifact を基に簡易 AI シグナルを生成する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.ai_signal_state import (
    build_ai_signal_state,
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


def _badge_class(value: str) -> str:
    if value in ("LONG BIAS", "ロング寄り"):
        return "badge-buy"

    if value in ("SHORT BIAS", "ショート寄り"):
        return "badge-sell"

    if value in ("WAIT", "待機"):
        return "badge-wait"

    return "badge-neutral"


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'ai_signal_title')}")

    signal_state = build_ai_signal_state()
    if not signal_state:
        st.warning(get_text(lang, "ai_signal_missing_data"))
        return

    imbalance = signal_state.get("imbalance")
    delta = signal_state.get("delta")
    regime = str(signal_state.get("regime") or "unknown")
    best_strategy = str(signal_state.get("best_strategy") or "unknown")
    replay_ts = signal_state.get("replay_ts")
    source_label = str(signal_state.get("source_label") or "unknown")
    summary_widget = load_execution_market_summary_widget_model()
    prediction_widget = load_execution_market_prediction_summary_widget_model()

    regime_label = get_text(lang, "ai_signal_value_range")
    if regime in {"trend_up", "trend_down"}:
        regime_label = get_text(lang, "ai_signal_value_trend")
    elif regime == "liquidity_vacuum":
        regime_label = get_text(lang, "warroom_value_liquidity_vacuum")
    elif regime == "absorption_zone":
        regime_label = get_text(lang, "warroom_value_absorption")

    decision = get_text(lang, "ai_signal_value_wait")

    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            decision = get_text(lang, "ai_signal_value_long_bias")

    elif regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            decision = get_text(lang, "ai_signal_value_short_bias")

    elif regime == "absorption_zone":
        if best_strategy in {"microstructure_v1", "regime_aware_microstructure_v1"}:
            if isinstance(delta, (int, float)) and delta < 0:
                decision = get_text(lang, "ai_signal_value_short_bias")
            elif isinstance(delta, (int, float)) and delta > 0:
                decision = get_text(lang, "ai_signal_value_long_bias")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "ai_signal_market_regime"), regime_label)
    c2.metric(
        get_text(lang, "ai_signal_orderbook_bias"),
        "-" if imbalance is None else round(float(imbalance), 3),
    )
    c3.metric(
        get_text(lang, "ai_signal_trade_delta"),
        "-" if delta is None else round(float(delta), 4),
    )
    c4.metric(get_text(lang, "ai_signal_decision"), decision)

    st.markdown(
        f"""
        <div class="warroom-badges">
            <span class="warroom-badge {_badge_class(decision)}">
                {get_text(lang, 'badge_ai_decision')}: {decision}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"best_strategy={best_strategy} / replay_ts={replay_ts} / "
        f"source={source_label}"
    )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    prediction_lines = prediction_snapshot_lines(prediction_widget)
    if prediction_lines:
        st.markdown("**Prediction snapshot**")
        for line in prediction_lines:
            st.markdown(f"- {line}")

    st.divider()