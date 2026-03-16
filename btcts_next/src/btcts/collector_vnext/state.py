# path: ./btcts_next/src/btcts/collector_vnext/state.py
# desc: State and health file helpers for Collector vNext runtime.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .config import CollectorConfig
from .paths import ensure_dir


def _state_dir(cfg: CollectorConfig) -> Path:
    out = cfg.roots()["state"]
    ensure_dir(out)
    return out


def write_json_state(cfg: CollectorConfig, filename: str, payload: Dict[str, Any]) -> Path:
    out = _state_dir(cfg) / filename
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def write_status(cfg: CollectorConfig, payload: Dict[str, Any]) -> Path:
    return write_json_state(cfg, "status.json", payload)


def write_health(cfg: CollectorConfig, payload: Dict[str, Any]) -> Path:
    return write_json_state(cfg, "health.json", payload)


def write_daemon_health(cfg: CollectorConfig, payload: Dict[str, Any]) -> Path:
    return write_json_state(cfg, "daemon_health.json", payload)


def write_checkpoint(cfg: CollectorConfig, payload: Dict[str, Any]) -> Path:
    return write_json_state(cfg, "checkpoint.json", payload)


def write_origin_status(
    cfg: CollectorConfig,
    *,
    exchange: str,
    channel: str,
    last_event_name: str,
    reason: str,
    stream_session_id: str,
    last_good_event_id: str | None = None,
    first_uncertain_event_id: str | None = None,
    provider: str | None = None,
    transport: str | None = None,
    error_class: str | None = None,
    error_message: str | None = None,
) -> Path:
    payload = {
        "exchange": exchange,
        "channel": channel,
        "last_event_name": last_event_name,
        "reason": reason,
        "stream_session_id": stream_session_id,
        "last_good_event_id": last_good_event_id,
        "first_uncertain_event_id": first_uncertain_event_id,
        "provider": provider,
        "transport": transport,
        "error_class": error_class,
        "error_message": error_message,
    }
    return write_json_state(cfg, "origin_status.json", payload)