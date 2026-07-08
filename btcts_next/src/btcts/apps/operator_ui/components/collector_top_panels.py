# path: ./btcts_next/src/btcts/apps/operator_ui/components/collector_top_panels.py
# desc: Collector ページ上部の summary / supervisor / rate / continuity を外出しした helper。

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.live_shell import make_slot_meta


def _request_rerun() -> None:
    """Immediately refresh Collector controls after a button action.

    The Collector tab is an operational control surface.  After writing a start,
    safe-stop, or restart request, rerun the page so disabled/enabled button
    states and pending-request captions are visible without waiting for the next
    auto-refresh tick.
    """
    rerun = getattr(st, "rerun", None)
    if callable(rerun):
        rerun()


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




def _severity_color(severity: str) -> tuple[str, str, str]:
    mapping = {
        "healthy": ("#16a34a", "#dcfce7", "#166534"),
        "warning": ("#d97706", "#fef3c7", "#92400e"),
        "danger": ("#dc2626", "#fee2e2", "#991b1b"),
        "unknown": ("#64748b", "#f1f5f9", "#334155"),
    }
    return mapping.get(str(severity or "unknown"), mapping["unknown"])


def _html_escape(value: object) -> str:
    import html

    return html.escape(str(value if value is not None else "-"))


def _compact_value(value: object, default: str = "-") -> str:
    text = str(value if value is not None else "").strip()
    return text if text else default


def _collector_runtime_summary_item(*, live_summary: dict, runtime: dict) -> dict:
    overall_state = str(live_summary.get("overall_state") or runtime.get("mode") or "UNKNOWN").upper()
    health = str(runtime.get("health_status") or live_summary.get("health_status") or "unknown").lower()
    feed = str(runtime.get("feed_state") or live_summary.get("feed_state") or "UNKNOWN").upper()
    reason = str(live_summary.get("overall_reason") or "")
    if overall_state in {"STOPPED", "OFFLINE"} or health == "stopped":
        severity = "danger"
        badge = "STOPPED"
        primary = "停止"
    elif overall_state == "RUNNING" and health == "healthy" and feed != "STALE":
        severity = "healthy"
        badge = "RUNNING"
        primary = "正常稼働"
    elif overall_state == "RUNNING":
        severity = "warning"
        badge = "WATCH"
        primary = "要監視"
    else:
        severity = "unknown"
        badge = overall_state or "UNKNOWN"
        primary = "不明"
    return {
        "runtime_id": "collector",
        "display_name": "Collector",
        "severity": severity,
        "badge_label": badge,
        "primary_status": primary,
        "secondary_status": f"feed={feed} / health={health}",
        "meta_items": [
            f"mode={runtime.get('mode') or '-'}",
            f"feed={feed}",
            f"reason={reason or '-'}",
        ],
        "detail_rows": [
            {"label": "overall_state", "value": overall_state},
            {"label": "health", "value": health},
            {"label": "feed", "value": feed},
            {"label": "reason", "value": reason or "-"},
            {"label": "last_sequence_id", "value": runtime.get("last_sequence_id") or "-"},
        ],
        "sort_order": 10,
    }


def _chart_engine_runtime_summary_item(snapshot: dict) -> dict:
    mode = str(snapshot.get("mode") or "UNKNOWN").upper()
    active = bool(snapshot.get("active"))
    pending = str(snapshot.get("pending_action") or "-") or "-"
    age = snapshot.get("status_age_sec")
    if active and mode == "RUNNING":
        severity = "healthy"
        badge = "RUNNING"
        primary = "稼働中"
    elif pending not in {"", "-", "None", "none"}:
        severity = "warning"
        badge = "PENDING"
        primary = "処理待ち"
    elif mode == "STOPPED" or not active:
        severity = "danger"
        badge = "STOPPED"
        primary = "停止"
    else:
        severity = "unknown"
        badge = mode or "UNKNOWN"
        primary = "不明"
    return {
        "runtime_id": "chart_engine",
        "display_name": "Chart Engine",
        "severity": severity,
        "badge_label": badge,
        "primary_status": primary,
        "secondary_status": f"active={'YES' if active else 'NO'} / pending={pending}",
        "meta_items": [
            f"pid={snapshot.get('runtime_pid') or '-'}",
            f"age={age if age is not None else '-'}s",
            f"endpoint={snapshot.get('endpoint') or '-'}",
        ],
        "detail_rows": [
            {"label": "mode", "value": mode},
            {"label": "active", "value": active},
            {"label": "runtime_pid", "value": snapshot.get("runtime_pid") or "-"},
            {"label": "pending_action", "value": pending},
            {"label": "status_age_sec", "value": age if age is not None else "-"},
            {"label": "status_path", "value": snapshot.get("status_path") or "-"},
            {"label": "request_path", "value": snapshot.get("request_path") or "-"},
        ],
        "sort_order": 20,
    }


