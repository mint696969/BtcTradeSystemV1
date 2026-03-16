# path: ./btcts_next/src/btcts/apps/operator_ui/components/system_stats.py
# desc: Collector vNext の live state / audit のみを基に Collector 統計を表示する live Operations パネル。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.live_bridge import collector_runtime_snapshot
from btcts.apps.operator_ui.ui_text import get_text


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'system_stats_title')}")

    runtime = collector_runtime_snapshot()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Mode", runtime["mode"])
    c2.metric("Health", runtime["health_status"])
    c3.metric(
        "Avg Cycle Latency",
        "-" if runtime["avg_latency_ms"] is None else runtime["avg_latency_ms"],
    )
    c4.metric("Active Topics", runtime["active_topics"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Last Sequence ID", runtime.get("last_sequence_id") or "-")
    c6.metric("Audit Rows", len(runtime["audit_rows"]))
    c7.metric("Stream Sessions", runtime["stream_sessions"])
    c8.metric("Feed State", runtime["feed_state"])

    st.caption(
        f"source=collector_vnext_live / "
        f"exchange_state={runtime['exchange_state']} / "
        f"status_mode={runtime.get('live_summary', {}).get('status_mode')} / "
        f"health_status={runtime.get('live_summary', {}).get('health_status')} / "
        f"daemon_status={runtime.get('live_summary', {}).get('daemon_status')}"
    )

    st.divider()