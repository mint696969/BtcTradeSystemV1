# path: ./btc_trade_system/features/audit_dev/writer.py
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


def set_mode(mode: str, *, source: str = "ui") -> None:
    m = (mode or "OFF").upper().strip()
    if m not in {"OFF", "DEBUG", "BOOST"}:
        raise ValueError(f"invalid dev-audit mode: {mode}")
    with _MODE_LOCK:
        global _MODE
        old = _MODE
        _MODE = m
    # モード切替はフィルタに関係なく必ず1行残す（emitを使わず生書き）
    try:
        _log_toggle_raw(old_mode=old, new_mode=_MODE, source=source)
    except Exception:
        pass

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

# === 軽量レート制御（既定OFF / UI変更なし） ==========================
# 目的: GPTに渡す際のノイズ低減。BOOST時の DEBUG/INFO 連発を短時間窓で間引きし、
#      溜まったら要約1行（dev.rate.dropped）を出す。
_RATE_ENABLED = False   # ★必要時だけ True に。既定は無効＝現在と同一動作
_RATE_WINDOW_MS = 2000
_RATE_MAX_PER_WINDOW = 60
_RATE_SUMMARY_EVERY = 200

from typing import List  # 既存で未使用ならスルー可
_RATE_STATE: Dict[str, Dict[str, int]] = {}

def _now_ms() -> int:
    return int(time.time() * 1000)

def _rate_sig(event: str, level: str, feature: str, payload: Any) -> str:
    kind = type(payload).__name__ if payload is not None else "-"
    note = ""
    if isinstance(payload, dict) and "note" in payload:
        note = str(payload.get("note", ""))[:24]
    return f"{event}|{level}|{feature}|{kind}|{note}"

def _log_event_raw(*, event: str, level: str, feature: str = "audit_dev", payload: Any = None, mode: Optional[str] = None) -> None:
    """
    フィルタを無視して 1 行を書き出す汎用版（要約通知などに使用）。
    """
    try:
        _ensure_parents()
        m = (mode or get_mode() or "OFF").upper()
        rec = {
            "ts": _ts_iso(),
            "mode": m,
            "event": event if event.startswith("dev.") else f"dev.{event}",
            "feature": feature,
            "level": (level or "INFO").upper(),
            "actor": None, "site": None, "session": None, "task": None, "trace_id": None,
            "payload": _truncate_payload(_redact_payload(payload)) if payload is not None else None,
        }
        f = _open_with_lock(_LOG_PATH)
        try:
            line = json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n"
            f.write(line); f.flush(); os.fsync(f.fileno())
        finally:
            _release_lock(f)
        if _LOG_PATH.exists() and _LOG_PATH.stat().st_size > _MAX_BYTES:
            _atomic_tail_trim(_LOG_PATH, _TRIM_TO)
    except Exception:
        pass

def _rate_should_drop(event: str, level: str, feature: str, payload: Any) -> bool:
    """
    Trueを返したら「この1行はDROP」。対象は BOOST かつ DEBUG/INFO。
    溜まったら dev.rate.dropped をINFOで1行だけ出す。
    """
    lvl = (level or "").upper()
    if lvl not in ("DEBUG", "INFO"):
        return False
    sig = _rate_sig(event, lvl, feature or "dev", payload)
    now = _now_ms()
    stt = _RATE_STATE.get(sig)
    if not stt:
        _RATE_STATE[sig] = stt = {"win_start": now, "count": 0, "dropped": 0, "last_summary": 0}
    # 窓進行
    if now - stt["win_start"] > _RATE_WINDOW_MS:
        stt["win_start"] = now
        stt["count"] = 0
    stt["count"] += 1
    if stt["count"] <= _RATE_MAX_PER_WINDOW:
        return False  # まだ通す
    # 以降はDROP扱い
    stt["dropped"] += 1
    # 過剰に要約が出ないよう、一定件数ごとにのみ出力
    if stt["dropped"] % _RATE_SUMMARY_EVERY == 0:
        try:
            _log_event_raw(
                event="dev.rate.dropped", level="INFO", feature="audit_dev",
                payload={"sig": sig, "dropped": stt["dropped"],
                         "window_ms": _RATE_WINDOW_MS, "max_per_window": _RATE_MAX_PER_WINDOW},
                mode=get_mode(),
            )
            stt["last_summary"] = now
        except Exception:
            pass
    return True

def _log_toggle_raw(old_mode: str, new_mode: str, source: str = "ui") -> None:
    """
    モード切替をフィルタに関係なく常に1行記録するための生書き関数。
    emit() を経由しない = OFF でも確実に残す。
    """
    try:
        _ensure_parents()
        rec = {
            "ts": _ts_iso(),
            "mode": new_mode,
            "event": "dev.ui.toggle",
            "feature": "audit_dev",
            "level": "INFO",
            "payload": {"old": old_mode, "new": new_mode, "source": source},
        }
        f = _open_with_lock(_LOG_PATH)
        try:
            line = json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n"
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        finally:
            _release_lock(f)

        if _LOG_PATH.exists() and _LOG_PATH.stat().st_size > _MAX_BYTES:
            _atomic_tail_trim(_LOG_PATH, _TRIM_TO)
    except Exception:
        # 記録失敗は握り潰す（モード切替そのものは継続）
        pass

def emit(event: str, level: str = "INFO", **fields: Any) -> None:
    mode = get_mode()
    if not _should_emit(mode, level):
        return

    _ensure_parents()

    # --- 予約キーを先に分離して、payload へは入れない ---
    RESERVED = ("feature", "actor", "site", "session", "task", "trace_id")
    meta: Dict[str, Any] = {}
    if fields:
        for k in list(fields.keys()):
            if k in RESERVED:
                meta[k] = fields.pop(k)

    # 残りの fields のみを payload 化（マスク→縮約）
    user_payload = fields or None
    if user_payload is not None:
        user_payload = _redact_payload(user_payload)
        user_payload = _truncate_payload(user_payload)

    rec: Dict[str, Any] = {
        "ts": _ts_iso(),  # ここはUTCのまま。JST表示はUIで変換する
        "mode": mode,
        "event": event if event.startswith("dev.") else f"dev.{event}",
        "feature": str(meta.get("feature") or "dev"),
        "level": level.upper(),
        "actor": meta.get("actor"),
        "site": meta.get("site"),
        "session": meta.get("session"),
        "task": meta.get("task"),
        "trace_id": meta.get("trace_id"),
        "payload": user_payload,
    }

    # --- レート制御：既定OFF／BOOSTのDEBUG/INFOのみ間引き ---
    if _RATE_ENABLED and (mode or "").upper() == "BOOST":
        if _rate_should_drop(rec["event"], rec["level"], rec["feature"], user_payload):
            return  # この行はスキップ（必要に応じて dev.rate.dropped が別途1行出る）

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