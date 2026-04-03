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
from btcts.apps.operator_ui.components.live_shell import get_registered_slots
from btcts.apps.operator_ui.components.slot_definitions import (
    warroom_chart_sensitive,
    warroom_chart_sensitive_count,
    warroom_graph_overlay_contract,
    warroom_graph_widget_bundle,
    warroom_layout_hints,
    warroom_overlay_contract_count,
    warroom_overlay_enabled,
    warroom_overlay_widget_ids,
    warroom_partial_update_enabled,
    warroom_refresh_mode_counts,
    warroom_refresh_policy,
    warroom_slot,
)


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
            warroom_slot(
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
            warroom_slot(
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
            warroom_slot(
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
            warroom_slot(
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
            warroom_slot(
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
            warroom_slot(
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
            warroom_slot(
                "primary_live",
                "market_regime",
                label=None,
                tone="primary",
                refresh_mode="poll_normal",
                priority=35,
            )
        ):
            market_regime_panel.render()

        def render_graph_widget_bundle(bundle):
            graph_widget_renderers = {
                "market_monitor": market_monitor.render,
                "liquidity_pressure": liquidity_pressure_panel.render,
                "trade_flow_monitor": trade_flow_monitor.render,
            }
            renderer = graph_widget_renderers.get(str(bundle["widget_id"]))
            if renderer is None:
                return

            with live_shell.slot_widget_from_meta(bundle["slot_meta"]):
                renderer(
                    overlay_contract=bundle["overlay_contract"],
                )

        graph_widget_bundles = [
            warroom_graph_widget_bundle("market_monitor"),
            warroom_graph_widget_bundle("liquidity_pressure"),
            warroom_graph_widget_bundle("trade_flow_monitor"),
        ]
        for bundle in graph_widget_bundles:
            render_graph_widget_bundle(bundle)

        with live_shell.slot_widget_from_meta(
            warroom_slot(
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
            warroom_slot(
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
            warroom_slot(
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
            warroom_slot(
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

            overlay_rows = [
                row
                for row in slot_rows
                if row.get("overlay_enabled")
            ]
            partial_update_rows = [
                row
                for row in slot_rows
                if row.get("partial_update_enabled")
            ]
            st.caption(
                f"overlay-enabled widgets: {len(overlay_rows)} / {warroom_overlay_contract_count()}"
            )
            st.caption(
                f"partial-update-enabled widgets: {len(partial_update_rows)} / {warroom_overlay_contract_count()}"
            )
        else:
            st.info(get_text(lang, "ui_slot_registry_empty_warroom"))

    with live_shell.render_folded_section("War Room Graph Overlay Diagnostics", expanded=False):
        overlay_diag = {
            widget_id: {
                "overlay_enabled": warroom_overlay_enabled(widget_id),
                "partial_update_enabled": warroom_partial_update_enabled(widget_id),
                "refresh_policy": warroom_refresh_policy(widget_id),
                "chart_sensitive": warroom_chart_sensitive(widget_id),
                "overlay_contract": warroom_graph_overlay_contract(widget_id),
                "layout_hints": warroom_layout_hints(widget_id),
            }
            for widget_id in warroom_overlay_widget_ids()
        }
        st.json(overlay_diag)
        st.caption(f"overlay diagnostics targets: {warroom_overlay_contract_count()}")
        st.caption(f"chart-sensitive widgets: {warroom_chart_sensitive_count()}")
        st.caption(f"refresh modes: {warroom_refresh_mode_counts()}")

    with live_shell.render_folded_section(get_text(lang, "ui_label_ai_diagnostics"), expanded=False):
        with live_shell.slot_widget_from_meta(
            warroom_slot(
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
            warroom_slot(
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
            warroom_slot(
                "ai_diagnostics",
                "ai_conversation_panel",
                label=None,
                tone="primary",
                refresh_mode="poll_slow",
                priority=90,
            )
        ):
            ai_conversation_panel.render()