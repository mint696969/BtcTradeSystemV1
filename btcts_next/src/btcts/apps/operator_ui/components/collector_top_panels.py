# path: ./btcts_next/src/btcts/apps/operator_ui/components/collector_top_panels.py
# desc: Collector ページ上部の summary / supervisor / rate / continuity を外出しした helper。

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.live_shell import make_slot_meta


def render_overview_summary_panel(
    *,
    lang: str,
    live_summary: dict,
    runtime: dict,
    get_text: Callable[[str, str], str],
    overall_status_label: Callable[[str], str],
    exchange_status_label: Callable[[str], str],
) -> None:
    with live_shell.zone_container(zone_kind="overview"):
        col1, col2, col3 = live_shell.responsive_columns(3, compact=True)

        with col1:
            with live_shell.slot_widget_from_meta(
                make_slot_meta(
                    "collector",
                    "overview",
                    "status_summary",
                    label=get_text(lang, "collector_metric_status"),
                    tone="strong",
                    refresh_mode="poll_normal",
                    priority=10,
                )
            ):
                st.metric(
                    get_text(lang, "collector_metric_status"),
                    overall_status_label(live_summary["overall_state"]),
                )

        with col2:
            with live_shell.slot_widget_from_meta(
                make_slot_meta(
                    "collector",
                    "overview",
                    "exchange_summary",
                    label=get_text(lang, "collector_metric_exchange"),
                    tone="primary",
                    refresh_mode="poll_normal",
                    priority=20,
                )
            ):
                st.metric(
                    get_text(lang, "collector_metric_exchange"),
                    exchange_status_label(runtime["exchange_state"]),
                )

        with col3:
            with live_shell.slot_widget_from_meta(
                make_slot_meta(
                    "collector",
                    "overview",
                    "feed_summary",
                    label=get_text(lang, "collector_metric_feed"),
                    tone="neutral",
                    refresh_mode="poll_fast",
                    priority=30,
                )
            ):
                st.metric(
                    get_text(lang, "collector_metric_feed"),
                    runtime["feed_state"],
                )


def render_supervisor_control_section(
    *,
    lang: str,
    get_text: Callable[[str, str], str],
    supervisor_status: dict,
    supervisor_request: dict,
    request_unified_restart: Callable[[], tuple[bool, str]],
    is_supervisor_running: Callable[[dict], bool],
    is_restart_request_pending: Callable[[dict], bool],
    supervisor_status_rows: Callable[[dict, dict], list[dict]],
) -> None:
    with live_shell.slot_widget_from_meta(
        make_slot_meta(
            "collector",
            "primary_live",
            "supervisor_control",
            label=get_text(lang, "ui_label_unified_supervisor"),
            tone="primary",
            refresh_mode="poll_normal",
            priority=40,
        )
    ):
        supervisor_running = is_supervisor_running(supervisor_status)
        restart_pending = is_restart_request_pending(supervisor_request)

        if not supervisor_running:
            st.warning(get_text(lang, "collector_msg_watchdog_not_running"))

        if restart_pending:
            st.info(get_text(lang, "collector_msg_restart_pending"))

        sup_col1, sup_col2, sup_col3, sup_col4 = st.columns([1.2, 1, 1, 1])
        with sup_col1:
            if st.button(
                get_text(lang, "collector_button_restart_unified"),
                use_container_width=True,
                disabled=restart_pending,
            ):
                ok, msg = request_unified_restart()
                if ok:
                    st.success(
                        get_text(lang, "collector_msg_restart_request_accepted").format(
                            message=msg,
                        )
                    )
                else:
                    st.error(
                        get_text(lang, "collector_msg_restart_request_failed").format(
                            message=msg,
                        )
                    )

        with sup_col2:
            st.metric(get_text(lang, "collector_metric_supervisor_mode"), supervisor_status.get("mode") or "-")

        with sup_col3:
            st.metric(get_text(lang, "collector_metric_pending_request"), supervisor_request.get("action") or "-")

        with sup_col4:
            st.metric(get_text(lang, "collector_metric_supervisor_uptime_sec"), supervisor_status.get("uptime_sec") or "-")

        if supervisor_status:
            st.caption(
                get_text(lang, "collector_caption_supervisor_health_line").format(
                    started_at=supervisor_status.get("started_at", "-"),
                    last_seen_ts=supervisor_status.get("last_seen_ts", "-"),
                )
            )

        rows = supervisor_status_rows(supervisor_status, supervisor_request)
        if rows:
            st.dataframe(rows, width="stretch")
        else:
            st.info(get_text(lang, "collector_msg_supervisor_status_unavailable"))


