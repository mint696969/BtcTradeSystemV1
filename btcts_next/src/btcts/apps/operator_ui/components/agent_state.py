# path: ./btcts_next/src/btcts/apps/operator_ui/components/agent_state.py
# desc: Agent Panels の state 組み立てと監査ログ読取を分離したデータ層。

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TypedDict

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)


def _audit_log_path() -> Path:
    logs_dir = os.environ.get("BTC_TS_LOGS_DIR", r"E:\btc_ts\logs")
    return Path(logs_dir) / "audit.jsonl"


def read_recent_audit(lines: int = 40) -> list[dict]:
    audit_log = _audit_log_path()

    if not audit_log.exists():
        return []

    with open(audit_log, "rb") as f:
        f.seek(0, 2)
        size = f.tell()

        block = 4096
        data = b""

        while size > 0 and data.count(b"\n") < lines:
            step = min(block, size)
            size -= step
            f.seek(size)
            data = f.read(step) + data

    out: list[dict] = []

    for line in data.splitlines()[-lines:]:
        try:
            obj = json.loads(line)
            payload = obj.get("payload", {})
            out.append(
                {
                    "event": obj.get("event"),
                    "latency_ms": payload.get("elapsed_ms"),
                    "topic": payload.get("topic"),
                }
            )
        except Exception:
            continue

    return out


class AgentState(TypedDict):
    audit_rows: list[dict]
    source_label: str
    spread: float
    imbalance: float
    delta: float
    wall_ratio: float | None
    pressure_bias: str | None
    event_ts: str | None
    regime: str
    best_strategy: str
    data_source: str


def analyze_agent_state() -> AgentState | None:
    audit_rows = read_recent_audit(lines=40)
    signal_state: MarketSignalContext | None = load_market_signal_context()
    if not signal_state:
        return None

    data_source = str(signal_state.get("data_source") or "unknown")
    source_label = (
        "live_canonical + research_experiment + audit_latency"
        if data_source == "live_canonical"
        else "replay_board+tradeflow + research_experiment + audit_latency"
    )

    return {
        "audit_rows": audit_rows,
        "source_label": source_label,
        **signal_state,
    }