# path: ./btcts_next/src/btcts/core/audit.py
# desc: 監査ログ（audit.jsonl）への追記I/F。NORMAL/DEBUG/BOOST を運用の正とし、OFF は互換として扱う。I/O は core/io.py に一本化する。

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path

from . import env
from . import io
from . import paths


# ---- public model -------------------------------------------------------------


@dataclass(frozen=True)
class AuditConfig:
    mode: str  # NORMAL / DEBUG / BOOST（OFFは互換）
    path: Path  # audit.jsonl のフルパス


def get_config() -> AuditConfig:
    """現在の監査設定（mode と出力先）を返す。"""
    p = paths.logs_dir() / "audit.jsonl"
    return AuditConfig(mode=env.mode(), path=p)


# ---- internals ----------------------------------------------------------------


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _base_payload() -> Dict[str, Any]:
    return {
        "pid": os.getpid(),
        "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "",
    }


def _should_emit(mode: str, level: str) -> bool:
    m = (mode or "NORMAL").upper()
    lv = (level or "INFO").upper()

    # 互換のため残すが、Phase2方針では基本使わない
    if m == "OFF":
        return False

    rank = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}.get(lv, 20)

    if m == "NORMAL":
        # 常時運用：DEBUGは捨てる
        return rank >= 20

    # DEBUG / BOOST：全レベル出力（BOOSTの“重い観測”は別途イベント側で増やす）
    return True

# ---- public API ---------------------------------------------------------------


def emit(
    event: str,
    *,
    level: str = "INFO",
    feature: str = "",
    payload: Optional[Dict[str, Any]] = None,
    actor: str = "",
    site: str = "",
    trace_id: Optional[str] = None,
) -> None:
    """監査ログへ1行追記する。

    - 出力先: <logs_dir>/audit.jsonl
    - 形式: 1行1JSON（UTF-8）
    """

    cfg = get_config()
    if not _should_emit(cfg.mode, level):
        return

    row: Dict[str, Any] = {
        "ts": _utc_iso(),
        "mode": cfg.mode,
        "event": event,
        "feature": feature,
        "level": (level or "INFO").upper(),
        "actor": actor,
        "site": site,
        "trace_id": trace_id or uuid.uuid4().hex,
        "payload": payload or {},
        "meta": _base_payload(),
    }

    path = cfg.path

    # 追記の整合性を担保（クロスプロセス）
    with io.file_lock(path, timeout_sec=10.0):
        io.append_jsonl(path, row, fsync_each=True)


# ---- optional helpers ---------------------------------------------------------


def tail(*, max_lines: int = 200) -> list[Dict[str, Any]]:
    """audit.jsonl の末尾を読み出す（UI表示用途）。"""
    path = paths.logs_dir(ensure=False) / "audit.jsonl"
    return io.read_jsonl_tail(path, max_lines=max_lines)


def flush_marker(event: str = "audit.flush") -> None:
    """動作確認用にマーカーを1行書く。"""
    emit(event, level="INFO", feature="audit", payload={"ok": True, "t": time.time()})

