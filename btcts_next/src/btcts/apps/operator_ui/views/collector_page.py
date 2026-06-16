# path: ./btcts_next/src/btcts/apps/operator_ui/views/collector_page.py
# desc: Collector vNext の live 運転状態を表示する Operator UI ページ。state / health / checkpoint / audit を基に監視する。

from __future__ import annotations
from datetime import datetime, timezone
import json
from uuid import uuid4
import streamlit as st

from btcts.apps.operator_ui.components import execution_feed_panel
from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.live_shell import get_registered_slots
from btcts.apps.operator_ui.components.slot_definitions import (
    collector_widget_ids,
    collector_widget_slot,
    collector_widget_zone_ids,
)
from btcts.apps.operator_ui.components import system_stats
from btcts.apps.operator_ui.components.collector_top_panels import (
    render_origin_continuity_summary_section,
    render_overview_summary_panel,
    render_rate_control_section,
    render_supervisor_control_section,
)
from btcts.apps.operator_ui.components.live_bridge import (
    collector_runtime_snapshot,
    read_recent_audit_events,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_execution_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.collector_state_service import load_state
from btcts.apps.operator_ui.market_state_service import market_state_diagnostics
from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.stack_control import (
    stack_runtime_snapshot,
    start_stack_detached,
)
from btcts.collector_vnext.unified_state import write_unified_supervisor_request
from btcts.core import paths as core_paths


def _exchange_status_label(value: str) -> str:
    mapping = {
        "CONNECTED": "接続中",
        "DEGRADED": "一部劣化",
        "STOPPED": "停止",
        "UNKNOWN": "不明",
    }
    return mapping.get(value, value)


def _overall_status_label(value: str) -> str:
    mapping = {
        "RUNNING": "正常稼働",
        "DEGRADED": "要監視",
        "STOPPED": "停止",
        "UNKNOWN": "不明",
    }
    return mapping.get(value, value)


def _rate_rows(rate_state: dict) -> list[dict]:
    items = rate_state.get("items") if isinstance(rate_state, dict) else {}
    if not isinstance(items, dict):
        return []

    rows: list[dict] = []
    for exchange, item in items.items():
        if not isinstance(item, dict):
            continue

        rows.append(
            {
                "exchange": exchange,
                "summary_state": item.get("summary_state"),
                "engaged": item.get("engaged"),
                "reason": item.get("reason"),
                "official_max_rps": item.get("official_max_rps"),
                "internal_safe_max_rps": item.get("internal_safe_max_rps"),
                "eff_max_rps": item.get("eff_max_rps"),
                "util_ratio": item.get("util_ratio"),
                "wait_ms": item.get("wait_ms"),
                "last_429_ts": item.get("last_429_ts"),
                "hold_until_ts": item.get("hold_until_ts"),
                "backoff_sec": item.get("backoff_sec"),
                "recovery_phase": item.get("recovery_phase"),
                "ts": item.get("ts"),
            }
        )
    return rows


def _origin_age_seconds(origin_state: dict) -> float | None:
    if not isinstance(origin_state, dict):
        return None

    ts = origin_state.get("ts")
    if not ts or not isinstance(ts, str):
        return None

    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None

    return max((datetime.now(timezone.utc) - dt).total_seconds(), 0.0)


def _origin_metric_rows(origin_state: dict) -> list[dict]:
    if not isinstance(origin_state, dict) or not origin_state:
        return []

    return [
        {
            "ws_state": origin_state.get("ws_state"),
            "snapshot_to_live_ms": origin_state.get("snapshot_to_live_ms"),
            "resync_occurred": origin_state.get("resync_occurred"),
            "pre_snapshot_delta_drop_count": origin_state.get("pre_snapshot_delta_drop_count"),
            "origin_age_sec": _origin_age_seconds(origin_state),
            "last_event_name": origin_state.get("last_event_name"),
            "reason": origin_state.get("reason"),
            "channel": origin_state.get("channel"),
        }
    ]


def _origin_stale_status(origin_state: dict, stale_sec: float = 30.0) -> tuple[str, str]:
    age = _origin_age_seconds(origin_state)
    ws_state = None
    if isinstance(origin_state, dict):
        ws_state = origin_state.get("ws_state")

    if not isinstance(origin_state, dict) or not origin_state:
        return ("UNKNOWN", "origin_status unavailable")

    if ws_state != "LIVE":
        return ("STALE", f"ws_state={ws_state or 'unknown'}")

    if age is None:
        return ("UNKNOWN", "origin ts unavailable")

    if age > stale_sec:
        return ("STALE", f"origin_age_sec>{stale_sec:.0f}")

    return ("LIVE", "origin_status fresh")


def _status_age_seconds(status_state: dict) -> float | None:
    if not isinstance(status_state, dict):
        return None

    ts = status_state.get("ts")
    if not ts or not isinstance(ts, str):
        return None

    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None

    return max((datetime.now(timezone.utc) - dt).total_seconds(), 0.0)


def _status_continuity_freshness(status_state: dict, stale_sec: float = 120.0) -> tuple[str, str]:
    age = _status_age_seconds(status_state)
    origin = status_state.get("origin_continuity") if isinstance(status_state, dict) else {}
    ws_state = origin.get("ws_state") if isinstance(origin, dict) else None

    if not isinstance(status_state, dict) or not status_state:
        return ("UNKNOWN", "status.json unavailable")

    if ws_state != "LIVE":
        return ("STALE", f"ws_state={ws_state or 'unknown'}")

    if age is None:
        return ("UNKNOWN", "status ts unavailable")

    if age > stale_sec:
        return ("STALE", f"status_age_sec>{stale_sec:.0f}")

    return ("LIVE", "status.json fresh")


def _origin_audit_summary(events: list[dict]) -> dict:
    summary = {
        "gap_detected": 0,
        "resync_started": 0,
        "resync_completed": 0,
        "resync_complete_ratio": None,
    }

    for row in events:
        event_name = row.get("event")
        if event_name == "origin.stream_gap_detected":
            summary["gap_detected"] += 1
        elif event_name == "origin.stream_resync_started":
            summary["resync_started"] += 1
        elif event_name == "origin.stream_resync_completed":
            summary["resync_completed"] += 1

    started = summary["resync_started"]
    completed = summary["resync_completed"]
    if started > 0:
        summary["resync_complete_ratio"] = completed / started

    return summary


def _request_unified_start() -> tuple[bool, str, bool]:
    try:
        result = start_stack_detached()
        started_components = result.get("started_components") or []
        if result.get("already_running"):
            return True, "stack already running", True

        if started_components:
            joined = ", ".join(
                f"{item.get('component')} pid={item.get('pid')}"
                for item in started_components
            )
            return True, f"stack started components={joined}", False

        return True, "stack start completed (no additional component launch was required)", False
    except Exception as exc:
        return False, str(exc), False


def _request_unified_safe_stop() -> tuple[bool, str]:
    try:
        cfg = load_config()
        request_id = uuid4().hex
        write_unified_supervisor_request(
            cfg,
            {
                "request_id": request_id,
                "action": "stop_stack",
                "requested_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "requested_by": "operator_ui",
                "reason": "maintenance_safe_stop",
            },
        )
        return True, f"safe stop request file written request_id={request_id}"
    except Exception as exc:
        return False, str(exc)


def _request_unified_restart() -> tuple[bool, str]:
    try:
        cfg = load_config()
        request_id = uuid4().hex
        write_unified_supervisor_request(
            cfg,
            {
                "request_id": request_id,
                "action": "restart",
                "requested_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "requested_by": "operator_ui",
                "reason": "manual_code_apply",
            },
        )
        return True, f"restart request file written request_id={request_id}"
    except Exception as exc:
        return False, str(exc)


def _supervisor_status_rows(supervisor_status: dict, supervisor_request: dict) -> list[dict]:
    if not isinstance(supervisor_status, dict) and not isinstance(supervisor_request, dict):
        return []

    return [
        {
            "supervisor_mode": (supervisor_status or {}).get("mode"),
            "started_at": (supervisor_status or {}).get("started_at"),
            "last_seen_ts": (supervisor_status or {}).get("last_seen_ts"),
            "uptime_sec": (supervisor_status or {}).get("uptime_sec"),
            "last_action": (supervisor_status or {}).get("last_action"),
            "last_requested_at": (supervisor_status or {}).get("last_requested_at"),
            "last_completed_at": (supervisor_status or {}).get("last_completed_at"),
            "last_error": (supervisor_status or {}).get("last_error"),
            "request_ack_ts": (supervisor_status or {}).get("request_ack_ts"),
            "acked_request_id": (supervisor_status or {}).get("acked_request_id"),
            "daemon_pid": (supervisor_status or {}).get("daemon_pid"),
            "supervisor_pid": (supervisor_status or {}).get("supervisor_pid"),
            "pending_request_id": (supervisor_request or {}).get("request_id"),
            "pending_action": (supervisor_request or {}).get("action"),
            "pending_reason": (supervisor_request or {}).get("reason"),
            "pending_requested_at": (supervisor_request or {}).get("requested_at"),
            "pending_requested_by": (supervisor_request or {}).get("requested_by"),
        }
    ]


def _is_restart_request_pending(supervisor_request: dict) -> bool:
    if not isinstance(supervisor_request, dict):
        return False
    return str(supervisor_request.get("action") or "").strip().lower() == "restart"


def _is_supervisor_running(supervisor_status: dict) -> bool:
    if not isinstance(supervisor_status, dict):
        return False
    return str(supervisor_status.get("mode") or "").strip().upper() == "RUNNING"


def _audit_rows_for_ui(events: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for row in events:
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}

        rows.append(
            {
                "ts": row.get("ts"),
                "event": row.get("event"),
                "level": row.get("level"),
                "feature": row.get("feature"),
                "reason": row.get("reason") or payload.get("reason"),
                "exchange": row.get("exchange") or payload.get("exchange"),
                "topic": row.get("topic") or payload.get("topic"),
                "stream_session_id": row.get("stream_session_id") or payload.get("stream_session_id"),
                "session_id": row.get("session_id") or payload.get("session_id"),
                "ok": row.get("ok"),
                "latency_ms": row.get("latency_ms"),
                "bytes": row.get("bytes"),
                "payload_preview": json.dumps(payload, ensure_ascii=False)[:240] if payload else "",
            }
        )
    return rows



def _render_scrollable_json_block(payload: object, *, max_height_px: int = 260) -> None:
    """Render existing Collector diagnostics payload as presentation-only scrollable JSON."""
    live_shell.render_scrollable_text_block(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        max_height_px=max_height_px,
        monospace=True,
    )

def render():
    live_shell.render_fragment_block(
        _render_collector_page_body,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
        refresh_mode="poll_fast",
        page_key="collector",
    )


def _render_collector_page_body():
    lang = st.session_state.get("ui_lang", "en")

    live_shell.render_compact_page_header(get_text(lang, "collector_title"))

    runtime = collector_runtime_snapshot()
    live_summary = runtime["live_summary"]

    collector_state = load_state()
    rate_state = collector_state.get("rate", {})
    origin_state = collector_state.get("origin", {})
    daemon_state = collector_state.get("health", {})
    supervisor_status = collector_state.get("supervisor_status", {})
    supervisor_request = collector_state.get("supervisor_request", {})
    stack_control = stack_runtime_snapshot()
    status_state = collector_state.get("status", {})
    daemon_stop_request = collector_state.get("daemon_stop_request", {})
    archive_copy_state = collector_state.get("archive_copy_state", {})
    archive_gc_state = collector_state.get("archive_gc_state", {})
    archive_recent = collector_state.get("archive_recent", {})
    archive_hot_remaining_files = collector_state.get("archive_hot_remaining_files", [])
    origin_continuity = status_state.get("origin_continuity", {}) if isinstance(status_state, dict) else {}
    state_dir_info = collector_state.get("state_dir", {})
    market_state_info = market_state_diagnostics()
    summary_widget = load_execution_market_summary_widget_model()
    recent_audit_events = read_recent_audit_events(lines=200)
    origin_audit_summary = _origin_audit_summary(recent_audit_events)

    render_overview_summary_panel(
        lang=lang,
        live_summary=live_summary,
        runtime=runtime,
        get_text=get_text,
        overall_status_label=_overall_status_label,
        exchange_status_label=_exchange_status_label,
    )

    live_shell.render_scrollable_text_block(
        get_text(lang, "collector_caption_reason_line").format(
            reason=live_summary["overall_reason"],
            live_mode=runtime["mode"],
            health=runtime["health_status"],
            daemon=live_summary["daemon_status"],
            sequence_id=runtime.get("last_sequence_id"),
        ),
        max_height_px=90,
        monospace=True,
    )

    if supervisor_status:
        st.caption(
            get_text(lang, "collector_caption_supervisor_line").format(
                mode=supervisor_status.get("mode", "-"),
                last_action=supervisor_status.get("last_action", "-"),
                last_error=supervisor_status.get("last_error", "-"),
            )
        )
    if supervisor_request and stack_control.get("pending_request_fresh"):
        st.caption(
            get_text(lang, "collector_caption_pending_request_line").format(
                action=supervisor_request.get("action", "-"),
                requested_by=supervisor_request.get("requested_by", "-"),
                reason=supervisor_request.get("reason", "-"),
            )
        )
    if daemon_stop_request:
        st.caption(
            get_text(lang, "collector_caption_daemon_stop_line").format(
                action=daemon_stop_request.get("action", "-"),
                requested_by=daemon_stop_request.get("requested_by", "-"),
            )
        )

    st.caption(get_text(lang, "collector_note_sequence"))

    st.caption(
        get_text(lang, "collector_caption_age_line").format(
            status_age=live_summary["status_age_label"],
            health_age=live_summary["health_age_label"],
            daemon_age=live_summary["daemon_age_label"],
            checkpoint_age=live_summary["checkpoint_age_label"],
        )
    )

    st.caption(
        get_text(lang, "collector_caption_state_dir_line").format(
            path=state_dir_info.get("path", "-"),
        )
    )
    st.caption(
        get_text(lang, "collector_caption_ui_roots_line").format(
            data_root=core_paths.data_dir(ensure=False),
            logs_root=core_paths.logs_dir(ensure=False),
            market_state_root=market_state_info.get("market_state_root"),
        )
    )

    with live_shell.render_folded_section("UI / MarketState Root Diagnostics", expanded=False):
        _render_scrollable_json_block(market_state_info, max_height_px=260)

    render_supervisor_control_section(
        lang=lang,
        get_text=get_text,
        supervisor_status=supervisor_status,
        supervisor_request=supervisor_request,
        stack_control_snapshot=stack_control,
        request_unified_start=_request_unified_start,
        request_unified_safe_stop=_request_unified_safe_stop,
        request_unified_restart=_request_unified_restart,
        is_supervisor_running=_is_supervisor_running,
        is_restart_request_pending=_is_restart_request_pending,
        supervisor_status_rows=_supervisor_status_rows,
    )

    with live_shell.render_folded_section(get_text(lang, "ui_label_collector_runtime_state"), expanded=False):
        _render_scrollable_json_block(
            {
                "live_summary": live_summary,
                "runtime": runtime,
                "collector_state_keys": sorted(list(collector_state.keys())),
            },
            max_height_px=280,
        )

    render_rate_control_section(
        lang=lang,
        get_text=get_text,
        rate_state=rate_state,
        rate_rows=_rate_rows,
    )

    with live_shell.render_folded_section(get_text(lang, "ui_label_ws_continuity_origin_status"), expanded=False):
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            origin_rows = _origin_metric_rows(origin_state)
            if origin_rows:
                metric = origin_rows[0]
                stale_label, stale_reason = _origin_stale_status(origin_state)

                c0, c1, c2, c3, c4, c5 = st.columns(6)
                c0.metric(get_text(lang, "collector_metric_continuity_status"), stale_label)
                c1.metric(get_text(lang, "collector_metric_ws_state"), metric.get("ws_state") or "-")
                c2.metric(get_text(lang, "collector_metric_snapshot_to_live_ms"), metric.get("snapshot_to_live_ms") or "-")
                c3.metric(get_text(lang, "collector_metric_resync_occurred"), metric.get("resync_occurred"))
                c4.metric(get_text(lang, "collector_metric_dropped_pre_snapshot_deltas"), metric.get("pre_snapshot_delta_drop_count") or 0)
                c5.metric(get_text(lang, "collector_metric_origin_age_sec"), metric.get("origin_age_sec") or "-")

                if stale_label == "LIVE":
                    st.success(f"WS continuity status: {stale_label} / {stale_reason}")
                elif stale_label == "STALE":
                    st.warning(f"WS continuity status: {stale_label} / {stale_reason}")
                else:
                    st.info(f"WS continuity status: {stale_label} / {stale_reason}")

            if origin_state:
                with live_shell.render_folded_section(get_text(lang, "ui_label_raw_origin_status_json"), expanded=False):
                    _render_scrollable_json_block(origin_state, max_height_px=260)
            else:
                st.info(get_text(lang, "collector_msg_origin_status_unavailable"))

        with col_r2:
            st.caption(get_text(lang, "ui_label_daemon_supervisor_health"))
            if daemon_state or supervisor_status or supervisor_request:
                _render_scrollable_json_block(
                    {
                        "daemon_health": daemon_state,
                        "supervisor_status": supervisor_status,
                        "supervisor_request": supervisor_request,
                    },
                    max_height_px=260,
                )
            else:
                st.info(get_text(lang, "collector_msg_daemon_health_unavailable"))

    with live_shell.render_folded_section(get_text(lang, "ui_label_raw_rate_state_json"), expanded=False):
        if rate_state:
            _render_scrollable_json_block(rate_state, max_height_px=260)
        else:
            st.info(get_text(lang, "collector_msg_rate_state_unavailable"))

    with live_shell.render_folded_section(get_text(lang, "ui_label_archive_retention_diagnostics"), expanded=False):
        ac1, ac2, ac3, ac4, ac5 = st.columns(5)
        ac1.metric(get_text(lang, "collector_metric_copy_mode"), archive_copy_state.get("mode") or "-")
        ac2.metric(get_text(lang, "collector_metric_gc_mode"), archive_gc_state.get("mode") or "-")
        ac3.metric(get_text(lang, "collector_metric_gc_enabled"), archive_gc_state.get("enabled") if archive_gc_state else "-")
        ac4.metric(get_text(lang, "collector_metric_gc_dry_run"), archive_gc_state.get("dry_run") if archive_gc_state else "-")
        ac5.metric(get_text(lang, "collector_metric_remaining_hot_files"), len(archive_hot_remaining_files))

        st.caption(
            get_text(lang, "collector_caption_archive_started_line").format(
                started_at=archive_copy_state.get("started_at", "-"),
                copy_last_scan_ts=archive_copy_state.get("last_scan_ts", "-"),
                gc_last_scan_ts=archive_gc_state.get("last_scan_ts", "-"),
            )
        )
        st.caption(
            get_text(lang, "collector_caption_archive_counts_line").format(
                copy_plan_count=archive_copy_state.get("last_plan_count", "-"),
                copy_copied_files=archive_copy_state.get("last_copied_files", "-"),
                gc_plan_count=archive_gc_state.get("last_plan_count", "-"),
                gc_deleted_files=archive_gc_state.get("last_deleted_files", "-"),
            )
        )
        st.caption(
            get_text(lang, "collector_caption_archive_audit_path_line").format(
                audit_path=archive_recent.get("audit_path", "-"),
            )
        )

        st.markdown(f"#### {get_text(lang, 'ui_label_archive_latest_copy')}")
        copy_rows = archive_recent.get("copy_rows", []) if isinstance(archive_recent, dict) else []
        if copy_rows:
            st.dataframe(copy_rows, width="stretch")
        else:
            st.info(get_text(lang, "collector_msg_latest_copy_unavailable"))

        st.markdown(f"#### {get_text(lang, 'ui_label_archive_latest_delete')}")
        delete_rows = archive_recent.get("delete_rows", []) if isinstance(archive_recent, dict) else []
        if delete_rows:
            st.dataframe(delete_rows, width="stretch")
        else:
            st.info(get_text(lang, "collector_msg_latest_delete_unavailable"))

        st.markdown(f"#### {get_text(lang, 'ui_label_archive_hot_remaining')}")
        if archive_hot_remaining_files:
            st.dataframe(archive_hot_remaining_files, width="stretch")
        else:
            st.info(get_text(lang, "collector_msg_hot_remaining_unavailable"))

    st.caption(get_text(lang, "collector_page_caption"))

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    render_origin_continuity_summary_section(
        lang=lang,
        get_text=get_text,
        status_state=status_state,
        origin_continuity=origin_continuity,
        status_continuity_freshness=_status_continuity_freshness,
        status_age_seconds=_status_age_seconds,
    )

    with live_shell.slot_widget_from_meta(
        collector_widget_slot("origin_continuity_audit")
    ):
        a1, a2, a3, a4 = st.columns(4)
        a1.metric(get_text(lang, "collector_metric_gap_detected"), origin_audit_summary.get("gap_detected") or 0)
        a2.metric(get_text(lang, "collector_metric_resync_started"), origin_audit_summary.get("resync_started") or 0)
        a3.metric(get_text(lang, "collector_metric_resync_completed"), origin_audit_summary.get("resync_completed") or 0)
        a4.metric(get_text(lang, "collector_metric_resync_complete_ratio"), origin_audit_summary.get("resync_complete_ratio") or "-")

    with live_shell.slot_widget_from_meta(
        collector_widget_slot("system_stats")
    ):
        system_stats.render()

    with live_shell.slot_widget_from_meta(
        collector_widget_slot("execution_feed")
    ):
        execution_feed_panel.render()

    _render_collector_recent_events(lang, recent_audit_events)
    _render_collector_diagnostics(lang)

def _render_collector_recent_events(lang: str, recent_audit_events: list[dict]) -> None:
    with live_shell.render_folded_section(get_text(lang, "collector_recent_events"), expanded=False):
        events = recent_audit_events[:30]
        if events:
            ui_rows = _audit_rows_for_ui(events)
            st.dataframe(ui_rows, width="stretch")
        else:
            st.warning(get_text(lang, "collector_audit_empty"))

def _render_collector_diagnostics(lang: str) -> None:
    with live_shell.render_folded_section(get_text(lang, "ui_slot_diagnostics_title"), expanded=False):
        st.caption(get_text(lang, "ui_slot_diagnostics_collector_caption"))
        slot_rows = get_registered_slots("collector")
        if slot_rows:
            st.dataframe(slot_rows, width="stretch")

            expected_widget_ids = set(collector_widget_ids())
            actual_widget_ids = {str(row.get("widget_id")) for row in slot_rows}
            missing_widget_ids = sorted(
                expected_widget_ids.difference(actual_widget_ids)
            )
            if missing_widget_ids:
                st.warning(
                    "missing collector slot registrations: " + ", ".join(missing_widget_ids)
                )

            actual_zone_ids = {
                str(row.get("zone_id"))
                for row in slot_rows
                if row.get("zone_id") is not None
            }
            unexpected_zone_ids = sorted(
                actual_zone_ids.difference(set(collector_widget_zone_ids()))
            )
            if unexpected_zone_ids:
                st.warning(
                    "unexpected collector zone ids: " + ", ".join(unexpected_zone_ids)
                )
        else:
            st.info(get_text(lang, "ui_slot_registry_empty_collector"))