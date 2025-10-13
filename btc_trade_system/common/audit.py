# path: btc_trade_system/common/audit.py
# desc: 監査イベント出力（緑/黄/赤の粒度に依らず1行JSONL）
from __future__ import annotations
import os, datetime as dt
from . import io_safe, paths

def audit(event: str, *, feature: str="core", level: str="INFO", payload: dict|None=None) -> None:
    """audit.jsonl へ1行追記。機密は呼び出し側でマスクする想定。"""
    paths.ensure_dirs()
    line = {
        "ts": dt.datetime.utcnow().isoformat() + "Z",
        "mode": os.getenv("BTC_TS_MODE", "DEBUG"),
        "event": event,
        "feature": feature,
        "level": level,
        "actor": os.getenv("ACTOR"),
        "site": os.getenv("SITE"),
        "session": os.getenv("SESSION"),
        "payload": payload or {},
    }
    io_safe.append_jsonl(paths.logs_dir() / "audit.jsonl", line)
