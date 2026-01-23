# path: ./btcts_next/src/btcts/collector/status.py
# desc: collector の状態（status.json）と rate_state（rate_state.json）を正準パスへ書き出す。UI/Health はこれを読む。

from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional

from btcts.core import audit, io, paths


@dataclass
class CollectorStatus:
    """collector 全体の状態（人間/Health/UI が読む前提）。"""

    ts: float
    mode: str  # RUNNING / STOPPED / ERROR
    message: str = ""
    last_error: str = ""
    items: Optional[list] = None  # endpoint 単位の状態（将来拡張）


def status_path() -> Path:
    return paths.data_dir() / "collector" / "status.json"


def rate_state_path() -> Path:
    # 互換維持：運用上の固定ファイル名（UI/Health が参照する）
    return paths.data_dir() / "collector" / "rate_state.json"


def write_status(st: CollectorStatus, *, emit_audit: bool = True) -> Path:
    p = status_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    obj = asdict(st)
    # health/UI が扱いやすいよう unix/ISO を付与（ts は unix のまま維持）
    obj["ts_unix"] = st.ts
    obj["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.ts))

    # items は常に list に正規化（None を書かない：items:null 回避）
    if obj.get("items") is None:
        obj["items"] = []

    with io.file_lock(p, timeout_sec=10.0, stale_sec=5.0):
        io.write_json(p, obj)

    if emit_audit:
        audit.emit(
            "collector.status.write",
            feature="collector",
            level="INFO",
            payload={"path": str(p), "mode": st.mode},
        )

    return p


def write_rate_state(snapshot: Dict[str, Any], *, emit_audit: bool = True) -> Path:
    """RateController.snapshot() を rate_state.json として保存する。"""
    p = rate_state_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    obj: Dict[str, Any] = {
        "ts": time.time(),
        "items": snapshot,
    }

    with io.file_lock(p, timeout_sec=10.0, stale_sec=5.0):
        io.write_json(p, obj)

    if emit_audit:
        audit.emit(
            "collector.rate_state.write",
            feature="collector",
            level="DEBUG",
            payload={"path": str(p), "exchanges": sorted(list(snapshot.keys()))},
        )

    return p


def read_status(*, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = status_path()
    return io.read_json(p, default=default or {}) or {}


def read_rate_state(*, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = rate_state_path()
    return io.read_json(p, default=default or {}) or {}
