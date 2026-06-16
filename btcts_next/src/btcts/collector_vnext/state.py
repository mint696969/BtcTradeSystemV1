# path: ./btcts_next/src/btcts/collector_vnext/state.py
# desc: State and health file helpers for Collector vNext runtime.

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

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
    stream_session_id: Optional[str],
    last_good_event_id: Optional[str],
    first_uncertain_event_id: Optional[str],
    provider: Optional[str],
    transport: Optional[str],
    ws_state: Optional[str] = None,
    snapshot_to_live_ms: Optional[float] = None,
    resync_occurred: Optional[bool] = None,
    pre_snapshot_delta_drop_count: Optional[int] = None,
    error_class: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Path:
    payload = {
        "ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exchange": exchange,
        "channel": channel,
        "last_event_name": last_event_name,
        "reason": reason,
        "stream_session_id": stream_session_id,
        "last_good_event_id": last_good_event_id,
        "first_uncertain_event_id": first_uncertain_event_id,
        "provider": provider,
        "transport": transport,
        "ws_state": ws_state,
        "snapshot_to_live_ms": snapshot_to_live_ms,
        "resync_occurred": resync_occurred,
        "pre_snapshot_delta_drop_count": pre_snapshot_delta_drop_count,
        "error_class": error_class,
        "error_message": error_message,
    }
    return write_json_state(cfg, "origin_status.json", payload)