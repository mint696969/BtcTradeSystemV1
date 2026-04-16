# path: ./btcts_next/src/btcts/apps/operator_ui/components/agent_panels.py
# desc: Live canonical / Research / Audit 優先で Analyst AI / Strategy AI / Risk AI を表示する WarRoom エージェントパネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.agent_logic import (
    analyst_view,
    risk_view,
    strategy_view,
)
from btcts.apps.operator_ui.components.agent_state import (
    analyze_agent_state,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_prediction_summary_widget_model,
)
from btcts.apps.operator_ui.components.prediction_summary_presenter import (
    prediction_snapshot_lines,
)
from btcts.apps.operator_ui.ui_text import get_text


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'agent_panels_title')}")

    state = analyze_agent_state()
    if not state:
        st.warning(get_text(lang, "agent_panels_missing_data"))
        return

    audit_rows = state["audit_rows"]
    source_label = state["source_label"]
    regime = state["regime"]
    best_strategy = state["best_strategy"]
    spread = state["spread"]
    imbalance = state["imbalance"]
    pressure_bias = state["pressure_bias"]
    wall_ratio = state["wall_ratio"]
    delta = state["delta"]

    analyst_regime, analyst_spread, analyst_pressure = analyst_view(
        lang,
        regime,
        spread,
        pressure_bias,
    )

    strategy_arch, strategy_stance = strategy_view(
        lang,
        regime,
        best_strategy,
        imbalance,
        delta,
    )

    risk_level, avg_latency = risk_view(
        lang,
        spread,
        imbalance,
        delta,
        wall_ratio,
        audit_rows,
    )
    prediction_widget = load_prediction_summary_widget_model()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"#### {get_text(lang, 'agent_analyst_title')}")
        st.metric(get_text(lang, "agent_analyst_regime"), analyst_regime)
        st.metric(get_text(lang, "agent_analyst_spread"), analyst_spread)
        st.metric(get_text(lang, "agent_analyst_pressure"), analyst_pressure)

    with col2:
        st.markdown(f"#### {get_text(lang, 'agent_strategy_title')}")
        st.metric(get_text(lang, "agent_strategy_archetype"), strategy_arch)
        st.metric(get_text(lang, "agent_strategy_stance"), strategy_stance)
        st.metric(
            get_text(lang, "agent_strategy_delta"),
            "-" if delta is None else round(float(delta), 4),
        )

    with col3:
        st.markdown(f"#### {get_text(lang, 'agent_risk_title')}")
        st.metric(get_text(lang, "agent_risk_level"), risk_level)
        st.metric(get_text(lang, "agent_risk_latency"), avg_latency)
        st.metric(
            get_text(lang, "agent_risk_wall_ratio"),
            "-" if wall_ratio is None else round(float(wall_ratio), 3),
        )

    st.caption(
        f"{get_text(lang, 'agent_panels_snapshot')}: "
        f"regime={regime}, spread={spread}, imbalance={imbalance}, "
        f"delta={delta}, wall_ratio={wall_ratio}, best={best_strategy} / "
        f"source={source_label}"
    )

    prediction_lines = prediction_snapshot_lines(prediction_widget)
    if prediction_lines:
        st.markdown("**Prediction snapshot**")
        for line in prediction_lines:
            st.markdown(f"- {line}")

    st.divider()