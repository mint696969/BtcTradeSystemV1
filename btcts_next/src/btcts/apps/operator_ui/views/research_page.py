# path: ./btcts_next/src/btcts/apps/operator_ui/views/research_page.py
# desc: Research Lab の入口ページ。市場状態メモリ・監査レイテンシ・collector データ状況を俯瞰表示する。

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.ai_memory_store import memory_jsonl_path
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (
    build_tactic_interpretation_display_lines,
    build_tactic_stance_display_lines,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.replay import list_experiment_sessions, load_experiment_session
from btcts.core import paths as core_paths

AUDIT_LOG = core_paths.logs_dir(ensure=False) / "audit.jsonl"
COLLECTOR_RAW_ROOT = core_paths.data_dir(ensure=False) / "collector_raw"
COLLECTOR_COMPACT_ROOT = core_paths.data_dir(ensure=False) / "collector_compact"
MARKET_DATA_ROOT = core_paths.data_dir(ensure=False) / "market_data"
RESEARCH_ROOT = core_paths.research_dir(ensure=False)


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


def _directory_snapshot(path: Path, patterns: tuple[str, ...] = ("*.jsonl",)) -> dict:
    if not path.exists():
        return {
            "files": 0,
            "latest_name": "-",
            "latest_size_mb": 0.0,
            "total_size_mb": 0.0,
        }

    files = []
    for pattern in patterns:
        files.extend(path.rglob(pattern))

    files = sorted(f for f in files if f.is_file())

    if not files:
        return {
            "files": 0,
            "latest_name": "-",
            "latest_size_mb": 0.0,
            "total_size_mb": 0.0,
        }

    latest = max(files, key=lambda f: f.stat().st_mtime)
    total_size_mb = round(sum(f.stat().st_size for f in files) / 1024 / 1024, 2)

    try:
        latest_name = str(latest.relative_to(path))
    except Exception:
        latest_name = latest.name

    return {
        "files": len(files),
        "latest_name": latest_name,
        "latest_size_mb": round(latest.stat().st_size / 1024 / 1024, 2),
        "total_size_mb": total_size_mb,
    }


def _memory_hint(lang: str, latest: pd.Series) -> str:

    if abs(float(latest["imbalance"])) > 0.2 or abs(float(latest["delta"])) > 0.2:
        return get_text(lang, "research_memory_hint_trend")

    return get_text(lang, "research_memory_hint_range")


def _experiment_sessions_df() -> pd.DataFrame:
    rows = list_experiment_sessions(RESEARCH_ROOT)
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    if "mtime" in df.columns:
        df["mtime"] = pd.to_datetime(df["mtime"], unit="s", errors="coerce")
    return df


def _strategy_reports_df(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    return df


def _replay_context_tactic_summary_lines(replay_ctx: dict | None) -> tuple[str, ...]:
    if not isinstance(replay_ctx, dict):
        return ()

    return tuple(
        str(line).strip()
        for line in (replay_ctx.get("tactic_summary_lines") or ())
        if str(line).strip()
    )


def _replay_context_tactic_interpretation_lines(
    replay_ctx: dict | None,
) -> tuple[str, ...]:
    if not isinstance(replay_ctx, dict):
        return ()

    return tuple(
        str(line).strip()
        for line in (replay_ctx.get("tactic_interpretation_lines") or ())
        if str(line).strip()
    )


def _replay_context_primary_tactic_interpretation_line(
    replay_ctx: dict | None,
) -> str:
    if not isinstance(replay_ctx, dict):
        return ""

    return str(
        replay_ctx.get("primary_tactic_interpretation_line") or ""
    ).strip()


def _replay_context_tactic_primary_summary_line(
    replay_ctx: dict | None,
) -> str:
    if not isinstance(replay_ctx, dict):
        return ""

    return str(
        replay_ctx.get("tactic_primary_summary_line") or ""
    ).strip()


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.title(get_text(lang, "research_title"))
    st.caption(get_text(lang, "research_subtitle"))

    replay_ctx = st.session_state.get("research_replay_context")
    summary_widget = load_market_summary_widget_model()

    if replay_ctx:
        st.info("Replay Context から遷移中です。現在の分析条件を表示します。")

        c1, c2, c3 = st.columns(3)
        c1.metric("Replay Session", replay_ctx.get("session_name") or "-")
        c2.metric("Kind Filter", replay_ctx.get("kind_filter") or "-")
        c3.metric("Filtered Rows", replay_ctx.get("filtered_rows") or 0)

        c4, c5, c6 = st.columns(3)
        c4.metric("Start", replay_ctx.get("start_ts") or "-")
        c5.metric("End", replay_ctx.get("end_ts") or "-")
        c6.metric("Jump", replay_ctx.get("jump_ts") or "-")

        st.caption(
            f"event_filter={replay_ctx.get('event_filter') or '-'}"
        )

        tactic_summary_lines = _replay_context_tactic_summary_lines(replay_ctx)
        tactic_interpretation_lines = _replay_context_tactic_interpretation_lines(
            replay_ctx
        )
        primary_tactic_interpretation_line = (
            _replay_context_primary_tactic_interpretation_line(replay_ctx)
        )
        tactic_primary_summary_line = (
            _replay_context_tactic_primary_summary_line(replay_ctx)
        )
        if tactic_summary_lines:
            st.markdown(
                f"#### {get_text(lang, 'research_tactic_stance_summary_title')}"
            )
            for line in build_tactic_stance_display_lines(
                tactic_summary_lines,
                lang,
            ):
                st.markdown(f"- {line}")

        if tactic_primary_summary_line:
            st.caption(f"★ {tactic_primary_summary_line}")

        if primary_tactic_interpretation_line:
            for line in build_tactic_interpretation_display_lines(
                (primary_tactic_interpretation_line,),
                lang,
            ):
                st.caption(f"★ {line}")

        if tactic_interpretation_lines:
            for line in build_tactic_interpretation_display_lines(
                tactic_interpretation_lines,
                lang,
            ):
                st.caption(line)

        a1, a2, a3 = st.columns(3)

        with a1:
            if st.button(
                "Back to Replay",
                key="research_back_to_replay",
            ):
                if replay_ctx.get("jump_ts"):
                    st.session_state.replay_jump_ts = replay_ctx.get("jump_ts")
                st.session_state.ui_selected_page_key = "replay"
                st.rerun()

        with a2:
            if st.button(
                "Back to War Room",
                key="research_back_to_warroom",
            ):
                st.session_state.ui_selected_page_key = "warroom"
                st.rerun()

        with a3:
            if st.button(
                "Clear Context",
                key="research_clear_context",
            ):
                st.session_state.research_replay_context = None
                st.rerun()

        st.divider()
        st.subheader("Replay Context Lens")

        kind_filter = replay_ctx.get("kind_filter")
        event_filter = replay_ctx.get("event_filter")
        jump_ts = replay_ctx.get("jump_ts")

        focus = "general replay analysis"
        hint = "review replay results table for structural signals"
        suggestion = "inspect replay results and sandbox trades"

        if kind_filter == "trade":
            focus = "trade flow analysis"
            hint = "focus on delta imbalance and absorption events"
            suggestion = "inspect micro_events and pressure_bias columns"

        elif kind_filter == "board":
            focus = "orderbook structure analysis"
            hint = "look for wall_side transitions and spread widening"
            suggestion = "check pressure_bias and wall events"

        if event_filter:
            focus = f"event investigation: {event_filter}"
            hint = "this filter isolates specific microstructure events"
            suggestion = "compare replay results around these events"

        if jump_ts:
            suggestion = "validate market behaviour immediately around jump timestamp"

        l1, l2, l3 = st.columns(3)
        l1.metric("Focus", focus)
        l2.metric("Hint", hint)
        l3.metric("Suggested Next Step", suggestion)

    mem_df = _load_memory_df()
    lat_df = _load_latency_df()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            get_text(lang, "research_tab_memory"),
            get_text(lang, "research_tab_latency"),
            get_text(lang, "research_tab_storage"),
            "Experiments",
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

        collector_raw = _directory_snapshot(COLLECTOR_RAW_ROOT, ("*.jsonl",))
        collector_compact = _directory_snapshot(COLLECTOR_COMPACT_ROOT, ("*.jsonl",))
        market_data = _directory_snapshot(MARKET_DATA_ROOT, ("*.jsonl",))
        research = _directory_snapshot(RESEARCH_ROOT, ("*.json", "*.jsonl"))

        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)

        with c1:
            st.markdown("#### Collector Raw")
            st.metric(get_text(lang, "research_storage_file_count"), collector_raw["files"])
            st.metric(get_text(lang, "research_storage_latest_size"), collector_raw["latest_size_mb"])
            st.metric(get_text(lang, "research_storage_total_size"), collector_raw["total_size_mb"])
            st.caption(f"{get_text(lang, 'research_storage_latest_file')}: {collector_raw['latest_name']}")

        with c2:
            st.markdown("#### Collector Compact")
            st.metric(get_text(lang, "research_storage_file_count"), collector_compact["files"])
            st.metric(get_text(lang, "research_storage_latest_size"), collector_compact["latest_size_mb"])
            st.metric(get_text(lang, "research_storage_total_size"), collector_compact["total_size_mb"])
            st.caption(f"{get_text(lang, 'research_storage_latest_file')}: {collector_compact['latest_name']}")

        with c3:
            st.markdown("#### Market Data")
            st.metric(get_text(lang, "research_storage_file_count"), market_data["files"])
            st.metric(get_text(lang, "research_storage_latest_size"), market_data["latest_size_mb"])
            st.metric(get_text(lang, "research_storage_total_size"), market_data["total_size_mb"])
            st.caption(f"{get_text(lang, 'research_storage_latest_file')}: {market_data['latest_name']}")

        with c4:
            st.markdown("#### Research Artifacts")
            st.metric(get_text(lang, "research_storage_file_count"), research["files"])
            st.metric(get_text(lang, "research_storage_latest_size"), research["latest_size_mb"])
            st.metric(get_text(lang, "research_storage_total_size"), research["total_size_mb"])
            st.caption(f"{get_text(lang, 'research_storage_latest_file')}: {research['latest_name']}")

    with tab4:
        st.subheader("Strategy Experiments")

        exp_df = _experiment_sessions_df()

        if exp_df.empty:
            st.warning("Research experiment がまだありません。")
        else:
            st.metric("Experiment Count", int(len(exp_df)))
            st.dataframe(
                exp_df[["session_name", "mtime", "has_summary", "has_best_strategy", "has_regime_report"]],
                width="stretch",
            )

            session_names = exp_df["session_name"].tolist()
            selected_name = st.selectbox("Experiment Session", session_names, index=0)
            selected_row = exp_df.loc[exp_df["session_name"] == selected_name].iloc[0]
            selected_session_dir = Path(str(selected_row["session_dir"]))

            payload = load_experiment_session(selected_session_dir)

            summary = payload.get("summary")
            best_strategy = payload.get("best_strategy")
            regime_report = payload.get("regime_report")
            strategy_reports = payload.get("strategy_reports", [])

            if summary:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Regime", str(summary.get("regime") or "-"))
                c2.metric("Best Strategy", str(summary.get("best_strategy") or "-"))
                c3.metric("Strategy Count", int(summary.get("strategy_count") or 0))
                c4.metric("Result Count", int(summary.get("result_count") or 0))

            if best_strategy:
                st.markdown("#### Best Strategy")
                st.json(best_strategy)

            if regime_report:
                st.markdown("#### Regime Report")
                st.json(regime_report)

            reports_df = _strategy_reports_df(strategy_reports)
            if reports_df.empty:
                st.warning("strategy_reports.jsonl が空です。")
            else:
                st.markdown("#### Strategy Reports")
                st.dataframe(reports_df, width="stretch")

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))