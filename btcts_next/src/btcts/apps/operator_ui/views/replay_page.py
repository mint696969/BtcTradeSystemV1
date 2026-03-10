# path: ./btcts_next/src/btcts/apps/operator_ui/views/replay_page.py
# desc: Replay Lab の入口ページ。直近 audit イベントと市場状態メモリ履歴を再確認するための土台を表示する。

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.ai_memory_store import memory_jsonl_path
from btcts.apps.operator_ui.ui_text import get_text

AUDIT_LOG = Path(r"E:\btc_ts\logs\audit.jsonl")


def _read_tail_jsonl(path: Path, lines: int = 200) -> list[dict]:

    if not path.exists():
        return []

    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()

        block = 4096
        data = b""

        while size > 0 and data.count(b"\n") < lines:
            step = min(block, size)
            size -= step
            f.seek(size)
            data = f.read(step) + data

    rows: list[dict] = []

    for line in data.splitlines()[-lines:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            continue

    return rows


def _load_event_df() -> pd.DataFrame:

    rows = _read_tail_jsonl(AUDIT_LOG, lines=200)

    out = []

    for row in rows:
        payload = row.get("payload", {}) or {}
        out.append(
            {
                "ts": row.get("ts"),
                "event": row.get("event"),
                "exchange": payload.get("exchange"),
                "topic": payload.get("topic"),
                "latency_ms": payload.get("elapsed_ms"),
                "bytes": payload.get("bytes"),
            }
        )

    if not out:
        return pd.DataFrame()

    df = pd.DataFrame(out)
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    return df.dropna(subset=["ts"])


def _load_memory_df() -> pd.DataFrame:

    rows = _read_tail_jsonl(memory_jsonl_path(), lines=120)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    keep = [c for c in ["ts", "spread", "imbalance", "delta", "wall_ratio"] if c in df.columns]
    df = df[keep].copy()

    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

    return df.dropna(subset=["ts"]) if "ts" in df.columns else df


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.title(get_text(lang, "replay_title"))
    st.caption(get_text(lang, "replay_subtitle"))

    tab1, tab2, tab3 = st.tabs(
        [
            get_text(lang, "replay_tab_events"),
            get_text(lang, "replay_tab_memory"),
            get_text(lang, "replay_tab_future"),
        ]
    )

    with tab1:
        st.subheader(get_text(lang, "replay_events_title"))

        event_df = _load_event_df()

        if event_df.empty:
            st.warning(get_text(lang, "replay_events_empty"))
        else:
            c1, c2, c3 = st.columns(3)

            c1.metric(get_text(lang, "replay_events_count"), int(len(event_df)))
            c2.metric(
                get_text(lang, "replay_events_avg_latency"),
                round(float(event_df["latency_ms"].dropna().mean()), 1)
                if event_df["latency_ms"].dropna().shape[0] > 0
                else "-",
            )
            c3.metric(
                get_text(lang, "replay_events_max_latency"),
                round(float(event_df["latency_ms"].dropna().max()), 1)
                if event_df["latency_ms"].dropna().shape[0] > 0
                else "-",
            )

            st.dataframe(event_df.tail(50), width="stretch")

    with tab2:
        st.subheader(get_text(lang, "replay_memory_title"))

        memory_df = _load_memory_df()

        if memory_df.empty:
            st.warning(get_text(lang, "replay_memory_empty"))
        else:
            chart_df = memory_df.set_index("ts")[["spread", "imbalance", "delta", "wall_ratio"]].copy()
            st.line_chart(chart_df, width="stretch")
            st.dataframe(memory_df.tail(40), width="stretch")

    with tab3:
        st.subheader(get_text(lang, "replay_future_title"))
        st.markdown(get_text(lang, "replay_future_desc"))
        st.markdown(
            "\n".join(
                [
                    f"- {get_text(lang, 'replay_future_item_1')}",
                    f"- {get_text(lang, 'replay_future_item_2')}",
                    f"- {get_text(lang, 'replay_future_item_3')}",
                ]
            )
        )