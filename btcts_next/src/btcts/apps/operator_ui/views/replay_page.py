# path: ./btcts_next/src/btcts/apps/operator_ui/views/replay_page.py
# desc: Replay Lab page that shows replay export sessions, reports, replay results, and strategy sandbox outputs.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.components.ai_operator_action_payloads import (
    build_research_context_base,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.core import paths as core_paths
from btcts.replay import (
    build_regime_report,
    build_strategy_report,
    list_replay_sessions,
    load_replay_session,
    run_strategy_sandbox,
)

from btcts.replay.strategy_compare import compare_strategies
from btcts.replay.strategy_registry import STRATEGY_REGISTRY

REPLAY_ROOT = core_paths.replay_dir(ensure=False)


def _sessions_df() -> pd.DataFrame:
    rows = list_replay_sessions(REPLAY_ROOT)
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    if "mtime" in df.columns:
        df["mtime"] = pd.to_datetime(df["mtime"], unit="s", errors="coerce")
    return df


def _results_df(rows: list[dict]) -> pd.DataFrame:
    out = []

    for row in rows:
        signal = row.get("result", {}).get("signal") if isinstance(row.get("result"), dict) else None
        micro = row.get("microstructure", []) if isinstance(row.get("microstructure"), list) else []
        events = row.get("result", {}).get("events", []) if isinstance(row.get("result"), dict) else []

        out.append(
            {
                "kind": row.get("kind"),
                "record_type": row.get("record_type"),
                "event_ts": row.get("event_ts"),
                "best_bid": row.get("result", {}).get("best_bid") if isinstance(row.get("result"), dict) else None,
                "best_ask": row.get("result", {}).get("best_ask") if isinstance(row.get("result"), dict) else None,
                "pressure_bias": None if not isinstance(signal, dict) else signal.get("pressure", {}).get("bias"),
                "wall_side": None if not isinstance(signal, dict) else signal.get("wall", {}).get("strongest_side"),
                "signal_events": ", ".join(
                    str(e.get("event_name")) for e in events if isinstance(e, dict) and e.get("event_name")
                ),
                "micro_events": ", ".join(
                    str(e.get("event_name")) for e in micro if isinstance(e, dict) and e.get("event_name")
                ),
            }
        )

    if not out:
        return pd.DataFrame()

    df = pd.DataFrame(out)
    if "event_ts" in df.columns:
        df["event_ts"] = pd.to_datetime(df["event_ts"], errors="coerce")

    sort_cols = [col for col in ["event_ts", "kind", "record_type"] if col in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols, ascending=[True] * len(sort_cols), na_position="last").reset_index(drop=True)

    return df


