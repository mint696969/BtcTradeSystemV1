# path: ./btcts_next/src/btcts/apps/operator_ui/components/health_detail_panels.py
# desc: Health ページの Current State / Recent Events を外出しした helper。

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.ui_time import format_ui_ts


def build_health_digest_current_state_caption(
    *,
    widget,
    payload: dict | None,
) -> str:
    if widget is None or not payload:
        return "health_digest unavailable"

    freshness = str(getattr(widget, "freshness_key", None) or "UNKNOWN")
    semantic_rows = int(payload.get("semantic_usage_contract_rows_count") or 0)
    summary_slots = int(payload.get("orderbook_summary_slots_count") or 0)
    active_event_rows = int(payload.get("orderbook_active_event_contracts_count") or 0)

    return (
        f"health_digest: freshness={freshness} / "
        f"semantic_rows={semantic_rows} / "
        f"summary_slots={summary_slots} / "
        f"active_event_rows={active_event_rows}"
    )


def render_current_state_section(
    *,
    lang: str,
    status_payload: dict,
    health_payload: dict,
    bitflyer_rate: dict,
    runtime_kind: str,
    runtime_mode: str,
    runtime_utilization,
    origin_payload: dict,
    checkpoint_payload: dict,
    ws_board_lane: dict,
    ws_executions_lane: dict,
    executions_payload: dict,
    ws_board_state: str,
    ws_board_last_error: str,
    ws_executions_state: str,
    ws_executions_last_error: str,
    market_latest: dict,
    market_diag: dict,
    health_digest_widget=None,
    health_digest_payload: dict | None = None,
    daemon_status_payload: dict,
    daemon_health_payload: dict,
    get_text: Callable[[str, str], str],
    health_value_label: Callable[[str | None, str], str],
    format_optional_ts: Callable[[str | None, str], str],
    format_age_seconds: Callable[[str | None], str],
    format_metric_number: Callable[..., str],
    ws_freshness_label_from_ts: Callable[[str | None, str], str],
) -> None:
    with live_shell.render_folded_section(
        get_text(lang, "health_section_current_state"),
        expanded=False,
    ):
        import streamlit as st

        def bool_flag_label(flag: bool) -> str:
            return get_text(lang, "health_value_on") if flag else get_text(lang, "health_value_off")

        st.caption(
            build_health_digest_current_state_caption(
                widget=health_digest_widget,
                payload=health_digest_payload,
            )
        )

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric(
            get_text(lang, "health_metric_status"),
            health_value_label(status_payload.get("mode"), lang),
            runtime_kind.upper() if runtime_kind else None,
        )
        m2.metric(
            get_text(lang, "health_metric_wait_ms"),
            get_text(lang, "health_table_empty_value")
            if not bitflyer_rate
            else health_value_label(runtime_mode, lang),
        )
        m3.metric(
            get_text(lang, "health_metric_util_ratio"),
            get_text(lang, "health_table_empty_value")
            if not bitflyer_rate
            else format_metric_number(
                runtime_utilization if runtime_utilization is not None else bitflyer_rate.get("util_ratio"),
                decimals=1,
                percent=True,
            ),
        )
        m4.metric(
            get_text(lang, "health_metric_last_429"),
            format_optional_ts(bitflyer_rate.get("last_429_ts"), lang),
        )
        m5.metric(
            get_text(lang, "health_metric_hold_until"),
            format_optional_ts(bitflyer_rate.get("hold_until_ts"), lang)
            if runtime_mode == "CRIT"
            else "-",
        )

        st.markdown(f"##### {get_text(lang, 'health_label_ws_board_exec_section')}")

        nb1, nb2, nb3, nb4, nb5 = st.columns(5)
        nb1.metric(
            get_text(lang, "health_metric_ws_board_state"),
            health_value_label(
                ws_board_lane.get("ws_state") or origin_payload.get("ws_state"),
                lang,
            ),
            ws_board_state if ws_board_state else None,
        )
        nb2.metric(
            get_text(lang, "health_metric_ws_board_freshness"),
            health_value_label(
                ws_board_lane.get("ws_freshness")
                or ws_freshness_label_from_ts(
                    ws_board_lane.get("last_event_ts") or origin_payload.get("ts"),
                    lang,
                ),
                lang,
            ),
        )
        nb3.metric(
            get_text(lang, "health_metric_ws_board_last_update"),
            format_optional_ts(
                ws_board_lane.get("last_event_ts") or origin_payload.get("ts"),
                lang,
            ),
        )
        nb4.metric(
            get_text(lang, "health_metric_ws_board_age_sec"),
            format_age_seconds(
                ws_board_lane.get("last_event_ts") or origin_payload.get("ts"),
            ),
        )
        nb5.metric(
            get_text(lang, "health_metric_ws_board_restart"),
            format_metric_number(ws_board_lane.get("restart_count")),
            ws_board_last_error if ws_board_last_error else None,
        )

        ne1, ne2, ne3, ne4, ne5 = st.columns(5)
        ne1.metric(
            get_text(lang, "health_metric_ws_exec_state"),
            health_value_label(
                ws_executions_lane.get("ws_state") or executions_payload.get("ws_state"),
                lang,
            ),
            ws_executions_state if ws_executions_state else None,
        )
        ne2.metric(
            get_text(lang, "health_metric_ws_exec_freshness"),
            health_value_label(
                ws_executions_lane.get("ws_freshness")
                or health_payload.get("ws_executions_freshness")
                or ws_freshness_label_from_ts(
                    ws_executions_lane.get("last_event_ts")
                    or ws_executions_lane.get("connected_ts")
                    or executions_payload.get("last_event_ts")
                    or executions_payload.get("connected_ts")
                    or executions_payload.get("ts"),
                    lang,
                ),
                lang,
            ),
        )
        ne3.metric(
            get_text(lang, "health_metric_ws_exec_last_update"),
            format_optional_ts(
                ws_executions_lane.get("last_event_ts")
                or ws_executions_lane.get("connected_ts")
                or executions_payload.get("last_event_ts")
                or executions_payload.get("connected_ts")
                or executions_payload.get("ts"),
                lang,
            ),
        )
        ne4.metric(
            get_text(lang, "health_metric_ws_exec_age_sec"),
            format_age_seconds(
                ws_executions_lane.get("last_event_ts")
                or ws_executions_lane.get("connected_ts")
                or executions_payload.get("last_event_ts")
                or executions_payload.get("connected_ts")
                or executions_payload.get("ts"),
            ),
        )
        ne5.metric(
            get_text(lang, "health_metric_ws_exec_trades"),
            format_metric_number(
                ws_executions_lane.get("trade_count")
                if ws_executions_lane
                else executions_payload.get("trade_count"),
            ),
            ws_executions_last_error if ws_executions_last_error else None,
        )

        n1, n2, n3 = st.columns(3)
        n1.metric(
            get_text(lang, "health_metric_snapshot_to_live"),
            format_metric_number(origin_payload.get("snapshot_to_live_ms")),
        )
        n2.metric(
            get_text(lang, "health_metric_resync"),
            bool_flag_label(bool(origin_payload.get("resync_active"))),
            bool_flag_label(bool(origin_payload.get("gap_detected"))),
        )
        n3.metric(
            get_text(lang, "health_metric_last_sequence_id"),
            format_metric_number(checkpoint_payload.get("last_sequence_id")),
        )

        p1, p2, p3, p4, p5, p6 = st.columns(6)
        p1.metric(
            get_text(lang, "health_metric_boundary_reason"),
            health_value_label(market_latest.get("boundary_reason"), lang),
        )
        p2.metric(
            get_text(lang, "health_metric_interpretation"),
            health_value_label(
                market_latest.get("interpretation_bucket")
                or market_diag.get("preferred_row_interpretation_bucket"),
                lang,
            ),
        )
        p3.metric(
            get_text(lang, "health_metric_daemon_status"),
            health_value_label(daemon_status_payload.get("mode"), lang),
        )
        p4.metric(
            get_text(lang, "health_metric_daemon_last_error"),
            str(daemon_status_payload.get("last_error") or "-"),
            ws_board_last_error if ws_board_last_error else None,
        )
        p5.metric(
            get_text(lang, "health_metric_daemon_failures"),
            format_metric_number(
                daemon_health_payload.get("consecutive_failures")
                if daemon_health_payload
                else None
            ),
        )
        p6.metric(
            get_text(lang, "health_metric_daemon_last_success"),
            format_optional_ts(daemon_health_payload.get("last_success_ts"), lang),
            format_optional_ts(origin_payload.get("ts"), lang),
        )


def render_recent_events_section(
    *,
    lang: str,
    recent_anomalies: list[dict],
    get_text: Callable[[str, str], str],
    health_event_label: Callable[[str | None, str], str],
) -> None:
    with live_shell.render_folded_section(
        get_text(lang, "health_section_recent_events"),
        expanded=False,
    ):
        import streamlit as st

        if not recent_anomalies:
            st.info(get_text(lang, "health_value_no_data"))
            return

        events_df = pd.DataFrame(recent_anomalies)

        if "ts" in events_df.columns:
            events_df["ts"] = events_df["ts"].apply(lambda x: format_ui_ts(x, lang=lang))
        if "event" in events_df.columns:
            events_df["event"] = events_df["event"].apply(lambda x: health_event_label(x, lang))
        if "reason" in events_df.columns:
            events_df["reason"] = events_df["reason"].apply(lambda x: health_event_label(x, lang))
        if "topic" in events_df.columns:
            events_df["topic"] = events_df["topic"].apply(lambda x: health_event_label(x, lang))
        if "exchange" in events_df.columns:
            events_df["exchange"] = events_df["exchange"].apply(lambda x: health_event_label(x, lang))

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