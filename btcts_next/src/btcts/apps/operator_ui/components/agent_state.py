# path: ./btcts_next/src/btcts/apps/operator_ui/components/agent_state.py
# desc: Agent Panels の state 組み立てと監査ログ読取を分離したデータ層。

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from btcts.core import paths as core_paths

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)


def _audit_log_path() -> Path:
    return core_paths.logs_dir(ensure=False) / "audit.jsonl"


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


def _source_label_for_data_source(data_source: str, *, suffix: str) -> str:
    labels = {
        "execution_market_live_canonical": f"execution_market_live_canonical + {suffix}",
        "execution_market_state": f"execution_market_state + {suffix}",
        # Legacy labels kept only for compatibility with old tests/callers.
        "live_canonical": f"live_canonical + {suffix}",
        "replay_board_tradeflow": f"replay_board+tradeflow + {suffix}",
        "replay_research": f"replay_board+tradeflow + {suffix}",
    }
    if data_source == "unknown":
        return f"unknown + {suffix}"
    return labels.get(data_source, f"{data_source} + {suffix}")


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
    source_label = _source_label_for_data_source(
        data_source,
        suffix="research_experiment + audit_latency",
    )

    return {
        "audit_rows": audit_rows,
        "source_label": source_label,
        **signal_state,
    }