# path: ./btcts_next/src/btcts/apps/operator_ui/views/health_page.py
# desc: Replay / Research / Audit / vNext state を基にシステム状態を表示する Operator Health ページ。

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    load_latest_experiment_payload,
    load_latest_replay_payload,
)

AUDIT_LOG = Path(r"E:\btc_ts\logs\audit.jsonl")
STATE_ROOT = Path(r"E:\btc_ts\state\collector_vnext")


def _read_json(path: Path):
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_recent_audit(lines: int = 100) -> list[dict]:
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
                }
            )
        except Exception:
            continue

    return rows


def _avg_latency(rows: list[dict]) -> float | None:
    values = [
        float(row["latency_ms"])
        for row in rows
        if row.get("latency_ms") is not None
    ]
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def _system_status_label(status_payload, health_payload, replay_payload, experiment_payload) -> str:
    if status_payload and str(status_payload.get("mode")) in {"RUNNING", "DEGRADED"}:
        return "RUNNING"
    if health_payload and health_payload.get("ok") is True:
        return "HEALTHY"
    if replay_payload or experiment_payload:
        return "DEGRADED"
    return "NO DATA"


def render():
    st.header("System Health")

    status_payload = _read_json(STATE_ROOT / "status.json")
    health_payload = _read_json(STATE_ROOT / "health.json")
    checkpoint_payload = _read_json(STATE_ROOT / "checkpoint.json")

    replay_payload = load_latest_replay_payload()
    experiment_payload = load_latest_experiment_payload()
    audit_rows = _read_recent_audit(lines=100)

    avg_latency = _avg_latency(audit_rows)
    replay_rows = replay_payload.get("results_tail", []) if replay_payload else []
    strategy_reports = experiment_payload.get("strategy_reports", []) if experiment_payload else []

    system_status = _system_status_label(
        status_payload,
        health_payload,
        replay_payload,
        experiment_payload,
    )

    last_sequence_id = 0
    if checkpoint_payload and checkpoint_payload.get("last_sequence_id") is not None:
        last_sequence_id = checkpoint_payload.get("last_sequence_id")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", system_status)
    c2.metric("Avg Latency", "-" if avg_latency is None else avg_latency)
    c3.metric("Replay Rows", len(replay_rows))
    c4.metric("Strategy Reports", len(strategy_reports))

    c5, c6, c7 = st.columns(3)
    c5.metric("Last Sequence ID", last_sequence_id)
    c6.metric("Audit Rows", len(audit_rows))
    c7.metric(
        "Health OK",
        "-" if not health_payload else str(bool(health_payload.get("ok"))),
    )

    if status_payload:
        st.markdown("#### vNext Status")
        st.json(status_payload)

    if health_payload:
        st.markdown("#### vNext Health")
        st.json(health_payload)

    if checkpoint_payload:
        st.markdown("#### vNext Checkpoint")
        st.json(checkpoint_payload)

    if audit_rows:
        st.markdown("#### Recent Audit Health Signals")
        df = pd.DataFrame(audit_rows[-20:])
        st.dataframe(df, width="stretch")