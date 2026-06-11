# path: ./btcts_next/src/btcts/apps/operator_ui/views/logs_page.py
# desc: audit / replay / research の最新ログと成果物を表示する Operator Logs ページ。

from __future__ import annotations

import json
from pathlib import Path
from btcts.core import paths as core_paths
import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.replay import (
    list_experiment_sessions,
    list_replay_sessions,
    load_experiment_session,
    load_replay_session,
)

AUDIT_LOG = core_paths.logs_dir(ensure=False) / "audit.jsonl"
REPLAY_ROOT = core_paths.replay_dir(ensure=False)
RESEARCH_ROOT = core_paths.research_dir(ensure=False)


def _read_recent_audit(lines: int = 120) -> list[dict]:
    if not AUDIT_LOG.exists():
        return []

    with open(AUDIT_LOG, "rb") as f:
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
                    "stream_session_id": payload.get("stream_session_id"),
                    "source": "audit",
                }
            )
        except Exception:
            continue

    return rows


def _latest_replay_payload():
    sessions = list_replay_sessions(REPLAY_ROOT)
    if not sessions:
        return None
    return load_replay_session(Path(str(sessions[0]["session_dir"])), tail_lines=100)


def _latest_experiment_payload():
    sessions = list_experiment_sessions(RESEARCH_ROOT)
    if not sessions:
        return None
    return load_experiment_session(Path(str(sessions[0]["session_dir"])))



def _render_logs_scrollable_json_block(payload: object, *, max_height_px: int = 260) -> None:
    """Render existing Logs-page payload as presentation-only scrollable JSON."""
    live_shell.render_scrollable_text_block(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        max_height_px=max_height_px,
        monospace=True,
    )

def render():
    st.header("System Logs")
    summary_widget = load_market_summary_widget_model()

    audit_rows = _read_recent_audit(lines=120)
    replay_payload = _latest_replay_payload()
    experiment_payload = _latest_experiment_payload()

    tab1, tab2, tab3 = st.tabs(
        [
            "Audit Feed",
            "Replay Tail",
            "Research Tail",
        ]
    )

    with tab1:
        st.subheader("Audit Feed")
        if not audit_rows:
            st.warning("audit.jsonl がまだありません。")
        else:
            st.metric("Audit Events", len(audit_rows))
            df = pd.DataFrame(audit_rows)
            st.dataframe(df, width="stretch")

    with tab2:
        st.subheader("Replay Tail")
        if not replay_payload:
            st.warning("Replay session がまだありません。")
        else:
            report = replay_payload.get("report") or {}
            rows = replay_payload.get("results_tail") or []

            c1, c2, c3 = st.columns(3)
            c1.metric("Result Count", int(report.get("result_count", 0)))
            c2.metric("Board Count", int(report.get("board_count", 0)))
            c3.metric("Trade Count", int(report.get("trade_count", 0)))

            if rows:
                st.dataframe(pd.DataFrame(rows), width="stretch")
            else:
                st.warning("Replay results tail が空です。")

    with tab3:
        st.subheader("Research Tail")
        if not experiment_payload:
            st.warning("Research experiment がまだありません。")
        else:
            summary = experiment_payload.get("summary") or {}
            best_strategy = experiment_payload.get("best_strategy") or {}
            strategy_reports = experiment_payload.get("strategy_reports") or []

            c1, c2, c3 = st.columns(3)
            c1.metric("Regime", str(summary.get("regime") or "-"))
            c2.metric("Best Strategy", str(summary.get("best_strategy") or "-"))
            c3.metric("Strategy Count", int(summary.get("strategy_count") or 0))

            st.markdown("#### Best Strategy")
            _render_logs_scrollable_json_block(best_strategy, max_height_px=260)

            if strategy_reports:
                st.markdown("#### Strategy Reports")
                st.dataframe(pd.DataFrame(strategy_reports), width="stretch")
            else:
                st.warning("strategy_reports が空です。")

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))