def _sandbox_trades_df(trades: list) -> pd.DataFrame:
    rows = []

    for trade in trades:
        rows.append(
            {
                "side": getattr(trade, "side", None),
                "entry_ts": getattr(trade, "entry_ts", None),
                "entry_price": getattr(trade, "entry_price", None),
                "exit_ts": getattr(trade, "exit_ts", None),
                "exit_price": getattr(trade, "exit_price", None),
                "size": getattr(trade, "size", None),
                "reason": getattr(trade, "reason", None),
                "exit_reason": getattr(trade, "exit_reason", None),
                "pnl": getattr(trade, "pnl", None),
            }
        )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    for col in ["entry_ts", "exit_ts"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.title(get_text(lang, "replay_title"))
    st.caption("Replay export / report / results / sandbox を閲覧する bridge")
    summary_widget = load_market_summary_widget_model()

    tab1, tab2, tab3 = st.tabs(
        [
            "Replay Sessions",
            "Replay Report",
            "Replay Results",
        ]
    )

    sessions_df = _sessions_df()

    with tab1:
        st.subheader("Replay Sessions")

        if sessions_df.empty:
            st.warning("Replay export session がまだありません。")
        else:
            st.metric("Session Count", int(len(sessions_df)))
            st.dataframe(
                sessions_df[["session_name", "mtime", "has_manifest", "has_report", "has_results"]],
                width="stretch",
            )

    selected_session_dir = None
    if not sessions_df.empty:
        session_names = sessions_df["session_name"].tolist()
        selected_name = st.selectbox("Session", session_names, index=0)
        selected_row = sessions_df.loc[sessions_df["session_name"] == selected_name].iloc[0]
        selected_session_dir = Path(str(selected_row["session_dir"]))

    session_payload = None
    if selected_session_dir is not None:
        session_payload = load_replay_session(selected_session_dir, tail_lines=200)

    sandbox = None
    sandbox_report = None
    regime_report = None

    if session_payload:
        rows = session_payload.get("results_tail", [])
        if isinstance(rows, list) and rows:
            regime_report = build_regime_report(rows)

            sandbox = run_strategy_sandbox(
                "ui_replay_sandbox",
                rows,
                size=1.0,
            )
            sandbox_report = build_strategy_report(sandbox)

    with tab2:
        st.subheader("Replay Report")
        st.caption("上部の Replay Report は保存済み report 全体集計、下部の Regime / Sandbox は results tail を基に再計算しています。")

        if not session_payload or not session_payload.get("report"):
            st.warning("replay_report.json を読み込めません。")
        else:
            report = session_payload["report"]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Results", int(report.get("result_count", 0)))
            c2.metric("Board", int(report.get("board_count", 0)))
            c3.metric("Trades", int(report.get("trade_count", 0)))
            c4.metric("Micro Events", int(report.get("microstructure_event_count", 0)))

            event_name_counts = report.get("event_name_counts", {})
            if isinstance(event_name_counts, dict) and event_name_counts:
                counts_df = pd.DataFrame(
                    [
                        {"event_name": key, "count": value}
                        for key, value in event_name_counts.items()
                    ]
                )
                st.dataframe(counts_df, width="stretch")

            st.json(report)

        st.divider()
        st.subheader("Tail Market Regime")

        if not regime_report:
            st.warning("Regime report を生成できません。")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Regime", str(regime_report.get("regime") or "unknown"))
            c2.metric("Spread", str(regime_report.get("spread_state") or "unknown"))
            c3.metric("Pressure", str(regime_report.get("pressure_state") or "unknown"))
            c4.metric("Absorption", int(regime_report.get("absorption_count", 0)))

            c5, c6, c7 = st.columns(3)
            avg_spread = regime_report.get("avg_spread")
            price_change = regime_report.get("price_change")
            price_change_pct = regime_report.get("price_change_pct")

            c5.metric("Avg Spread", None if avg_spread is None else round(float(avg_spread), 2))
            c6.metric("Price Change", None if price_change is None else round(float(price_change), 2))
            c7.metric(
                "Price Change %",
                None if price_change_pct is None else round(float(price_change_pct) * 100.0, 4),
            )

            st.json(regime_report)

        st.divider()
        st.subheader("Tail Strategy Sandbox Report")

        if not sandbox_report:
            st.warning("Sandbox report を生成できません。")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Trades", int(sandbox_report.get("trade_count", 0)))
            c2.metric("Closed", int(sandbox_report.get("closed_trade_count", 0)))
            c3.metric("Wins", int(sandbox_report.get("win_count", 0)))
            c4.metric("Losses", int(sandbox_report.get("loss_count", 0)))

            c5, c6 = st.columns(2)
            c5.metric("Total PnL", round(float(sandbox_report.get("total_pnl", 0.0)), 2))
            avg_pnl = sandbox_report.get("avg_pnl")
            c6.metric("Avg PnL", None if avg_pnl is None else round(float(avg_pnl), 2))

            st.json(sandbox_report)

    with tab3:
        st.subheader("Replay Results")
        st.caption("この表は replay_results.jsonl の tail を表示しています。")

        st.subheader("Replay Time Navigator")

        t1, t2, t3 = st.columns(3)

        with t1:
            start_ts = st.text_input(
                "Start timestamp (optional)",
                "",
                key="replay_start_ts",
            )

        with t2:
            end_ts = st.text_input(
                "End timestamp (optional)",
                "",
                key="replay_end_ts",
            )

        replay_jump_default = st.session_state.get("replay_jump_ts", "")

        with t3:
            jump_ts = st.text_input(
                "Jump to timestamp",
                replay_jump_default,
                key="replay_jump_ts",
            )

        st.subheader("Replay Filters")

        f1, f2, f3 = st.columns(3)

        with f1:
            kind_filter = st.selectbox(
                "Kind",
                ["all", "board", "trade"],
                index=0,
                key="replay_kind_filter",
            )

        with f2:
            event_filter = st.text_input(
                "Event contains",
                "",
                key="replay_event_filter",
            )

        with f3:
            limit_rows = st.slider(
                "Max rows",
                min_value=50,
                max_value=2000,
                value=500,
                step=50,
                key="replay_limit_rows",
            )

        if not session_payload:
            st.warning("Replay session が選択されていません。")
        else:
            rows = session_payload.get("results_tail", [])
            results_df = _results_df(rows)

            # --- time filtering ---

            if start_ts:
                try:
                    start_dt = pd.to_datetime(start_ts)
                    results_df = results_df[results_df["event_ts"] >= start_dt]
                except Exception:
                    st.warning("Invalid start timestamp format")

            if end_ts:
                try:
                    end_dt = pd.to_datetime(end_ts)
                    results_df = results_df[results_df["event_ts"] <= end_dt]
                except Exception:
                    st.warning("Invalid end timestamp format")

            # jump to nearest timestamp

            if jump_ts:
                try:
                    jump_dt = pd.to_datetime(jump_ts)
                    idx = (results_df["event_ts"] - jump_dt).abs().idxmin()
                    results_df = results_df.loc[[idx]]
                except Exception:
                    st.warning("Invalid jump timestamp")

            if st.session_state.get("replay_jump_ts"):
                st.session_state.replay_jump_ts = ""

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Rows (time-filtered)", int(len(results_df)))
            c2.metric(
                "Buy Pressure",
                int((results_df["pressure_bias"] == "buy_pressure").sum()) if "pressure_bias" in results_df.columns else 0,
            )
            c3.metric(
                "Sell Pressure",
                int((results_df["pressure_bias"] == "sell_pressure").sum()) if "pressure_bias" in results_df.columns else 0,
            )
            c4.metric(
                "Wall Events",
                int(results_df["wall_side"].notna().sum()) if "wall_side" in results_df.columns else 0,
            )

            if kind_filter != "all":
                results_df = results_df[results_df["kind"] == kind_filter]

            if event_filter:
                mask = (
                    results_df["signal_events"].astype(str).str.contains(event_filter, case=False)
                    | results_df["micro_events"].astype(str).str.contains(event_filter, case=False)
                )
                results_df = results_df[mask]

            results_df = results_df.tail(limit_rows).reset_index(drop=True)

            st.caption(
                f"filtered_rows={len(results_df)} / "
                f"kind={kind_filter} / "
                f"event_filter={'-' if not event_filter else event_filter} / "
                f"max_rows={limit_rows}"
            )

            if results_df.empty:
                st.warning("Replay結果がありません。filter条件で0件の可能性があります。")
            else:
                st.metric("Tail Rows", int(len(results_df)))
                st.dataframe(results_df, width="stretch")

                if st.button(
                    "Open in Research",
                    key="replay_open_in_research",
                ):
                    st.session_state.research_replay_context = (
                        build_research_context_base(
                            session_name=(
                                selected_name if "selected_name" in locals() else ""
                            ),
                            start_ts=start_ts,
                            end_ts=end_ts,
                            jump_ts=jump_ts,
                            kind_filter=kind_filter,
                            event_filter=event_filter,
                            filtered_rows=int(len(results_df)),
                        )
                    )
                    st.session_state.ui_selected_page_key = "research"
                    st.rerun()

        st.divider()
        st.subheader("Tail Sandbox Trades")
        st.caption("Sandbox は現在、選択中 session の tail を基に再計算しています。")
        
        if sandbox is None:
            st.warning("Sandbox result がありません。")
        else:
            trades_df = _sandbox_trades_df(sandbox.trades)
            if trades_df.empty:
                st.warning("Sandbox trade がありません。")
            else:
                st.metric("Sandbox Trade Count", int(len(trades_df)))
                st.dataframe(trades_df, width="stretch")

        st.divider()
        st.subheader("Tail Strategy Comparison")
        st.caption("Strategy Comparison は現在、選択中 session の tail 全体を基に再計算しています。")
        
        if session_payload:
            rows = session_payload.get("results_tail", [])

            if rows:
                comparison = compare_strategies(
                    STRATEGY_REGISTRY,
                    rows,
                    size=1.0,
                )

                df = pd.DataFrame(comparison.reports)
                st.dataframe(df, width="stretch")
            else:
                st.warning("Replay results がありません。")
        else:
            st.warning("Replay session が選択されていません。")

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))