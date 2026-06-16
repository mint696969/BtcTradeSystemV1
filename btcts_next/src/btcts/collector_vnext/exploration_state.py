# path: ./btcts_next/src/btcts/collector_vnext/exploration_state.py
# desc: Exploration Runtime 専用の state/status/health 出力 helper。

from __future__ import annotations

from typing import Any, Dict

from .config import CollectorConfig
from .state import write_json_state


def write_exploration_status(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "exploration_status.json", payload)


def write_exploration_health(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "exploration_health.json", payload)


def write_exploration_daemon_status(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "exploration_daemon_status.json", payload)


def write_exploration_daemon_health(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "exploration_daemon_health.json", payload)


def write_exploration_rate_state(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "exploration_rate_state.json", payload)


def write_exploration_scheduler_state(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "exploration_scheduler_state.json", payload)


def write_exploration_checkpoint(cfg: CollectorConfig, payload: Dict[str, Any]):
    return write_json_state(cfg, "exploration_checkpoint.json", payload)