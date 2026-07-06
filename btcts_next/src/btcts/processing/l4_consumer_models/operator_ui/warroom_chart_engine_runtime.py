# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/warroom_chart_engine_runtime.py
# desc: Operator-control helper for the WarRoom Chart Engine runtime. UI writes start/stop/restart requests; runtime owns candle generation and serving.

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from btcts.collector_vnext.lock import is_pid_alive
from btcts.core import paths as core_paths

WARROOM_CHART_ENGINE_RUNTIME_VERSION = "warroom_chart_engine_runtime.2026_07_07.v1_ui_managed_l4_runtime"
WARROOM_CHART_ENGINE_LAYER = "L4_CONSUMER_MODEL_OPERATOR_UI_RUNTIME"
WARROOM_CHART_ENGINE_CANONICAL_MODULE = "btcts.processing.l4_consumer_models.operator_ui.warroom_chart_engine_runtime"
WARROOM_CHART_ENGINE_STATE_DIRNAME = "warroom_chart_engine"
DEFAULT_ENDPOINT = "http://127.0.0.1:8765/warroom/plain-candles/latest"
DEFAULT_TIMEFRAMES_SEC = "60,300,900,1800,3600,86400"
DEFAULT_RETENTION_DAYS = 92
DEFAULT_INTERVAL_SEC = 5


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _normalize_runtime_root(root: Path) -> Path:
    """Return the hot root that contains data/market_data, not the nested data directory."""
    candidate = Path(root)
    if (candidate / "data" / "market_data").exists():
        return candidate
    if candidate.name.lower() == "data" and (candidate / "market_data").exists():
        return candidate.parent
    return candidate


def _data_root() -> Path:
    override = str(os.environ.get("BTCTS_DATA_ROOT") or os.environ.get("BTC_TS_DATA_DIR") or "").strip()
    if override:
        return _normalize_runtime_root(Path(override))
    return _normalize_runtime_root(core_paths.data_dir(ensure=False))


def chart_engine_state_dir(data_root: Path | None = None) -> Path:
    return (data_root or _data_root()) / "state" / WARROOM_CHART_ENGINE_STATE_DIRNAME


