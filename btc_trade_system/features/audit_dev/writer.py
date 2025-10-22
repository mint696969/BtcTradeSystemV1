# path: features/audit_dev/writer.py
# desc: 開発監査（dev audit）出力。logs_dir()を使用し、128MB超時に末尾32MB保持。portalocker対応、全変数定義済み。
from __future__ import annotations

import io
import json
import os
import sys
import time
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from btc_trade_system.common.paths import logs_dir

# === 定数（固定仕様） ===
_LOG_DIR = Path(logs_dir())  # 正規のログディレクトリ D:\BtcTS_V1\logs など
_LOG_PATH = _LOG_DIR / "dev_audit.jsonl"
_LOCKFILE = _LOG_DIR / ".dev_audit.lock"
_MAX_BYTES = 128 * 1024 * 1024  # 128MB
_TRIM_TO = 32 * 1024 * 1024     # 32MB（末尾のみ保持）

# === プロセス内のモード状態（非永続） ===
_MODE = "OFF"
_MODE_LOCK = threading.RLock()

# === 書込ロック（並行書込対策） ===
try:
    import portalocker  # type: ignore
    _HAS_PORTALOCKER = True
except Exception:  # pragma: no cover
    portalocker = None  # type: ignore
    _HAS_PORTALOCKER = False

_FILE_LOCK = threading.RLock()


def _ensure_parents() -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def set_mode(mode: str) -> None:
    m = mode.upper().strip()
    if m not in {"OFF", "DEBUG", "BOOST"}:
        raise ValueError(f"invalid dev-audit mode: {mode}")
    with _MODE_LOCK:
        global _MODE
        _MODE = m

def get_mode() -> str:
    with _MODE_LOCK:
        return _MODE

_LEVEL_RANK = {"DEBUG": 10, "INFO": 20, "WARN": 30, "WARNING": 30, "ERROR": 40, "CRIT": 50, "CRITICAL": 50}

def _should_emit(current_mode: str, level: str) -> bool:
    lvl = level.upper()
    if current_mode == "OFF":
        return False
    if current_mode == "DEBUG":
        return _LEVEL_RANK.get(lvl, 999) >= _LEVEL_RANK["WARN"]
    return True

def _ts_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{int((time.time()%1)*1000):03d}Z"

def _open_with_lock(path: Path):
    if _HAS_PORTALOCKER:
        f = open(path, "a", encoding="utf-8", newline="")
        portalocker.lock(f, portalocker.LOCK_EX)
        return f
    _FILE_LOCK.acquire()
    return open(path, "a", encoding="utf-8", newline="")


def _release_lock(f: io.TextIOBase) -> None:
    try:
        if _HAS_PORTALOCKER:
            try:
                portalocker.unlock(f)
            except Exception:
                pass
        f.close()
    finally:
        if not _HAS_PORTALOCKER:
            try:
                _FILE_LOCK.release()
            except RuntimeError:
                pass


def _atomic_tail_trim(path: Path, keep_bytes: int) -> None:
    size = path.stat().st_size
    if size <= _MAX_BYTES:
        return

    # 書き換え時の競合を避けるためロック下で実施
    if _HAS_PORTALOCKER:
        with open(path, "a", encoding="utf-8", newline="") as lf:
            portalocker.lock(lf, portalocker.LOCK_EX)
            _tail_replace_locked(path, keep_bytes)
            portalocker.unlock(lf)
    else:
        with _FILE_LOCK:
            _tail_replace_locked(path, keep_bytes)

def _tail_replace_locked(path: Path, keep_bytes: int) -> None:
    size = path.stat().st_size
    with open(path, "rb") as rf:
        if size > keep_bytes:
            rf.seek(size - keep_bytes)
        tail = rf.read()
    nl = tail.find(b"\n")
    if nl != -1:
        tail = tail[nl + 1 :]
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as wf:
        wf.write(tail)
        wf.flush()
        os.fsync(wf.fileno())
    os.replace(tmp, path)

# === マスキング & サイズ制御（正準） ===
import re

_MASK_KEY_RE = re.compile(
    r"(?i)(key|secret|token|pass|pwd|cookie|authorization|bearer|credential|sign|private|api[_-]?key|access[_-]?key|refresh)"
)

