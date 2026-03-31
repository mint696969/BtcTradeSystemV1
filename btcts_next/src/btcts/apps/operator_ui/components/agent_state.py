# path: ./btcts_next/src/btcts/apps/operator_ui/components/agent_state.py
# desc: Agent Panels の state 組み立てと監査ログ読取を分離したデータ層。

from __future__ import annotations

import json
import os
from pathlib import Path


from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
    recent_live_tradeflow_metrics,
)
from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_best_strategy_name,
    latest_board_row,
    latest_regime_name,
    latest_trade_row,
    load_latest_experiment_payload,
    load_latest_replay_payload,
    tradeflow_metrics,
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


def analyze_agent_state() -> dict | None:
    experiment_payload = load_latest_experiment_payload()
    audit_rows = read_recent_audit(lines=40)

    live_board = latest_live_board_metrics()
    live_flow = recent_live_tradeflow_metrics(lines=80)

    source_label = "replay_board+tradeflow + research_experiment + audit_latency"

    board = None
    flow = None

    live_spread = live_board.get("spread")
    live_delta = live_flow.get("delta")

    if live_spread is not None and live_delta is not None:
        bid_depth = live_board.get("bid_depth")
        ask_depth = live_board.get("ask_depth")

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

        board = {
            "spread": float(live_spread),
            "imbalance": imbalance,
            "pressure_bias": "live_orderbook",
            "wall_ratio": None,
        }
        flow = {
            "trade_delta": float(live_delta),
        }
        source_label = "live_canonical + research_experiment + audit_latency"

    if not board or not flow:
        replay_payload = load_latest_replay_payload()
        board = board_signal_metrics(latest_board_row(replay_payload))
        flow = tradeflow_metrics(latest_trade_row(replay_payload))

    if not board or not flow:
        return None

    return {
        "audit_rows": audit_rows,
        "source_label": source_label,
        "regime": latest_regime_name(experiment_payload),
        "best_strategy": latest_best_strategy_name(experiment_payload),
        "spread": board.get("spread"),
        "imbalance": board.get("imbalance"),
        "pressure_bias": board.get("pressure_bias"),
        "wall_ratio": board.get("wall_ratio"),
        "delta": flow.get("trade_delta"),
    }