def chart_engine_paths(data_root: Path | None = None) -> dict[str, Path]:
    state_dir = chart_engine_state_dir(data_root)
    return {
        "state_dir": state_dir,
        "status": state_dir / "status.json",
        "health": state_dir / "health.json",
        "request": state_dir / "request.json",
        "lock": state_dir / "runtime.lock.json",
        "stdout": state_dir / "runtime.stdout.log",
        "stderr": state_dir / "runtime.stderr.log",
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        item = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(item) if isinstance(item, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _parse_ts(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def _age_seconds(value: object) -> float | None:
    ts = _parse_ts(value)
    if ts is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - ts.astimezone(timezone.utc)).total_seconds())


def chart_engine_runtime_snapshot(data_root: Path | None = None) -> dict[str, Any]:
    paths = chart_engine_paths(data_root)
    status = _read_json(paths["status"])
    health = _read_json(paths["health"])
    request = _read_json(paths["request"])
    lock = _read_json(paths["lock"])
    pid = lock.get("pid") or status.get("runtime_pid")
    active = bool(is_pid_alive(pid))
    pending_action = str(request.get("action") or "").strip().lower()
    status_ts = status.get("ts") or status.get("last_seen_ts")
    age = _age_seconds(status_ts)
    mode = str(status.get("mode") or ("RUNNING" if active else "STOPPED")).upper()
    return {
        "ok": True,
        "version": WARROOM_CHART_ENGINE_RUNTIME_VERSION,
        "layer": WARROOM_CHART_ENGINE_LAYER,
        "state_dir": str(paths["state_dir"]),
        "status_path": str(paths["status"]),
        "health_path": str(paths["health"]),
        "request_path": str(paths["request"]),
        "lock_path": str(paths["lock"]),
        "mode": mode,
        "active": active,
        "runtime_pid": pid,
        "status_age_sec": age,
        "pending_action": pending_action,
        "status": status,
        "health": health,
        "request": request,
        "lock": lock,
        "endpoint": status.get("endpoint") or DEFAULT_ENDPOINT,
        "latest_candle_end_ts_utc": status.get("latest_candle_end_ts_utc") or (status.get("last_endpoint_meta") or {}).get("end_ts_utc"),
        "gap_policy": status.get("gap_policy") or "absent_candles_no_synthetic_null",
        "read_only_source": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def _runtime_python() -> str:
    repo_root = _repo_root()
    override = str(os.environ.get("BTCTS_RUNTIME_PYTHON") or "").strip()
    if override and Path(override).exists():
        return override
    candidates = []
    if os.name == "nt":
        candidates.extend([repo_root / ".venv" / "Scripts" / "pythonw.exe", repo_root / ".venv" / "Scripts" / "python.exe"])
    else:
        candidates.append(repo_root / ".venv" / "bin" / "python")
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def _pwsh_exe() -> str:
    return str(os.environ.get("BTCTS_PWSH") or "pwsh")


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
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def _child_env(data_root: Path) -> dict[str, str]:
    repo_root = _repo_root()
    env = dict(os.environ)
    env.setdefault("PYTHONPATH", str(repo_root / "btcts_next" / "src"))
    env.setdefault("BTC_TS_DATA_DIR", str(data_root))
    env.setdefault("BTCTS_DATA_ROOT", str(data_root))
    env.setdefault("WARROOM_PLAIN_CANDLE_CHART_ENDPOINT", DEFAULT_ENDPOINT)
    return env


def start_chart_engine_detached(data_root: Path | None = None, *, interval_sec: int = DEFAULT_INTERVAL_SEC) -> tuple[bool, str, bool]:
    root = data_root or _data_root()
    snapshot = chart_engine_runtime_snapshot(root)
    if snapshot.get("active"):
        return True, f"chart engine already running pid={snapshot.get('runtime_pid')}", True
    repo_root = _repo_root()
    script = repo_root / "tools" / "run_warroom_chart_engine.ps1"
    if not script.exists():
        return False, f"runtime tool missing: {script}", False
    paths = chart_engine_paths(root)
    paths["state_dir"].mkdir(parents=True, exist_ok=True)
    command_args = [
        _pwsh_exe(),
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-RawRoot",
        str(root),
        "-CacheRoot",
        str(root),
        "-IntervalSec",
        str(max(2, int(interval_sec))),
        "-MaxCycles",
        "0",
    ]
    with paths["stdout"].open("ab") as stdout_handle, paths["stderr"].open("ab") as stderr_handle:
        proc = subprocess.Popen(
            command_args,
            cwd=str(repo_root),
            env=_child_env(root),
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=_windows_creationflags(),
            startupinfo=_windows_startupinfo(),
            close_fds=True,
        )
    _write_json(
        paths["status"],
        {
            "ts": _now_iso(),
            "mode": "STARTING",
            "runtime_pid": int(proc.pid),
            "endpoint": DEFAULT_ENDPOINT,
            "requested_by": "operator_ui",
            "data_root_normalized": str(root),
            "command_args": command_args,
            "stdout_path": str(paths["stdout"]),
            "stderr_path": str(paths["stderr"]),
            "max_cycles": 0,
            "version": WARROOM_CHART_ENGINE_RUNTIME_VERSION,
            "layer": WARROOM_CHART_ENGINE_LAYER,
            "read_only_source": True,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        },
    )
    return True, f"chart engine start requested pid={int(proc.pid)}", False


def _write_request(action: str, *, reason: str, data_root: Path | None = None) -> tuple[bool, str]:
    root = data_root or _data_root()
    paths = chart_engine_paths(root)
    request_id = uuid4().hex
    payload = {
        "ok": True,
        "version": WARROOM_CHART_ENGINE_RUNTIME_VERSION,
        "request_id": request_id,
        "action": action,
        "requested_at": _now_iso(),
        "requested_by": "operator_ui",
        "reason": reason,
        "host_name": os.environ.get("COMPUTERNAME") or socket.gethostname(),
        "read_only_source": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
    _write_json(paths["request"], payload)
    return True, f"chart engine {action} request written request_id={request_id}"


def request_chart_engine_safe_stop(data_root: Path | None = None) -> tuple[bool, str]:
    return _write_request("safe_stop", reason="maintenance_safe_stop", data_root=data_root)


def request_chart_engine_restart(data_root: Path | None = None) -> tuple[bool, str]:
    return _write_request("restart", reason="manual_restart", data_root=data_root)
