# path: ./btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py
# desc: Health ページ上部の guide / summary / continuity 群を外出しした helper。

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.live_shell import make_slot_meta
from btcts.apps.operator_ui.components.health_continuity import render_continuity_rail


def render_read_guide_section(
    *,
    lang: str,
    get_text: Callable[[str, str], str],
) -> None:
    with live_shell.render_folded_section(
        get_text(lang, "health_section_read_guide"),
        expanded=False,
    ):
        st.caption(f"1. {get_text(lang, 'health_read_guide_line1')}")
        st.caption(f"2. {get_text(lang, 'health_read_guide_line2')}")
        st.caption(f"3. {get_text(lang, 'health_read_guide_line3')}")


def render_overview_summary_panel(
    *,
    lang: str,
    status_payload: dict,
    health_payload: dict,
    bitflyer_rate: dict,
    origin_payload: dict,
    market_latest: dict,
    market_diag: dict,
    get_text: Callable[[str, str], str],
    collector_summary_label: Callable[[dict, dict, str], str],
    api_summary_label: Callable[[dict, str], str],
    ws_summary_label: Callable[[dict, str], str],
    layer3_summary_label: Callable[[dict, dict, str], str],
) -> None:
    c1, c2, c3, c4 = live_shell.responsive_columns(4, compact=True)

    with c1:
        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "health",
                "overview",
                "collector_summary",
                label=None,
                tone="strong",
                refresh_mode="poll_normal",
                priority=10,
            )
        ):
            st.metric(
                get_text(lang, "health_summary_collector"),
                collector_summary_label(status_payload, health_payload, lang),
            )

    with c2:
        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "health",
                "overview",
                "api_summary",
                label=None,
                tone="primary",
                refresh_mode="poll_fast",
                priority=20,
            )
        ):
            st.metric(
                get_text(lang, "health_summary_api"),
                api_summary_label(bitflyer_rate, lang),
            )

    with c3:
        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "health",
                "overview",
                "ws_summary",
                label=None,
                tone="primary",
                refresh_mode="poll_fast",
                priority=30,
            )
        ):
            st.metric(
                get_text(lang, "health_summary_ws"),
                ws_summary_label(origin_payload, lang),
            )

    with c4:
        with live_shell.slot_widget_from_meta(
            make_slot_meta(
                "health",
                "overview",
                "layer3_summary",
                label=None,
                tone="neutral",
                refresh_mode="poll_normal",
                priority=40,
            )
        ):
            st.metric(
                get_text(lang, "health_summary_layer3"),
                layer3_summary_label(market_latest, market_diag, lang),
            )


def render_continuity_panels(
    *,
    lang: str,
    range_key: str,
    api_continuity_rail: list[dict],
    ws_continuity_rail: list[dict],
    get_text: Callable[[str, str], str],
    section_title_with_range: Callable[[str, str], str],
) -> None:
    with live_shell.slot_widget_from_meta(
        make_slot_meta(
            "health",
            "primary_live",
            "api_continuity_panel",
            label=section_title_with_range(
                get_text(lang, "health_section_continuity_api"),
                range_key,
            ),
            tone="primary",
            refresh_mode="poll_normal",
            priority=80,
        )
    ):
        if api_continuity_rail:
            render_continuity_rail(api_continuity_rail, lang)
            st.caption(get_text(lang, "health_continuity_caption_api"))
        else:
            st.info(get_text(lang, "health_value_no_data"))

    with live_shell.slot_widget_from_meta(
        make_slot_meta(
            "health",
            "primary_live",
            "ws_continuity_panel",
            label=section_title_with_range(
                get_text(lang, "health_section_continuity_ws"),
                range_key,
            ),
            tone="primary",
            refresh_mode="poll_normal",
            priority=90,
        )
    ):
        if ws_continuity_rail:
            render_continuity_rail(ws_continuity_rail, lang)
            st.caption(get_text(lang, "health_continuity_caption_ws"))
        else:
            st.info(get_text(lang, "health_value_no_data"))