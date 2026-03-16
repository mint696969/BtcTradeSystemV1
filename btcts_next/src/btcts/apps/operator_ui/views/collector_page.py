# path: ./btcts_next/src/btcts/apps/operator_ui/views/collector_page.py
# desc: Collector vNext の live 運転状態を表示する Operator UI ページ。state / health / checkpoint / audit を基に監視する。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components import execution_feed_panel
from btcts.apps.operator_ui.components import system_stats
from btcts.apps.operator_ui.components.live_bridge import (
    collector_runtime_snapshot,
    read_recent_audit_events,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.collector_state_service import load_state


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


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.title(get_text(lang, "collector_title"))

    runtime = collector_runtime_snapshot()
    live_summary = runtime["live_summary"]

    # Collector state files (rate / origin / daemon health)
    collector_state = load_state()
    rate_state = collector_state.get("rate", {})
    origin_state = collector_state.get("origin", {})
    daemon_state = collector_state.get("health", {})

    col1, col2, col3 = st.columns(3)
    col1.metric("総合状態", _overall_status_label(live_summary["overall_state"]))
    col2.metric("取引所", _exchange_status_label(runtime["exchange_state"]))
    col3.metric("Feed", runtime["feed_state"])

    st.caption(
        f"reason={live_summary['overall_reason']} / "
        f"live_mode={runtime['mode']} / "
        f"health={runtime['health_status']} / "
        f"daemon={live_summary['daemon_status']} / "
        f"last_sequence_id={runtime.get('last_sequence_id')}"
    )

    st.caption(
        f"age status={live_summary['status_age_label']} / "
        f"health={live_summary['health_age_label']} / "
        f"daemon={live_summary['daemon_age_label']} / "
        f"checkpoint={live_summary['checkpoint_age_label']}"
    )

    st.markdown("## Live Operations")

    st.markdown("### Collector Runtime State")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.caption("Rate Control State")
        if rate_state:
            st.json(rate_state)
        else:
            st.info("rate_state.json not available")

    with col_r2:
        st.caption("WS Continuity (origin_status)")
        if origin_state:
            st.json(origin_state)
        else:
            st.info("origin_status.json not available")

    st.caption("Daemon Health")
    if daemon_state:
        st.json(daemon_state)
    else:
        st.info("daemon_health.json not available")

    st.caption(
        "このページは Collector vNext の state.json / health.json / "
        "checkpoint.json / audit.jsonl を基に、現在の live 運転状態のみを表示します。"
    )

    system_stats.render()
    execution_feed_panel.render()

    st.subheader(get_text(lang, "collector_recent_events"))

    events = read_recent_audit_events(lines=30)
    if events:
        localized_events = []
        for row in events:
            localized_events.append(
                {
                    get_text(lang, "event_col_time"): row.get("ts"),
                    get_text(lang, "event_col_event"): row.get("event"),
                    get_text(lang, "event_col_exchange"): row.get("exchange"),
                    get_text(lang, "event_col_topic"): row.get("topic"),
                    get_text(lang, "event_col_latency"): row.get("latency_ms"),
                    get_text(lang, "event_col_bytes"): row.get("bytes"),
                    "stream_session_id": row.get("stream_session_id"),
                    "source": row.get("source"),
                }
            )
        st.dataframe(localized_events, width="stretch")
    else:
        st.warning("live audit event がまだありません。")