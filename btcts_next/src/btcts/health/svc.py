# path: ./btcts_next/src/btcts/health/svc.py
# desc: status.json と monitoring.yaml から収集健全性を評価し、UI向けサマリを返す。

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from btcts.settings import load_yaml


@dataclass(frozen=True)
class HealthItem:
    exchange: str
    topic: str
    age_sec: float
    status: str  # OK / WARN / CRIT
    cause: Optional[str] = None
    retries: int = 0
    last_ok: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class HealthSummary:
    updated_at: str
    counts: Dict[str, int]
    items: List[HealthItem]
    reasons: List[str]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get_thresholds() -> Tuple[float, float]:
    """
    monitoring 実効値（load_yaml("monitoring")）から warn/crit を取り出す。

    対応する形：
    - thresholds.age_sec.warn/crit（旧）
    - thresholds.default.age_sec.warn/crit（新・正）
    - presets を使う拡張が入っても “default を基準”に読めるようにする
    """
    cfg = load_yaml("monitoring") or {}

    # 1) まずは新系（正）: thresholds.default.age_sec
    age = (
        (cfg.get("thresholds") or {})
        .get("default", {})
        .get("age_sec", {})
    )
    warn = age.get("warn", None)
    crit = age.get("crit", None)

    # 2) フォールバック（旧）: thresholds.age_sec
    if warn is None or crit is None:
        age2 = (cfg.get("thresholds") or {}).get("age_sec", {})
        if warn is None:
            warn = age2.get("warn", None)
        if crit is None:
            crit = age2.get("crit", None)

    # 強制デフォルト（運用で困らない値）
    if warn is None:
        warn = 60.0
    if crit is None:
        crit = 300.0

    try:
        warn_f = float(warn)
    except Exception:
        warn_f = 60.0
    try:
        crit_f = float(crit)
    except Exception:
        crit_f = 300.0

    if crit_f < warn_f:
        crit_f = warn_f

    return warn_f, crit_f


def _judge(age_sec: float, warn: float, crit: float) -> str:
    if age_sec >= crit:
        return "CRIT"
    if age_sec >= warn:
        return "WARN"
    return "OK"


def read_health() -> HealthSummary:
    """
    btcts.collector.status.read_status() を使う想定。
    ただし、collector未起動/ファイル欠損でも落とさない（空で返す）。
    """
    reasons: List[str] = []
    warn_th, crit_th = _get_thresholds()

    try:
        from btcts.collector.status import read_status
    except Exception as e:
        # これはコード不整合なので reasons に残す
        return HealthSummary(
            updated_at=_now_iso(),
            counts={"OK": 0, "WARN": 0, "CRIT": 0},
            items=[],
            reasons=[f"import btcts.collector.status failed: {type(e).__name__}: {e}"],
        )

    st = read_status()

    # read_status() は CollectorStatus / dict の両方を許容する（移植中の揺れ対策）
    if isinstance(st, dict):
        mode = str(st.get("mode", "") or "")
        raw_items = st.get("items", None)
    else:
        mode = str(getattr(st, "mode", "") or "")
        raw_items = getattr(st, "items", None)

    # dict.items (builtin method) を拾ってしまった場合もここで無効化
    if callable(raw_items):
        raw_items = None

    if raw_items is None:
        # items が欠損/未取得（型揺れ・ファイル欠損等）
        if mode != "RUNNING":
            reasons.append("collector is not running (status.items is None)")
        else:
            reasons.append("collector is RUNNING but status.items is None")
        return HealthSummary(
            updated_at=_now_iso(),
            counts={"OK": 0, "WARN": 0, "CRIT": 0},
            items=[],
            reasons=reasons,
        )

    if isinstance(raw_items, list) and len(raw_items) == 0:
        # collector は動いているが endpoints=0 等で items が空のケースを区別
        if mode != "RUNNING":
            reasons.append("collector is not running (status.items is empty)")
        else:
            reasons.append("collector is RUNNING but no items (endpoints=0?)")
        return HealthSummary(
            updated_at=_now_iso(),
            counts={"OK": 0, "WARN": 0, "CRIT": 0},
            items=[],
            reasons=reasons,
        )

    items: List[HealthItem] = []
    counts = {"OK": 0, "WARN": 0, "CRIT": 0}

    for it in raw_items:
        if not isinstance(it, dict):
            continue

        # it は dict を想定
        ex = str(it.get("exchange", ""))
        tp = str(it.get("topic", ""))
        age = float(it.get("age_sec", 0.0) or 0.0)
        cause = it.get("cause")
        retries = int(it.get("retries", 0) or 0)
        last_ok = it.get("last_ok")
        notes = it.get("notes")

        stt = _judge(age, warn_th, crit_th)
        counts[stt] += 1

        items.append(
            HealthItem(
                exchange=ex,
                topic=tp,
                age_sec=age,
                status=stt,
                cause=cause,
                retries=retries,
                last_ok=last_ok,
                notes=notes,
            )
        )

    # 状態が悪いものを上に
    order = {"CRIT": 0, "WARN": 1, "OK": 2}
    items.sort(key=lambda x: (order.get(x.status, 9), x.exchange, x.topic))

    # 設定がデフォルトに落ちた可能性は reasons に出す（妥協なく透明化）
    cfg = load_yaml("monitoring") or {}
    age = (cfg.get("thresholds") or {}).get("default", {}).get("age_sec", {})
    if age.get("warn", None) is None:
        reasons.append("monitoring.thresholds.default.age_sec.warn is missing -> default=60s")
    if age.get("crit", None) is None:
        reasons.append("monitoring.thresholds.default.age_sec.crit is missing -> default=300s")

    return HealthSummary(
        updated_at=_now_iso(),
        counts=counts,
        items=items,
        reasons=reasons,
    )
