# path: ./btcts_next/src/btcts/prediction/market_regime/operator_ui_runtime.py
# desc: Operator UI runtime helper for manual market-regime preflight/run-once controls. No scheduler, daemon loop, broker, AutoTrade, or UI render-path inference.

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from btcts.collector_vnext.lock import is_pid_alive
from btcts.core import paths as core_paths

from .tools.write_latest import preflight_market_regime_latest_artifacts_once, write_market_regime_latest_artifacts_once

MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION = "prediction.market_regime.operator_ui_runtime.2026_07_08.v1"
MARKET_REGIME_OPERATOR_UI_STATE_DIRNAME = "market_regime_inference"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_hot_root(root: Path) -> Path:
    candidate = Path(root)
    if candidate.name.lower() == "data":
        return candidate.parent
    return candidate


def market_regime_hot_root() -> Path:
    hot_root = str(os.environ.get("BTCTS_HOT_ROOT") or "").strip()
    if hot_root:
        return _normalize_hot_root(Path(hot_root))
    data_root = str(os.environ.get("BTCTS_DATA_ROOT") or os.environ.get("BTC_TS_DATA_DIR") or "").strip()
    if data_root:
        return _normalize_hot_root(Path(data_root))
    return _normalize_hot_root(core_paths.data_dir(ensure=False))


