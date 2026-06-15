# path: ./btcts_next/src/btcts/apps/operator_ui/components/health_continuity.py
# desc: Health タブの continuity rail 描画 helper をまとめる。

from __future__ import annotations

import html

import streamlit as st

from btcts.apps.operator_ui.ui_text import get_text


def continuity_cell_color(level: str) -> str:
    if level == "green":
        return "#22c55e"
    if level == "yellow":
        return "#facc15"
    if level == "orange":
        return "#f59e0b"
    if level == "red":
        return "#ef4444"
    return "#6b7280"


def continuity_level_label(level: str, lang: str) -> str:
    key_map = {
        "green": "health_continuity_level_green",
        "yellow": "health_continuity_level_yellow",
        "orange": "health_continuity_level_orange",
        "red": "health_continuity_level_red",
        "gray": "health_continuity_level_gray",
    }
    return get_text(lang, key_map.get(level, "health_continuity_level_gray"))


def continuity_venue_display(venue: str, lang: str) -> tuple[str, str]:
    mapping = {
        "bitflyer_api_market_data": (
            "API REST",
            "REST / board snapshot / trades polling",
        ),
        "bitflyer_ws_board": (
            "WS Board",
            "板・orderbook stream",
        ),
        "bitflyer_ws_executions": (
            "WS Executions",
            "約定・trades stream",
        ),
    }
    return mapping.get(str(venue or ""), (str(venue or "-"), ""))


def _coverage_warning_label(warning: str) -> str:
    mapping = {
        "audit_tail_has_no_rows_in_selected_window": "audit has no rows in selected window",
        "audit_tail_did_not_cover_full_window": "audit tail does not cover full window",
        "audit_tail_empty_or_unparseable": "audit tail is empty or unparseable",
    }
    return mapping.get(str(warning or ""), str(warning or ""))


def render_continuity_rail(rail_rows: list[dict], lang: str) -> None:
    st.markdown(
        """
        <style>
        .health-continuity-row {
            display: grid;
            grid-template-columns: 170px 1fr;
            gap: 0.75rem;
            align-items: center;
            margin-bottom: 0.45rem;
        }
        .health-continuity-venue {
            font-weight: 700;
            line-height: 1.25;
        }
        .health-continuity-venue-detail {
            margin-top: 0.10rem;
            color: rgba(107,114,128,0.95);
            font-size: 0.72rem;
            font-weight: 500;
        }
        .health-continuity-current-pill {
            display: inline-block;
            margin-top: 0.25rem;
            padding: 0.08rem 0.38rem;
            border-radius: 999px;
            color: white;
            font-size: 0.72rem;
            font-weight: 700;
        }
        .health-continuity-coverage-warning {
            margin-top: 0.20rem;
            color: #f59e0b;
            font-size: 0.70rem;
            font-weight: 700;
        }
        .health-continuity-cells {
            display: grid;
            gap: 2px;
        }
        .health-continuity-cell {
            height: 16px;
            border-radius: 2px;
        }
        .health-continuity-cell-current {
            outline: 2px solid rgba(255,255,255,0.70);
            outline-offset: -2px;
        }
        .health-continuity-reason {
            min-height: 56px;
            border: 1px solid rgba(128,128,128,0.25);
            border-radius: 6px;
            padding: 0.65rem 0.8rem;
            margin-top: 0.4rem;
            margin-bottom: 0.9rem;
        }
        .health-continuity-legend {
            color: rgba(107,114,128,0.95);
            font-size: 0.75rem;
            margin-bottom: 0.45rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='health-continuity-legend'>"
        "1 cell = 1 minute. green=normal update / yellow=single instability / "
        "orange=repeated instability or warning / red=broken or dangerous / gray=no observed data. "
        "The rightmost outlined cell includes current lane truth."
        "</div>",
        unsafe_allow_html=True,
    )

    for row in rail_rows:
        raw_venue = str(row.get("venue") or "-")
        venue_label, venue_detail = continuity_venue_display(raw_venue, lang)
        cells = row.get("cells") or []
        current_level = str(row.get("current_level") or "gray")
        current_reason_key = str(row.get("current_reason") or "health_continuity_reason_none")
        current_reason = get_text(lang, current_reason_key)
        current_label = continuity_level_label(current_level, lang)
        current_color = continuity_cell_color(current_level)

        coverage_warning = ""
        coverage_window_start_ts = ""
        coverage_oldest_available_ts = ""
        coverage_latest_available_ts = ""
        for cell in cells:
            warning = str(cell.get("coverage_warning") or "").strip()
            if warning:
                coverage_warning = warning
                coverage_window_start_ts = str(cell.get("coverage_window_start_ts") or "")
                coverage_oldest_available_ts = str(cell.get("coverage_oldest_available_ts") or "")
                coverage_latest_available_ts = str(cell.get("coverage_latest_available_ts") or "")
                break

        cell_html_parts: list[str] = []
        for cell in cells:
            level = str(cell.get("level") or "gray")
            reason_text = get_text(lang, str(cell.get("reason") or "health_continuity_reason_none"))
            is_current_overlay = bool(cell.get("current_truth_overlay"))
            classes = "health-continuity-cell"
            if is_current_overlay:
                classes += " health-continuity-cell-current"
            title = (
                f"{cell.get('ts', '')} / {reason_text}"
                + (" / current truth" if is_current_overlay else "")
            )
            cell_html_parts.append(
                f"<div class='{classes}' "
                f"style='background:{continuity_cell_color(level)};' "
                f"title='{html.escape(title)}'></div>"
            )
        cells_html = "".join(cell_html_parts)
        cell_count = max(1, len(cells))

        coverage_badge = ""
        if coverage_warning:
            coverage_badge = (
                "<div class='health-continuity-coverage-warning'>"
                f"{html.escape(_coverage_warning_label(coverage_warning))}"
                "</div>"
            )

        st.markdown(
            (
                "<div class='health-continuity-row'>"
                "<div class='health-continuity-venue'>"
                f"{html.escape(venue_label)}"
                f"<div class='health-continuity-venue-detail'>{html.escape(venue_detail)}</div>"
                f"<span class='health-continuity-current-pill' style='background:{current_color};'>"
                f"current: {html.escape(current_label)}</span>"
                f"{coverage_badge}"
                "</div>"
                f"<div class='health-continuity-cells' "
                f"style='grid-template-columns: repeat({cell_count}, minmax(8px, 1fr));'>"
                f"{cells_html}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        coverage_line = ""
        if coverage_warning:
            coverage_line = (
                "<br><span style='color:#f59e0b;'>"
                f"coverage={html.escape(_coverage_warning_label(coverage_warning))}"
                f" / window_start={html.escape(coverage_window_start_ts or '-')}"
                f" / oldest={html.escape(coverage_oldest_available_ts or '-')}"
                f" / latest={html.escape(coverage_latest_available_ts or '-')}"
                "</span>"
            )

        st.markdown(
            (
                "<div class='health-continuity-reason'>"
                f"<strong>{get_text(lang, 'health_continuity_reason_title')}</strong><br>"
                f"current={html.escape(current_label)} / {html.escape(current_reason)}"
                f"{coverage_line}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
