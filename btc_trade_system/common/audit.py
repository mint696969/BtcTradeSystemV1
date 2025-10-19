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
    "trace_id": None,  # 処理束ね用
}

def set_context(*, actor: str | None = None, site: str | None = None,
                session: str | None = None, task: str | None = None,
                mode: str | None = None, trace_id: str | None = None) -> None:
    """監査共通文脈（誰が/どこで/どのセッション/どの作業/どのモード/同一処理束ねID）。Noneは無視。"""
    if actor is not None:    _CTX["actor"] = actor
    if site is not None:     _CTX["site"] = site
    if session is not None:  _CTX["session"] = session
    if task is not None:     _CTX["task"] = task
    if mode is not None:     _CTX["mode"] = mode
    if trace_id is not None: _CTX["trace_id"] = trace_id

_MASK_KEYS = ("secret", "token", "apikey", "password", "passphrase")

# --- mode gate ---------------------------------------------------------------
_LEVEL_ORDER = {"INFO": 10, "WARN": 20, "ERROR": 30, "CRIT": 40}

def _norm_level(s: str | None) -> str:
    return (s or "INFO").upper()

def _norm_mode(s: str | None) -> str:
    m = (s or "DEBUG").upper()
    return m if m in ("PROD", "DEBUG", "DIAG") else "DEBUG"

def should_emit(*, mode: str | None, level: str | None, event: str, fields: dict | None = None) -> bool:
    """
    モード別の出力判定（最小ルール）:
      - DIAG: すべて出す
      - DEBUG: WARN以上はすべて / INFOは一部（retry/rate-limit/latency>1s/開始終了）
      - PROD: ERROR/CRIT / 重大遷移(OK->WARN|CRIT) / 開始終了のみ
    """
    m = _norm_mode(mode)
    lv = _norm_level(level)
    ev = (event or "").lower()
    fx = fields or {}

    if m == "DIAG":
        return True

    # 共通：開始/終了イベントは常に出す（起動/停止の監査）
    if ev.endswith(".start") or ev.endswith(".stop"):
        return True

    # 重大遷移: *.transition で to=WARN|CRIT
    to_state = (fx.get("to") or fx.get("next") or "").upper()
    if ev.endswith(".transition") and to_state in ("WARN", "CRIT"):
        return True

    if m == "PROD":
        return lv in ("ERROR", "CRIT")

    # DEBUG
    if lv in ("WARN", "ERROR", "CRIT"):
        return True

    # INFO のうち重要そうなものだけ
    cause = (fx.get("cause") or "").upper()
    if ".retry" in ev or cause in ("RATE_LIMIT", "NET_BLOCK"):
        return True
    try:
        lat = float(fx.get("latency_ms", 0) or 0)
        if lat >= 1000:  # 1s 以上は採取
            return True
    except Exception:
        pass
    return False

_AUDIT_REL = "audit.jsonl"
_router = StorageRouter(Path("."))

def _write_audit_line(obj: dict) -> None:
    """
    StorageRouter へまず書き込み、成功したらローカル固定追記はスキップ。
    Router が失敗した場合のみローカル固定（片系フォールバック）。
    → 同一物理パスを指す環境での二重書込ノイズを抑止。
    """
    wrote = False
    # 1) Router 側
    try:
        _router.append_jsonl("logs", _AUDIT_REL, obj)
        wrote = True
    except Exception:
        wrote = False  # フォールバックへ

    # 2) Router が失敗した時だけローカル固定（./logs/audit.jsonl）
    if not wrote:
        try:
            io_safe.append_jsonl(paths.logs_dir() / _AUDIT_REL, obj)
        except Exception:
            # 監査が原因で本流を止めない
            pass

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
    """audit.jsonl へ1行追記（モード別ゲートで間引き）。
    - 既存互換: 呼び出し側の引数はそのまま。
    - 追加: should_emit(mode, level, event, fields) で PROD/DEBUG/DIAG を切替。
    - 追加: set_context の文脈を採用。payload/fields は _redact() で簡易マスキング。
    """
    paths.ensure_dirs()
    # 文脈は set_context 優先 → 環境変数（後方互換）
    mode = _CTX.get("mode") or os.getenv("BTC_TS_MODE", "DEBUG")
    actor = _CTX.get("actor") or os.getenv("ACTOR")
    site = _CTX.get("site") or os.getenv("SITE")
    session = _CTX.get("session") or os.getenv("SESSION")
    task = _CTX.get("task")  # env には通常載せない

    # ---- ここでモード別の出力判定（間引き）----
    try:
        if not should_emit(mode=mode, level=level, event=event, fields=fields):
            return
    except Exception:
        # 何があっても監査が原因で本流を止めない
        pass

    # 監査1行の骨格
    line = {
        "ts": dt.datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "mode": mode,
        "event": event,
        "feature": feature,
        "level": _norm_level(level),
        "actor": actor,
        "site": site,
        "session": session,
        "task": task,
    }

    # 文脈 trace_id（任意）
    if _CTX.get("trace_id"):
        line["trace_id"] = _CTX["trace_id"]

    # 任意の追加フィールド（endpoint/code/latency_ms など）
    if fields:
        try:
            line.update(_redact(fields))
        except Exception:
            # もし型が崩れても監査は止めない
            line.update(fields)

    # payload はマスク後にモード別上限で要約
    redacted = _redact(payload or {})
    line["payload"] = _truncate_payload(redacted, mode=mode)

    # 最終書き出し
    _write_audit_line(line)

def _payload_limit_for_mode(mode: str) -> int:
    """モード別のpayload上限（バイト）。PROD=1KB / DEBUG=2KB / DIAG=8KB"""
    m = _norm_mode(mode)
    return 1024 if m == "PROD" else (2048 if m == "DEBUG" else 8192)

def _truncate_payload(obj: dict, *, mode: str) -> dict:
    """
    payload を簡易要約して上限内に収める。
    - まずはマスク後の dict を JSON にシリアライズして長さ判定
    - 超過時は先頭プレビューを残し、_truncated フラグと合計サイズを付与
    """
    import json
    try:
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        raw = str(obj)

    limit = _payload_limit_for_mode(mode)
    if len(raw.encode("utf-8")) <= limit:
        return obj

    # プレビューは概ね limit の 70% 程度を目安に（UTF-8境界は雑に扱う）
    preview_bytes = int(limit * 0.7)
    preview = raw.encode("utf-8")[:preview_bytes].decode("utf-8", errors="ignore")
    return {
        "_truncated": True,
        "_preview": preview,
        "_orig_bytes": len(raw.encode("utf-8")),
    }

# --- convenience wrappers ----------------------------------------------------
def audit_ok(event: str, *, feature: str = "core", payload: dict | None = None, **fields) -> None:
    audit(event, feature=feature, level=_norm_level("INFO"), payload=payload, **fields)

def audit_warn(event: str, *, feature: str = "core", payload: dict | None = None, **fields) -> None:
    audit(event, feature=feature, level=_norm_level("WARN"), payload=payload, **fields)

def audit_err(event: str, *, feature: str = "core", payload: dict | None = None, **fields) -> None:
    audit(event, feature=feature, level=_norm_level("ERROR"), payload=payload, **fields)
