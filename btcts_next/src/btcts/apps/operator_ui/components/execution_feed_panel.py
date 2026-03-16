# path: ./btcts_next/src/btcts/apps/operator_ui/components/execution_feed_panel.py
# desc: audit.jsonl を基に Collector vNext の live execution feed を表示する WarRoom パネル。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.live_bridge import (
    average_latency,
    feed_state_from_events,
    latest_event,
    read_recent_audit_events,
)

from btcts.apps.operator_ui.ui_text import get_text


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'execution_feed_title')}")

    events = read_recent_audit_events(lines=80)
    if not events:
        st.warning("live execution feed がまだありません。")
        st.divider()
        return

    total_events = len(events)
    avg_latency = average_latency(events)
    feed_state = feed_state_from_events(events)
    load_state = "BUSY" if avg_latency is not None and avg_latency >= 450 else "NORMAL"
    max_latency = max(
        [float(row["latency_ms"]) for row in events if row.get("latency_ms") is not None],
        default=0.0,
    )

    board_count = sum(
        1
        for row in events
        if str(row.get("topic")) in {"board_snapshot", "board_ws"}
    )

    trades_count = sum(
        1
        for row in events
        if str(row.get("topic")) in {"executions", "executions_ws"}
    )

    smoke_cycles = sum(
        1
        for row in events
        if str(row.get("topic")) == "collector_vnext_smoke"
    )

    session_count = len(
        {
            row.get("stream_session_id")
            for row in events
            if row.get("stream_session_id")
        }
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("総イベント数", total_events)
    c2.metric("平均サイクル遅延(ms)", "-" if avg_latency is None else avg_latency)
    c3.metric("最大サイクル遅延(ms)", round(max_latency, 1))
    c4.metric("Feed状態", feed_state)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Orderbook件数", board_count)
    c6.metric("Trades件数", trades_count)
    c7.metric("Smoke Cycles", smoke_cycles)
    c8.metric("処理負荷", load_state)

    latest = latest_event(events) or {}
    latest_text = (
        f"{latest.get('event')} / "
        f"{latest.get('exchange')} / "
        f"{latest.get('topic')} / "
        f"{latest.get('source')}"
    )
    st.caption(f"{get_text(lang, 'execution_feed_latest')}: {latest_text}")

    st.divider()