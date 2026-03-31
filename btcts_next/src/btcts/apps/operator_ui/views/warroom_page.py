# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py
# desc: Replay / Research artifact を基に市場分析と AI 解釈を行う War Room 専用ページ。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components import agent_panels
from btcts.apps.operator_ui.components import ai_conversation_panel
from btcts.apps.operator_ui.components import ai_market_summary_panel
from btcts.apps.operator_ui.components import ai_reasoning_panel
from btcts.apps.operator_ui.components import ai_operator_panel
from btcts.apps.operator_ui.components import live_shell
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
from btcts.apps.operator_ui.components.live_shell import get_registered_slots, make_slot_meta


def render():
    lang = st.session_state.get("ui_lang", "en")

    live_shell.render_compact_page_header(get_text(lang, "warroom_title"))

    with live_shell.render_folded_section(get_text(lang, "ui_label_guide"), expanded=False):
        st.caption(
            get_text(lang, "warroom_caption")
        )

    with live_shell.zone_container(
        label=get_text(lang, "ui_label_overview"),
        zone_kind="overview",
    ):
        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "overview",
                "warroom_header",
                label=None,
                tone="primary",
                refresh_mode="poll_normal",
                priority=10,
            )
        ):
            warroom_header.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "overview",
                "warroom_alert_engine",
                label=None,
                tone="primary",
                refresh_mode="poll_normal",
                priority=20,
            )
        ):
            warroom_alert_engine.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "overview",
                "ai_operator_panel",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=30,
            )
        ):
            ai_operator_panel.render()
    with live_shell.zone_container(
        label=get_text(lang, "ui_label_operator_support"),
        zone_kind="secondary",
    ):
        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "secondary",
                "decision_log_panel",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=40,
            )
        ):
            decision_log_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "secondary",
                "watch_list_panel",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=50,
            )
        ):
            watch_list_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "secondary",
                "warroom_timeline",
                label=None,
                tone="primary",
                refresh_mode="poll_normal",
                priority=60,
            )
        ):
            warroom_timeline.render()

    with live_shell.zone_container(
        label=get_text(lang, "ui_label_primary_live"),
        zone_kind="primary_live",
    ):
        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "primary_live",
                "market_regime",
                label=None,
                tone="primary",
                refresh_mode="poll_normal",
                priority=35,
            )
        ):
            market_regime_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "primary_live",
                "market_monitor",
                label=None,
                tone="primary",
                refresh_mode="poll_fast",
                priority=30,
            )
        ):
            market_monitor.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "primary_live",
                "liquidity_pressure",
                label=None,
                tone="primary",
                refresh_mode="poll_fast",
                priority=20,
            )
        ):
            liquidity_pressure_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "primary_live",
                "trade_flow_monitor",
                label=None,
                tone="primary",
                refresh_mode="poll_fast",
                priority=10,
            )
        ):
            trade_flow_monitor.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "primary_live",
                "ai_signal",
                label=None,
                tone="primary",
                refresh_mode="poll_normal",
                priority=40,
            )
        ):
            ai_signal_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "primary_live",
                "strategy_state",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=45,
            )
        ):
            strategy_state_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "primary_live",
                "risk_monitor",
                label=None,
                tone="primary",
                refresh_mode="poll_normal",
                priority=50,
            )
        ):
            risk_monitor_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "primary_live",
                "agent_panels",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=60,
            )
        ):
            agent_panels.render()

    with live_shell.render_folded_section(get_text(lang, "ui_slot_diagnostics_title"), expanded=False):
        slot_rows = get_registered_slots("warroom")
        if slot_rows:
            st.dataframe(slot_rows, width="stretch")
        else:
            st.info(get_text(lang, "ui_slot_registry_empty_warroom"))

    with live_shell.render_folded_section(get_text(lang, "ui_label_ai_diagnostics"), expanded=False):
        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "ai_diagnostics",
                "ai_reasoning_panel",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=70,
            )
        ):
            ai_reasoning_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "ai_diagnostics",
                "ai_market_summary_panel",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=80,
            )
        ):
            ai_market_summary_panel.render()

        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "warroom",
                "ai_diagnostics",
                "ai_conversation_panel",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=90,
            )
        ):
            ai_conversation_panel.render()