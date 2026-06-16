# path: ./btcts_next/src/btcts/collector/control.py
# desc: collector プロセスの起動/停止/状態確認を司る制御層。UI/Health から呼ばれる正準I/F。

from __future__ import annotations

import ctypes
import ctypes.wintypes
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from btcts.core import audit, io, paths
from .status import (
    CollectorControlCommand,
    CollectorStatus,
    read_control,
    write_control,
    write_status,
)


@dataclass
class CollectorProc:
    pid: int
    cmd: list[str]
    started_ts: float


PID_FILE = "collector.pid"


def _pid_path() -> Path:
    return paths.logs_dir() / PID_FILE


def _log_path() -> Path:
    return paths.logs_dir() / "collector.log"


def _now() -> float:
    return time.time()


def _iso_utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _runtime_mode() -> str:
    return (os.environ.get("BTC_TS_MODE", "") or "NORMAL").strip().upper()


def _new_request_id() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + f"_{int((_now() % 1.0) * 1000):03d}"


def _read_pid() -> Optional[int]:
    p = _pid_path()
    if not p.exists():
        return None
    try:
        return int(p.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def _safe_last_control() -> Dict[str, Any]:
    try:
        return read_control(default={}) or {}
    except Exception:
        return {}


def _status_with_control(
    *,
    mode: str,
    message: str,
    last_error: str = "",
    pid: Optional[int] = None,
) -> CollectorStatus:
    ctl = _safe_last_control()
    actual_mode = _runtime_mode()

    control_info = {}
    if ctl:
        control_info = {
            "last_request_id": ctl.get("request_id", ""),
            "desired_state": ctl.get("desired_state", ""),
            "desired_mode": ctl.get("desired_mode", ""),
            "requested_at": ctl.get("requested_at", ""),
            "requested_by": ctl.get("requested_by", ""),
            "reason": ctl.get("reason", ""),
        }

    return CollectorStatus(
        ts=_now(),
        mode=mode,
        message=message,
        last_error=last_error,
        items=[],
        actual_state=mode,
        actual_mode=actual_mode,
        pid=pid,
        last_heartbeat=_iso_utc(_now()),
        control=control_info,
    )


def _emit_control_applied(action: str, cmd: CollectorControlCommand, *, pid: Optional[int] = None) -> None:
    audit.emit(
        "control.applied",
        feature="collector",
        level="INFO",
        payload={
            "action": action,
            "request_id": cmd.request_id,
            "desired_state": cmd.desired_state,
            "desired_mode": cmd.desired_mode,
            "requested_by": cmd.requested_by,
            "reason": cmd.reason,
            "pid": pid,
        },
    )


def _emit_control_rejected(action: str, cmd: CollectorControlCommand, reason: str) -> None:
    audit.emit(
        "control.rejected",
        feature="collector",
        level="WARN",
        payload={
            "action": action,
            "request_id": cmd.request_id,
            "desired_state": cmd.desired_state,
            "desired_mode": cmd.desired_mode,
            "requested_by": cmd.requested_by,
            "reason": cmd.reason,
            "reject_reason": reason,
        },
    )


def _is_alive(pid: int) -> bool:
    # Windows: OpenProcess が失敗する環境があるため、tasklist で最終判定する
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259

        h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if h:
            try:
                code = ctypes.wintypes.DWORD()
                ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
                if ok:
                    if int(code.value) == STILL_ACTIVE:
                        return True
                    return False
            finally:
                ctypes.windll.kernel32.CloseHandle(h)

        try:
            r = subprocess.run(
                ["tasklist", "/FI", f"PID eq {int(pid)}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            out = (r.stdout or "") + "\n" + (r.stderr or "")
            return str(int(pid)) in out
        except Exception:
            # 判定不能なら生存扱いに倒す
            return True

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _terminate_windows(pid: int) -> bool:
    """WindowsでPIDを確実に終了させる。可能なら taskkill /T /F を優先。"""
    taskkill = shutil.which("taskkill")
    if taskkill:
        try:
            r = subprocess.run(
                [taskkill, "/PID", str(int(pid)), "/T", "/F"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if r.returncode == 0:
                return True
            msg = (r.stdout or "") + "\n" + (r.stderr or "")
            if "not found" in msg.lower() or "見つかりません" in msg:
                return True
        except Exception:
            pass

    PROCESS_TERMINATE = 0x0001
    h = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, int(pid))
    if not h:
        return False
    try:
        ok = ctypes.windll.kernel32.TerminateProcess(h, 1)
        return bool(ok)
    finally:
        ctypes.windll.kernel32.CloseHandle(h)


# -----------------------------------------------------------------------------
# public API
# -----------------------------------------------------------------------------


def status() -> CollectorStatus:
    """現在の collector 状態を返す（PID ベース + control.json 文脈付き）。"""
    p = _pid_path()
    pid = _read_pid()

    if pid is None:
        if p.exists():
            return _status_with_control(mode="ERROR", message="invalid pid file", last_error="invalid pid")
        return _status_with_control(mode="STOPPED", message="pid not found")

    if not _is_alive(pid):
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
        return _status_with_control(mode="STOPPED", message="process not alive", pid=pid)

    return _status_with_control(mode="RUNNING", message=f"pid={pid}", pid=pid)


def start(
    *,
    python: Optional[str] = None,
    desired_mode: Optional[str] = None,
    requested_by: str = "operator",
    reason: str = "",
) -> CollectorStatus:
    """collector をバックグラウンド起動する。二重起動は防止。"""
    req_mode = (desired_mode or _runtime_mode() or "NORMAL").strip().upper()

    cmd_req = CollectorControlCommand(
        request_id=_new_request_id(),
        desired_state="running",
        desired_mode=req_mode,
        requested_by=requested_by,
        reason=reason or "start collector",
    )
    write_control(cmd_req)

    try:
        # Start 全体を直列化（連打・同時押しで二重起動や孤児を作らない）
        with io.file_lock(_pid_path(), timeout_sec=20.0):
            st = status()
            if st.mode == "RUNNING":
                _emit_control_rejected("start", cmd_req, "already_running")
                return st

            py = python or sys.executable
            cmd = [py, "-m", "btcts.collector.main"]

            env = os.environ.copy()
            env["BTC_TS_MODE"] = req_mode
            repo_btcts_next = paths.repo_root()
            src = repo_btcts_next / "src"

            sep = ";" if os.name == "nt" else ":"
            cur = env.get("PYTHONPATH", "")
            parts = [p for p in cur.split(sep) if p] if cur else []
            if str(src) not in parts:
                parts.insert(0, str(src))
            if str(repo_btcts_next) not in parts:
                parts.append(str(repo_btcts_next))
            env["PYTHONPATH"] = sep.join(parts)

            lp = _log_path()
            lp.parent.mkdir(parents=True, exist_ok=True)

            logf = open(lp, "a", encoding="utf-8", errors="replace")

            proc = subprocess.Popen(
                cmd,
                cwd=str(paths.repo_root()),
                stdout=logf,
                stderr=logf,
                env=env,
                start_new_session=True,
            )
            try:
                logf.close()
            except Exception:
                pass

            # 起動直後に落ちたケースを検出
            time.sleep(0.15)
            if proc.poll() is not None:
                st_err = _status_with_control(
                    mode="ERROR",
                    message="collector process exited immediately",
                    last_error=f"exitcode={proc.returncode}",
                    pid=proc.pid,
                )
                write_status(st_err)
                audit.emit(
                    "collector.start.fail",
                    feature="collector",
                    level="CRIT",
                    payload={"cmd": cmd, "returncode": proc.returncode},
                )
                _emit_control_rejected("start", cmd_req, "exited_immediately")
                return st_err

            # ハンドシェイク：collector 本体が回り始めた証拠（rate_state.json の更新）を待つ
            from .status import rate_state_path  # 遅延importで循環回避

            _rsp = rate_state_path()
            _prev_mtime = _rsp.stat().st_mtime if _rsp.exists() else 0.0

            t0 = _now()
            ok = False
            while _now() - t0 < 2.0:
                if proc.poll() is not None:
                    break

                if _rsp.exists():
                    try:
                        _cur_mtime = _rsp.stat().st_mtime
                    except Exception:
                        _cur_mtime = 0.0

                    if _cur_mtime > _prev_mtime:
                        ok = True
                        break

                time.sleep(0.05)

            if not ok:
                try:
                    proc.terminate()
                except Exception:
                    pass
                t1 = _now()
                while _now() - t1 < 1.0:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.05)
                if proc.poll() is None and os.name == "nt":
                    try:
                        _terminate_windows(proc.pid)
                    except Exception:
                        pass

                st_err = _status_with_control(
                    mode="ERROR",
                    message="collector did not produce rate_state.json",
                    last_error=f"pid={proc.pid} poll={proc.poll()} log={_log_path()}",
                    pid=proc.pid,
                )
                write_status(st_err)
                audit.emit(
                    "collector.start.fail",
                    feature="collector",
                    level="CRIT",
                    payload={"cmd": cmd, "pid": proc.pid, "log": str(_log_path())},
                )
                _emit_control_rejected("start", cmd_req, "no_rate_state")
                return st_err

            _pid_path().write_text(str(proc.pid), encoding="utf-8")

            st2 = _status_with_control(mode="RUNNING", message=f"started pid={proc.pid}", pid=proc.pid)
            write_status(st2)

            audit.emit(
                "collector.start",
                feature="collector",
                level="INFO",
                payload={"pid": proc.pid, "cmd": cmd},
            )
            _emit_control_applied("start", cmd_req, pid=proc.pid)
            return st2

    except TimeoutError as e:
        st_err = _status_with_control(
            mode="ERROR",
            message="lock timeout (collector control)",
            last_error=str(e),
        )
        audit.emit(
            "collector.lock.timeout",
            feature="collector",
            level="WARN",
            payload={"where": "start", "err": str(e)},
        )
        _emit_control_rejected("start", cmd_req, "lock_timeout")
        return st_err


def stop(
    *,
    timeout_sec: float = 5.0,
    requested_by: str = "operator",
    reason: str = "",
) -> CollectorStatus:
    """collector を停止する（SIGTERM → SIGKILL）。"""
    cmd_req = CollectorControlCommand(
        request_id=_new_request_id(),
        desired_state="stopped",
        desired_mode=_runtime_mode(),
        requested_by=requested_by,
        reason=reason or "stop collector",
    )
    write_control(cmd_req)

    try:
        with io.file_lock(_pid_path(), timeout_sec=max(20.0, timeout_sec + 10.0)):
            p = _pid_path()
            pid = _read_pid()

            if pid is None:
                if p.exists():
                    st = _status_with_control(mode="ERROR", message="invalid pid file", last_error="invalid pid")
                    write_status(st)
                    _emit_control_rejected("stop", cmd_req, "invalid_pid_file")
                    return st

                st = _status_with_control(mode="STOPPED", message="pid not found")
                write_status(st)
                _emit_control_rejected("stop", cmd_req, "already_stopped")
                return st

            if os.name == "nt":
                ok = _terminate_windows(pid)
                t0 = _now()
                while _now() - t0 < timeout_sec:
                    if not _is_alive(pid):
                        break
                    time.sleep(0.1)

                if _is_alive(pid):
                    st = _status_with_control(
                        mode="ERROR",
                        message=f"failed to stop pid={pid}",
                        last_error=f"terminate_ok={ok} (still alive after {timeout_sec:.1f}s)",
                        pid=pid,
                    )
                    write_status(st)
                    audit.emit(
                        "collector.stop.fail",
                        feature="collector",
                        level="CRIT",
                        payload={"pid": pid, "terminate_ok": ok},
                    )
                    _emit_control_rejected("stop", cmd_req, "still_alive_after_timeout")
                    return st

            p.unlink(missing_ok=True)

            st2 = _status_with_control(mode="STOPPED", message=f"stopped pid={pid}", pid=pid)
            write_status(st2)

            audit.emit(
                "collector.stop",
                feature="collector",
                level="INFO",
                payload={"pid": pid},
            )
            _emit_control_applied("stop", cmd_req, pid=pid)
            return st2

    except TimeoutError as e:
        st_err = _status_with_control(
            mode="ERROR",
            message="lock timeout (collector control)",
            last_error=str(e),
        )
        audit.emit(
            "collector.lock.timeout",
            feature="collector",
            level="WARN",
            payload={"where": "stop", "err": str(e)},
        )
        _emit_control_rejected("stop", cmd_req, "lock_timeout")
        return st_err
    
def restart(
    *,
    timeout_sec: float = 5.0,
    python: Optional[str] = None,
    desired_mode: Optional[str] = None,
    requested_by: str = "operator",
    reason: str = "",
) -> CollectorStatus:
    """collector を再起動する。"""
    stop(
        timeout_sec=timeout_sec,
        requested_by=requested_by,
        reason=reason or "restart collector (stop phase)",
    )
    return start(
        python=python,
        desired_mode=desired_mode,
        requested_by=requested_by,
        reason=reason or "restart collector (start phase)",
    )    