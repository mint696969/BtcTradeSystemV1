# path: ./btcts_next/src/btcts/apps/operator_ui/components/strategy_state_panel.py
# desc: Market / Liquidity / Trade Flow と Research の最新実験結果から現在の戦略状態を表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_execution_market_prediction_summary_widget_model,
    load_execution_market_prediction_tactic_proposal_payload,
    load_execution_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (
    build_tactic_compact_reading_line,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.components.prediction_summary_presenter import (
    prediction_compact_reading_line,
    prediction_snapshot_lines,
)
from btcts.apps.operator_ui.components.research_bridge import load_latest_experiment_payload
from btcts.apps.operator_ui.ui_text import get_text


def _mode_badge_class(value: str) -> str:
    if value in ("上昇トレンド", "LONG TREND"):
        return "badge-buy"

    if value in ("下降トレンド", "SHORT TREND"):
        return "badge-sell"

    if value in ("中立", "NEUTRAL"):
        return "badge-neutral"

    return "badge-wait"


def _risk_badge_class(value: str) -> str:
    if value in ("高", "HIGH"):
        return "badge-risk-high"

    if value in ("低", "LOW"):
        return "badge-risk-low"

    return "badge-neutral"


def _strategy_display_name(name: str, lang: str) -> str:
    mapping = {
        "microstructure_v1": "Microstructure v1",
        "regime_aware_microstructure_v1": "Regime-aware Microstructure v1",
        "baseline_none": "Baseline None",
    }
    return mapping.get(name, name)


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'strategy_state_title')}")

    payload = load_latest_experiment_payload()
    if not payload:
        st.warning(get_text(lang, "strategy_state_artifact_missing"))
        return

    summary = payload.get("summary") or {}
    best_strategy = payload.get("best_strategy") or {}
    regime_report = payload.get("regime_report") or {}

    regime = str(regime_report.get("regime") or summary.get("regime") or "unknown")
    best_name = str(best_strategy.get("strategy") or summary.get("best_strategy") or "unknown")
    summary_widget = load_execution_market_summary_widget_model()
    prediction_widget = load_execution_market_prediction_summary_widget_model()
    tactic_payload = load_execution_market_prediction_tactic_proposal_payload()
    total_pnl = float(best_strategy.get("total_pnl") or 0.0)
    wins = int(best_strategy.get("wins") or 0)
    losses = int(best_strategy.get("losses") or 0)
    trade_count = int(best_strategy.get("trade_count") or 0)

    strategy_mode = get_text(lang, "strategy_state_value_neutral")
    risk_state = get_text(lang, "strategy_state_value_medium")
    confidence = 0.50
    recommended_archetype = _strategy_display_name(best_name, lang)

    if regime == "trend_up":
        strategy_mode = get_text(lang, "strategy_state_value_long_trend")
        risk_state = get_text(lang, "strategy_state_value_low")
        confidence = 0.78
    elif regime == "trend_down":
        strategy_mode = get_text(lang, "strategy_state_value_short_trend")
        risk_state = get_text(lang, "strategy_state_value_low")
        confidence = 0.78
    elif regime == "range":
        strategy_mode = get_text(lang, "strategy_state_value_range_scalp")
        risk_state = get_text(lang, "strategy_state_value_medium")
        confidence = 0.64
    elif regime == "liquidity_vacuum":
        strategy_mode = get_text(lang, "strategy_state_value_volatility_watch")
        risk_state = get_text(lang, "strategy_state_value_high")
        confidence = 0.59
    elif regime == "absorption_zone":
        strategy_mode = get_text(lang, "strategy_state_value_volatility_watch")
        risk_state = get_text(lang, "strategy_state_value_medium")
        confidence = 0.74
    elif regime == "sweep_risk":
        strategy_mode = get_text(lang, "strategy_state_value_volatility_watch")
        risk_state = get_text(lang, "strategy_state_value_high")
        confidence = 0.57

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "strategy_state_mode"), strategy_mode)
    c2.metric(get_text(lang, "strategy_state_risk"), risk_state)
    c3.metric(get_text(lang, "strategy_state_archetype"), recommended_archetype)
    c4.metric(get_text(lang, "strategy_state_confidence"), round(confidence, 2))

    st.markdown(
        f"""
        <div class="warroom-badges">
            <span class="warroom-badge {_mode_badge_class(strategy_mode)}">
                {get_text(lang, 'badge_strategy_mode')}: {strategy_mode}
            </span>
            <span class="warroom-badge {_risk_badge_class(risk_state)}">
                {get_text(lang, 'badge_risk_state')}: {risk_state}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        f"{get_text(lang, 'strategy_state_research_summary')}: "
        f"regime={regime} / best={recommended_archetype} / "
        f"PnL={round(total_pnl, 2)} / wins={wins} / losses={losses} / trades={trade_count}"
    )

    with st.expander(get_text(lang, "strategy_state_artifact_title")):
        st.json(
            {
                "summary": summary,
                "best_strategy": best_strategy,
                "regime_report": regime_report,
            }
        )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    tactic_reading = build_tactic_compact_reading_line(tactic_payload)
    if tactic_reading != "tactic_reading unavailable":
        st.caption(tactic_reading)

    prediction_reading = prediction_compact_reading_line(prediction_widget)
    if prediction_reading != "prediction_reading unavailable":
        st.caption(prediction_reading)

    prediction_lines = prediction_snapshot_lines(prediction_widget)
    if prediction_lines:
        st.markdown("**Prediction snapshot**")
        for line in prediction_lines:
            st.markdown(f"- {line}")

    st.divider()