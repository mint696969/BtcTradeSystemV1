# path: ./btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py
# desc: Minimal Streamlit component renderer for dashboard hub display source presenter. No app.py/page routing/runtime wiring.

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.hub.display_source_presenter import (
    dashboard_hub_display_source_presenter,
)
from btcts.apps.operator_ui.ui_text import get_text

DASHBOARD_HUB_SOURCE_PANEL_CONTRACT = {
    "panel_type": "dashboard_hub_display_source_panel",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "streamlit_rendering": True,
    "component_only_rendering": True,
    "not_app_py_wiring": True,
    "not_page_routing": True,
    "not_runtime_wiring": True,
    "not_broker_or_order_wiring": True,
}


def _rows_for_table(rows: tuple[dict, ...] | list[dict]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in rows or ():
        if not isinstance(row, dict):
            continue
        normalized.append(
            {
                "label": str(row.get("label") or ""),
                "value": str(row.get("value") or ""),
            }
        )
    return normalized


def _status_tone(status_label: str) -> str:
    if status_label == "ready":
        return "primary"
    return "danger"


def render_dashboard_hub_display_source_panel(presenter: dict | None = None) -> dict:
    lang = str(st.session_state.get("ui_lang", "en"))
    payload = presenter or dashboard_hub_display_source_presenter()
    title = get_text(lang, "health_widget_dashboard_source_title")
    subtitle = get_text(lang, "health_widget_dashboard_source_subtitle")
    status_label = str(payload.get("status_label") or "blocked")
    summary_rows = _rows_for_table(payload.get("summary_rows") or ())
    detail_rows = _rows_for_table(payload.get("detail_rows") or ())
    hot_cold_rows = _rows_for_table(payload.get("hot_cold_detail_rows") or ())
    hot_cold_status_label = str(payload.get("hot_cold_status_label") or "unknown")
    hot_cold_metadata_detail_status = str(payload.get("hot_cold_metadata_detail_status") or "unknown")

    with live_shell.panel_container(
        label=title,
        tone=_status_tone(status_label),
        help_text=subtitle,
    ):
        st.caption(f"{get_text(lang, 'health_widget_status_label')}: {status_label}")
        if summary_rows:
            live_shell.render_scrollable_key_value_rows(summary_rows, max_height_px=180)
        if detail_rows or hot_cold_rows:
            with st.expander(get_text(lang, "health_widget_details_label"), expanded=False):
                if detail_rows:
                    live_shell.render_scrollable_key_value_rows(detail_rows, max_height_px=260)
                if hot_cold_rows:
                    st.caption(get_text(lang, "health_widget_hot_cold_metadata_title"))
                    live_shell.render_scrollable_key_value_rows(hot_cold_rows, max_height_px=220)
        if not summary_rows and not detail_rows and not hot_cold_rows:
            st.caption(get_text(lang, "health_widget_no_dashboard_source_diagnostics"))

    return {
        **DASHBOARD_HUB_SOURCE_PANEL_CONTRACT,
        "presenter_type": payload.get("presenter_type"),
        "status_label": status_label,
        "summary_row_count": len(summary_rows),
        "detail_row_count": len(detail_rows),
        "hot_cold_row_count": len(hot_cold_rows),
        "hot_cold_status_label": hot_cold_status_label,
        "hot_cold_metadata_detail_status": hot_cold_metadata_detail_status,
        "hot_cold_rows_present": bool(hot_cold_rows),
        "hot_cold_table_rendered": bool(hot_cold_rows),
        "hot_cold_table_caption": "Hot/Cold metadata" if hot_cold_rows else "",
        "rendered": True,
        "app_py_wired": False,
        "page_routing_wired": False,
        "runtime_wired": False,
        "compact_line": (
            "dashboard_hub_source_panel="
            f"status:{status_label};summary_rows:{len(summary_rows)};detail_rows:{len(detail_rows)};"
            f"hot_cold_status:{hot_cold_status_label};hot_cold_rows:{len(hot_cold_rows)}"
        ),
    }
