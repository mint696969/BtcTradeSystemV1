# path: ./btcts_next/src/btcts/apps/operator_ui/collector_state_service.py
# desc: Load collector vNext status, health, rate, and origin state files for the operator UI.

from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Any

from btcts.core import paths as core_paths


def _state_dir() -> Path:
    r"""
    Collector vNext の state 正本を解決する。

    現在の運用では logs_dir の兄弟に state/collector_vnext を置く。
    例:
      D:\btc_ts_hot\logs -> D:\btc_ts_hot\state\collector_vnext
      E:\btc_ts\logs     -> E:\btc_ts\state\collector_vnext
    """
    return core_paths.logs_dir(ensure=False).parent / "state" / "collector_vnext"


def _safe_read(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _safe_read_first(paths: list[Path]) -> Dict[str, Any]:
    for path in paths:
        data = _safe_read(path)
        if data:
            return data
    return {}


def load_state() -> Dict[str, Any]:
    state_dir = _state_dir()

    status = _safe_read_first(
        [
            state_dir / "unified_status.json",
            state_dir / "exploration_status.json",
            state_dir / "status.json",
        ]
    )
    health = _safe_read_first(
        [
            state_dir / "unified_daemon_health.json",
            state_dir / "unified_health.json",
            state_dir / "exploration_daemon_health.json",
            state_dir / "exploration_health.json",
            state_dir / "daemon_health.json",
            state_dir / "health.json",
        ]
    )
    rate = _safe_read_first(
        [
            state_dir / "unified_rate_state.json",
            state_dir / "exploration_rate_state.json",
            state_dir / "rate_state.json",
        ]
    )
    checkpoint = _safe_read_first(
        [
            state_dir / "unified_checkpoint.json",
            state_dir / "exploration_checkpoint.json",
            state_dir / "checkpoint.json",
        ]
    )
    origin = _safe_read_first(
        [
            state_dir / "unified_origin_status.json",
            state_dir / "origin_status.json",
        ]
    )
    daemon_status = _safe_read_first(
        [
            state_dir / "unified_daemon_status.json",
            state_dir / "exploration_daemon_status.json",
        ]
    )
    supervisor_request = _safe_read(state_dir / "unified_supervisor_request.json")
    supervisor_status = _safe_read(state_dir / "unified_supervisor_status.json")
    daemon_stop_request = _safe_read(state_dir / "unified_daemon_stop_request.json")

    rate_items = (rate.get("items") or {}) if isinstance(rate, dict) else {}
    bitflyer_rate = rate_items.get("bitflyer") or {}
    rate_domains = (bitflyer_rate.get("domains") or {}) if isinstance(bitflyer_rate, dict) else {}
    domain_names = list(bitflyer_rate.get("domain_names") or []) if isinstance(bitflyer_rate, dict) else []
    shared_ip = (bitflyer_rate.get("shared_ip") or {}) if isinstance(bitflyer_rate, dict) else {}
    shared_ip_budget = (shared_ip.get("budget") or {}) if isinstance(shared_ip, dict) else {}

    return {
        "status": status,
        "health": health,
        "rate": rate,
        "rate_domains": rate_domains,
        "domain_names": domain_names,
        "shared_ip": shared_ip,
        "shared_ip_budget": shared_ip_budget,
        "origin": origin,
        "executions": _safe_read(state_dir / "unified_executions_status.json"),
        "checkpoint": checkpoint,
        "daemon_status": daemon_status,
        "supervisor_request": supervisor_request,
        "supervisor_status": supervisor_status,
        "daemon_stop_request": daemon_stop_request,
        "exploration_daemon_status": _safe_read(state_dir / "exploration_daemon_status.json"),
        "unified_scheduler_state": _safe_read(state_dir / "unified_scheduler_state.json"),
        "exploration_scheduler_state": _safe_read(state_dir / "exploration_scheduler_state.json"),
        "state_dir": {"path": str(state_dir)},
    }