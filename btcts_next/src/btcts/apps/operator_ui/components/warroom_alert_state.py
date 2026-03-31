# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_alert_state.py
# desc: War Room alert の live / replay state 組み立てと監査レイテンシ取得を分離したデータ層。

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
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

AUDIT_LOG = Path(r"E:\btc_ts\logs\audit.jsonl")


def recent_audit_latency(lines: int = 40):
    if not AUDIT_LOG.exists():
        return None

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


def build_live_alert_state() -> dict | None:
    live_board = latest_live_board_metrics()
    live_flow = recent_live_tradeflow_metrics(lines=80)
    experiment_payload = load_latest_experiment_payload()

    spread = live_board.get("spread")
    if spread is None:
        return None

    bid_depth = live_board.get("bid_depth")
    ask_depth = live_board.get("ask_depth")
    delta = live_flow.get("delta")
    alert_ts = live_flow.get("event_ts") or live_board.get("event_ts")

    regime = latest_regime_name(experiment_payload)
    best_strategy = latest_best_strategy_name(experiment_payload)

    imbalance = None
    if bid_depth is not None and ask_depth is not None:
        try:
            bid_depth_f = float(bid_depth)
            ask_depth_f = float(ask_depth)
            denom = bid_depth_f + ask_depth_f
            if denom > 0:
                imbalance = (bid_depth_f - ask_depth_f) / denom
        except Exception:
            imbalance = None

    return {
        "spread": spread,
        "imbalance": imbalance,
        "delta": 0.0 if delta is None else delta,
        "alert_ts": alert_ts,
        "regime": regime,
        "best_strategy": best_strategy,
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