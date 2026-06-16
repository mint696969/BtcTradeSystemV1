# path: ./btcts_next/src/btcts/apps/operator_ui/components/research_bridge.py
# desc: Operator UI components 用の vNext / Replay / Research artifact 読み込み共通ブリッジ

from __future__ import annotations

from pathlib import Path
from typing import Optional

from btcts.core import paths as core_paths

from btcts.replay import (
    list_experiment_sessions,
    list_replay_sessions,
    load_experiment_session,
    load_replay_session,
)

def _replay_root() -> Path:
    return core_paths.replay_dir(ensure=False)


def _research_root() -> Path:
    return core_paths.research_dir(ensure=False)


def load_latest_replay_payload() -> Optional[dict]:
    sessions = list_replay_sessions(_replay_root())
    if not sessions:
        return None

    latest = sessions[0]
    session_dir = Path(str(latest["session_dir"]))
    return load_replay_session(session_dir, tail_lines=200)


def load_latest_experiment_payload() -> Optional[dict]:
    sessions = list_experiment_sessions(_research_root())
    if not sessions:
        return None

    latest = sessions[0]
    session_dir = Path(str(latest["session_dir"]))
    return load_experiment_session(session_dir)


def replay_tail_rows(replay_payload: Optional[dict], limit: int = 20) -> list[dict]:
    if not replay_payload:
        return []

    rows = replay_payload.get("results_tail", [])
    if not isinstance(rows, list):
        return []

    out: list[dict] = []
    for row in rows[-limit:]:
        if isinstance(row, dict):
            out.append(row)

    return out


def latest_board_row(replay_payload: Optional[dict]) -> Optional[dict]:
    if not replay_payload:
        return None

    rows = replay_payload.get("results_tail", [])
    for row in reversed(rows):
        if row.get("kind") == "board" and isinstance(row.get("result"), dict):
            return row

    return None


def latest_trade_row(replay_payload: Optional[dict]) -> Optional[dict]:
    if not replay_payload:
        return None

    rows = replay_payload.get("results_tail", [])
    for row in reversed(rows):
        if row.get("kind") == "trade":
            return row

    return None


def board_signal_metrics(board_row: Optional[dict]) -> Optional[dict]:
    if not board_row:
        return None

    result = board_row.get("result")
    if not isinstance(result, dict):
        return None

    signal = result.get("signal") or {}
    summary = signal.get("summary") or {}
    pressure = signal.get("pressure") or {}
    wall = signal.get("wall") or {}

    best_bid = result.get("best_bid")
    best_ask = result.get("best_ask")
    spread = signal.get("spread", summary.get("spread"))

    return {
        "event_ts": board_row.get("event_ts"),
        "record_type": board_row.get("record_type"),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": spread,
        "mid": signal.get("mid", summary.get("mid")),
        "bid_depth": summary.get("bid_depth"),
        "ask_depth": summary.get("ask_depth"),
        "imbalance": summary.get("imbalance"),
        "pressure_bias": pressure.get("bias"),
        "wall_detected": wall.get("wall_detected"),
        "wall_side": wall.get("strongest_side"),
        "wall_ratio": wall.get("strongest_ratio"),
        "bid_wall_size": wall.get("bid_wall_size"),
        "ask_wall_size": wall.get("ask_wall_size"),
    }


def tradeflow_metrics(trade_row: Optional[dict]) -> Optional[dict]:
    if not trade_row:
        return None

    tradeflow = trade_row.get("tradeflow")
    if not isinstance(tradeflow, dict):
        return None

    micro = trade_row.get("microstructure", [])
    micro_names = [
        str(event.get("event_name"))
        for event in micro
        if isinstance(event, dict) and event.get("event_name")
    ]

    return {
        "event_ts": trade_row.get("event_ts"),
        "trade_count": tradeflow.get("trade_count"),
        "buy_volume": tradeflow.get("buy_volume"),
        "sell_volume": tradeflow.get("sell_volume"),
        "trade_delta": tradeflow.get("trade_delta"),
        "avg_price": tradeflow.get("avg_price"),
        "micro_event_names": micro_names,
    }


def latest_best_strategy_name(experiment_payload: Optional[dict]) -> str:
    if not experiment_payload:
        return "unknown"

    best = experiment_payload.get("best_strategy") or {}
    return str(best.get("strategy") or "unknown")


def latest_regime_name(experiment_payload: Optional[dict]) -> str:
    if not experiment_payload:
        return "unknown"

    regime_report = experiment_payload.get("regime_report") or {}
    return str(regime_report.get("regime") or "unknown")


def replay_review_hint_summary_payload(replay_payload: Optional[dict]) -> dict:
    """Return read-only Position/Execution review hint summaries from a replay payload."""
    if not replay_payload:
        return {
            "context_type": "prediction_review_hint_summary_context",
            "source_kind": "replay_report",
            "available": False,
            "position_summary": None,
            "execution_summary": None,
            "read_only_contract": True,
            "not_runtime_wiring": True,
            "not_ui_rendering": True,
        }

    report = replay_payload.get("report") or {}
    if not isinstance(report, dict):
        report = {}

    position_summary = report.get("prediction_position_review_hint_summary")
    execution_summary = report.get("prediction_execution_review_hint_summary")
    if not isinstance(position_summary, dict):
        position_summary = None
    if not isinstance(execution_summary, dict):
        execution_summary = None

    return {
        "context_type": "prediction_review_hint_summary_context",
        "source_kind": "replay_report",
        "available": position_summary is not None or execution_summary is not None,
        "position_summary": position_summary,
        "execution_summary": execution_summary,
        "read_only_contract": True,
        "not_runtime_wiring": True,
        "not_ui_rendering": True,
    }


def load_latest_replay_review_hint_summary_payload() -> dict:
    return replay_review_hint_summary_payload(load_latest_replay_payload())
