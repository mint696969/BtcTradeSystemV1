# path: ./btcts_next/src/btcts/collector_vnext/unified_state.py
# desc: Unified Collector 専用の state/status/health 出力 helper。

from __future__ import annotations

from typing import Any, Dict

from .config import CollectorConfig
from .state import write_json_state


def write_unified_status(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_status.json", payload)


def write_unified_health(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_health.json", payload)


def write_unified_daemon_status(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_daemon_status.json", payload)


def write_unified_daemon_health(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_daemon_health.json", payload)


def write_unified_rate_state(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_rate_state.json", payload)


def write_unified_scheduler_state(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_scheduler_state.json", payload)


def write_unified_origin_status(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_origin_status.json", payload)


def write_unified_executions_status(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_executions_status.json", payload)


def write_unified_checkpoint(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_checkpoint.json", payload)


def write_unified_market_state_status(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_market_state_status.json", payload)


def read_unified_state(cfg: CollectorConfig, filename: str) -> Dict[str, Any]:
    path = cfg.roots()["state"] / filename
    if not path.exists():
        return {}

    try:
        return path.read_text(encoding="utf-8") and __import__("json").loads(
            path.read_text(encoding="utf-8")
        )
    except Exception:
        return {}


def write_unified_supervisor_request(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_supervisor_request.json", payload)


def read_unified_supervisor_request(cfg: CollectorConfig) -> Dict[str, Any]:
    return read_unified_state(cfg, "unified_supervisor_request.json")


def write_unified_supervisor_status(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_supervisor_status.json", payload)


def read_unified_supervisor_status(cfg: CollectorConfig) -> Dict[str, Any]:
    return read_unified_state(cfg, "unified_supervisor_status.json")


def write_unified_daemon_stop_request(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "unified_daemon_stop_request.json", payload)


def read_unified_daemon_stop_request(cfg: CollectorConfig) -> Dict[str, Any]:
    return read_unified_state(cfg, "unified_daemon_stop_request.json")