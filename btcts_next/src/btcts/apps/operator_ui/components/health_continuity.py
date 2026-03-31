# path: ./btcts_next/src/btcts/apps/operator_ui/components/health_continuity.py
# desc: Health タブの continuity rail 描画 helper をまとめる。

from __future__ import annotations

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


def render_continuity_rail(rail_rows: list[dict], lang: str) -> None:
    st.markdown(
        """
        <style>
        .health-continuity-row {
            display: grid;
            grid-template-columns: 110px 1fr;
            gap: 0.75rem;
            align-items: center;
            margin-bottom: 0.45rem;
        }
        .health-continuity-venue {
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
        .health-continuity-reason {
            min-height: 56px;
            border: 1px solid rgba(128,128,128,0.25);
            border-radius: 6px;
            padding: 0.65rem 0.8rem;
            margin-top: 0.4rem;
            margin-bottom: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    for row in rail_rows:
        venue = str(row.get("venue") or "-")
        cells = row.get("cells") or []
        current_level = str(row.get("current_level") or "gray")
        current_reason_key = str(row.get("current_reason") or "health_continuity_reason_none")
        current_reason = get_text(lang, current_reason_key)

        cells_html = "".join(
            [
                (
                    f"<div class='health-continuity-cell' "
                    f"style='background:{continuity_cell_color(str(cell.get('level') or 'gray'))};' "
                    f"title='{cell.get('ts', '')} / {get_text(lang, str(cell.get('reason') or 'health_continuity_reason_none'))}'></div>"
                )
                for cell in cells
            ]
        )

        cell_count = max(1, len(cells))

        st.markdown(
            (
                "<div class='health-continuity-row'>"
                f"<div class='health-continuity-venue'>{venue}</div>"
                f"<div class='health-continuity-cells' "
                f"style='grid-template-columns: repeat({cell_count}, minmax(8px, 1fr));'>"
                f"{cells_html}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                "<div class='health-continuity-reason'>"
                f"<strong>{get_text(lang, 'health_continuity_reason_title')}</strong><br>"
                f"{continuity_level_label(current_level, lang)} / {current_reason}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )