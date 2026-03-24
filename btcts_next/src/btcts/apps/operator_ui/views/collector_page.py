# path: ./btcts_next/src/btcts/apps/operator_ui/views/collector_page.py
# desc: Collector vNext の live 運転状態を表示する Operator UI ページ。state / health / checkpoint / audit を基に監視する。

from __future__ import annotations
from datetime import datetime, timezone
import json
import streamlit as st

from btcts.apps.operator_ui.components import execution_feed_panel
from btcts.apps.operator_ui.components import system_stats
from btcts.apps.operator_ui.components.live_bridge import (
    collector_runtime_snapshot,
    read_recent_audit_events,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.collector_state_service import load_state
from btcts.apps.operator_ui.market_state_service import market_state_diagnostics
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


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.title(get_text(lang, "collector_title"))

    runtime = collector_runtime_snapshot()
    live_summary = runtime["live_summary"]

    collector_state = load_state()
    rate_state = collector_state.get("rate", {})
    origin_state = collector_state.get("origin", {})
    daemon_state = collector_state.get("health", {})
    status_state = collector_state.get("status", {})
    origin_continuity = status_state.get("origin_continuity", {}) if isinstance(status_state, dict) else {}
    state_dir_info = collector_state.get("state_dir", {})
    market_state_info = market_state_diagnostics()
    recent_audit_events = read_recent_audit_events(lines=200)
    origin_audit_summary = _origin_audit_summary(recent_audit_events)

    col1, col2, col3 = st.columns(3)
    col1.metric(get_text(lang, "collector_metric_status"), _overall_status_label(live_summary["overall_state"]))
    col2.metric(get_text(lang, "collector_metric_exchange"), _exchange_status_label(runtime["exchange_state"]))
    col3.metric(get_text(lang, "collector_metric_feed"), runtime["feed_state"])

    st.caption(
        f"reason={live_summary['overall_reason']} / "
        f"live_mode={runtime['mode']} / "
        f"health={runtime['health_status']} / "
        f"daemon={live_summary['daemon_status']} / "
        f"cycle_last_sequence_id={runtime.get('last_sequence_id')}"
    )

    st.caption(get_text(lang, "collector_note_sequence"))

    st.caption(
        f"age status={live_summary['status_age_label']} / "
        f"health={live_summary['health_age_label']} / "
        f"daemon={live_summary['daemon_age_label']} / "
        f"checkpoint={live_summary['checkpoint_age_label']}"
    )

    st.caption(f"state_dir={state_dir_info.get('path', '-')}")
    st.caption(
        f"ui_data_root={core_paths.data_dir(ensure=False)} / "
        f"ui_logs_root={core_paths.logs_dir(ensure=False)} / "
        f"ui_market_state_root={market_state_info.get('market_state_root')}"
    )

    with st.expander("UI / MarketState Root Diagnostics"):
        st.json(market_state_info)

    st.markdown("## Live Operations")
    st.markdown("### Collector Runtime State")

    st.markdown("### Rate Control Summary")
    rate_rows = _rate_rows(rate_state)
    if rate_rows:
        first_rate = rate_rows[0]

        engaged = bool(first_rate.get("engaged"))
        last_429_ts = first_rate.get("last_429_ts")
        rate_posture = "THROTTLED" if engaged else "NORMAL"
        recent_429 = "YES" if last_429_ts else "NO"

        r1, r2, r3, r4, r5, r6 = st.columns(6)
        r1.metric("Rate Posture", rate_posture)
        r2.metric("Recent 429", recent_429)
        r3.metric("Rate Summary", first_rate.get("summary_state") or "-")
        r4.metric("Wait (ms)", first_rate.get("wait_ms") or 0)
        r5.metric("Util Ratio", first_rate.get("util_ratio") or 0)
        r6.metric("Recovery", first_rate.get("recovery_phase") or "-")

        if engaged:
            st.warning(
                f"rate control engaged / reason={first_rate.get('reason') or '-'} / "
                f"hold_until_ts={first_rate.get('hold_until_ts') or '-'}"
            )
        elif last_429_ts:
            st.info(
                f"recent 429 detected / last_429_ts={last_429_ts} / "
                f"recovery_phase={first_rate.get('recovery_phase') or '-'}"
            )
        else:
            st.caption(
                f"rate posture normal / reason={first_rate.get('reason') or '-'} / "
                f"backoff_sec={first_rate.get('backoff_sec') or '-'}"
            )

        st.dataframe(rate_rows, width="stretch")
    else:
        st.info("rate_state.json not available")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.caption("WS Continuity (origin_status)")

        origin_rows = _origin_metric_rows(origin_state)
        if origin_rows:
            metric = origin_rows[0]
            stale_label, stale_reason = _origin_stale_status(origin_state)

            c0, c1, c2, c3, c4, c5 = st.columns(6)
            c0.metric("Continuity Status", stale_label)
            c1.metric("WS State", metric.get("ws_state") or "-")
            c2.metric("Snapshot→LIVE (ms)", metric.get("snapshot_to_live_ms") or "-")
            c3.metric("Resync Occurred", metric.get("resync_occurred"))
            c4.metric("Dropped Pre-Snapshot Deltas", metric.get("pre_snapshot_delta_drop_count") or 0)
            c5.metric("Origin Age (sec)", metric.get("origin_age_sec") or "-")

            if stale_label == "LIVE":
                st.success(f"WS continuity status: {stale_label} / {stale_reason}")
            elif stale_label == "STALE":
                st.warning(f"WS continuity status: {stale_label} / {stale_reason}")
            else:
                st.info(f"WS continuity status: {stale_label} / {stale_reason}")

        if origin_state:
            with st.expander("Raw origin_status JSON"):
                st.json(origin_state)
        else:
            st.info("origin_status.json not available")

    with col_r2:
        st.caption("Daemon Health")
        if daemon_state:
            st.json(daemon_state)
        else:
            st.info("daemon health state not available")

    with st.expander("Raw Rate State JSON"):
        if rate_state:
            st.json(rate_state)
        else:
            st.info("rate_state.json not available")

    st.caption(get_text(lang, "collector_page_caption"))

    st.markdown("### Origin Continuity Summary (status.json)")
    status_freshness_label, status_freshness_reason = _status_continuity_freshness(status_state)
    status_age = _status_age_seconds(status_state)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Status Freshness", status_freshness_label)
    c2.metric("Status Age (sec)", status_age or "-")
    c3.metric("Origin WS State", origin_continuity.get("ws_state") or "-")
    c4.metric("Origin Snapshot→LIVE (ms)", origin_continuity.get("snapshot_to_live_ms") or "-")
    c5.metric("Origin Pre-Snapshot Drops", origin_continuity.get("pre_snapshot_delta_drop_count") or 0)

    if origin_continuity:
        if status_freshness_label == "LIVE":
            st.caption(f"origin_continuity=status.json / {status_freshness_reason}")
        elif status_freshness_label == "STALE":
            st.warning(f"origin_continuity=status.json / {status_freshness_reason}")
        else:
            st.info(f"origin_continuity=status.json / {status_freshness_reason}")
    else:
        st.info("status.json origin_continuity not available")

    st.markdown("### Origin Continuity Audit Summary (recent 200 lines)")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Gap Detected", origin_audit_summary.get("gap_detected") or 0)
    a2.metric("Resync Started", origin_audit_summary.get("resync_started") or 0)
    a3.metric("Resync Completed", origin_audit_summary.get("resync_completed") or 0)
    a4.metric("Resync Complete Ratio", origin_audit_summary.get("resync_complete_ratio") or "-")

    system_stats.render()
    execution_feed_panel.render()

    st.subheader(get_text(lang, "collector_recent_events"))

    events = recent_audit_events[:30]
    if events:
        ui_rows = _audit_rows_for_ui(events)
        st.dataframe(ui_rows, width="stretch")
    else:
        st.warning(get_text(lang, "collector_audit_empty"))