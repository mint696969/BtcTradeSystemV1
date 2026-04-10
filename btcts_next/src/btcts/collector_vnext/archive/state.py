# path: ./btcts_next/src/btcts/collector_vnext/archive/state.py
# desc: Archive worker state helpers.

from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Any

from btcts.collector_vnext.events import now_iso_utc
from btcts.collector_vnext.lock import is_pid_alive

from .config import ArchiveConfig


def _state_dir(cfg: ArchiveConfig) -> Path:
    path = cfg.hot_root / "state" / "collector_vnext"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_archive_copy_state(cfg: ArchiveConfig, payload: dict[str, Any]) -> Path:
    out = _state_dir(cfg) / "archive_copy_state.json"
    body = {"ts": now_iso_utc(), **payload}
    return _write_json(out, body)


def write_archive_gc_state(cfg: ArchiveConfig, payload: dict[str, Any]) -> Path:
    out = _state_dir(cfg) / "archive_gc_state.json"
    body = {"ts": now_iso_utc(), **payload}
    return _write_json(out, body)


def archive_stop_request_path(cfg: ArchiveConfig) -> Path:
    return _state_dir(cfg) / "archive_stop_request.json"


def write_archive_stop_request(cfg: ArchiveConfig, payload: dict[str, Any]) -> Path:
    out = archive_stop_request_path(cfg)
    body = {"ts": now_iso_utc(), **payload}
    return _write_json(out, body)


def read_archive_stop_request(cfg: ArchiveConfig) -> dict[str, Any]:
    return _read_json(archive_stop_request_path(cfg))


def clear_archive_stop_request(cfg: ArchiveConfig) -> None:
    try:
        archive_stop_request_path(cfg).unlink(missing_ok=True)
    except Exception:
        pass


def read_archive_copy_state(cfg: ArchiveConfig) -> dict[str, Any]:
    return _read_json(_state_dir(cfg) / "archive_copy_state.json")


def read_archive_gc_state(cfg: ArchiveConfig) -> dict[str, Any]:
    return _read_json(_state_dir(cfg) / "archive_gc_state.json")


def archive_worker_lock_path(cfg: ArchiveConfig) -> Path:
    return _state_dir(cfg) / "archive_worker.lock.json"


def read_archive_worker_lock(cfg: ArchiveConfig) -> dict[str, Any]:
    return _read_json(archive_worker_lock_path(cfg))


def acquire_archive_worker_lock(cfg: ArchiveConfig) -> tuple[bool, dict[str, Any]]:
    path = archive_worker_lock_path(cfg)
    payload = {
        "pid": os.getpid(),
        "host_name": socket.gethostname(),
        "started_at": now_iso_utc(),
        "command": "python -m btcts.collector_vnext.archive.worker",
    }

    while True:
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                os.write(fd, json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"))
            finally:
                os.close(fd)
            return True, payload
        except FileExistsError:
            existing = read_archive_worker_lock(cfg)
            if not existing:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    return False, {
                        "error": "lock_exists_but_unreadable",
                        "path": str(path),
                    }
                continue

            if is_pid_alive(existing.get("pid")):
                return False, existing

            try:
                path.unlink(missing_ok=True)
            except Exception:
                return False, {
                    **existing,
                    "error": "stale_lock_unlink_failed",
                    "path": str(path),
                }
            continue
        except Exception as exc:
            return False, {
                "error": f"lock_write_failed: {exc}",
                "path": str(path),
            }


def release_archive_worker_lock(cfg: ArchiveConfig) -> None:
    existing = read_archive_worker_lock(cfg)
    if not existing:
        return
    if existing.get("pid") != os.getpid():
        return

    try:
        archive_worker_lock_path(cfg).unlink(missing_ok=True)
    except Exception:
        pass