# path: ./btcts_next/src/btcts/apps/operator_ui/components/execution_feed_panel.py
# desc: audit.jsonl の直近イベントから Execution Feed の件数・レイテンシ・異常傾向を要約表示する WarRoom パネル

import json
from pathlib import Path

import streamlit as st

from btcts.apps.operator_ui.ui_text import get_text

LOG_PATH = Path(r"E:\btc_ts\logs\audit.jsonl")


def _read_recent_events(lines: int = 80):

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
                    "event": obj.get("event", ""),
                    "exchange": payload.get("exchange"),
                    "topic": payload.get("topic"),
                    "latency_ms": payload.get("elapsed_ms"),
                    "bytes": payload.get("bytes"),
                }
            )
        except Exception:
            continue

    return rows


def _avg_latency(events):

    values = [
        float(row["latency_ms"])
        for row in events
        if row.get("latency_ms") is not None
    ]

    if not values:
        return None

    return round(sum(values) / len(values), 1)


def _feed_status(lang: str, events):

    if not events:
        return get_text(lang, "execution_feed_status_empty")

    hold_count = sum(1 for row in events if row.get("event") == "collector.rate.hold")
    error_like = sum(
        1
        for row in events
        if "error" in str(row.get("event", "")).lower()
        or "fail" in str(row.get("event", "")).lower()
    )

    avg_latency = _avg_latency(events)

    if error_like > 0:
        return get_text(lang, "execution_feed_status_alert")

    if avg_latency is not None and avg_latency >= 450:
        return get_text(lang, "execution_feed_status_busy")

    if hold_count >= max(3, len(events) // 4):
        return get_text(lang, "execution_feed_status_throttled")

    return get_text(lang, "execution_feed_status_normal")


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'execution_feed_title')}")

    events = _read_recent_events(lines=80)

    if not events:
        st.warning(get_text(lang, "execution_feed_empty"))
        st.divider()
        return

    total_events = len(events)
    hold_count = sum(1 for row in events if row.get("event") == "collector.rate.hold")
    orderbook_count = sum(1 for row in events if row.get("topic") == "orderbook")
    trades_count = sum(1 for row in events if row.get("topic") == "trades")
    avg_latency = _avg_latency(events)
    max_latency = max(
        [float(row["latency_ms"]) for row in events if row.get("latency_ms") is not None],
        default=0.0,
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "execution_feed_total"), total_events)
    c2.metric(get_text(lang, "execution_feed_avg_latency"), avg_latency if avg_latency is not None else "-")
    c3.metric(get_text(lang, "execution_feed_max_latency"), round(max_latency, 1))
    c4.metric(get_text(lang, "execution_feed_status"), _feed_status(lang, events))

    c5, c6, c7 = st.columns(3)
    c5.metric(get_text(lang, "execution_feed_orderbook"), orderbook_count)
    c6.metric(get_text(lang, "execution_feed_trades"), trades_count)
    c7.metric(get_text(lang, "execution_feed_rate_hold"), hold_count)

    latest = events[-1]
    latest_text = (
        f"{latest.get('event')} / "
        f"{latest.get('exchange')} / "
        f"{latest.get('topic')}"
    )

    st.caption(
        f"{get_text(lang, 'execution_feed_latest')}: {latest_text}"
    )

    st.divider()