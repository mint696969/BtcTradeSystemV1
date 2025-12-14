# path: ./btc_trade_system/features/collector/collector_control.py
# desc: Collector プロセスの起動・停止と状態確認（開発機向けの簡易制御モジュール）

from __future__ import annotations

import os
import subprocess
import sys
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal

from btc_trade_system.features.audit_dev import writer as W

# Windows 用のコンソール抑制フラグ
if os.name == "nt":
    _CREATE_NO_WINDOW = 0x08000000  # コンソール非表示
    _DETACHED_PROCESS = 0x00000008  # 親コンソールから切り離し
else:
    _CREATE_NO_WINDOW = 0
    _DETACHED_PROCESS = 0


StateLiteral = Literal["RUNNING", "STOPPED", "UNKNOWN"]


@dataclass
class CollectorState:
    """collector の簡易状態"""
    state: StateLiteral
    pid: Optional[int] = None
    detail: str = ""


# DATA ルートと pid ファイルの場所（開発環境前提）
_DATA_ROOT = Path(os.environ.get("BTC_TS_DATA_DIR", r"D:\BtcTS_V1\data"))
_PID_PATH = _DATA_ROOT / "collector" / "collector_dev.pid"


def _read_pid() -> Optional[int]:
    """pid ファイルから PID を読み取る（無ければ None）。"""
    try:
        text = _PID_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _write_pid(pid: int) -> None:
    _PID_PATH.parent.mkdir(parents=True, exist_ok=True)
    _PID_PATH.write_text(str(pid), encoding="utf-8")


def _remove_pid() -> None:
    try:
        _PID_PATH.unlink()
    except FileNotFoundError:
        pass


def _is_alive(pid: int) -> bool:
    """PID が生きているかの簡易判定。失敗したら False 扱い。"""
    try:
        # Windows / Unix ともに、0 シグナルは「存在確認」用途
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def get_state() -> CollectorState:
    """
    collector の起動状態を返す。

    - pid ファイルが無ければ STOPPED
    - pid が存在し、プロセスが生きていれば RUNNING
    - pid はあるがプロセスが死んでいれば STOPPED（pid ファイルは掃除）
    """
    pid = _read_pid()
    if pid is None:
        return CollectorState(state="STOPPED", pid=None, detail="pid file not found")

    if _is_alive(pid):
        return CollectorState(state="RUNNING", pid=pid, detail="process alive")

    # stale pid
    _remove_pid()
    return CollectorState(state="STOPPED", pid=None, detail="stale pid removed")


def start_collector() -> CollectorState:
    """
    collector を起動する。

    - すでに RUNNING の場合は、そのまま状態だけ返す。
    - 新規起動時は python -m btc_trade_system.features.collector.collector_main を非同期起動。
    """
    current = get_state()
    if current.state == "RUNNING":
        return current

    cmd = [
        sys.executable,
        "-m",
        "btc_trade_system.features.collector.collector_main",
    ]

    popen_kwargs: dict = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
    }

    # Windows では親プロセス終了と切り離しておく（ダッシュボードを閉じても残す）
    if os.name == "nt":
        creationflags = 0
        if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            creationflags |= subprocess.CREATE_NEW_PROCESS_GROUP
        if hasattr(subprocess, "DETACHED_PROCESS"):
            creationflags |= subprocess.DETACHED_PROCESS
        if creationflags:
            popen_kwargs["creationflags"] = creationflags

    proc = subprocess.Popen(cmd, **popen_kwargs)
    _write_pid(proc.pid)

    return CollectorState(state="RUNNING", pid=proc.pid, detail="started by ui")


def stop_collector() -> CollectorState:
    """
    collector を停止する。

    - pid ファイルが無い場合は STOPPED を返す。
    - pid が存在する場合は OS に応じた方法で kill し、pid ファイルを削除。
      （実際の終了まで多少ラグが出る可能性はある）
    """
    pid = _read_pid()
    if pid is None:
        return CollectorState(state="STOPPED", pid=None, detail="no pid to kill")

    detail: str

    if os.name == "nt":
        # Windows は taskkill を使う方が安定する
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                detail = "taskkill /PID succeeded"
            else:
                detail = f"taskkill failed (code={result.returncode}): {result.stderr.strip()}"
        except Exception as e:  # noqa: BLE001
            detail = f"taskkill error: {e!r}"
    else:
        # Unix 系は従来どおり SIGTERM
        try:
            os.kill(pid, signal.SIGTERM)
            detail = "sent SIGTERM"
        except OSError as e:
            detail = f"kill failed: {e!r}"

    _remove_pid()
    return CollectorState(state="STOPPED", pid=None, detail=detail)
