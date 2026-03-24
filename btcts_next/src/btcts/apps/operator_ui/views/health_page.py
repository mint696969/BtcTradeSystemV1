# path: ./btcts_next/src/btcts/apps/operator_ui/views/health_page.py
# desc: 実運用向けの System Health ページ。collector / audit / market_state を基に短期監視を表示する。

from __future__ import annotations

import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.health_data_service import load_health_snapshot
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts


def _collector_summary_label(status_payload: dict, health_payload: dict, lang: str) -> str:
    mode = str(status_payload.get("mode") or "")
    ok = health_payload.get("ok")

    if mode == "RUNNING" and ok is True:
        return get_text(lang, "health_value_healthy")
    if mode in {"RUNNING", "DEGRADED"}:
        return get_text(lang, "health_value_caution")
    if mode:
        return get_text(lang, "health_value_broken")
    return get_text(lang, "health_value_no_data")


def _api_summary_label(rate_item: dict, lang: str) -> str:
    if not rate_item:
        return get_text(lang, "health_value_no_data")

    mode = str(rate_item.get("mode") or rate_item.get("summary_state") or "").upper()

    if rate_item.get("last_429_ts"):
        return get_text(lang, "health_value_caution")

    if bool(rate_item.get("engaged")):
        return get_text(lang, "health_value_caution")

    if mode in {"NORMAL"}:
        return get_text(lang, "health_value_healthy")

    if mode in {"WARN", "RECOVERY", "CRIT"}:
        return get_text(lang, "health_value_caution")

    return get_text(lang, "health_value_broken")


def _ws_summary_label(origin_payload: dict, lang: str) -> str:
    ws_state = str(origin_payload.get("ws_state") or "").upper()

    if ws_state == "LIVE":
        return get_text(lang, "health_value_healthy")
    if ws_state in {"SYNCING", "CONNECTING"}:
        return get_text(lang, "health_value_caution")
    if ws_state:
        return get_text(lang, "health_value_broken")
    return get_text(lang, "health_value_no_data")


def _layer3_summary_label(market_latest: dict, market_diag: dict, lang: str) -> str:
    trust_state = str(market_latest.get("trust_state") or market_diag.get("preferred_row_trust_state") or "")
    interpretation_bucket = str(
        market_latest.get("interpretation_bucket")
        or market_diag.get("preferred_row_interpretation_bucket")
        or ""
    )

    if trust_state == "trusted" and interpretation_bucket == "allow_structural_use":
        return get_text(lang, "health_value_healthy")
    if trust_state in {"provisional", "trusted"} or interpretation_bucket == "observe_only":
        return get_text(lang, "health_value_caution")
    if trust_state or interpretation_bucket:
        return get_text(lang, "health_value_broken")
    return get_text(lang, "health_value_no_data")


def _format_optional_ts(value: str | None, lang: str) -> str:
    if not value:
        return "-"
    return format_ui_ts(value, lang=lang)


def _format_metric_number(
    value,
    *,
    decimals: int = 0,
    percent: bool = False,
) -> str:
    if value is None or value == "":
        return "-"

    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)

    if percent:
        return f"{num * 100:.{decimals}f}%"

    if decimals <= 0:
        return str(int(round(num)))

    return f"{num:.{decimals}f}"