def _mask_value(v: Any) -> Any:
    if v is None:
        return None
    if not isinstance(v, (str, bytes)):
        return "[REDACTED]" if isinstance(v, (dict, list, tuple, set)) else v
    if isinstance(v, bytes):
        return "[REDACTED]"
    s = v
    if len(s) < 8:
        return "[REDACTED]"
    return s[:4] + ("*" * max(4, len(s) - 8)) + s[-4:]

def _redact_payload(obj: Any) -> Any:
    try:
        if isinstance(obj, dict):
            return {k: (_mask_value(v) if _MASK_KEY_RE.search(k) else _redact_payload(v)) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_redact_payload(x) for x in obj]
        return obj
    except Exception:
        return "[REDACTED]"

def _truncate_payload(obj: Any, *, field_limit_bytes: int = 2 * 1024, line_limit_bytes: int = 10 * 1024) -> Any:
    """
    - 各フィールド最大 ~2KB
    - 1行（JSONL）最大 ~10KB を目安に縮約（超過時は '...(truncated N bytes)' を付記）
    """
    def _clip_str(s: str) -> str:
        b = s.encode("utf-8", "ignore")
        if len(b) <= field_limit_bytes:
            return s
        over = len(b) - field_limit_bytes
        return b[:field_limit_bytes].decode("utf-8", "ignore") + f"...(truncated {over} bytes)"

    def _walk(x: Any) -> Any:
        if isinstance(x, dict):
            return {k: _walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [_walk(v) for v in x]
        if isinstance(x, str):
            return _clip_str(x)
        return x

    trimmed = _walk(obj)
    # 仕上げに行全体の上限をざっくり担保
    try:
        blob = json.dumps(trimmed, ensure_ascii=False, separators=(",", ":")).encode("utf-8", "ignore")
        if len(blob) <= line_limit_bytes:
            return trimmed
        over = len(blob) - line_limit_bytes
        return {"payload_truncated": True, "note": f"line truncated {over} bytes"}
    except Exception:
        return trimmed

def emit(event: str, level: str = "INFO", **fields: Any) -> None:
    mode = get_mode()
    if not _should_emit(mode, level):
        return

    _ensure_parents()

    # 入力payloadを先に取り出し
    user_payload = fields if fields else None
    if user_payload is not None:
        user_payload = _redact_payload(user_payload)
        user_payload = _truncate_payload(user_payload)

    rec: Dict[str, Any] = {
        "ts": _ts_iso(),
        "mode": mode,
        "event": event if event.startswith("dev.") else f"dev.{event}",
        "feature": str(fields.pop("feature", "dev")) if fields and "feature" in fields else "dev",
        "level": level.upper(),
        "actor": (fields.pop("actor", None) if fields else None),
        "site": (fields.pop("site", None) if fields else None),
        "session": (fields.pop("session", None) if fields else None),
        "task": (fields.pop("task", None) if fields else None),
        "trace_id": (fields.pop("trace_id", None) if fields else None),
        "payload": user_payload,
    }

    _LOCKFILE.parent.mkdir(parents=True, exist_ok=True)
    _LOCKFILE.touch(exist_ok=True)

    f = _open_with_lock(_LOG_PATH)
    try:
        line = json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n"
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
    finally:
        _release_lock(f)

    try:
        if _LOG_PATH.exists() and _LOG_PATH.stat().st_size > _MAX_BYTES:
            _atomic_tail_trim(_LOG_PATH, _TRIM_TO)
    except Exception:
        pass

def audit_debug(event: str, **kw): return emit(event, level="DEBUG", **kw)
def audit_info(event: str, **kw):  return emit(event, level="INFO", **kw)
def audit_warn(event: str, **kw):  return emit(event, level="WARN", **kw)
def audit_error(event: str, **kw): return emit(event, level="ERROR", **kw)
def audit_crit(event: str, **kw):  return emit(event, level="CRIT", **kw)

if __name__ == "__main__":
    set_mode("DEBUG")
    emit("ui.toggle", level="INFO", feature="audit_dev", detail="toggle to DEBUG")
    set_mode("BOOST")
    for i in range(3):
        emit("boost.info", level="DEBUG", feature="audit_dev", i=i, note="BOOST allows all levels")
    print(f"wrote -> {_LOG_PATH}")