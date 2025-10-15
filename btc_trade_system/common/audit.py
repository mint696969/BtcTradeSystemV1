# path: btc_trade_system/common/audit.py
# desc: 監査イベント出力（緑/黄/赤の粒度に依らず1行JSONL）
from __future__ import annotations
import os, datetime as dt
from pathlib import Path
from btc_trade_system.common.storage_router import StorageRouter
from . import io_safe, paths

# --- context (actor/site/session/task/mode) & redact helpers ----------------
_CTX: dict[str, str | None] = {
    "actor": None,
    "site": None,
    "session": None,
    "task": None,
    "mode": os.getenv("BTC_TS_MODE", "DEBUG"),
}

def set_context(*, actor: str | None = None, site: str | None = None,
                session: str | None = None, task: str | None = None,
                mode: str | None = None) -> None:
    """監査共通文脈（誰が/どこで/どのセッション/どの作業/どのモード）を設定。Noneは無視。"""
    if actor is not None:   _CTX["actor"] = actor
    if site is not None:    _CTX["site"] = site
    if session is not None: _CTX["session"] = session
    if task is not None:    _CTX["task"] = task
    if mode is not None:    _CTX["mode"] = mode

_MASK_KEYS = ("secret", "token", "apikey", "password", "passphrase")

_AUDIT_REL = "audit.jsonl"
_router = StorageRouter(Path("."))

def _write_audit_line(obj: dict) -> None:
    """
    primary(ENV) → secondary(./local/logs) の自動切替で追記。
    ルータで失敗した場合は従来の io_safe にフォールバック。
    """
    try:
        _router.append_jsonl("logs", _AUDIT_REL, obj)
    except Exception:
        io_safe.append_jsonl(paths.logs_dir() / _AUDIT_REL, obj)

def _redact(obj):
    """簡易マスキング：キー名に機密っぽい語が含まれる場合は値を '***' に置換。"""
    try:
        from collections.abc import Mapping, Sequence  # 遅延 import で起動時軽量化
    except Exception:  # pragma: no cover
        Mapping = dict
        Sequence = (list, tuple)

    if isinstance(obj, Mapping):
        out = {}
        for k, v in obj.items():
            lk = str(k).lower()
            out[k] = "***" if any(t in lk for t in _MASK_KEYS) else _redact(v)
        return out
    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        return type(obj)(_redact(v) for v in obj)
    return obj

def audit(event: str, *, feature: str = "core", level: str = "INFO",
          payload: dict | None = None, **fields) -> None:
    """audit.jsonl へ1行追記。
    - 既存互換: 引数は同じ（payload任意）。呼び出し側は変更不要。
    - 追加: set_context で与えた actor/site/session/task/mode を優先採用。
    - 追加: payload と追加フィールドは _redact() で簡易マスキングして保存。
    """
    paths.ensure_dirs()
    # 文脈は set_context 優先 → 環境変数（後方互換）
    mode = _CTX.get("mode") or os.getenv("BTC_TS_MODE", "DEBUG")
    actor = _CTX.get("actor") or os.getenv("ACTOR")
    site = _CTX.get("site") or os.getenv("SITE")
    session = _CTX.get("session") or os.getenv("SESSION")
    task = _CTX.get("task")  # env には通常載せない

    line = {
        "ts": dt.datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "mode": mode,
        "event": event,
        "feature": feature,
        "level": level,
        "actor": actor,
        "site": site,
        "session": session,
        "task": task,
    }
    # 任意の追加フィールド（例: endpoint, code, latency_ms など）
    if fields:
        line.update(_redact(fields))
    # payload は従来キーを維持しつつマスク
    line["payload"] = _redact(payload or {})

    _write_audit_line(line)

# --- convenience wrappers ----------------------------------------------------
def audit_ok(event: str, *, feature: str = "core", payload: dict | None = None, **fields) -> None:
    audit(event, feature=feature, level="INFO", payload=payload, **fields)

def audit_warn(event: str, *, feature: str = "core", payload: dict | None = None, **fields) -> None:
    audit(event, feature=feature, level="WARN", payload=payload, **fields)

def audit_err(event: str, *, feature: str = "core", payload: dict | None = None, **fields) -> None:
    audit(event, feature=feature, level="ERROR", payload=payload, **fields)