def _market_regime_runtime_summary_item(*, loop_snapshot: dict, card_snapshot: dict) -> dict:
    loop_active = bool(loop_snapshot.get("active"))
    loop_mode = str(loop_snapshot.get("mode") or "STOPPED").upper()
    cards_available = bool(card_snapshot.get("latest_cards_available"))
    card_count = int(card_snapshot.get("card_count") or 0)
    latest_label = str(card_snapshot.get("first_card_label") or "-")
    confidence = card_snapshot.get("first_card_confidence")
    if loop_active:
        severity = "healthy"
        badge = "RUNNING"
        primary = "推論loop稼働中"
    elif loop_mode == "STOPPED" and cards_available:
        severity = "warning"
        badge = "STOPPED"
        primary = "停止中・カードあり"
    elif loop_mode == "STOPPED":
        severity = "danger"
        badge = "STOPPED"
        primary = "停止"
    else:
        severity = "unknown"
        badge = loop_mode or "UNKNOWN"
        primary = "不明"
    return {
        "runtime_id": "market_regime",
        "display_name": "MarketRegime",
        "severity": severity,
        "badge_label": badge,
        "primary_status": primary,
        "secondary_status": f"cards={card_count} / first={latest_label} {confidence if confidence is not None else '-'}%",
        "meta_items": [
            f"pid={loop_snapshot.get('runtime_pid') or '-'}",
            f"writes={loop_snapshot.get('writes') or 0}",
            f"latest={card_snapshot.get('latest_run_id') or loop_snapshot.get('latest_run_id') or '-'}",
        ],
        "detail_rows": [
            {"label": "loop_mode", "value": loop_mode},
            {"label": "loop_active", "value": loop_active},
            {"label": "runtime_pid", "value": loop_snapshot.get("runtime_pid") or "-"},
            {"label": "writes", "value": loop_snapshot.get("writes") or 0},
            {"label": "blocked", "value": loop_snapshot.get("blocked") or 0},
            {"label": "latest_run_id", "value": card_snapshot.get("latest_run_id") or loop_snapshot.get("latest_run_id") or "-"},
            {"label": "latest_generated_at", "value": card_snapshot.get("latest_generated_at") or "-"},
            {"label": "latest_cards_path", "value": card_snapshot.get("latest_cards_path") or "-"},
            {"label": "loop_status_path", "value": loop_snapshot.get("loop_status_path") or "-"},
            {"label": "loop_control_path", "value": loop_snapshot.get("loop_control_path") or "-"},
        ],
        "sort_order": 30,
    }


def build_linked_runtime_summary_items(
    *,
    live_summary: dict,
    runtime: dict,
    chart_engine_snapshot: dict,
    market_regime_loop_snapshot: dict,
    market_regime_snapshot: dict,
) -> list[dict]:
    items = [
        _collector_runtime_summary_item(live_summary=live_summary, runtime=runtime),
        _chart_engine_runtime_summary_item(chart_engine_snapshot),
        _market_regime_runtime_summary_item(loop_snapshot=market_regime_loop_snapshot, card_snapshot=market_regime_snapshot),
    ]
    return sorted(items, key=lambda item: int(item.get("sort_order") or 0))