def _health_value_label(value: str | None, lang: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "-"

    key_map = {
        "RUNNING": "health_value_running",
        "DEGRADED": "health_value_degraded",
        "STOPPED": "health_value_stopped",
        "NORMAL": "health_value_normal_mode",
        "WARN": "health_value_warn_mode",
        "RECOVERY": "health_value_recovery_mode",
        "CRIT": "health_value_crit_mode",
        "continuous": "health_value_continuous",
        "disrupted": "health_value_disrupted",
        "LIVE": "health_value_live_freshness",
        "QUIET": "health_value_quiet_freshness",
        "STALE": "health_value_stale_freshness",
        "trusted": "health_value_trusted",
        "provisional": "health_value_provisional",
        "broken": "health_value_broken_trust",
        "allow_structural_use": "health_value_allow_structural_use",
        "observe_only": "health_value_observe_only",
        "none": "health_value_none_boundary",
    }

    text_key = key_map.get(raw)
    if text_key:
        return get_text(lang, text_key)
    return raw


def _continuity_cell_color(level: str) -> str:
    if level == "green":
        return "#22c55e"
    if level == "yellow":
        return "#facc15"
    if level == "orange":
        return "#f59e0b"
    if level == "red":
        return "#ef4444"
    return "#6b7280"


def _continuity_level_label(level: str, lang: str) -> str:
    key_map = {
        "green": "health_continuity_level_green",
        "yellow": "health_continuity_level_yellow",
        "orange": "health_continuity_level_orange",
        "red": "health_continuity_level_red",
        "gray": "health_continuity_level_gray",
    }
    return get_text(lang, key_map.get(level, "health_continuity_level_gray"))


def _health_event_label(value: str | None, lang: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return get_text(lang, "health_table_empty_value")

    key_map = {
        "origin.stream_gap_detected": "health_event_gap_detected",
        "origin.stream_resync_started": "health_event_resync_started",
        "origin.stream_resync_completed": "health_event_resync_completed",
        "crit": "health_event_exploration_crit",
        "recovery": "health_event_exploration_recovery",
        "warn": "health_event_exploration_warn",
        "normal": "health_event_exploration_normal",
        "delta_arrived_before_snapshot": "health_reason_delta_arrived_before_snapshot",
        "snapshot_received_after_gap": "health_reason_snapshot_received_after_gap",
        "none": "health_table_empty_value",
        "None": "health_table_empty_value",
    }

    text_key = key_map.get(raw)
    if text_key:
        return get_text(lang, text_key)
    return raw


def _render_continuity_rail(rail_rows: list[dict], lang: str):
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
            grid-template-columns: repeat(60, minmax(8px, 1fr));
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
                    f"style='background:{_continuity_cell_color(str(cell.get('level') or 'gray'))};' "
                    f"title='{cell.get('ts', '')} / {get_text(lang, str(cell.get('reason') or 'health_continuity_reason_none'))}'></div>"
                )
                for cell in cells
            ]
        )

        st.markdown(
            (
                "<div class='health-continuity-row'>"
                f"<div class='health-continuity-venue'>{venue}</div>"
                f"<div class='health-continuity-cells'>{cells_html}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                "<div class='health-continuity-reason'>"
                f"<strong>{get_text(lang, 'health_continuity_reason_title')}</strong><br>"
                f"{_continuity_level_label(current_level, lang)} / {current_reason}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def render():
    lang = st.session_state.get("ui_lang", "en")
    snapshot = load_health_snapshot()

    collector_state = snapshot.get("collector_state") or {}
    status_payload = collector_state.get("status") or {}
    health_payload = collector_state.get("health") or {}
    rate_payload = collector_state.get("rate") or {}
    origin_payload = collector_state.get("origin") or {}
    checkpoint_payload = collector_state.get("checkpoint") or {}
    daemon_status_payload = collector_state.get("exploration_daemon_status") or {}
    daemon_health_payload = collector_state.get("health") or {}

    rate_items = rate_payload.get("items") or {}
    bitflyer_rate = rate_items.get("bitflyer") or {}
    bitflyer_rate_classes = bitflyer_rate.get("request_classes") or {}
    bitflyer_rate_snapshot = bitflyer_rate_classes.get("board_snapshot") or {}
    bitflyer_rate_trades = bitflyer_rate_classes.get("rest_trades") or {}

    exploration_mode = str(bitflyer_rate.get("mode") or bitflyer_rate.get("summary_state") or "")
    exploration_active_target_ratio = bitflyer_rate.get("active_target_ratio")
    exploration_utilization = bitflyer_rate.get("utilization")

    market_latest = snapshot.get("market_latest") or {}
    market_diag = snapshot.get("market_diag") or {}

    api_ws_series = snapshot.get("api_ws_series_1h") or []
    rate_overlay = snapshot.get("rate_overlay_1h") or []
    layer3_series = snapshot.get("layer3_series_1h") or []
    api_continuity_rail = snapshot.get("api_continuity_rail_1h") or []
    ws_continuity_rail = snapshot.get("ws_continuity_rail_1h") or []
    recent_anomalies = snapshot.get("recent_anomalies") or []

    st.header(get_text(lang, "health_title"))

    st.markdown(f"#### {get_text(lang, 'health_section_read_guide')}")
    st.caption(f"1. {get_text(lang, 'health_read_guide_line1')}")
    st.caption(f"2. {get_text(lang, 'health_read_guide_line2')}")
    st.caption(f"3. {get_text(lang, 'health_read_guide_line3')}")

    st.markdown(f"#### {get_text(lang, 'health_section_continuity_api')}")
    if api_continuity_rail:
        _render_continuity_rail(api_continuity_rail, lang)
        st.caption(get_text(lang, "health_continuity_caption_api"))
    else:
        st.info(get_text(lang, "health_value_no_data"))

    st.markdown(f"#### {get_text(lang, 'health_section_continuity_ws')}")
    if ws_continuity_rail:
        _render_continuity_rail(ws_continuity_rail, lang)
        st.caption(get_text(lang, "health_continuity_caption_ws"))
    else:
        st.info(get_text(lang, "health_value_no_data"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        get_text(lang, "health_summary_collector"),
        _collector_summary_label(status_payload, health_payload, lang),
    )
    c2.metric(
        get_text(lang, "health_summary_api"),
        _api_summary_label(bitflyer_rate, lang),
    )
    c3.metric(
        get_text(lang, "health_summary_ws"),
        _ws_summary_label(origin_payload, lang),
    )
    c4.metric(
        get_text(lang, "health_summary_layer3"),
        _layer3_summary_label(market_latest, market_diag, lang),
    )

    st.markdown(f"#### {get_text(lang, 'health_section_api_chart')}")
    if api_ws_series:
        api_df = pd.DataFrame(api_ws_series)
        api_df["ts"] = pd.to_datetime(api_df["ts"], utc=True)

        latest_api = api_df.iloc[-1].to_dict() if not api_df.empty else {}

        a1, a2, a3, a4 = st.columns(4)
        a1.metric(
            get_text(lang, "health_metric_req_1m"),
            "-" if not bitflyer_rate else _format_metric_number(bitflyer_rate.get("requests_60s")),
        )
        a2.metric(
            get_text(lang, "health_metric_req_5m"),
            "-" if not bitflyer_rate else _format_metric_number(bitflyer_rate.get("requests_300s")),
        )
        a3.metric(
            get_text(lang, "health_metric_req_snapshot_1m"),
            "-" if not bitflyer_rate_snapshot else _format_metric_number(bitflyer_rate_snapshot.get("requests_60s")),
        )
        a4.metric(
            get_text(lang, "health_metric_req_trades_1m"),
            "-" if not bitflyer_rate_trades else _format_metric_number(bitflyer_rate_trades.get("requests_60s")),
        )

        api_chart_df = api_df.set_index("ts")[
            [
                "api_events",
                "api_rolling_5m",
                "api_limit_5m",
                "events_429_marker",
            ]
        ].rename(
            columns={
                "api_events": get_text(lang, "health_chart_api_events"),
                "api_rolling_5m": get_text(lang, "health_chart_api_rolling_5m"),
                "api_limit_5m": get_text(lang, "health_chart_api_limit_5m"),
                "events_429_marker": get_text(lang, "health_chart_429_events"),
            }
        )
        st.line_chart(api_chart_df, height=260, width="stretch")

        if rate_overlay:
            overlay_df = pd.DataFrame(rate_overlay)
            overlay_df["ts"] = pd.to_datetime(overlay_df["ts"], utc=True)

            o1, o2, o3, o4 = st.columns(4)
            latest_overlay = overlay_df.iloc[-1].to_dict() if not overlay_df.empty else {}

            o1.metric(
                get_text(lang, "health_metric_budget_60s"),
                _format_metric_number(latest_overlay.get("budget_60s")),
            )
            o2.metric(
                get_text(lang, "health_metric_budget_300s"),
                _format_metric_number(latest_overlay.get("budget_300s")),
            )
            o3.metric(
                get_text(lang, "health_metric_target_ratio"),
                _format_metric_number(latest_overlay.get("target_utilization"), decimals=1, percent=True),
            )
            o4.metric(
                get_text(lang, "health_metric_hard_cap_ratio"),
                _format_metric_number(latest_overlay.get("hard_cap_utilization"), decimals=1, percent=True),
            )

            overlay_chart_df = overlay_df.set_index("ts")[
                [
                    "utilization",
                    "active_target_ratio",
                    "target_utilization",
                    "hard_cap_utilization",
                ]
            ].rename(
                columns={
                    "utilization": get_text(lang, "health_chart_current_utilization"),
                    "active_target_ratio": get_text(lang, "health_chart_active_target_ratio"),
                    "target_utilization": get_text(lang, "health_chart_target_utilization"),
                    "hard_cap_utilization": get_text(lang, "health_chart_hard_cap_utilization"),
                }
            )
            st.line_chart(overlay_chart_df, height=220, width="stretch")

        st.caption(get_text(lang, "health_chart_api_caption"))
    else:
        st.info(get_text(lang, "health_value_no_data"))

    st.markdown(f"#### {get_text(lang, 'health_section_ws_chart')}")
    if api_ws_series:
        ws_df = pd.DataFrame(api_ws_series)
        ws_df["ts"] = pd.to_datetime(ws_df["ts"], utc=True)

        latest_ws = ws_df.iloc[-1].to_dict() if not ws_df.empty else {}

        w1, w2, w3 = st.columns(3)
        w1.metric(
            get_text(lang, "health_metric_ws_events_1m"),
            "-" if not latest_ws else _format_metric_number(latest_ws.get("ws_events")),
        )
        w2.metric(
            get_text(lang, "health_metric_gap_1m"),
            "-" if not latest_ws else _format_metric_number(latest_ws.get("gap_events")),
        )
        w3.metric(
            get_text(lang, "health_metric_resync_1m"),
            "-" if not latest_ws else _format_metric_number(latest_ws.get("resync_events")),
        )

        ws_chart_df = ws_df.set_index("ts")[
            [
                "ws_events",
                "gap_events",
                "resync_events",
            ]
        ].rename(
            columns={
                "ws_events": get_text(lang, "health_chart_ws_events"),
                "gap_events": get_text(lang, "health_chart_gap_events"),
                "resync_events": get_text(lang, "health_chart_resync_events"),
            }
        )
        st.line_chart(ws_chart_df, height=220, width="stretch")
        st.caption(get_text(lang, "health_chart_ws_caption"))
    else:
        st.info(get_text(lang, "health_value_no_data"))

    st.markdown(f"#### {get_text(lang, 'health_section_layer3_chart')}")
    if layer3_series:
        l1, l2, l3, l4 = st.columns(4)
        l1.metric(
            get_text(lang, "health_metric_trust_state"),
            _health_value_label(
                market_latest.get("trust_state") or market_diag.get("preferred_row_trust_state"),
                lang,
            ),
        )
        l2.metric(
            get_text(lang, "health_metric_continuity_state"),
            _health_value_label(
                market_latest.get("continuity_state") or market_diag.get("preferred_row_continuity_state"),
                lang,
            ),
        )
        l3.metric(
            get_text(lang, "health_metric_interpretation"),
            _health_value_label(
                market_latest.get("interpretation_bucket")
                or market_diag.get("preferred_row_interpretation_bucket"),
                lang,
            ),
        )
        l4.metric(
            get_text(lang, "health_metric_freshness"),
            _health_value_label(market_diag.get("preferred_row_freshness"), lang),
        )

        layer3_df = pd.DataFrame(layer3_series)
        layer3_df["ts"] = pd.to_datetime(layer3_df["ts"], utc=True)
        layer3_chart_df = layer3_df.set_index("ts")[
            [
                "trust_score",
                "continuity_score",
                "interpretation_score",
                "freshness_score",
            ]
        ].rename(
            columns={
                "trust_score": get_text(lang, "health_chart_trust_score"),
                "continuity_score": get_text(lang, "health_chart_continuity_score"),
                "interpretation_score": get_text(lang, "health_chart_interpretation_score"),
                "freshness_score": get_text(lang, "health_chart_freshness_score"),
            }
        )
        st.line_chart(layer3_chart_df, height=220, width="stretch")
        st.caption(get_text(lang, "health_chart_layer3_caption"))
    else:
        st.info(get_text(lang, "health_value_no_data"))

    st.markdown(f"#### {get_text(lang, 'health_section_current_state')}")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(
        get_text(lang, "health_metric_status"),
        _health_value_label(status_payload.get("mode"), lang),
    )
    m2.metric(
        get_text(lang, "health_metric_wait_ms"),
        "-" if not bitflyer_rate else _health_value_label(exploration_mode, lang),
    )
    m3.metric(
        get_text(lang, "health_metric_util_ratio"),
        "-" if not bitflyer_rate else _format_metric_number(
            exploration_utilization if exploration_utilization is not None else bitflyer_rate.get("util_ratio"),
            decimals=1,
            percent=True,
        ),
    )
    m4.metric(
        get_text(lang, "health_metric_last_429"),
        _format_optional_ts(bitflyer_rate.get("last_429_ts"), lang),
    )
    m5.metric(
        get_text(lang, "health_metric_hold_until"),
        _format_optional_ts(bitflyer_rate.get("hold_until_ts"), lang),
    )

    n1, n2, n3, n4 = st.columns(4)
    n1.metric(
        get_text(lang, "health_metric_ws_state"),
        _health_value_label(origin_payload.get("ws_state"), lang),
    )
    n2.metric(
        get_text(lang, "health_metric_snapshot_to_live"),
        _format_metric_number(origin_payload.get("snapshot_to_live_ms")),
    )
    n3.metric(
        get_text(lang, "health_metric_resync"),
        "-" if exploration_active_target_ratio is None else _format_metric_number(
            exploration_active_target_ratio,
            decimals=1,
            percent=True,
        ),
    )
    n4.metric(
        get_text(lang, "health_metric_last_sequence_id"),
        _format_metric_number(checkpoint_payload.get("last_sequence_id")),
    )

    p1, p2, p3, p4, p5, p6 = st.columns(6)
    p1.metric(
        get_text(lang, "health_metric_boundary_reason"),
        _health_value_label(market_latest.get("boundary_reason"), lang),
    )
    p2.metric(
        get_text(lang, "health_metric_interpretation"),
        _health_value_label(
            market_latest.get("interpretation_bucket")
            or market_diag.get("preferred_row_interpretation_bucket"),
            lang,
        ),
    )
    p3.metric(
        get_text(lang, "health_metric_daemon_status"),
        _health_value_label(daemon_status_payload.get("mode"), lang),
    )
    p4.metric(
        get_text(lang, "health_metric_daemon_last_error"),
        str(daemon_status_payload.get("last_error") or "-"),
    )
    p5.metric(
        get_text(lang, "health_metric_daemon_failures"),
        _format_metric_number(
            daemon_health_payload.get("consecutive_failures")
            if daemon_health_payload
            else None
        ),
    )
    p6.metric(
        get_text(lang, "health_metric_daemon_last_success"),
        _format_optional_ts(daemon_health_payload.get("last_success_ts"), lang),
    )

    st.markdown(f"#### {get_text(lang, 'health_section_recent_events')}")
    if recent_anomalies:
        events_df = pd.DataFrame(recent_anomalies)

        if "ts" in events_df.columns:
            events_df["ts"] = events_df["ts"].apply(lambda x: format_ui_ts(x, lang=lang))
        if "event" in events_df.columns:
            events_df["event"] = events_df["event"].apply(lambda x: _health_event_label(x, lang))
        if "reason" in events_df.columns:
            events_df["reason"] = events_df["reason"].apply(lambda x: _health_event_label(x, lang))
        if "topic" in events_df.columns:
            events_df["topic"] = events_df["topic"].apply(lambda x: _health_event_label(x, lang))
        if "exchange" in events_df.columns:
            events_df["exchange"] = events_df["exchange"].apply(lambda x: _health_event_label(x, lang))

        events_df = events_df.rename(
            columns={
                "ts": get_text(lang, "health_table_ts"),
                "event": get_text(lang, "health_table_event"),
                "topic": get_text(lang, "health_table_topic"),
                "reason": get_text(lang, "health_table_reason"),
                "exchange": get_text(lang, "health_table_exchange"),
            }
        )

        st.dataframe(events_df, width="stretch", hide_index=True)
    else:
        st.info(get_text(lang, "health_value_no_data"))