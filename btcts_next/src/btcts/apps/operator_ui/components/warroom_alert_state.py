# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_alert_state.py
# desc: War Room alert の live / replay state 組み立てと監査レイテンシ取得を分離したデータ層。

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from btcts.core import paths as core_paths

from btcts.apps.operator_ui.components.market_signal_state import (
    MarketSignalContext,
    load_market_signal_context,
)
from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_best_strategy_name,
    latest_regime_name,
    load_latest_experiment_payload,
    load_latest_replay_payload,
    replay_tail_rows,
    tradeflow_metrics,
)

def _audit_log_path() -> Path:
    return core_paths.logs_dir(ensure=False) / "audit.jsonl"


def recent_audit_latency(lines: int = 40):
    audit_log = _audit_log_path()
    if not audit_log.exists():
        return None

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

    rows = []

    for line in data.splitlines()[-lines:]:
        try:
            obj = json.loads(line)
            payload = obj.get("payload", {})
            if payload.get("elapsed_ms") is not None:
                rows.append(float(payload["elapsed_ms"]))
        except Exception:
            continue

    if not rows:
        return None

    return sum(rows) / len(rows)


class WarroomLiveAlertState(TypedDict):
    spread: float
    imbalance: float
    delta: float
    alert_ts: str | None
    regime: str
    best_strategy: str
    latency: float | None


def build_live_alert_state() -> WarroomLiveAlertState | None:
    signal_state: MarketSignalContext | None = load_market_signal_context()
    if not signal_state:
        return None

    if str(signal_state.get("data_source") or "") != "live_canonical":
        return None

    return {
        "spread": signal_state.get("spread"),
        "imbalance": signal_state.get("imbalance"),
        "delta": 0.0 if signal_state.get("delta") is None else signal_state.get("delta"),
        "alert_ts": signal_state.get("event_ts"),
        "regime": signal_state.get("regime"),
        "best_strategy": signal_state.get("best_strategy"),
        "latency": recent_audit_latency(),
    }


def build_replay_alert_state() -> dict | None:
    replay_payload = load_latest_replay_payload()
    experiment_payload = load_latest_experiment_payload()

    tail = replay_tail_rows(replay_payload, limit=20)
    if not tail:
        return None

    board_snapshots = []
    trade_snapshots = []

    for row in tail:
        if not isinstance(row, dict):
            continue

        kind = row.get("kind")
        if kind == "board":
            board = board_signal_metrics(row)
            if board:
                board_snapshots.append(board)
        elif kind == "trade":
            flow = tradeflow_metrics(row)
            if flow:
                trade_snapshots.append(flow)

    if not board_snapshots:
        return None

    latest_board = board_snapshots[-1]
    previous_board = board_snapshots[-2] if len(board_snapshots) >= 2 else None
    latest_flow = trade_snapshots[-1] if trade_snapshots else None

    alert_ts = (
        str(latest_board.get("event_ts"))
        if latest_board.get("event_ts")
        else str(latest_flow.get("event_ts"))
        if isinstance(latest_flow, dict) and latest_flow.get("event_ts")
        else None
    )

    return {
        "previous_board": previous_board,
        "latest_board": latest_board,
        "latest_flow": latest_flow,
        "spread": latest_board.get("spread"),
        "imbalance": latest_board.get("imbalance"),
        "pressure_bias": latest_board.get("pressure_bias"),
        "wall_ratio": latest_board.get("wall_ratio"),
        "delta": latest_flow.get("trade_delta") if isinstance(latest_flow, dict) else None,
        "alert_ts": alert_ts,
        "regime": latest_regime_name(experiment_payload),
        "best_strategy": latest_best_strategy_name(experiment_payload),
        "latency": recent_audit_latency(),
    }