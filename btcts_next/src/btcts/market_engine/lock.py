# path: ./btcts_next/src/btcts/market_engine/lock.py
# desc: Market Engine live runtime の単一起動を保証する lock file 管理。

from __future__ import annotations

import ctypes
import json
import os
import socket
import time
from pathlib import Path

from btcts.core.paths import runtime_root

from .config import MarketEngineConfig, load_market_engine_config


def _resolve_cfg(cfg: MarketEngineConfig | None = None) -> MarketEngineConfig:
    return cfg or load_market_engine_config()


def _state_dir(cfg: MarketEngineConfig | None = None) -> Path:
    _resolve_cfg(cfg)
    path = runtime_root(ensure=True) / "state" / "market_engine"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_name(text: str, *, default: str) -> str:
    value = str(text or "").strip().lower() or default
    return value.replace("/", "_").replace("\\", "_").replace(":", "_").replace(" ", "_")


def live_runtime_lock_path(
    cfg: MarketEngineConfig | None = None,
    *,
    runtime_name: str = "live_runtime",
) -> Path:
    resolved = _resolve_cfg(cfg)
    exchange = _safe_name(resolved.exchange, default="unknown_exchange")
    symbol = _safe_name(resolved.symbol_raw, default="unknown_symbol")
    runtime = _safe_name(runtime_name, default="live_runtime")
    return _state_dir(resolved) / f"{exchange}_{symbol}_{runtime}.lock.json"


def _now_unix() -> float:
    return time.time()


def _lock_payload(
    cfg: MarketEngineConfig,
    *,
    runtime_name: str = "live_runtime",
) -> dict:
    return {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "started_at_unix": _now_unix(),
        "started_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_name": str(runtime_name or "live_runtime"),
        "exchange": str(cfg.exchange),
        "symbol_raw": str(cfg.symbol_raw),
        "market_uid": str(cfg.market_uid),
        "command": ".\\tools\\run_market_engine_live_runtime.py",
        "python_executable": os.sys.executable,
    }


def read_live_runtime_lock(
    cfg: MarketEngineConfig | None = None,
    *,
    runtime_name: str = "live_runtime",
) -> dict | None:
    path = live_runtime_lock_path(cfg, runtime_name=runtime_name)
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


def _write_lock_file(
    path: Path,
    *,
    cfg: MarketEngineConfig,
    runtime_name: str = "live_runtime",
) -> dict:
    payload = _lock_payload(cfg, runtime_name=runtime_name)
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)

    return payload


def acquire_live_runtime_lock(
    cfg: MarketEngineConfig | None = None,
    *,
    runtime_name: str = "live_runtime",
) -> tuple[bool, dict]:
    resolved = _resolve_cfg(cfg)
    path = live_runtime_lock_path(resolved, runtime_name=runtime_name)

    while True:
        try:
            current = _write_lock_file(
                path,
                cfg=resolved,
                runtime_name=runtime_name,
            )
            return True, current

        except FileExistsError:
            existing = read_live_runtime_lock(resolved, runtime_name=runtime_name)
            if not existing:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    return False, {
                        "pid": None,
                        "runtime_name": runtime_name,
                        "error": "lock_exists_but_unreadable",
                        "path": str(path),
                    }
                continue

            existing_pid = existing.get("pid")
            if is_pid_alive(existing_pid):
                return False, {
                    **existing,
                    "path": str(path),
                }

            try:
                path.unlink(missing_ok=True)
            except Exception:
                return False, {
                    **existing,
                    "runtime_name": runtime_name,
                    "error": "stale_lock_unlink_failed",
                    "path": str(path),
                }
            continue

        except Exception as exc:
            return False, {
                "pid": None,
                "runtime_name": runtime_name,
                "error": f"lock_write_failed: {exc}",
                "path": str(path),
            }


def release_live_runtime_lock(
    cfg: MarketEngineConfig | None = None,
    *,
    runtime_name: str = "live_runtime",
) -> None:
    resolved = _resolve_cfg(cfg)
    path = live_runtime_lock_path(resolved, runtime_name=runtime_name)
    existing = read_live_runtime_lock(resolved, runtime_name=runtime_name)
    if not existing:
        return

    if existing.get("pid") != os.getpid():
        return

    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass