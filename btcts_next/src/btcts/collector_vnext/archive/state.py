# path: ./btcts_next/src/btcts/collector_vnext/archive/state.py
# desc: Archive worker state helpers.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from btcts.collector_vnext.events import now_iso_utc

from .config import ArchiveConfig


def _state_dir(cfg: ArchiveConfig) -> Path:
    path = cfg.hot_root / "state" / "collector_vnext"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_archive_copy_state(cfg: ArchiveConfig, payload: dict[str, Any]) -> Path:
    out = _state_dir(cfg) / "archive_copy_state.json"
    body = {"ts": now_iso_utc(), **payload}
    out.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def write_archive_gc_state(cfg: ArchiveConfig, payload: dict[str, Any]) -> Path:
    out = _state_dir(cfg) / "archive_gc_state.json"
    body = {"ts": now_iso_utc(), **payload}
    out.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def archive_stop_request_path(cfg: ArchiveConfig) -> Path:
    return _state_dir(cfg) / "archive_stop_request.json"


def read_archive_stop_request(cfg: ArchiveConfig) -> dict[str, Any]:
    path = archive_stop_request_path(cfg)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def clear_archive_stop_request(cfg: ArchiveConfig) -> None:
    try:
        archive_stop_request_path(cfg).unlink(missing_ok=True)
    except Exception:
        pass