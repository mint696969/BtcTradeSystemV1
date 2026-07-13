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


def continuity_scale_config(range_key: str, lang: str) -> dict[str, object]:
    normalized = str(range_key or "1h")
    if normalized == "24h":
        return {
            "cell_label": "1セル＝30分" if lang == "ja" else "1 cell = 30 minutes",
            "major_every": 6,
            "major_label": "3時間ごと" if lang == "ja" else "every 3 hours",
            "time_format": "%H:%M",
        }
    if normalized == "1w":
        return {
            "cell_label": "1セル＝3時間" if lang == "ja" else "1 cell = 3 hours",
            "major_every": 8,
            "major_label": "1日ごと" if lang == "ja" else "every day",
            "time_format": "%m/%d %H:%M",
        }
    return {
        "cell_label": "1セル＝1分" if lang == "ja" else "1 cell = 1 minute",
        "major_every": 10,
        "major_label": "10分ごと" if lang == "ja" else "every 10 minutes",
        "time_format": "%H:%M",
    }


def _compact_ts_label(value: object, *, time_format: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "-"
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    return dt.strftime(time_format)


def render_continuity_legend(*, range_key: str = "1h", lang: str = "ja") -> None:
    scale = continuity_scale_config(range_key, lang)
    if lang == "ja":
        text = (
            f"{scale['cell_label']}。緑=正常更新 / 黄=単発の不安定 / "
            "橙=繰り返し不安定または警告 / 赤=断絶または危険 / 灰=観測データなし。"
            "右端の枠付きセルには現在状態を重ねます。"
        )
    else:
        text = (
            f"{scale['cell_label']}. green=normal update / yellow=single instability / "
            "orange=repeated instability or warning / red=broken or dangerous / gray=no observed data. "
            "The rightmost outlined cell includes current lane truth."
        )
    st.markdown(
        f"<div class='health-continuity-legend'>{html.escape(text)}</div>",
        unsafe_allow_html=True,
    )


def render_continuity_rail(
    rail_rows: list[dict],
    lang: str,
    *,
    range_key: str = "1h",
    show_legend: bool = True,
) -> None:
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
        .health-continuity-cell-major {
            box-shadow: inset 2px 0 0 rgba(55,65,81,0.32);
        }
        .health-continuity-scale {
            display: grid;
            grid-template-columns: 170px 1fr;
            gap: 0.75rem;
            margin-top: -0.05rem;
            margin-bottom: 0.20rem;
            color: rgba(75,85,99,0.96);
            font-size: 0.70rem;
        }
        .health-continuity-scale-track {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
        }
        .health-continuity-scale-track span:nth-child(2) {
            justify-self: center;
        }
        .health-continuity-scale-track span:last-child {
            justify-self: end;
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
            display: flex;
            align-items: baseline;
            gap: 1.25rem;
            flex-wrap: wrap;
        }
        .health-continuity-reason-title {
            font-weight: 700;
            white-space: nowrap;
        }
        .health-continuity-reason-text {
            min-width: 0;
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

    if show_legend:
        render_continuity_legend(range_key=range_key, lang=lang)

    scale = continuity_scale_config(range_key, lang)

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
        major_every = max(1, int(scale["major_every"]))
        for index, cell in enumerate(cells):
            level = str(cell.get("level") or "gray")
            reason_text = get_text(lang, str(cell.get("reason") or "health_continuity_reason_none"))
            is_current_overlay = bool(cell.get("current_truth_overlay"))
            classes = "health-continuity-cell"
            if index > 0 and index % major_every == 0:
                classes += " health-continuity-cell-major"
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

        if cells:
            first_label = _compact_ts_label(cells[0].get("ts"), time_format=str(scale["time_format"]))
            middle_label = _compact_ts_label(
                cells[len(cells) // 2].get("ts"),
                time_format=str(scale["time_format"]),
            )
            last_label = _compact_ts_label(cells[-1].get("ts"), time_format=str(scale["time_format"]))
        else:
            first_label = middle_label = last_label = "-"

        st.markdown(
            (
                "<div class='health-continuity-scale'>"
                f"<div>{html.escape(str(scale['cell_label']))} / "
                f"{html.escape(str(scale['major_label']))}</div>"
                "<div class='health-continuity-scale-track'>"
                f"<span>{html.escape(first_label)}</span>"
                f"<span>{html.escape(middle_label)}</span>"
                f"<span>{html.escape(last_label)}</span>"
                "</div></div>"
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
                "<span class='health-continuity-reason-title'>"
                f"{get_text(lang, 'health_continuity_reason_title')}"
                "</span>"
                "<span class='health-continuity-reason-text'>"
                f"current={html.escape(current_label)} / {html.escape(current_reason)}"
                f"{coverage_line}"
                "</span>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
