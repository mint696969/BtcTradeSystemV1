# path: ./btcts_next/src/btcts/apps/operator_ui/views/collector_page.py
# desc: Collector のリアルタイムイベントを audit.jsonl から読み表示する Operator UI ページ（WarRoom形式）。

import streamlit as st
import json
from pathlib import Path
from btcts.apps.operator_ui.components import system_stats
from btcts.apps.operator_ui.components import market_regime_panel
from btcts.apps.operator_ui.components import market_monitor
from btcts.apps.operator_ui.components import liquidity_pressure_panel
from btcts.apps.operator_ui.components import trade_flow_monitor
from btcts.apps.operator_ui.components import ai_signal_panel
from btcts.apps.operator_ui.components import strategy_state_panel
from btcts.apps.operator_ui.components import ai_market_summary_panel
from btcts.apps.operator_ui.components import ai_conversation_panel
from btcts.apps.operator_ui.components import execution_feed_panel
from btcts.apps.operator_ui.components import risk_monitor_panel
from btcts.apps.operator_ui.components import agent_panels
from btcts.apps.operator_ui.ui_text import get_text

LOG_PATH = Path(r"E:\btc_ts\logs\audit.jsonl")


def read_recent_events(lines=30):

    if not LOG_PATH.exists():
        return []

    with open(LOG_PATH, "rb") as f:

        f.seek(0, 2)
        size = f.tell()

        block = 4096
        data = b""

        while size > 0 and data.count(b"\n") < lines:

            step = min(block, size)
            size -= step
            f.seek(size)

            data = f.read(step) + data

    rows = []

    for line in data.splitlines()[-lines:]:

        try:
            obj = json.loads(line)

            payload = obj.get("payload", {})

            rows.append(
                {
                    "ts": obj.get("ts"),
                    "event": obj.get("event"),
                    "exchange": payload.get("exchange"),
                    "topic": payload.get("topic"),
                    "latency_ms": payload.get("elapsed_ms"),
                    "bytes": payload.get("bytes"),
                }
            )

        except Exception:
            pass

    return rows


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.title(get_text(lang, "collector_title"))

    col1, col2, col3 = st.columns(3)

    col1.metric(
        get_text(lang, "collector_metric_status"),
        get_text(lang, "collector_status_running"),
    )
    col2.metric(
        get_text(lang, "collector_metric_exchange"),
        get_text(lang, "collector_status_connected"),
    )
    col3.metric(
        get_text(lang, "collector_metric_eps"),
        get_text(lang, "collector_status_live"),
    )

    system_stats.render()
    market_regime_panel.render()
    market_monitor.render()
    liquidity_pressure_panel.render()
    trade_flow_monitor.render()
    ai_signal_panel.render()
    strategy_state_panel.render()
    risk_monitor_panel.render()
    agent_panels.render()
    ai_market_summary_panel.render()
    ai_conversation_panel.render()
    execution_feed_panel.render()
    st.subheader(get_text(lang, "collector_recent_events"))

    events = read_recent_events()

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
                }
            )

        st.dataframe(localized_events, width="stretch")
    else:
        st.warning(get_text(lang, "collector_no_events"))
