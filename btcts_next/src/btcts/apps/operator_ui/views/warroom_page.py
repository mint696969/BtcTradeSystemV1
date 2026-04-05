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
    WarroomGraphWidgetBundle,
    warroom_chart_sensitive,
    warroom_chart_sensitive_count,
    warroom_graph_overlay_contract,
    warroom_graph_widget_bundle,
    warroom_graph_widget_ids,
    warroom_layout_hints,
    warroom_overlay_contract_count,
    warroom_overlay_enabled,
    warroom_overlay_widget_ids,
    warroom_partial_update_enabled,
    warroom_first_partial_redraw_candidate,
    warroom_refresh_mode_counts,
    warroom_refresh_policy,
    warroom_rerender_scope_counts,
    warroom_all_widget_ids,
    warroom_widget_slot,
    warroom_widget_zone_ids,
)


_GRAPH_WIDGET_RENDERERS = {
    "market_monitor": market_monitor.render,
    "liquidity_pressure": liquidity_pressure_panel.render,
    "trade_flow_monitor": trade_flow_monitor.render,
}


def _render_graph_widget_bundle(bundle: WarroomGraphWidgetBundle) -> None:
    renderer = _GRAPH_WIDGET_RENDERERS.get(str(bundle["widget_id"]))
    if renderer is None:
        return

    with live_shell.slot_widget_from_meta(bundle["slot_meta"]):
        renderer(
            overlay_contract=bundle["overlay_contract"],
        )


def _expected_warroom_widget_ids() -> set[str]:
    return set(warroom_all_widget_ids())


def _missing_registered_widget_ids(slot_rows: list[dict]) -> list[str]:
    actual_widget_ids = {str(row.get("widget_id")) for row in slot_rows}
    return sorted(_expected_warroom_widget_ids().difference(actual_widget_ids))


def _unexpected_registered_zone_ids(slot_rows: list[dict]) -> list[str]:
    actual_zone_ids = {
        str(row.get("zone_id"))
        for row in slot_rows
        if row.get("zone_id") is not None
    }
    return sorted(actual_zone_ids.difference(set(warroom_widget_zone_ids())))


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
            warroom_widget_slot("warroom_header")
        ):
            warroom_header.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("warroom_alert_engine")
        ):
            warroom_alert_engine.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("ai_operator_panel")
        ):
            ai_operator_panel.render()
    with live_shell.zone_container(
        label=get_text(lang, "ui_label_operator_support"),
        zone_kind="secondary",
    ):
        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("decision_log_panel")
        ):
            decision_log_panel.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("watch_list_panel")
        ):
            watch_list_panel.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("warroom_timeline")
        ):
            warroom_timeline.render()

    with live_shell.zone_container(
        label=get_text(lang, "ui_label_primary_live"),
        zone_kind="primary_live",
    ):
        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("market_regime")
        ):
            market_regime_panel.render()

        graph_widget_bundles = [
            warroom_graph_widget_bundle(widget_id)
            for widget_id in warroom_graph_widget_ids()
        ]
        for bundle in graph_widget_bundles:
            _render_graph_widget_bundle(bundle)

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("ai_signal")
        ):
            ai_signal_panel.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("strategy_state")
        ):
            strategy_state_panel.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("risk_monitor")
        ):
            risk_monitor_panel.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("agent_panels")
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
                get_text(
                    lang,
                    "warroom_overlay_enabled_widgets_caption",
                ).format(
                    count=len(overlay_rows),
                    total=warroom_overlay_contract_count(),
                )
            )
            st.caption(
                get_text(
                    lang,
                    "warroom_partial_update_enabled_widgets_caption",
                ).format(
                    count=len(partial_update_rows),
                    total=warroom_overlay_contract_count(),
                )
            )
            missing_widget_ids = _missing_registered_widget_ids(slot_rows)
            if missing_widget_ids:
                st.warning(
                    "missing slot registrations: " + ", ".join(missing_widget_ids)
                )

            unexpected_zone_ids = _unexpected_registered_zone_ids(slot_rows)
            if unexpected_zone_ids:
                st.warning(
                    "unexpected zone ids: " + ", ".join(unexpected_zone_ids)
                )
        else:
            st.info(get_text(lang, "ui_slot_registry_empty_warroom"))

    with live_shell.render_folded_section(
        get_text(lang, "warroom_graph_overlay_diagnostics_title"),
        expanded=False,
    ):
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
        st.caption(
            get_text(
                lang,
                "warroom_overlay_diagnostics_targets_caption",
            ).format(
                count=warroom_overlay_contract_count(),
            )
        )
        st.caption(
            get_text(
                lang,
                "warroom_chart_sensitive_widgets_caption",
            ).format(
                count=warroom_chart_sensitive_count(),
            )
        )
        st.caption(
            get_text(
                lang,
                "warroom_refresh_modes_caption",
            ).format(
                counts=warroom_refresh_mode_counts(),
            )
        )
        st.caption(
            "rerender scope counts: "
            + str(warroom_rerender_scope_counts())
        )
        first_candidate = warroom_first_partial_redraw_candidate()
        if first_candidate is not None:
            st.caption(
                "first partial redraw candidate: "
                + first_candidate
            )
            if first_candidate == "market_monitor":
                st.caption(
                    "W3 entry fixed: market_monitor"
                )

    with live_shell.render_folded_section(get_text(lang, "ui_label_ai_diagnostics"), expanded=False):
        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("ai_reasoning_panel")
        ):
            ai_reasoning_panel.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("ai_market_summary_panel")
        ):
            ai_market_summary_panel.render()

        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("ai_conversation_panel")
        ):
            ai_conversation_panel.render()