def render_rate_control_section(
    *,
    lang: str,
    get_text: Callable[[str, str], str],
    rate_state: dict,
    rate_rows: Callable[[dict], list[dict]],
) -> None:
    with live_shell.slot_widget_from_meta(
        make_slot_meta(
            "collector",
            "primary_live",
            "rate_control",
            label=get_text(lang, "ui_label_rate_control"),
            tone="primary",
            refresh_mode="poll_fast",
            priority=50,
        )
    ):
        rows = rate_rows(rate_state)
        if not rows:
            st.info(get_text(lang, "collector_msg_rate_state_unavailable"))
            return

        first_rate = rows[0]

        engaged = bool(first_rate.get("engaged"))
        last_429_ts = first_rate.get("last_429_ts")
        rate_posture = (
            get_text(lang, "collector_value_rate_posture_throttled")
            if engaged
            else get_text(lang, "collector_value_rate_posture_normal")
        )
        recent_429 = (
            get_text(lang, "collector_value_yes")
            if last_429_ts
            else get_text(lang, "collector_value_no")
        )

        r1, r2, r3, r4, r5, r6 = st.columns(6)
        r1.metric(get_text(lang, "collector_metric_rate_posture"), rate_posture)
        r2.metric(get_text(lang, "collector_metric_recent_429"), recent_429)
        r3.metric(get_text(lang, "collector_metric_rate_summary"), first_rate.get("summary_state") or "-")
        r4.metric(get_text(lang, "collector_metric_wait_ms"), first_rate.get("wait_ms") or 0)
        r5.metric(get_text(lang, "collector_metric_util_ratio"), first_rate.get("util_ratio") or 0)
        r6.metric(get_text(lang, "collector_metric_recovery"), first_rate.get("recovery_phase") or "-")

        if engaged:
            st.warning(
                f"{get_text(lang, 'collector_msg_rate_control_engaged')} / "
                f"reason={first_rate.get('reason') or '-'} / "
                f"hold_until_ts={first_rate.get('hold_until_ts') or '-'}"
            )
        elif last_429_ts:
            st.info(
                f"{get_text(lang, 'collector_msg_recent_429_detected')} / "
                f"last_429_ts={last_429_ts} / "
                f"recovery_phase={first_rate.get('recovery_phase') or '-'}"
            )
        else:
            st.caption(
                f"{get_text(lang, 'collector_msg_rate_posture_normal')} / "
                f"reason={first_rate.get('reason') or '-'} / "
                f"backoff_sec={first_rate.get('backoff_sec') or '-'}"
            )

        st.dataframe(rows, width="stretch")


def render_origin_continuity_summary_section(
    *,
    lang: str,
    get_text: Callable[[str, str], str],
    status_state: dict,
    origin_continuity: dict,
    status_continuity_freshness: Callable[[dict], tuple[str, str]],
    status_age_seconds: Callable[[dict], float | None],
) -> None:
    with live_shell.slot_widget_from_meta(
        make_slot_meta(
            "collector",
            "primary_live",
            "origin_continuity_summary",
            label=get_text(lang, "ui_label_origin_continuity"),
            tone="primary",
            refresh_mode="poll_normal",
            priority=60,
        )
    ):
        status_freshness_label, status_freshness_reason = status_continuity_freshness(status_state)
        status_age = status_age_seconds(status_state)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric(get_text(lang, "collector_metric_status_freshness"), status_freshness_label)
        c2.metric(get_text(lang, "collector_metric_status_age_sec"), status_age or "-")
        c3.metric(get_text(lang, "collector_metric_origin_ws_state"), origin_continuity.get("ws_state") or "-")
        c4.metric(get_text(lang, "collector_metric_origin_snapshot_to_live_ms"), origin_continuity.get("snapshot_to_live_ms") or "-")
        c5.metric(get_text(lang, "collector_metric_origin_pre_snapshot_drops"), origin_continuity.get("pre_snapshot_delta_drop_count") or 0)

        if origin_continuity:
            if status_freshness_label == "LIVE":
                st.caption(
                    get_text(lang, "collector_msg_origin_continuity_line").format(
                        reason=status_freshness_reason,
                    )
                )
            elif status_freshness_label == "STALE":
                st.warning(
                    get_text(lang, "collector_msg_origin_continuity_line").format(
                        reason=status_freshness_reason,
                    )
                )
            else:
                st.info(
                    get_text(lang, "collector_msg_origin_continuity_line").format(
                        reason=status_freshness_reason,
                    )
                )
        else:
            st.info(get_text(lang, "collector_msg_status_origin_unavailable"))