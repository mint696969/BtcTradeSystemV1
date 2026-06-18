# path: ./btcts_next/src/btcts/collector_vnext/lock.py
# desc: Collector vNext daemon の単一起動を保証する lock file 管理。

from __future__ import annotations

import ctypes
from ctypes import wintypes
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


def daemon_lock_path(
    cfg: CollectorConfig | None = None,
    *,
    runtime_family: str = "smoke",
) -> Path:
    family = str(runtime_family or "smoke").strip().lower() or "smoke"
    return _state_dir(cfg) / f"{family}_daemon.lock.json"


def _now_unix() -> float:
    return time.time()


def _lock_payload(*, runtime_family: str = "smoke") -> dict:
    family = str(runtime_family or "smoke").strip().lower() or "smoke"
    command_map = {
        "smoke": "python -m btcts.collector_vnext.daemon",
        "exploration": "python -m btcts.collector_vnext.exploration_daemon",
        "unified": "python -m btcts.collector_vnext.unified_daemon",
    }

    return {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "started_at_unix": _now_unix(),
        "started_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_family": family,
        "command": command_map.get(family, f"python -m btcts.collector_vnext.{family}_daemon"),
    }


def read_lock_info(
    cfg: CollectorConfig | None = None,
    *,
    runtime_family: str = "smoke",
) -> dict | None:
    path = daemon_lock_path(cfg, runtime_family=runtime_family)
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


def _write_lock_file(path: Path, *, runtime_family: str = "smoke") -> dict:
    payload = _lock_payload(runtime_family=runtime_family)
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)

    return payload


def acquire_daemon_lock(
    cfg: CollectorConfig | None = None,
    *,
    runtime_family: str = "smoke",
) -> tuple[bool, dict]:
    path = daemon_lock_path(cfg, runtime_family=runtime_family)

    while True:
        try:
            current = _write_lock_file(path, runtime_family=runtime_family)
            return True, current

        except FileExistsError:
            existing = read_lock_info(cfg, runtime_family=runtime_family)
            if not existing:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    return False, {
                        "pid": None,
                        "runtime_family": runtime_family,
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
                    "runtime_family": runtime_family,
                    "error": "stale_lock_unlink_failed",
                    "path": str(path),
                }
            continue

        except Exception as exc:
            return False, {
                "pid": None,
                "runtime_family": runtime_family,
                "error": f"lock_write_failed: {exc}",
                "path": str(path),
            }


def release_daemon_lock(
    cfg: CollectorConfig | None = None,
    *,
    runtime_family: str = "smoke",
) -> None:
    path = daemon_lock_path(cfg, runtime_family=runtime_family)
    existing = read_lock_info(cfg, runtime_family=runtime_family)
    if not existing:
        return

    if existing.get("pid") != os.getpid():
        return

    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass

def _normalize_windows_mutex_name(name: str) -> str:
    r"""Normalize Windows mutex namespace separators.

    Windows named mutexes use a single namespace separator, for example
    Local\\BTCTS_NAME in source form, which becomes Local\BTCTS_NAME at
    runtime.  Accidentally passing a raw string with two concrete separators,
    such as r"Local\\BTCTS_NAME", fails with ERROR_INVALID_NAME (123).
    Normalize that class of caller mistake before CreateMutexW.
    """
    mutex_name = str(name or "").strip().replace("/", "\\")
    if os.name != "nt":
        return mutex_name

    for namespace in ("Local", "Global"):
        single_prefix = namespace + "\\"
        doubled_prefix = namespace + "\\\\"
        while mutex_name.startswith(doubled_prefix):
            mutex_name = single_prefix + mutex_name[len(doubled_prefix):]
    return mutex_name


def _kernel32_for_mutex():
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.GetLastError.argtypes = ()
    kernel32.GetLastError.restype = wintypes.DWORD
    return kernel32


def acquire_process_singleton_mutex(name: str) -> tuple[bool, dict]:
    """Acquire a Windows named mutex for process-family singleton enforcement.

    File locks protect the configured state root.  This mutex protects the
    current Windows logon session even when two Python runtimes or environment
    roots accidentally launch the same collector component.
    """
    raw_mutex_name = str(name or "").strip()
    mutex_name = _normalize_windows_mutex_name(raw_mutex_name)
    if not mutex_name:
        return False, {"error": "mutex_name_empty"}

    if os.name != "nt":
        return True, {
            "mutex_name": mutex_name,
            "raw_mutex_name": raw_mutex_name,
            "handle": None,
            "platform": os.name,
        }

    kernel32 = _kernel32_for_mutex()
    handle = kernel32.CreateMutexW(None, False, mutex_name)
    if not handle:
        return False, {
            "mutex_name": mutex_name,
            "raw_mutex_name": raw_mutex_name,
            "error": "create_mutex_failed",
            "last_error": int(kernel32.GetLastError()),
        }

    ERROR_ALREADY_EXISTS = 183
    last_error = int(kernel32.GetLastError())
    if last_error == ERROR_ALREADY_EXISTS:
        try:
            kernel32.CloseHandle(handle)
        except Exception:
            pass
        return False, {
            "mutex_name": mutex_name,
            "raw_mutex_name": raw_mutex_name,
            "already_running": True,
            "error": "singleton_mutex_already_exists",
        }

    return True, {
        "mutex_name": mutex_name,
        "raw_mutex_name": raw_mutex_name,
        "handle": int(handle),
        "platform": os.name,
    }


def release_process_singleton_mutex(info: dict | None) -> None:
    """Release a mutex acquired by acquire_process_singleton_mutex."""
    if os.name != "nt" or not isinstance(info, dict):
        return

    handle = info.get("handle")
    if not handle:
        return

    try:
        _kernel32_for_mutex().CloseHandle(int(handle))
    except Exception:
        pass
