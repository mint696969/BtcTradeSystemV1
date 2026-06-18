# path: ./btcts_next/src/btcts/collector_vnext/unified_watchdog.py
# desc: Unified Collector 用の watchdog。manual restart / safe stop request を受けて orchestration する。

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from ._env_utils import env_int
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .archive.config import load_archive_config
from .archive.state import (
    read_archive_copy_state,
    read_archive_gc_state,
    read_archive_worker_lock,
    write_archive_stop_request,
)
from .config import load_config
from .events import now_iso_utc
from .lock import (
    acquire_process_singleton_mutex,
    is_pid_alive,
    release_process_singleton_mutex,
)
from .unified_state import (
    read_unified_supervisor_request,
    read_unified_supervisor_status,
    write_unified_daemon_stop_request,
    write_unified_supervisor_status,
)


def _parse_ts(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None

    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        return datetime.fromisoformat(text)
    except Exception:
        return None


def _request_age_sec(request: dict[str, Any]) -> float | None:
    requested_at = _parse_ts(str(request.get("requested_at") or ""))
    if requested_at is None:
        return None

    now = datetime.now(timezone.utc)
    try:
        return max(0.0, (now - requested_at.astimezone(timezone.utc)).total_seconds())
    except Exception:
        return None


def _uptime_sec(started_at: str | None) -> int | None:
    started_dt = _parse_ts(started_at)
    if started_dt is None:
        return None

    now = datetime.now(timezone.utc)
    try:
        return max(0, int((now - started_dt.astimezone(timezone.utc)).total_seconds()))
    except Exception:
        return None


def _supervisor_lock_path(cfg) -> Path:
    return cfg.roots()["state"] / "unified_supervisor.lock.json"


def _supervisor_request_path(cfg) -> Path:
    return cfg.roots()["state"] / "unified_supervisor_request.json"


def _daemon_stop_request_path(cfg) -> Path:
    return cfg.roots()["state"] / "unified_daemon_stop_request.json"


def _audit_path(cfg) -> Path:
    return cfg.roots()["logs"] / "unified_supervisor_audit.jsonl"


def _append_audit(cfg, event: str, *, level: str = "INFO", extra: dict[str, Any] | None = None) -> None:
    payload = {
        "ts": now_iso_utc(),
        "level": level,
        "event": event,
    }
    if extra:
        payload.update(extra)

    path = _audit_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _write_status(
    cfg,
    *,
    mode: str,
    last_action: str | None = None,
    last_requested_at: str | None = None,
    last_completed_at: str | None = None,
    last_error: str | None = None,
    daemon_pid: int | None = None,
    request_ack_ts: str | None = None,
    acked_request_id: str | None = None,
    started_at: str | None = None,
    last_seen_ts: str | None = None,
    uptime_sec: int | None = None,
) -> None:
    write_unified_supervisor_status(
        cfg,
        {
            "ts": now_iso_utc(),
            "mode": mode,
            "last_action": last_action,
            "last_requested_at": last_requested_at,
            "last_completed_at": last_completed_at,
            "last_error": last_error,
            "daemon_pid": daemon_pid,
            "request_ack_ts": request_ack_ts,
            "acked_request_id": acked_request_id,
            "started_at": started_at,
            "last_seen_ts": last_seen_ts,
            "uptime_sec": uptime_sec,
            "runtime_family": "unified",
            "supervisor_pid": os.getpid(),
            "host_name": socket.gethostname(),
        },
    )


def _read_lock(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _acquire_supervisor_lock(cfg) -> tuple[bool, dict[str, Any]]:
    path = _supervisor_lock_path(cfg)
    payload = {
        "pid": os.getpid(),
        "started_at": now_iso_utc(),
        "runtime_family": "unified",
        "command": "python -m btcts.collector_vnext.unified_watchdog",
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
            existing = _read_lock(path)
            if not existing:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    return False, {"error": "lock_exists_but_unreadable", "path": str(path)}
                continue

            if is_pid_alive(existing.get("pid")):
                return False, existing

            try:
                path.unlink(missing_ok=True)
            except Exception:
                return False, {"error": "stale_lock_unlink_failed", "path": str(path), **existing}
            continue
        except Exception as exc:
            return False, {"error": f"lock_write_failed: {exc}", "path": str(path)}


def _release_supervisor_lock(cfg) -> None:
    path = _supervisor_lock_path(cfg)
    existing = _read_lock(path)
    if not existing:
        return
    if existing.get("pid") != os.getpid():
        return
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass


def _clear_request_file(cfg) -> None:
    try:
        _supervisor_request_path(cfg).unlink(missing_ok=True)
    except Exception:
        pass


def _clear_daemon_stop_request(cfg) -> None:
    try:
        _daemon_stop_request_path(cfg).unlink(missing_ok=True)
    except Exception:
        pass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _repo_runtime_python() -> str:
    override = str(os.getenv("BTCTS_RUNTIME_PYTHON", "") or "").strip()
    if override:
        candidate = Path(override)
        if candidate.exists():
            return str(candidate)

    repo_root = _repo_root()

    if os.name == "nt":
        candidates = [
            repo_root / ".venv" / "Scripts" / "pythonw.exe",
            repo_root / ".venv" / "Scripts" / "python.exe",
        ]
    else:
        candidates = [
            repo_root / ".venv" / "bin" / "python",
        ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    exe = Path(sys.executable)
    if os.name == "nt" and exe.name.lower() == "python.exe":
        pythonw = exe.with_name("pythonw.exe")
        if pythonw.exists():
            return str(pythonw)
    return str(exe)


def _windows_startupinfo():
    if os.name != "nt":
        return None

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 0)
    startupinfo.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
    return startupinfo


def _windows_creationflags() -> int:
    if os.name != "nt":
        return 0

    return (
        getattr(subprocess, "CREATE_NO_WINDOW", 0)
        | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    )


def _heartbeat_running_status(
    cfg,
    *,
    started_at: str,
    daemon_pid: int | None,
    default_last_action: str = "start",
) -> None:
    current = read_unified_supervisor_status(cfg) or {}

    _write_status(
        cfg,
        mode="RUNNING",
        last_action=str(current.get("last_action") or default_last_action),
        last_requested_at=current.get("last_requested_at"),
        last_completed_at=current.get("last_completed_at"),
        last_error=current.get("last_error"),
        daemon_pid=daemon_pid,
        request_ack_ts=current.get("request_ack_ts"),
        acked_request_id=current.get("acked_request_id"),
        started_at=started_at,
        last_seen_ts=now_iso_utc(),
        uptime_sec=_uptime_sec(started_at),
    )


def _start_unified_daemon() -> subprocess.Popen:
    return subprocess.Popen(
        [_repo_runtime_python(), "-m", "btcts.collector_vnext.unified_daemon"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=_windows_creationflags(),
        startupinfo=_windows_startupinfo(),
        close_fds=True,
    )


def _request_daemon_stop(
    cfg,
    request: dict[str, Any],
    *,
    reason_default: str,
    restart_requested: bool,
) -> None:
    write_unified_daemon_stop_request(
        cfg,
        {
            "action": "stop",
            "requested_at": now_iso_utc(),
            "requested_by": "unified_watchdog",
            "reason": request.get("reason") or reason_default,
            "restart_requested": restart_requested,
            "supervisor_request": request,
        },
    )


def _request_archive_stop(archive_cfg, request: dict[str, Any]) -> None:
    write_archive_stop_request(
        archive_cfg,
        {
            "action": "stop",
            "requested_at": now_iso_utc(),
            "requested_by": "unified_watchdog",
            "reason": request.get("reason") or "maintenance_safe_stop",
            "supervisor_request": request,
        },
    )


def _graceful_stop(proc: subprocess.Popen, timeout_sec: int) -> bool:
    deadline = time.time() + max(timeout_sec, 1)
    while time.time() < deadline:
        if proc.poll() is not None:
            return True
        time.sleep(0.5)
    return proc.poll() is not None


def _active_supervisor_request(cfg) -> dict[str, Any]:
    payload = read_unified_supervisor_request(cfg)
    if not isinstance(payload, dict):
        return {}

    action = str(payload.get("action") or "").strip().lower()
    if action not in {"restart", "stop_stack"}:
        return {}
    return payload


def _archive_worker_alive(archive_cfg) -> bool:
    lock_info = read_archive_worker_lock(archive_cfg)
    if not isinstance(lock_info, dict) or not lock_info:
        return False
    return is_pid_alive(lock_info.get("pid"))


def _archive_state_recent(payload: dict[str, Any], max_age_sec: int = 30) -> bool:
    if not isinstance(payload, dict) or not payload:
        return False

    ts = _parse_ts(str(payload.get("ts") or ""))
    if ts is None:
        ts = _parse_ts(str(payload.get("last_scan_ts") or ""))
    if ts is None:
        ts = _parse_ts(str(payload.get("started_at") or ""))
    if ts is None:
        return False

    now = datetime.now(timezone.utc)
    try:
        age = max(0.0, (now - ts.astimezone(timezone.utc)).total_seconds())
    except Exception:
        return False
    return age <= max_age_sec


def _archive_stopped(archive_cfg) -> tuple[bool, dict[str, Any], dict[str, Any]]:
    copy_state = read_archive_copy_state(archive_cfg)
    gc_state = read_archive_gc_state(archive_cfg)

    copy_mode = str(copy_state.get("mode") or "").strip().upper()
    gc_mode = str(gc_state.get("mode") or "").strip().upper()

    if copy_mode == "STOPPED" and gc_mode == "STOPPED":
        return True, copy_state, gc_state

    if not _archive_worker_alive(archive_cfg):
        copy_recent = _archive_state_recent(copy_state, max_age_sec=30)
        gc_recent = _archive_state_recent(gc_state, max_age_sec=30)

        graceful_copy = copy_mode in {"STOPPING", "STOPPED"}
        graceful_gc = gc_mode in {"STOPPING", "STOPPED", "IDLE"}

        if copy_recent and gc_recent and graceful_copy and graceful_gc:
            return True, copy_state, gc_state

    return False, copy_state, gc_state


def run_forever() -> int:
    singleton_locked, singleton_info = acquire_process_singleton_mutex(
        r"Local\BTCTS_COLLECTOR_VNEXT_UNIFIED_WATCHDOG"
    )
    if not singleton_locked:
        print(
            json.dumps(
                {
                    "ok": False,
                    "supervisor": True,
                    "runtime_family": "unified",
                    "already_running": True,
                    "singleton_info": singleton_info,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    cfg = load_config()
    archive_cfg = load_archive_config()

    locked, lock_info = _acquire_supervisor_lock(cfg)
    if not locked:
        release_process_singleton_mutex(singleton_info)
        print(
            json.dumps(
                {
                    "ok": False,
                    "supervisor": True,
                    "runtime_family": "unified",
                    "already_running": True,
                    "lock_info": lock_info,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    graceful_timeout_sec = env_int("BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC", 30)
    restart_backoff_sec = env_int("BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC", 3)
    max_failures = env_int("BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES", 10)
    request_max_age_sec = env_int("BTCTS_UNIFIED_REQUEST_MAX_AGE_SEC", 600)
    safe_stop_timeout_sec = env_int("BTCTS_UNIFIED_SAFE_STOP_TIMEOUT_SEC", 180)

    proc: subprocess.Popen | None = None
    consecutive_failures = 0
    supervisor_started_at = now_iso_utc()

    try:
        _append_audit(cfg, "watchdog.start")
        _write_status(
            cfg,
            mode="STARTING",
            last_action="start",
            started_at=supervisor_started_at,
            last_seen_ts=now_iso_utc(),
            uptime_sec=_uptime_sec(supervisor_started_at),
        )
        proc = _start_unified_daemon()
        _append_audit(cfg, "watchdog.start.daemon", extra={"daemon_pid": proc.pid})
        _write_status(
            cfg,
            mode="RUNNING",
            last_action="start",
            daemon_pid=proc.pid,
            started_at=supervisor_started_at,
            last_seen_ts=now_iso_utc(),
            uptime_sec=_uptime_sec(supervisor_started_at),
        )

        while True:
            if proc.poll() is not None:
                consecutive_failures += 1
                _append_audit(
                    cfg,
                    "watchdog.observe.daemon_exited",
                    level="WARN",
                    extra={
                        "daemon_pid": proc.pid,
                        "exit_code": proc.returncode,
                        "consecutive_failures": consecutive_failures,
                    },
                )

                if consecutive_failures >= max_failures:
                    _write_status(
                        cfg,
                        mode="FAILED",
                        last_action="restart",
                        last_error=f"too_many_failures={consecutive_failures}",
                        daemon_pid=proc.pid,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )
                    _append_audit(cfg, "watchdog.stop.too_many_fails", level="ERROR")
                    return 1

                _write_status(
                    cfg,
                    mode="BACKOFF",
                    last_action="restart",
                    last_error=f"daemon_exit_code={proc.returncode}",
                    daemon_pid=proc.pid,
                    started_at=supervisor_started_at,
                    last_seen_ts=now_iso_utc(),
                    uptime_sec=_uptime_sec(supervisor_started_at),
                )
                time.sleep(restart_backoff_sec)
                proc = _start_unified_daemon()
                _append_audit(cfg, "watchdog.restart.completed", extra={"daemon_pid": proc.pid})
                _write_status(
                    cfg,
                    mode="RUNNING",
                    last_action="restart",
                    last_completed_at=now_iso_utc(),
                    daemon_pid=proc.pid,
                    started_at=supervisor_started_at,
                    last_seen_ts=now_iso_utc(),
                    uptime_sec=_uptime_sec(supervisor_started_at),
                )
                continue

            _heartbeat_running_status(
                cfg,
                started_at=supervisor_started_at,
                daemon_pid=proc.pid,
                default_last_action="start",
            )

            request = _active_supervisor_request(cfg)
            if request:
                action = str(request.get("action") or "").strip().lower()
                requested_at = str(request.get("requested_at") or now_iso_utc())
                request_id = str(request.get("request_id") or "").strip() or None
                request_age_sec = _request_age_sec(request)

                if request_age_sec is not None and request_age_sec > request_max_age_sec:
                    _append_audit(
                        cfg,
                        f"watchdog.{action}.request.stale_ignored",
                        level="WARN",
                        extra={
                            "request_id": request_id,
                            "requested_at": requested_at,
                            "request_age_sec": round(request_age_sec, 1),
                            "request_max_age_sec": request_max_age_sec,
                        },
                    )
                    _clear_request_file(cfg)
                    _write_status(
                        cfg,
                        mode="RUNNING",
                        last_action=action,
                        last_requested_at=requested_at,
                        last_error=f"stale_request_ignored age_sec={round(request_age_sec, 1)}",
                        daemon_pid=proc.pid,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )
                    time.sleep(1.0)
                    continue

                _clear_request_file(cfg)

                if action == "restart":
                    _append_audit(
                        cfg,
                        "watchdog.restart.requested",
                        extra={
                            "request_id": request_id,
                            "requested_at": requested_at,
                            "requested_by": request.get("requested_by"),
                            "reason": request.get("reason"),
                            "daemon_pid": proc.pid,
                        },
                    )
                    _write_status(
                        cfg,
                        mode="RESTART_REQUESTED",
                        last_action="restart",
                        last_requested_at=requested_at,
                        daemon_pid=proc.pid,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )

                    _request_daemon_stop(
                        cfg,
                        request,
                        reason_default="manual_restart",
                        restart_requested=True,
                    )
                    _append_audit(
                        cfg,
                        "watchdog.restart.graceful_begin",
                        extra={"daemon_pid": proc.pid, "request_id": request_id},
                    )
                    _write_status(
                        cfg,
                        mode="GRACEFUL_STOPPING",
                        last_action="restart",
                        last_requested_at=requested_at,
                        daemon_pid=proc.pid,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )

                    stopped = _graceful_stop(proc, graceful_timeout_sec)
                    if not stopped:
                        _append_audit(
                            cfg,
                            "watchdog.restart.graceful_timeout",
                            level="WARN",
                            extra={"daemon_pid": proc.pid, "request_id": request_id},
                        )
                        proc.kill()
                        try:
                            proc.wait(timeout=5)
                        except Exception:
                            pass
                        _append_audit(
                            cfg,
                            "watchdog.restart.force_kill",
                            level="WARN",
                            extra={"daemon_pid": proc.pid, "request_id": request_id},
                        )

                    _clear_daemon_stop_request(cfg)

                    _write_status(
                        cfg,
                        mode="BACKOFF",
                        last_action="restart",
                        last_requested_at=requested_at,
                        daemon_pid=None,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )
                    time.sleep(restart_backoff_sec)

                    proc = _start_unified_daemon()
                    consecutive_failures = 0
                    completed_at = now_iso_utc()

                    _append_audit(
                        cfg,
                        "watchdog.restart.completed",
                        extra={"daemon_pid": proc.pid, "request_id": request_id},
                    )
                    _write_status(
                        cfg,
                        mode="RUNNING",
                        last_action="restart",
                        last_requested_at=requested_at,
                        last_completed_at=completed_at,
                        daemon_pid=proc.pid,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )
                    continue

                if action == "stop_stack":
                    _append_audit(
                        cfg,
                        "watchdog.stop_stack.requested",
                        extra={
                            "request_id": request_id,
                            "requested_at": requested_at,
                            "requested_by": request.get("requested_by"),
                            "reason": request.get("reason"),
                            "daemon_pid": proc.pid,
                        },
                    )
                    _write_status(
                        cfg,
                        mode="STOP_REQUESTED",
                        last_action="stop_stack",
                        last_requested_at=requested_at,
                        daemon_pid=proc.pid,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )

                    _request_daemon_stop(
                        cfg,
                        request,
                        reason_default="maintenance_safe_stop",
                        restart_requested=False,
                    )
                    _append_audit(
                        cfg,
                        "watchdog.stop_stack.daemon_graceful_begin",
                        extra={"daemon_pid": proc.pid, "request_id": request_id},
                    )
                    _write_status(
                        cfg,
                        mode="GRACEFUL_STOPPING",
                        last_action="stop_stack",
                        last_requested_at=requested_at,
                        daemon_pid=proc.pid,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )

                    stopped = _graceful_stop(proc, graceful_timeout_sec)
                    if not stopped:
                        _append_audit(
                            cfg,
                            "watchdog.stop_stack.daemon_graceful_timeout",
                            level="WARN",
                            extra={"daemon_pid": proc.pid, "request_id": request_id},
                        )
                        proc.kill()
                        try:
                            proc.wait(timeout=5)
                        except Exception:
                            pass
                        _append_audit(
                            cfg,
                            "watchdog.stop_stack.daemon_force_kill",
                            level="WARN",
                            extra={"daemon_pid": proc.pid, "request_id": request_id},
                        )

                    _clear_daemon_stop_request(cfg)

                    _write_status(
                        cfg,
                        mode="DAEMON_STOPPED",
                        last_action="stop_stack",
                        last_requested_at=requested_at,
                        daemon_pid=None,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )

                    _request_archive_stop(archive_cfg, request)
                    _append_audit(
                        cfg,
                        "watchdog.stop_stack.archive_drain_requested",
                        extra={"request_id": request_id},
                    )
                    _write_status(
                        cfg,
                        mode="ARCHIVE_DRAIN_REQUESTED",
                        last_action="stop_stack",
                        last_requested_at=requested_at,
                        daemon_pid=None,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )

                    deadline = time.time() + max(safe_stop_timeout_sec, 1)
                    archive_completed = False
                    copy_state: dict[str, Any] = {}
                    gc_state: dict[str, Any] = {}

                    while time.time() < deadline:
                        archive_completed, copy_state, gc_state = _archive_stopped(archive_cfg)
                        if archive_completed:
                            break

                        _write_status(
                            cfg,
                            mode="ARCHIVE_DRAINING",
                            last_action="stop_stack",
                            last_requested_at=requested_at,
                            daemon_pid=None,
                            request_ack_ts=now_iso_utc(),
                            acked_request_id=request_id,
                            started_at=supervisor_started_at,
                            last_seen_ts=now_iso_utc(),
                            uptime_sec=_uptime_sec(supervisor_started_at),
                        )
                        time.sleep(1.0)

                    if not archive_completed:
                        _append_audit(
                            cfg,
                            "watchdog.stop_stack.archive_timeout",
                            level="ERROR",
                            extra={
                                "request_id": request_id,
                                "timeout_sec": safe_stop_timeout_sec,
                                "archive_copy_mode": str(copy_state.get("mode") or ""),
                                "archive_gc_mode": str(gc_state.get("mode") or ""),
                            },
                        )
                        _write_status(
                            cfg,
                            mode="FAILED",
                            last_action="stop_stack",
                            last_requested_at=requested_at,
                            last_error=(
                                "archive_stop_timeout "
                                f"copy_mode={str(copy_state.get('mode') or '-')}"
                                f" gc_mode={str(gc_state.get('mode') or '-')}"
                            ),
                            daemon_pid=None,
                            request_ack_ts=now_iso_utc(),
                            acked_request_id=request_id,
                            started_at=supervisor_started_at,
                            last_seen_ts=now_iso_utc(),
                            uptime_sec=_uptime_sec(supervisor_started_at),
                        )
                        return 1

                    completed_at = now_iso_utc()
                    _append_audit(
                        cfg,
                        "watchdog.stop_stack.completed",
                        extra={
                            "request_id": request_id,
                            "archive_copy_mode": str(copy_state.get("mode") or ""),
                            "archive_gc_mode": str(gc_state.get("mode") or ""),
                        },
                    )
                    _write_status(
                        cfg,
                        mode="SAFE_STOP_COMPLETED",
                        last_action="stop_stack",
                        last_requested_at=requested_at,
                        last_completed_at=completed_at,
                        daemon_pid=None,
                        request_ack_ts=now_iso_utc(),
                        acked_request_id=request_id,
                        started_at=supervisor_started_at,
                        last_seen_ts=now_iso_utc(),
                        uptime_sec=_uptime_sec(supervisor_started_at),
                    )
                    return 0

            time.sleep(1.0)

    except KeyboardInterrupt:
        _append_audit(cfg, "watchdog.exit", extra={"reason": "keyboard_interrupt"})
        _write_status(
            cfg,
            mode="STOPPED",
            last_action="stop",
            last_error=None,
            daemon_pid=None,
            started_at=supervisor_started_at,
            last_seen_ts=now_iso_utc(),
            uptime_sec=_uptime_sec(supervisor_started_at),
        )
        return 0

    except Exception as exc:
        _append_audit(cfg, "watchdog.exception", level="ERROR", extra={"error": str(exc)})
        _write_status(
            cfg,
            mode="FAILED",
            last_action="restart",
            last_error=str(exc),
            daemon_pid=None,
            started_at=supervisor_started_at,
            last_seen_ts=now_iso_utc(),
            uptime_sec=_uptime_sec(supervisor_started_at),
        )
        raise

    finally:
        if proc is not None and proc.poll() is None:
            try:
                write_unified_daemon_stop_request(
                    cfg,
                    {
                        "action": "stop",
                        "requested_at": now_iso_utc(),
                        "requested_by": "unified_watchdog",
                        "reason": "watchdog_exit",
                    },
                )
                if not _graceful_stop(proc, 10):
                    proc.kill()
                    try:
                        proc.wait(timeout=5)
                    except Exception:
                        pass
            except Exception:
                pass

        _clear_request_file(cfg)
        _clear_daemon_stop_request(cfg)
        _release_supervisor_lock(cfg)
        release_process_singleton_mutex(singleton_info)


def main() -> int:
    return run_forever()


if __name__ == "__main__":
    raise SystemExit(main())