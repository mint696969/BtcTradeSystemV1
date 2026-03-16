# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py
# desc: Replay / Research artifact を基に市場分析と AI 解釈を行う War Room 専用ページ。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components import agent_panels
from btcts.apps.operator_ui.components import ai_conversation_panel
from btcts.apps.operator_ui.components import ai_market_summary_panel
from btcts.apps.operator_ui.components import ai_reasoning_panel
from btcts.apps.operator_ui.components import ai_operator_panel
from btcts.apps.operator_ui.components import ai_signal_panel
from btcts.apps.operator_ui.components import liquidity_pressure_panel
from btcts.apps.operator_ui.components import market_monitor
from btcts.apps.operator_ui.components import market_regime_panel
from btcts.apps.operator_ui.components import risk_monitor_panel
from btcts.apps.operator_ui.components import strategy_state_panel
from btcts.apps.operator_ui.components import trade_flow_monitor
from btcts.apps.operator_ui.components import watch_list_panel
from btcts.apps.operator_ui.components import warroom_header
from btcts.apps.operator_ui.components import warroom_timeline
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.components import warroom_alert_engine
from btcts.apps.operator_ui.components import decision_log_panel


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.title(get_text(lang, "warroom_title"))

    st.caption(
        get_text(lang, "warroom_caption")
    )

    warroom_header.render()
    warroom_alert_engine.render()
    ai_operator_panel.render()
    decision_log_panel.render()
    watch_list_panel.render()
    warroom_timeline.render()

    market_regime_panel.render()
    market_monitor.render()
    liquidity_pressure_panel.render()
    trade_flow_monitor.render()
    ai_signal_panel.render()
    strategy_state_panel.render()
    risk_monitor_panel.render()
    agent_panels.render()
    ai_reasoning_panel.render()
    ai_market_summary_panel.render()
    ai_conversation_panel.render()