def market_regime_operator_ui_paths(hot_root: Path | None = None) -> dict[str, Path]:
    root = _normalize_hot_root(hot_root or market_regime_hot_root())
    state_dir = root / "state" / MARKET_REGIME_OPERATOR_UI_STATE_DIRNAME
    return {
        "hot_root": root,
        "state_dir": state_dir,
        "status": state_dir / "status.json",
        "latest_cards": root / "prediction" / "market_regime" / "latest_cards.json",
        "latest_read_model": root / "prediction" / "market_regime" / "latest_read_model.json",
        "calibration_latest_read_model": root / "prediction" / "market_regime" / "calibration" / "latest_read_model.json",
        "trace_ledger_dir": root / "prediction" / "market_regime" / "ledgers",
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")




def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _runtime_python() -> str:
    repo_root = _repo_root()
    override = str(os.environ.get("BTCTS_RUNTIME_PYTHON") or "").strip()
    if override and Path(override).exists():
        return override
    candidates: list[Path] = []
    if os.name == "nt":
        candidates.extend([repo_root / ".venv" / "Scripts" / "pythonw.exe", repo_root / ".venv" / "Scripts" / "python.exe"])
    else:
        candidates.append(repo_root / ".venv" / "bin" / "python")
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


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


def _child_env(hot_root: Path) -> dict[str, str]:
    repo_root = _repo_root()
    env = dict(os.environ)
    repo_src = str(repo_root / "btcts_next" / "src")
    inherited_pythonpath = str(env.get("PYTHONPATH") or "")
    inherited_parts = [part for part in inherited_pythonpath.split(os.pathsep) if part and part != repo_src]
    env["PYTHONPATH"] = os.pathsep.join([repo_src, *inherited_parts])
    env["BTCTS_HOT_ROOT"] = str(hot_root)
    env["BTCTS_DATA_ROOT"] = str(hot_root / "data")
    env["BTC_TS_DATA_DIR"] = str(hot_root / "data")
    return env


def _pid_active(value: object) -> bool:
    try:
        return bool(is_pid_alive(value))
    except Exception:
        return False


def market_regime_producer_loop_runtime_paths(hot_root: Path | None = None) -> dict[str, Path]:
    base = market_regime_operator_ui_paths(hot_root)
    state_dir = base["state_dir"]
    return {
        **base,
        "loop_control": state_dir / "control.json",
        "loop_status": state_dir / "producer_loop_status.json",
        "loop_heartbeat": state_dir / "producer_loop_heartbeat.json",
        "loop_lock": state_dir / "producer_loop.lock.json",
        "loop_stdout": state_dir / "producer_loop.stdout.log",
        "loop_stderr": state_dir / "producer_loop.stderr.log",
    }


def market_regime_producer_loop_runtime_snapshot(hot_root: Path | None = None) -> dict[str, Any]:
    root = _normalize_hot_root(hot_root or market_regime_hot_root())
    paths = market_regime_producer_loop_runtime_paths(root)
    status = _read_json(paths["loop_status"])
    heartbeat = _read_json(paths["loop_heartbeat"])
    control = _read_json(paths["loop_control"])
    lock = _read_json(paths["loop_lock"])
    pid = lock.get("pid") or status.get("runtime_pid")
    active = _pid_active(pid)
    mode = str(status.get("mode") or ("RUNNING" if active else "STOPPED"))
    return {
        "ok": True,
        "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
        "hot_root": str(root),
        "state_dir": str(paths["state_dir"]),
        "loop_control_path": str(paths["loop_control"]),
        "loop_status_path": str(paths["loop_status"]),
        "loop_heartbeat_path": str(paths["loop_heartbeat"]),
        "loop_lock_path": str(paths["loop_lock"]),
        "mode": mode,
        "active": active,
        "runtime_pid": pid,
        "pending_action": str(control.get("action") or ""),
        "iteration": int(status.get("iteration") or heartbeat.get("iteration") or 0),
        "writes": int(status.get("writes") or heartbeat.get("writes") or 0),
        "blocked": int(status.get("blocked") or heartbeat.get("blocked") or 0),
        "latest_run_id": str(status.get("latest_run_id") or heartbeat.get("latest_run_id") or ""),
        "last_error": str(status.get("last_error") or heartbeat.get("last_error") or ""),
        "last_heartbeat_ts": heartbeat.get("ts") or status.get("ts") or "",
        "stdout_path": str(paths["loop_stdout"]),
        "stderr_path": str(paths["loop_stderr"]),
        "status": status,
        "heartbeat": heartbeat,
        "control": control,
        "lock": lock,
        "preflight_required": True,
        "scheduler_enabled": False,
        "producer_loop_enabled": active,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }


def _clear_stale_market_regime_loop_control(paths: Mapping[str, Path]) -> bool:
    control_path = paths.get("loop_control")
    if control_path is None or not control_path.exists():
        return False
    try:
        payload = _read_json(control_path)
        action = str(payload.get("action") or "").strip().lower()
        if action in {"safe_stop", "stop", "restart"}:
            control_path.unlink(missing_ok=True)
            return True
    except Exception:
        try:
            control_path.unlink(missing_ok=True)
            return True
        except Exception:
            return False
    return False


def start_market_regime_producer_loop_detached(hot_root: Path | None = None, *, interval_sec: int = 30) -> tuple[bool, str, bool]:
    root = _normalize_hot_root(hot_root or market_regime_hot_root())
    snapshot = market_regime_producer_loop_runtime_snapshot(root)
    if snapshot.get("active"):
        return True, f"market_regime producer loop already running pid={snapshot.get('runtime_pid')}", True
    paths = market_regime_producer_loop_runtime_paths(root)
    paths["state_dir"].mkdir(parents=True, exist_ok=True)
    cleared_stale_control = _clear_stale_market_regime_loop_control(paths)
    command_args = [
        _runtime_python(),
        "-m",
        "btcts.prediction.market_regime.producer_loop",
        "--hot-root",
        str(root),
        "--interval-sec",
        str(max(5, int(interval_sec))),
        "--max-iterations",
        "0",
        "--once-loop",
    ]
    with paths["loop_stdout"].open("ab") as stdout_handle, paths["loop_stderr"].open("ab") as stderr_handle:
        proc = subprocess.Popen(
            command_args,
            cwd=str(_repo_root()),
            env=_child_env(root),
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=_windows_creationflags(),
            startupinfo=_windows_startupinfo(),
            close_fds=True,
        )
    lock = {
        "ok": True,
        "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
        "pid": int(proc.pid),
        "started_at": _now_iso(),
        "requested_by": "operator_ui",
        "hot_root": str(root),
        "command_args": command_args,
        "stdout_path": str(paths["loop_stdout"]),
        "stderr_path": str(paths["loop_stderr"]),
        "cleared_stale_control_on_start": bool(cleared_stale_control),
        "preflight_required": True,
        "scheduler_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }
    _write_json(paths["loop_lock"], lock)
    _write_json(
        paths["loop_status"],
        {
            "ok": True,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "STARTING",
            "active": True,
            "runtime_pid": int(proc.pid),
            "ts": _now_iso(),
            "hot_root": str(root),
            "interval_sec": max(5, int(interval_sec)),
            "cleared_stale_control_on_start": bool(cleared_stale_control),
            "preflight_required": True,
            "scheduler_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        },
    )
    return True, f"market_regime producer loop start requested pid={int(proc.pid)}", False


def request_market_regime_producer_loop_safe_stop(hot_root: Path | None = None) -> tuple[bool, str]:
    from .producer_loop import write_market_regime_producer_control_request

    root = _normalize_hot_root(hot_root or market_regime_hot_root())
    result = write_market_regime_producer_control_request(root, action="safe_stop", reason="operator_ui_safe_stop")
    return bool(result.get("ok")), f"market_regime producer loop safe_stop request written action={result.get('action')}"


def request_market_regime_producer_loop_restart(hot_root: Path | None = None, *, interval_sec: int = 30) -> tuple[bool, str]:
    from .producer_loop import write_market_regime_producer_control_request

    root = _normalize_hot_root(hot_root or market_regime_hot_root())
    snapshot = market_regime_producer_loop_runtime_snapshot(root)
    if snapshot.get("active"):
        result = write_market_regime_producer_control_request(root, action="restart", reason="operator_ui_restart")
        return bool(result.get("ok")), f"market_regime producer loop restart request written action={result.get('action')}"
    ok, msg, _already = start_market_regime_producer_loop_detached(root, interval_sec=interval_sec)
    return ok, msg


def _calibration_bucket_counts(bucket: Mapping[str, Any]) -> dict[str, int]:
    counts = bucket.get("counts") if isinstance(bucket.get("counts"), Mapping) else {}
    return {
        "hit": int(counts.get("hit") or 0),
        "partial": int(counts.get("partial") or 0),
        "miss": int(counts.get("miss") or 0),
        "unknown": int(counts.get("unknown") or 0),
        "invalidated": int(counts.get("invalidated") or 0),
    }


def _calibration_score(bucket: Mapping[str, Any]) -> float | None:
    value = bucket.get("calibration_score")
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except Exception:
        return None

def market_regime_operator_ui_snapshot(hot_root: Path | None = None) -> dict[str, Any]:
    paths = market_regime_operator_ui_paths(hot_root)
    status = _read_json(paths["status"])
    latest_cards = _read_json(paths["latest_cards"])
    calibration_read_model = _read_json(paths["calibration_latest_read_model"])
    calibration_primary = calibration_read_model.get("primary") if isinstance(calibration_read_model.get("primary"), Mapping) else {}
    calibration_reference = calibration_read_model.get("latest_cards_current_reference") if isinstance(calibration_read_model.get("latest_cards_current_reference"), Mapping) else {}
    first_card = {}
    cards = latest_cards.get("cards") if isinstance(latest_cards.get("cards"), list) else []
    if cards and isinstance(cards[0], dict):
        first_card = dict(cards[0])
    return {
        "ok": True,
        "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
        "mode": str(status.get("mode") or "READY"),
        "hot_root": str(paths["hot_root"]),
        "state_dir": str(paths["state_dir"]),
        "status_path": str(paths["status"]),
        "latest_cards_path": str(paths["latest_cards"]),
        "latest_cards_available": bool(paths["latest_cards"].exists()),
        "calibration_latest_read_model_path": str(paths["calibration_latest_read_model"]),
        "calibration_read_model_available": bool(paths["calibration_latest_read_model"].exists()),
        "calibration_primary_observation_source": str(calibration_read_model.get("primary_observation_source") or ""),
        "calibration_primary_score": _calibration_score(calibration_primary),
        "calibration_primary_known_total": int(calibration_primary.get("known_total") or 0),
        "calibration_primary_counts": _calibration_bucket_counts(calibration_primary),
        "calibration_reference_score": _calibration_score(calibration_reference),
        "calibration_read_model": calibration_read_model,
        "latest_run_id": latest_cards.get("run_id") or status.get("latest_run_id") or "",
        "latest_generated_at": latest_cards.get("generated_at") or status.get("generated_at") or "",
        "card_count": int(latest_cards.get("horizon_count") or len(cards) or 0),
        "first_card_label": str(first_card.get("regime_label") or first_card.get("regime_code") or ""),
        "first_card_confidence": first_card.get("confidence_percent"),
        "first_card_freshness": str(first_card.get("freshness_badge") or ""),
        "first_card_calibration_state": str(
            (first_card.get("detail") or {}).get("calibration_state")
            if isinstance(first_card.get("detail"), Mapping)
            else ""
        ),
        "first_card_calibrated_probability_claim": bool(
            (first_card.get("detail") or {}).get("calibrated_probability_claim")
            if isinstance(first_card.get("detail"), Mapping)
            else False
        ),
        "first_card_calibrated_reliability_percent": (
            (first_card.get("detail") or {}).get("calibrated_reliability_percent")
            if isinstance(first_card.get("detail"), Mapping)
            else None
        ),
        "first_card_calibration_display_confidence_percent": (
            (first_card.get("detail") or {}).get("calibration_display_confidence_percent")
            if isinstance(first_card.get("detail"), Mapping)
            else None
        ),
        "last_preflight_can_write": bool(status.get("can_write_live_once")),
        "last_preflight_missing_sources": list(status.get("missing_sources") or []),
        "last_preflight_warnings": list(status.get("warnings") or []),
        "last_action": status.get("last_action") or "",
        "last_error": status.get("last_error") or "",
        "status": status,
        "active": False,
        "preflight_only_supported": True,
        "run_once_supported": True,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }


def request_market_regime_preflight(hot_root: Path | None = None) -> tuple[bool, str, dict[str, Any]]:
    paths = market_regime_operator_ui_paths(hot_root)
    try:
        result = preflight_market_regime_latest_artifacts_once(hot_root=paths["hot_root"])
        status = {
            "ok": True,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "PREFLIGHT_OK" if result.get("can_write_live_once") else "PREFLIGHT_BLOCKED",
            "last_action": "preflight",
            "ts": _now_iso(),
            "hot_root": str(paths["hot_root"]),
            "can_write_live_once": bool(result.get("can_write_live_once")),
            "source_snapshot_ok": bool(result.get("source_snapshot_ok")),
            "missing_sources": list(result.get("missing_sources") or []),
            "warnings": list(result.get("warnings") or []),
            "card_count": int(result.get("card_count") or 0),
            "latest_cards_validation": dict(result.get("latest_cards_validation") or {}),
            "expected_artifacts": dict(result.get("expected_artifacts") or {}),
            "last_error": "",
            "preflight_only": True,
            "would_write": False,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        }
        _write_json(paths["status"], status)
        return True, f"market_regime preflight can_write_live_once={status['can_write_live_once']}", status
    except Exception as exc:
        status = {
            "ok": False,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "PREFLIGHT_ERROR",
            "last_action": "preflight",
            "ts": _now_iso(),
            "hot_root": str(paths["hot_root"]),
            "last_error": str(exc),
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        }
        _write_json(paths["status"], status)
        return False, f"market_regime preflight failed: {exc}", status


def request_market_regime_run_once(hot_root: Path | None = None) -> tuple[bool, str, dict[str, Any]]:
    paths = market_regime_operator_ui_paths(hot_root)
    preflight_ok, preflight_msg, preflight_status = request_market_regime_preflight(paths["hot_root"])
    if not preflight_ok or not preflight_status.get("can_write_live_once"):
        status = dict(preflight_status)
        status.update({
            "mode": "RUN_ONCE_BLOCKED",
            "last_action": "run_once",
            "run_once_blocked_reason": preflight_msg,
            "would_write": False,
            "ts": _now_iso(),
        })
        _write_json(paths["status"], status)
        return False, f"market_regime run_once blocked: {preflight_msg}", status
    try:
        result = write_market_regime_latest_artifacts_once(hot_root=paths["hot_root"])
        status = {
            "ok": True,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "RUN_ONCE_OK",
            "last_action": "run_once",
            "ts": _now_iso(),
            "hot_root": str(paths["hot_root"]),
            "latest_run_id": str(result.get("run_id") or ""),
            "generated_at": str(result.get("generated_at") or ""),
            "source_snapshot_ok": bool(result.get("source_snapshot_ok")),
            "card_count": int(result.get("card_count") or 0),
            "latest_cards_validation": dict(result.get("latest_cards_validation") or {}),
            "trace_ledger_append": dict(result.get("trace_ledger_append") or {}),
            "written": list(result.get("written") or []),
            "last_error": "",
            "would_write": True,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        }
        _write_json(paths["status"], status)
        return True, f"market_regime run_once ok run_id={status['latest_run_id']}", status
    except Exception as exc:
        status = {
            "ok": False,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "RUN_ONCE_ERROR",
            "last_action": "run_once",
            "ts": _now_iso(),
            "hot_root": str(paths["hot_root"]),
            "last_error": str(exc),
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        }
        _write_json(paths["status"], status)
        return False, f"market_regime run_once failed: {exc}", status
