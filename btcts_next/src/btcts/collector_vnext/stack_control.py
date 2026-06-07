# path: ./btcts_next/src/btcts/collector_vnext/stack_control.py
# desc: Operator UI から collector stack を hidden / detached 起動する helper。

from __future__ import annotations

import json
import shutil
import socket
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btcts.collector_vnext.archive.config import load_archive_config
from btcts.collector_vnext.archive.state import (
    read_archive_copy_state,
    read_archive_gc_state,
    read_archive_worker_lock,
)
from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.lock import is_pid_alive, read_lock_info
from btcts.collector_vnext.unified_state import (
    read_unified_supervisor_request,
    read_unified_supervisor_status,
)

_ACTIVE_SUPERVISOR_MODES = {
    "STARTING",
    "RUNNING",
    "BACKOFF",
    "RESTART_REQUESTED",
    "GRACEFUL_STOPPING",
    "STOP_REQUESTED",
    "DAEMON_STOPPED",
    "ARCHIVE_DRAIN_REQUESTED",
    "ARCHIVE_DRAINING",
}

_ACTIVE_ARCHIVE_MODES = {
    "RUNNING",
    "IDLE",
    "STOPPING",
}

_SUPERVISOR_STATUS_STALE_SEC = 120
_ARCHIVE_STATE_STALE_SEC = 180
_REQUEST_STALE_SEC = 120


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _safe_read(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _safe_mode(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("mode") or "").strip().upper()


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


def _is_fresh(payload: dict[str, Any], *, stale_sec: int) -> bool:
    if not isinstance(payload, dict) or not payload:
        return False

    ts = _parse_ts(str(payload.get("ts") or ""))
    if ts is None:
        ts = _parse_ts(str(payload.get("last_seen_ts") or ""))
    if ts is None:
        ts = _parse_ts(str(payload.get("started_at") or ""))
    if ts is None:
        return False

    now = datetime.now(timezone.utc)
    try:
        age = max(0.0, (now - ts.astimezone(timezone.utc)).total_seconds())
    except Exception:
        return False
    return age <= stale_sec


def _request_is_fresh(payload: dict[str, Any], *, stale_sec: int) -> bool:
    if not isinstance(payload, dict) or not payload:
        return False

    requested_at = _parse_ts(str(payload.get("requested_at") or ""))
    if requested_at is None:
        return False

    now = datetime.now(timezone.utc)
    try:
        age = max(0.0, (now - requested_at.astimezone(timezone.utc)).total_seconds())
    except Exception:
        return False
    return age <= stale_sec


def _supervisor_lock_path(cfg) -> Path:
    return cfg.roots()["state"] / "unified_supervisor.lock.json"


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _backup_stale_control_files(state_dir: Path) -> str | None:
    names = [
        "unified_supervisor.lock.json",
        "unified_daemon.lock.json",
        "archive_worker.lock.json",
        "stack_start.lock.json",
        "unified_supervisor_request.json",
        "archive_stop_request.json",
        "unified_daemon_stop_request.json",
        "unified_supervisor_status.json",
        "archive_copy_state.json",
        "archive_gc_state.json",
    ]
    existing = [state_dir / name for name in names if (state_dir / name).exists()]
    if not existing:
        return None

    backup_dir = state_dir / f"_recovery_auto_stale_control_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for path in existing:
        shutil.copy2(path, backup_dir / path.name)
    return str(backup_dir)


def _unlink_state_file(state_dir: Path, name: str) -> None:
    try:
        (state_dir / name).unlink(missing_ok=True)
    except Exception:
        pass


def _actual_stack_process_alive(
    *,
    supervisor_status: dict[str, Any],
    daemon_lock: dict[str, Any],
    archive_lock: dict[str, Any],
    supervisor_lock: dict[str, Any],
) -> bool:
    pids = [
        supervisor_lock.get("pid"),
        daemon_lock.get("pid"),
        archive_lock.get("pid"),
        supervisor_status.get("supervisor_pid"),
        supervisor_status.get("daemon_pid"),
    ]
    return any(is_pid_alive(pid) for pid in pids)


def _has_active_or_pending_control_state(
    *,
    supervisor_status: dict[str, Any],
    supervisor_request: dict[str, Any],
    archive_copy_state: dict[str, Any],
    archive_gc_state: dict[str, Any],
    supervisor_lock: dict[str, Any],
    daemon_lock: dict[str, Any],
    archive_lock: dict[str, Any],
) -> bool:
    supervisor_mode = _safe_mode(supervisor_status)
    archive_copy_mode = _safe_mode(archive_copy_state)
    archive_gc_mode = _safe_mode(archive_gc_state)
    pending_action = str(supervisor_request.get("action") or "").strip().lower()
    return bool(
        supervisor_lock
        or daemon_lock
        or archive_lock
        or pending_action in {"restart", "stop_stack"}
        or supervisor_mode in _ACTIVE_SUPERVISOR_MODES
        or archive_copy_mode in _ACTIVE_ARCHIVE_MODES
        or archive_gc_mode in _ACTIVE_ARCHIVE_MODES
    )


def _write_recovered_stopped_state(state_dir: Path, *, backup_dir: str | None) -> None:
    now = _now_iso_utc()
    note = "auto stale control state recovery; no collector_vnext control process was alive"
    if backup_dir:
        note = f"{note}; backup={backup_dir}"

    _write_json_file(
        state_dir / "unified_supervisor_status.json",
        {
            "ts": now,
            "mode": "STOPPED",
            "last_action": "auto_stale_control_state_recovery",
            "last_requested_at": None,
            "last_completed_at": now,
            "last_error": None,
            "daemon_pid": None,
            "request_ack_ts": None,
            "acked_request_id": None,
            "started_at": None,
            "last_seen_ts": now,
            "uptime_sec": None,
            "runtime_family": "unified",
            "supervisor_pid": None,
            "host_name": os.environ.get("COMPUTERNAME") or socket.gethostname(),
            "recovery_note": note,
        },
    )
    _write_json_file(
        state_dir / "archive_copy_state.json",
        {
            "ts": now,
            "mode": "STOPPED",
            "current_phase": "stopped",
            "started_at": None,
            "last_error": None,
            "last_scan_ts": now,
            "last_plan_count": 0,
            "last_copied_files": 0,
            "last_copied_dirs": 0,
            "last_copied_bytes": 0,
            "error_count": 0,
            "plan_sample": [],
            "recovery_note": note,
        },
    )
    _write_json_file(
        state_dir / "archive_gc_state.json",
        {
            "ts": now,
            "mode": "STOPPED",
            "current_phase": "stopped",
            "started_at": None,
            "dry_run": True,
            "enabled": True,
            "last_error": None,
            "last_scan_ts": now,
            "last_plan_count": 0,
            "last_deleted_files": 0,
            "last_deleted_bytes": 0,
            "error_count": 0,
            "plan_sample": [],
            "recovery_note": note,
        },
    )


def _reconcile_stale_control_state_if_safe(
    *,
    state_dir: Path,
    supervisor_status: dict[str, Any],
    supervisor_request: dict[str, Any],
    archive_copy_state: dict[str, Any],
    archive_gc_state: dict[str, Any],
    supervisor_lock: dict[str, Any],
    daemon_lock: dict[str, Any],
    archive_lock: dict[str, Any],
) -> dict[str, Any]:
    actual_alive = _actual_stack_process_alive(
        supervisor_status=supervisor_status,
        daemon_lock=daemon_lock,
        archive_lock=archive_lock,
        supervisor_lock=supervisor_lock,
    )
    has_artifacts = _has_active_or_pending_control_state(
        supervisor_status=supervisor_status,
        supervisor_request=supervisor_request,
        archive_copy_state=archive_copy_state,
        archive_gc_state=archive_gc_state,
        supervisor_lock=supervisor_lock,
        daemon_lock=daemon_lock,
        archive_lock=archive_lock,
    )

    if actual_alive or not has_artifacts:
        return {
            "stale_control_state_recovered": False,
            "stale_control_state_detected": bool(has_artifacts and not actual_alive),
            "stale_control_state_backup_dir": None,
        }

    backup_dir = _backup_stale_control_files(state_dir)
    for name in [
        "unified_supervisor.lock.json",
        "unified_daemon.lock.json",
        "archive_worker.lock.json",
        "stack_start.lock.json",
        "unified_supervisor_request.json",
        "archive_stop_request.json",
        "unified_daemon_stop_request.json",
    ]:
        _unlink_state_file(state_dir, name)
    _write_recovered_stopped_state(state_dir, backup_dir=backup_dir)
    return {
        "stale_control_state_recovered": True,
        "stale_control_state_detected": True,
        "stale_control_state_backup_dir": backup_dir,
        "stale_control_state_reason": "no_collector_vnext_control_process_alive",
    }


def stack_runtime_snapshot() -> dict[str, Any]:
    collector_cfg = load_config()
    archive_cfg = load_archive_config()
    state_dir = collector_cfg.roots()["state"]

    supervisor_status = read_unified_supervisor_status(collector_cfg)
    supervisor_request = read_unified_supervisor_request(collector_cfg)
    archive_copy_state = read_archive_copy_state(archive_cfg)
    archive_gc_state = read_archive_gc_state(archive_cfg)

    daemon_lock = read_lock_info(collector_cfg, runtime_family="unified") or {}
    archive_lock = read_archive_worker_lock(archive_cfg) or {}
    supervisor_lock = _safe_read(_supervisor_lock_path(collector_cfg))

    recovery = _reconcile_stale_control_state_if_safe(
        state_dir=state_dir,
        supervisor_status=supervisor_status,
        supervisor_request=supervisor_request,
        archive_copy_state=archive_copy_state,
        archive_gc_state=archive_gc_state,
        supervisor_lock=supervisor_lock,
        daemon_lock=daemon_lock,
        archive_lock=archive_lock,
    )
    if recovery.get("stale_control_state_recovered"):
        supervisor_status = read_unified_supervisor_status(collector_cfg)
        supervisor_request = read_unified_supervisor_request(collector_cfg)
        archive_copy_state = read_archive_copy_state(archive_cfg)
        archive_gc_state = read_archive_gc_state(archive_cfg)
        daemon_lock = read_lock_info(collector_cfg, runtime_family="unified") or {}
        archive_lock = read_archive_worker_lock(archive_cfg) or {}
        supervisor_lock = _safe_read(_supervisor_lock_path(collector_cfg))

    pending_action_raw = str(supervisor_request.get("action") or "").strip().lower()
    pending_request_fresh = _request_is_fresh(supervisor_request, stale_sec=_REQUEST_STALE_SEC)
    pending_action = pending_action_raw if pending_request_fresh else ""

    supervisor_lock_alive = is_pid_alive(supervisor_lock.get("pid"))
    daemon_lock_alive = is_pid_alive(daemon_lock.get("pid"))
    archive_lock_alive = is_pid_alive(archive_lock.get("pid"))

    supervisor_mode = _safe_mode(supervisor_status)
    archive_copy_mode = _safe_mode(archive_copy_state)
    archive_gc_mode = _safe_mode(archive_gc_state)

    supervisor_status_fresh = _is_fresh(supervisor_status, stale_sec=_SUPERVISOR_STATUS_STALE_SEC)
    archive_copy_state_fresh = _is_fresh(archive_copy_state, stale_sec=_ARCHIVE_STATE_STALE_SEC)
    archive_gc_state_fresh = _is_fresh(archive_gc_state, stale_sec=_ARCHIVE_STATE_STALE_SEC)

    supervisor_active = supervisor_lock_alive or (
        supervisor_status_fresh and supervisor_mode in _ACTIVE_SUPERVISOR_MODES
    )
    archive_active = archive_lock_alive or (
        archive_copy_state_fresh and archive_copy_mode in _ACTIVE_ARCHIVE_MODES
    ) or (
        archive_gc_state_fresh and archive_gc_mode in _ACTIVE_ARCHIVE_MODES
    )

    snapshot = {
        "supervisor_mode": supervisor_mode,
        "archive_copy_mode": archive_copy_mode,
        "archive_gc_mode": archive_gc_mode,
        "pending_action": pending_action,
        "pending_action_raw": pending_action_raw,
        "pending_request_fresh": pending_request_fresh,
        "supervisor_lock_alive": supervisor_lock_alive,
        "daemon_lock_alive": daemon_lock_alive,
        "archive_lock_alive": archive_lock_alive,
        "supervisor_status_fresh": supervisor_status_fresh,
        "archive_copy_state_fresh": archive_copy_state_fresh,
        "archive_gc_state_fresh": archive_gc_state_fresh,
        "supervisor_status": supervisor_status,
        "supervisor_request": supervisor_request,
        "archive_copy_state": archive_copy_state,
        "archive_gc_state": archive_gc_state,
        "supervisor_active": supervisor_active,
        "archive_active": archive_active,
        **recovery,
    }

    snapshot["stack_active"] = (
        supervisor_active
        or daemon_lock_alive
        or archive_active
        or pending_action in {"restart", "stop_stack"}
    )
    return snapshot


def _setdefault_env(env: dict[str, str], key: str, value: str) -> None:
    if not str(env.get(key) or "").strip():
        env[key] = value


def _build_child_env() -> dict[str, str]:
    repo_root = _repo_root()
    cfg = load_config()

    env = dict(os.environ)

    _setdefault_env(env, "PYTHONPATH", str(repo_root / "btcts_next" / "src"))
    _setdefault_env(env, "BTC_TS_DATA_DIR", str(cfg.data_root))
    _setdefault_env(env, "BTC_TS_LOGS_DIR", str(cfg.logs_root))
    _setdefault_env(env, "BTCTS_STATE_ROOT", str(cfg.state_root))
    _setdefault_env(env, "BTCTS_DATA_ROOT", env["BTC_TS_DATA_DIR"])
    _setdefault_env(env, "BTCTS_LOGS_ROOT", env["BTC_TS_LOGS_DIR"])

    _setdefault_env(env, "BTCTS_UNIFIED_LOOP_SLEEP_SEC", "0.25")
    _setdefault_env(env, "BTCTS_UNIFIED_MAX_FAILURES", "20")
    _setdefault_env(env, "BTCTS_UNIFIED_FAILURE_BACKOFF_SEC", "3")
    _setdefault_env(env, "BTCTS_UNIFIED_WS_BOARD_RECONNECT_BACKOFF_SEC", "2")
    _setdefault_env(env, "BTCTS_UNIFIED_WS_EXECUTIONS_RECONNECT_BACKOFF_SEC", "2")
    _setdefault_env(env, "BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC", "30")
    _setdefault_env(env, "BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC", "3")
    _setdefault_env(env, "BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES", "10")
    _setdefault_env(env, "BTCTS_WS_SSL_VERIFY", "false")

    _setdefault_env(env, "BTCTS_ARCHIVE_COLD_ROOT", r"E:\btc_ts")
    _setdefault_env(env, "BTCTS_ARCHIVE_SCAN_INTERVAL_SEC", "30")
    _setdefault_env(env, "BTCTS_ARCHIVE_STABLE_AGE_SEC", "3600")
    _setdefault_env(env, "BTCTS_ARCHIVE_COPY_MIN_AGE_DAYS", "1")
    _setdefault_env(env, "BTCTS_ARCHIVE_GC_MIN_AGE_DAYS", "10")
    _setdefault_env(env, "BTCTS_ARCHIVE_MAX_FILES_PER_CYCLE", "64")
    _setdefault_env(env, "BTCTS_ARCHIVE_MAX_BYTES_PER_CYCLE", "268435456")
    _setdefault_env(env, "BTCTS_ARCHIVE_GC_ENABLED", "true")
    _setdefault_env(env, "BTCTS_ARCHIVE_GC_DRY_RUN", "true")
    _setdefault_env(env, "BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE", "32")
    _setdefault_env(env, "BTCTS_ARCHIVE_MAX_DELETE_BYTES_PER_CYCLE", "26843545600")

    return env


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


def _spawn_hidden(module_name: str) -> int:
    repo_root = _repo_root()
    env = _build_child_env()
    runtime_python = _repo_runtime_python()
    proc = subprocess.Popen(
        [runtime_python, "-m", module_name],
        cwd=str(repo_root),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=_windows_creationflags(),
        startupinfo=_windows_startupinfo(),
        close_fds=True,
    )
    return int(proc.pid)


def _stack_start_lock_path(cfg) -> Path:
    return cfg.roots()["state"] / "stack_start.lock.json"


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _acquire_stack_start_lock(cfg) -> tuple[bool, dict[str, Any]]:
    path = _stack_start_lock_path(cfg)
    payload = {
        "pid": os.getpid(),
        "started_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "command": "stack_control.start_stack_detached",
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
            existing = _read_json_file(path)
            if not existing:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    return False, {"error": "stack_start_lock_unreadable", "path": str(path)}
                continue

            if is_pid_alive(existing.get("pid")):
                return False, existing

            try:
                path.unlink(missing_ok=True)
            except Exception:
                return False, {"error": "stale_stack_start_lock_unlink_failed", "path": str(path), **existing}
            continue
        except Exception as exc:
            return False, {"error": f"stack_start_lock_write_failed: {exc}", "path": str(path)}


def _release_stack_start_lock(cfg) -> None:
    path = _stack_start_lock_path(cfg)
    existing = _read_json_file(path)
    if not existing:
        return
    if existing.get("pid") != os.getpid():
        return
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass


def start_stack_detached() -> dict[str, Any]:
    collector_cfg = load_config()

    locked, lock_info = _acquire_stack_start_lock(collector_cfg)
    if not locked:
        return {
            "ok": True,
            "already_running": True,
            "started_components": [],
            "reason": "start_already_in_progress",
            "lock_info": lock_info,
        }

    try:
        before = stack_runtime_snapshot()
        if before["stack_active"]:
            return {
                "ok": True,
                "already_running": True,
                "started_components": [],
                "snapshot_before": before,
            }

        started_components: list[dict[str, Any]] = []

        if not before["archive_active"]:
            started_components.append(
                {
                    "component": "archive_worker",
                    "pid": _spawn_hidden("btcts.collector_vnext.archive.worker"),
                }
            )

        if not before["supervisor_active"] and not before["daemon_lock_alive"]:
            started_components.append(
                {
                    "component": "unified_watchdog",
                    "pid": _spawn_hidden("btcts.collector_vnext.unified_watchdog"),
                }
            )

        # spawn直後は state/lock 反映前なので、少し待って stack_active を確認してから lock を離す
        deadline = time.time() + 8.0
        snapshot_after = before

        while time.time() < deadline:
            snapshot_after = stack_runtime_snapshot()
            if snapshot_after.get("stack_active"):
                break
            time.sleep(0.25)

        return {
            "ok": True,
            "already_running": False,
            "started_components": started_components,
            "snapshot_before": before,
            "snapshot_after": snapshot_after,
        }
    finally:
        _release_stack_start_lock(collector_cfg)