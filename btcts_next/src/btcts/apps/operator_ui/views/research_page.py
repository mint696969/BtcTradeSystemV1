# path: ./btcts_next/src/btcts/apps/operator_ui/views/research_page.py
# desc: Research Lab の入口ページ。市場状態メモリ・監査レイテンシ・collector データ状況を俯瞰表示する。

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.ai_memory_store import memory_jsonl_path
from btcts.apps.operator_ui.ui_text import get_text

AUDIT_LOG = Path(r"E:\btc_ts\logs\audit.jsonl")
ORDERBOOK_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\orderbook")
TRADES_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\trades")


def _read_tail_jsonl(path: Path, lines: int = 120) -> list[dict]:

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


def _load_latency_df() -> pd.DataFrame:

    rows = _read_tail_jsonl(AUDIT_LOG, lines=150)

    out = []

    for row in rows:
        payload = row.get("payload", {}) or {}
        latency = payload.get("elapsed_ms")

        if latency is None:
            continue

        out.append(
            {
                "ts": row.get("ts"),
                "event": row.get("event"),
                "topic": payload.get("topic"),
                "latency_ms": latency,
            }
        )

    if not out:
        return pd.DataFrame()

    df = pd.DataFrame(out)
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    return df.dropna(subset=["ts"])


def _directory_snapshot(path: Path) -> dict:

    if not path.exists():
        return {
            "files": 0,
            "latest_name": "-",
            "latest_size_mb": 0.0,
            "total_size_mb": 0.0,
        }

    files = sorted(path.glob("*.jsonl"))

    if not files:
        return {
            "files": 0,
            "latest_name": "-",
            "latest_size_mb": 0.0,
            "total_size_mb": 0.0,
        }

    latest = files[-1]
    total_size_mb = round(sum(f.stat().st_size for f in files) / 1024 / 1024, 2)

    return {
        "files": len(files),
        "latest_name": latest.name,
        "latest_size_mb": round(latest.stat().st_size / 1024 / 1024, 2),
        "total_size_mb": total_size_mb,
    }


def _memory_hint(lang: str, latest: pd.Series) -> str:

    if abs(float(latest["imbalance"])) > 0.2 or abs(float(latest["delta"])) > 0.2:
        return get_text(lang, "research_memory_hint_trend")

    return get_text(lang, "research_memory_hint_range")


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.title(get_text(lang, "research_title"))
    st.caption(get_text(lang, "research_subtitle"))

    mem_df = _load_memory_df()
    lat_df = _load_latency_df()

    tab1, tab2, tab3 = st.tabs(
        [
            get_text(lang, "research_tab_memory"),
            get_text(lang, "research_tab_latency"),
            get_text(lang, "research_tab_storage"),
        ]
    )

    with tab1:
        st.subheader(get_text(lang, "research_memory_title"))

        if mem_df.empty:
            st.warning(get_text(lang, "research_memory_empty"))
        else:
            c1, c2, c3, c4 = st.columns(4)

            latest = mem_df.iloc[-1]
            prev = mem_df.iloc[-2] if len(mem_df) >= 2 else None

            c1.metric(get_text(lang, "research_memory_spread"), round(float(latest["spread"]), 1))
            c2.metric(get_text(lang, "research_memory_imbalance"), round(float(latest["imbalance"]), 3))
            c3.metric(get_text(lang, "research_memory_delta"), round(float(latest["delta"]), 3))
            c4.metric(get_text(lang, "research_memory_wall_ratio"), round(float(latest["wall_ratio"]), 3))

            if prev is not None:
                d1, d2, d3, d4 = st.columns(4)
                d1.metric(
                    get_text(lang, "research_memory_delta_from_prev"),
                    round(float(latest["spread"] - prev["spread"]), 1),
                )
                d2.metric(
                    get_text(lang, "research_memory_delta_from_prev"),
                    round(float(latest["imbalance"] - prev["imbalance"]), 3),
                )
                d3.metric(
                    get_text(lang, "research_memory_delta_from_prev"),
                    round(float(latest["delta"] - prev["delta"]), 3),
                )
                d4.metric(
                    get_text(lang, "research_memory_delta_from_prev"),
                    round(float(latest["wall_ratio"] - prev["wall_ratio"]), 3),
                )

            st.info(
                f"{get_text(lang, 'research_memory_regime_hint')}: "
                f"{_memory_hint(lang, latest)}"
            )

            chart_df = mem_df.set_index("ts")[["spread", "imbalance", "delta", "wall_ratio"]].copy()
            st.line_chart(chart_df, width="stretch")

            st.dataframe(mem_df.tail(20), width="stretch")

    with tab2:
        st.subheader(get_text(lang, "research_latency_title"))

        if lat_df.empty:
            st.warning(get_text(lang, "research_latency_empty"))
        else:
            c1, c2, c3 = st.columns(3)

            c1.metric(get_text(lang, "research_latency_avg"), round(float(lat_df["latency_ms"].mean()), 1))
            c2.metric(get_text(lang, "research_latency_max"), round(float(lat_df["latency_ms"].max()), 1))
            c3.metric(get_text(lang, "research_latency_count"), int(lat_df["latency_ms"].count()))

            chart_df = lat_df.set_index("ts")[["latency_ms"]].copy()
            st.line_chart(chart_df, width="stretch")

            topic_df = (
                lat_df.groupby("topic", dropna=False)["latency_ms"]
                .agg(["mean", "count"])
                .reset_index()
                .rename(
                    columns={
                        "topic": get_text(lang, "research_latency_topic"),
                        "mean": get_text(lang, "research_latency_topic_avg"),
                        "count": get_text(lang, "research_latency_topic_count"),
                    }
                )
            )
            if get_text(lang, "research_latency_topic_avg") in topic_df.columns:
                topic_df[get_text(lang, "research_latency_topic_avg")] = topic_df[
                    get_text(lang, "research_latency_topic_avg")
                ].round(1)

            st.markdown(f"#### {get_text(lang, 'research_latency_by_topic')}")
            st.dataframe(topic_df, width="stretch")

            st.dataframe(lat_df.tail(30), width="stretch")

    with tab3:
        st.subheader(get_text(lang, "research_storage_title"))

        orderbook = _directory_snapshot(ORDERBOOK_DIR)
        trades = _directory_snapshot(TRADES_DIR)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"#### {get_text(lang, 'research_storage_orderbook')}")
            st.metric(get_text(lang, "research_storage_file_count"), orderbook["files"])
            st.metric(get_text(lang, "research_storage_latest_size"), orderbook["latest_size_mb"])
            st.metric(get_text(lang, "research_storage_total_size"), orderbook["total_size_mb"])
            st.caption(f"{get_text(lang, 'research_storage_latest_file')}: {orderbook['latest_name']}")

        with c2:
            st.markdown(f"#### {get_text(lang, 'research_storage_trades')}")
            st.metric(get_text(lang, "research_storage_file_count"), trades["files"])
            st.metric(get_text(lang, "research_storage_latest_size"), trades["latest_size_mb"])
            st.metric(get_text(lang, "research_storage_total_size"), trades["total_size_mb"])
            st.caption(f"{get_text(lang, 'research_storage_latest_file')}: {trades['latest_name']}")