def _render_runtime_status_card(item: dict) -> None:
    border, background, text_color = _severity_color(str(item.get("severity") or "unknown"))
    badge = _html_escape(item.get("badge_label") or "UNKNOWN")
    name = _html_escape(item.get("display_name") or item.get("runtime_id") or "runtime")
    primary = _html_escape(item.get("primary_status") or "-")
    secondary = _html_escape(item.get("secondary_status") or "-")
    meta_items = item.get("meta_items") if isinstance(item.get("meta_items"), list) else []
    meta_line = _html_escape(" / ".join(str(value) for value in meta_items[:3]) or "-")
    st.markdown(
        (
            f"<div style='border:1px solid {border}; border-left:4px solid {border}; "
            "border-radius:0.55rem; padding:0.50rem 0.60rem; min-height:7.2rem; "
            "background:rgba(148,163,184,0.06);'>"
            "<div style='display:flex; justify-content:space-between; gap:0.45rem; align-items:center;'>"
            f"<div style='font-weight:800; font-size:0.86rem;'>{name}</div>"
            f"<span style='font-size:0.68rem; font-weight:800; color:{text_color}; background:{background}; "
            f"border:1px solid {border}; border-radius:999px; padding:0.08rem 0.45rem;'>{badge}</span>"
            "</div>"
            f"<div style='font-size:1.00rem; font-weight:800; margin-top:0.32rem;'>{primary}</div>"
            f"<div style='font-size:0.76rem; opacity:0.82; margin-top:0.20rem;'>{secondary}</div>"
            f"<div style='font-size:0.68rem; opacity:0.68; margin-top:0.35rem; overflow-wrap:anywhere;'>{meta_line}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    with st.popover("詳細", use_container_width=True):
        st.caption(f"{item.get('display_name') or item.get('runtime_id')} runtime details")
        rows = item.get("detail_rows") if isinstance(item.get("detail_rows"), list) else []
        if rows:
            st.dataframe(rows, width="stretch", hide_index=True)
        else:
            st.write(item)


def render_linked_runtime_summary_section(
    *,
    live_summary: dict,
    runtime: dict,
    chart_engine_snapshot: dict,
    market_regime_loop_snapshot: dict,
    market_regime_snapshot: dict,
) -> None:
    items = build_linked_runtime_summary_items(
        live_summary=live_summary,
        runtime=runtime,
        chart_engine_snapshot=chart_engine_snapshot,
        market_regime_loop_snapshot=market_regime_loop_snapshot,
        market_regime_snapshot=market_regime_snapshot,
    )
    with live_shell.slot_widget_from_meta(
        make_slot_meta(
            "collector",
            "overview",
            "linked_runtime_summary",
            label="Linked Runtime Summary",
            tone="primary",
            refresh_mode="poll_fast",
            priority=5,
        )
    ):
        cols = live_shell.responsive_columns(max(1, len(items)), compact=True)
        for col, item in zip(cols, items):
            with col:
                _render_runtime_status_card(item)


def render_supervisor_control_section(
    *,
    lang: str,
    get_text: Callable[[str, str], str],
    supervisor_status: dict,
    supervisor_request: dict,
    stack_control_snapshot: dict,
    request_unified_start: Callable[[], tuple[bool, str, bool]],
    request_unified_safe_stop: Callable[[], tuple[bool, str]],
    request_unified_restart: Callable[[], tuple[bool, str]],
    linked_runtime_active: bool = False,
    linked_runtime_label: str = "linked runtime",
    is_supervisor_running: Callable[[dict], bool] | None = None,
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
        supervisor_running = is_supervisor_running(supervisor_status) if is_supervisor_running is not None else False

        pending_action = str(
            stack_control_snapshot.get("pending_action") or ""
        ).strip().lower()
        restart_pending = pending_action == "restart"

        safe_stop_pending = pending_action == "stop_stack"
        stack_active = bool(stack_control_snapshot.get("stack_active"))
        linked_runtime_active = bool(linked_runtime_active)
        stop_restart_target_active = bool(stack_active or linked_runtime_active)
        supervisor_active = bool(stack_control_snapshot.get("supervisor_active"))
        archive_active = bool(stack_control_snapshot.get("archive_active"))

        supervisor_mode = str(
            stack_control_snapshot.get("supervisor_mode")
            or supervisor_status.get("mode")
            or "-"
        )
        archive_copy_mode = str(
            stack_control_snapshot.get("archive_copy_mode") or "-"
        )
        archive_gc_mode = str(
            stack_control_snapshot.get("archive_gc_mode") or "-"
        )
        archive_copy_phase = str(
            (stack_control_snapshot.get("archive_copy_state") or {}).get("current_phase")
            or "-"
        )
        archive_gc_phase = str(
            (stack_control_snapshot.get("archive_gc_state") or {}).get("current_phase")
            or "-"
        )

        if not stack_active:
            st.info(get_text(lang, "collector_msg_stack_not_running"))
        elif stack_active and not supervisor_running:
            st.warning(get_text(lang, "collector_msg_watchdog_not_running"))

        if restart_pending:
            st.info(get_text(lang, "collector_msg_restart_pending"))

        if safe_stop_pending:
            st.info(get_text(lang, "collector_msg_safe_stop_pending"))

        if linked_runtime_active and not stack_active:
            st.info(f"{linked_runtime_label} is active; unified safe stop remains available.")

        sup_col1, sup_col2, sup_col3, sup_col4, sup_col5, sup_col6 = st.columns(6)

        with sup_col1:
            if st.button(
                get_text(lang, "collector_button_start_unified"),
                use_container_width=True,
                disabled=stack_active or restart_pending or safe_stop_pending,
            ):
                ok, msg, already_running = request_unified_start()
                if ok and already_running:
                    st.info(
                        get_text(lang, "collector_msg_start_already_running").format(
                            message=msg,
                        )
                    )
                elif ok:
                    st.success(
                        get_text(lang, "collector_msg_start_request_accepted").format(
                            message=msg,
                        )
                    )
                else:
                    st.error(
                        get_text(lang, "collector_msg_start_request_failed").format(
                            message=msg,
                        )
                    )
                _request_rerun()

        with sup_col2:
            if st.button(
                get_text(lang, "collector_button_safe_stop_unified"),
                use_container_width=True,
                disabled=(not stop_restart_target_active) or safe_stop_pending,
            ):
                ok, msg = request_unified_safe_stop()
                if ok:
                    st.success(
                        get_text(lang, "collector_msg_safe_stop_request_accepted").format(
                            message=msg,
                        )
                    )
                else:
                    st.error(
                        get_text(lang, "collector_msg_safe_stop_request_failed").format(
                            message=msg,
                        )
                    )
                _request_rerun()

        with sup_col3:
            if st.button(
                get_text(lang, "collector_button_restart_unified"),
                use_container_width=True,
                disabled=(not stop_restart_target_active) or restart_pending or safe_stop_pending,
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
                _request_rerun()

        with sup_col4:
            st.metric(
                get_text(lang, "collector_metric_supervisor_mode"),
                supervisor_mode,
            )

        with sup_col5:
            st.metric(
                get_text(lang, "collector_metric_pending_request"),
                pending_action or "-",
            )

        with sup_col6:
            st.metric(
                get_text(lang, "collector_metric_stack_active"),
                get_text(
                    lang,
                    "collector_value_yes" if stack_active else "collector_value_no",
                ),
            )

        st.caption(
            get_text(lang, "collector_caption_stack_control_line").format(
                stack_active=get_text(
                    lang,
                    "collector_value_yes" if stack_active else "collector_value_no",
                ),
                supervisor_active=get_text(
                    lang,
                    "collector_value_yes" if supervisor_active else "collector_value_no",
                ),
                archive_active=get_text(
                    lang,
                    "collector_value_yes" if archive_active else "collector_value_no",
                ),
                safe_stop_phase=supervisor_mode,
                archive_copy_mode=archive_copy_mode,
                archive_copy_phase=archive_copy_phase,
                archive_gc_mode=archive_gc_mode,
                archive_gc_phase=archive_gc_phase,
            )
        )

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