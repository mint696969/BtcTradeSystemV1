# path: ./btcts_next/src/btcts/collector/status.py
# desc: collector の Command/State スナップショットを正準パスへ書き出す。UI/Health/Soak はこれを読む。

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from btcts.core import audit, io, paths


@dataclass
class CollectorStatus:
    """collector 全体の実状態（人間/Health/UI が読む前提）。

    互換維持:
    - 既存 callers は ts/mode/message/last_error/items だけ渡してよい
    - write_status() 側で actual_state / actual_mode などを補完する
    """

    ts: float
    mode: str  # backward-compat: RUNNING / STOPPED / ERROR
    message: str = ""
    last_error: str = ""
    items: Optional[List[Dict[str, Any]]] = None

    # ---- Phase3B: canonical state fields ---------------------------------
    actual_state: str = ""            # RUNNING / STOPPED / ERROR
    actual_mode: str = ""             # BTC_TS_MODE: NORMAL / DEBUG / BOOST
    pid: Optional[int] = None
    started_at: str = ""
    last_heartbeat: str = ""
    restart_count: int = 0

    control: Optional[Dict[str, Any]] = None
    watchdog: Optional[Dict[str, Any]] = None
    derived: Optional[Dict[str, Any]] = None
    rate_control: Optional[Dict[str, Any]] = None


@dataclass
class CollectorControlCommand:
    """collector への意図（Command）。

    actual reflection is represented by status.json.
    """

    request_id: str
    desired_state: str                 # running / stopped
    desired_mode: str = "NORMAL"       # BTC_TS_MODE
    requested_at: str = ""
    requested_by: str = "operator"
    reason: str = ""
    note: str = ""


def _iso_utc(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def _runtime_mode() -> str:
    return (os.environ.get("BTC_TS_MODE", "") or "NORMAL").strip().upper()


def status_path() -> Path:
    return paths.data_dir() / "collector" / "status.json"


def rate_state_path() -> Path:
    return paths.data_dir() / "collector" / "rate_state.json"


def control_path() -> Path:
    return paths.data_dir() / "collector" / "control.json"


def _normalize_status_obj(st: CollectorStatus) -> Dict[str, Any]:
    obj = asdict(st)

    ts_unix = float(st.ts)
    ts_iso = _iso_utc(ts_unix)
    actual_state = (st.actual_state or st.mode or "UNKNOWN").upper()
    actual_mode = (st.actual_mode or _runtime_mode() or "NORMAL").upper()

    # 既存互換キー
    obj["ts"] = ts_unix
    obj["mode"] = st.mode

    # Phase3B 正準キー
    obj["ts_unix"] = ts_unix
    obj["ts_iso"] = ts_iso
    obj["actual_state"] = actual_state
    obj["actual_mode"] = actual_mode

    if obj.get("items") is None:
        obj["items"] = []
    if obj.get("control") is None:
        obj["control"] = {}
    if obj.get("watchdog") is None:
        obj["watchdog"] = {}
    if obj.get("derived") is None:
        obj["derived"] = {}
    if obj.get("rate_control") is None:
        obj["rate_control"] = {}

    return obj


def write_status(st: CollectorStatus, *, emit_audit: bool = True) -> Path:
    p = status_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    obj = _normalize_status_obj(st)

    with io.file_lock(p, timeout_sec=10.0, stale_sec=5.0):
        io.write_json(p, obj)

    if emit_audit:
        audit.emit(
            "collector.status.write",
            feature="collector",
            level="DEBUG",
            payload={
                "path": str(p),
                "actual_state": obj.get("actual_state"),
                "actual_mode": obj.get("actual_mode"),
            },
        )

    return p


def write_rate_state(snapshot: Dict[str, Any], *, emit_audit: bool = True) -> Path:
    """RateController.snapshot() を rate_state.json として保存する。"""
    p = rate_state_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    # 互換維持:
    # - snapshot が {"items": {...}} を返しても
    # - snapshot が直接 {"bitflyer": {...}} を返しても
    # どちらでも rate_state.json の items に正規化する
    items = snapshot.get("items", snapshot) if isinstance(snapshot, dict) else {}

    obj: Dict[str, Any] = {
        "ts": time.time(),
        "items": items,
    }

    with io.file_lock(p, timeout_sec=10.0, stale_sec=5.0):
        io.write_json(p, obj)

    if emit_audit:
        exchanges = sorted(list(items.keys())) if isinstance(items, dict) else []
        audit.emit(
            "collector.rate_state.write",
            feature="collector",
            level="DEBUG",
            payload={"path": str(p), "exchanges": exchanges},
        )

    return p


def write_control(cmd: CollectorControlCommand, *, emit_audit: bool = True) -> Path:
    p = control_path()
    p.parent.mkdir(parents=True, exist_ok=True)

    obj = asdict(cmd)
    if not obj.get("requested_at"):
        obj["requested_at"] = _iso_utc(time.time())

    with io.file_lock(p, timeout_sec=10.0, stale_sec=5.0):
        io.write_json(p, obj)

    if emit_audit:
        audit.emit(
            "control.requested",
            feature="collector",
            level="INFO",
            payload={
                "path": str(p),
                "request_id": obj.get("request_id"),
                "desired_state": obj.get("desired_state"),
                "desired_mode": obj.get("desired_mode"),
                "requested_by": obj.get("requested_by"),
                "reason": obj.get("reason"),
            },
        )

    return p


def read_status(*, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = status_path()
    return io.read_json(p, default=default or {}) or {}


def read_rate_state(*, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = rate_state_path()
    return io.read_json(p, default=default or {}) or {}


def read_control(*, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = control_path()
    return io.read_json(p, default=default or {}) or {}