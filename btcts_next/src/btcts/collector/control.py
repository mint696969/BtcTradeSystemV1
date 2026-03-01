# path: ./btcts_next/src/btcts/collector/control.py
# desc: collector プロセスの起動/停止/状態確認を司る制御層。UI/Health から呼ばれる正準I/F。

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import ctypes
import ctypes.wintypes

from btcts.core import audit, io, paths
from .status import CollectorStatus, write_status


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
                    # 終了コードが STILL_ACTIVE 以外なら終了済み
                    return False
            finally:
                ctypes.windll.kernel32.CloseHandle(h)

        # OpenProcess / GetExitCodeProcess が使えない場合の最終判定（確実）
        try:
            r = subprocess.run(
                ["tasklist", "/FI", f"PID eq {int(pid)}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            out = (r.stdout or "") + "\n" + (r.stderr or "")
            # tasklist は存在しない場合でもヘッダを返すので、PID文字列が含まれるかで判定
            return str(int(pid)) in out
        except Exception:
            # 最後まで判定不能なら「生きてる扱い」に倒す（誤STOPPEDが一番危険）
            return True

    # POSIX: signal 0 で生存確認
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def _terminate_windows(pid: int) -> bool:
    """WindowsでPIDを確実に終了させる。可能なら taskkill /T /F を優先。"""
    # 1) 最優先：taskkill（プロセスツリーごと）
    taskkill = shutil.which("taskkill")
    if taskkill:
        try:
            r = subprocess.run(
                [taskkill, "/PID", str(int(pid)), "/T", "/F"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # 0: 成功 / 128, 1 など: 対象なし or 失敗（環境により異なる）
            if r.returncode == 0:
                return True
            # 対象が無い系メッセージの場合は「既に死んでいる」扱いに寄せる
            msg = (r.stdout or "") + "\n" + (r.stderr or "")
            if "not found" in msg.lower() or "見つかりません" in msg:
                return True
        except Exception:
            pass

    # 2) フォールバック：TerminateProcess
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
    """現在の collector 状態を返す（PID ベース）。"""
    p = _pid_path()
    if not p.exists():
        return CollectorStatus(ts=time.time(), mode="STOPPED", message="pid not found", items=[])

    try:
        pid = int(p.read_text().strip())
    except Exception:
        return CollectorStatus(ts=time.time(), mode="ERROR", message="invalid pid file", items=[])

    if not _is_alive(pid):
        # stale pid を残さない（UI/healthの混乱源になる）
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
        return CollectorStatus(ts=time.time(), mode="STOPPED", message="process not alive", items=[])

    return CollectorStatus(ts=time.time(), mode="RUNNING", message=f"pid={pid}", items=[])


def start(*, python: Optional[str] = None) -> CollectorStatus:
    """collector をバックグラウンド起動する。二重起動は防止。"""
    try:
        # Start 全体を直列化（連打・同時押しで二重起動や孤児を作らない）
        with io.file_lock(_pid_path(), timeout_sec=20.0):
            st = status()
            if st.mode == "RUNNING":
                return st

            py = python or sys.executable

            # パス固定は事故る（btcts_next 配下に移植しているため）。
            # ここは PYTHONPATH を前提に、モジュール実行で起動する。
            cmd = [py, "-m", "btcts.collector.main"]

            # 子プロセスで btcts を import できるように PYTHONPATH を保証する
            env = os.environ.copy()
            # paths.repo_root() は btcts_next/ を返す（env.py の仕様）
            repo_btcts_next = paths.repo_root()
            src = repo_btcts_next / "src"

            sep = ";" if os.name == "nt" else ":"
            cur = env.get("PYTHONPATH", "")
            parts = [p for p in cur.split(sep) if p] if cur else []
            # btcts を確実に import できる最小セット（src優先）
            if str(src) not in parts:
                parts.insert(0, str(src))
            # btcts_next 自体を PYTHONPATH に入れる必要は通常ないが、相対import事故の保険で後ろに足す
            if str(repo_btcts_next) not in parts:
                parts.append(str(repo_btcts_next))
            env["PYTHONPATH"] = sep.join(parts)

            lp = _log_path()
            lp.parent.mkdir(parents=True, exist_ok=True)

            # collector 側の即死原因を必ず見える化する（DEVNULLは禁止）
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

            # 起動直後に落ちたケースを検出（パスミス・importミス等）
            time.sleep(0.15)
            if proc.poll() is not None:
                st_err = CollectorStatus(
                    ts=time.time(),
                    mode="ERROR",
                    message="collector process exited immediately",
                    last_error=f"exitcode={proc.returncode}",
                    items=[],
                )
                write_status(st_err)
                audit.emit(
                    "collector.start.fail",
                    feature="collector",
                    level="CRIT",
                    payload={"cmd": cmd, "returncode": proc.returncode},
                )
                return st_err

            # ハンドシェイク：collector 本体が回り始めた証拠（rate_state.json 生成）を待つ
            from .status import rate_state_path  # 遅延importで循環回避

            t0 = time.time()
            ok = False
            while time.time() - t0 < 2.0:
                if proc.poll() is not None:
                    break
                if rate_state_path().exists():
                    ok = True
                    break
                time.sleep(0.05)

            if not ok:
                # 起動に失敗しているので、孤児プロセス化を防ぐため止める
                try:
                    proc.terminate()
                except Exception:
                    pass
                t1 = time.time()
                while time.time() - t1 < 1.0:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.05)
                if proc.poll() is None and os.name == "nt":
                    try:
                        _terminate_windows(proc.pid)
                    except Exception:
                        pass

                st_err = CollectorStatus(
                    ts=time.time(),
                    mode="ERROR",
                    message="collector did not produce rate_state.json",
                    last_error=f"pid={proc.pid} poll={proc.poll()} log={_log_path()}",
                    items=[],
                )
                write_status(st_err)
                audit.emit(
                    "collector.start.fail",
                    feature="collector",
                    level="CRIT",
                    payload={"cmd": cmd, "pid": proc.pid, "log": str(_log_path())},
                )
                return st_err

            _pid_path().write_text(str(proc.pid))

            st2 = CollectorStatus(
                ts=time.time(),
                mode="RUNNING",
                message=f"started pid={proc.pid}",
                items=[],
            )
            write_status(st2)

            audit.emit(
                "collector.start",
                feature="collector",
                level="INFO",
                payload={"pid": proc.pid, "cmd": cmd},
            )

            return st2

    except TimeoutError as e:
        # ロック競合時は write_status すると再度 lock を取りに行って落ちる可能性があるため禁止
        st_err = CollectorStatus(
            ts=time.time(),
            mode="ERROR",
            message="lock timeout (collector control)",
            last_error=str(e),
            items=[],
        )
        audit.emit(
            "collector.lock.timeout",
            feature="collector",
            level="WARN",
            payload={"where": "start", "err": str(e)},
        )
        return st_err


def stop(*, timeout_sec: float = 5.0) -> CollectorStatus:
    """collector を停止する（SIGTERM → SIGKILL）。"""
    try:
        # Stop 全体を直列化（連打・同時押しで pidfile/状態を破壊しない）
        with io.file_lock(_pid_path(), timeout_sec=max(20.0, timeout_sec + 10.0)):
            p = _pid_path()
            if not p.exists():
                st = CollectorStatus(ts=time.time(), mode="STOPPED", message="pid not found", items=[])
                write_status(st)
                return st

            try:
                pid = int(p.read_text().strip())
            except Exception:
                st = CollectorStatus(ts=time.time(), mode="ERROR", message="invalid pid file", items=[])
                write_status(st)
                return st

            if os.name == "nt":
                ok = _terminate_windows(pid)
                t0 = time.time()
                while time.time() - t0 < timeout_sec:
                    if not _is_alive(pid):
                        break
                    time.sleep(0.1)

                if _is_alive(pid):
                    # 死んでないのに pidfile を消すのは禁止
                    st = CollectorStatus(
                        ts=time.time(),
                        mode="ERROR",
                        message=f"failed to stop pid={pid}",
                        last_error=f"terminate_ok={ok} (still alive after {timeout_sec:.1f}s)",
                        items=[],
                    )
                    write_status(st)
                    audit.emit(
                        "collector.stop.fail",
                        feature="collector",
                        level="CRIT",
                        payload={"pid": pid, "terminate_ok": ok},
                    )
                    return st

            p.unlink(missing_ok=True)

            st2 = CollectorStatus(ts=time.time(), mode="STOPPED", message=f"stopped pid={pid}", items=[])
            write_status(st2)

            audit.emit(
                "collector.stop",
                feature="collector",
                level="INFO",
                payload={"pid": pid},
            )

            return st2
    except TimeoutError as e:
        # ロック競合時は write_status すると再度 lock を取りに行って落ちる可能性があるため禁止
        st_err = CollectorStatus(
            ts=time.time(),
            mode="ERROR",
            message="lock timeout (collector control)",
            last_error=str(e),
            items=[],
        )
        audit.emit(
            "collector.lock.timeout",
            feature="collector",
            level="WARN",
            payload={"where": "stop", "err": str(e)},
        )
        return st_err
