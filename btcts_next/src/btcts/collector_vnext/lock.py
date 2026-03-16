# path: ./btcts_next/src/btcts/collector_vnext/lock.py
# desc: Collector vNext daemon の単一起動を保証する lock file 管理。

from __future__ import annotations

import ctypes
import json
import os
import socket
import time
from pathlib import Path

from .config import CollectorConfig, load_config


def _resolve_cfg(cfg: CollectorConfig | None = None) -> CollectorConfig:
    return cfg or load_config()


def _state_dir(cfg: CollectorConfig | None = None) -> Path:
    cfg = _resolve_cfg(cfg)
    state_dir = cfg.roots()["state"]
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def daemon_lock_path(cfg: CollectorConfig | None = None) -> Path:
    return _state_dir(cfg) / "daemon.lock.json"


def _now_unix() -> float:
    return time.time()


def _lock_payload() -> dict:
    return {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "started_at_unix": _now_unix(),
        "started_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": "python -m btcts.collector_vnext.daemon",
    }


def read_lock_info(cfg: CollectorConfig | None = None) -> dict | None:
    path = daemon_lock_path(cfg)
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def is_pid_alive(pid: int | None) -> bool:
    if pid is None:
        return False

    try:
        pid = int(pid)
    except Exception:
        return False

    if pid <= 0:
        return False

    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        SYNCHRONIZE = 0x00100000
        access = PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE

        handle = ctypes.windll.kernel32.OpenProcess(access, False, pid)
        if not handle:
            return False

        try:
            WAIT_TIMEOUT = 0x00000102
            result = ctypes.windll.kernel32.WaitForSingleObject(handle, 0)
            return result == WAIT_TIMEOUT
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)

    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _write_lock_file(path: Path) -> dict:
    payload = _lock_payload()
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)

    return payload


def acquire_daemon_lock(cfg: CollectorConfig | None = None) -> tuple[bool, dict]:
    path = daemon_lock_path(cfg)

    while True:
        try:
            current = _write_lock_file(path)
            return True, current

        except FileExistsError:
            existing = read_lock_info(cfg)
            if not existing:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    return False, {
                        "pid": None,
                        "error": "lock_exists_but_unreadable",
                        "path": str(path),
                    }
                continue

            existing_pid = existing.get("pid")
            if is_pid_alive(existing_pid):
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
                "pid": None,
                "error": f"lock_write_failed: {exc}",
                "path": str(path),
            }


def release_daemon_lock(cfg: CollectorConfig | None = None) -> None:
    path = daemon_lock_path(cfg)
    existing = read_lock_info(cfg)
    if not existing:
        return

    if existing.get("pid") != os.getpid():
        return

    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass