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
    monitoring.yaml の想定キー（例）:
      thresholds:
        age_sec:
          warn: 60
          crit: 300
    無ければ妥協せず明示デフォルトに落とす（UIで理由を出す）
    """
    cfg = load_yaml("monitoring") or {}
    warn = None
    crit = None
    try:
        warn = float(cfg.get("thresholds", {}).get("age_sec", {}).get("warn"))
    except Exception:
        warn = None
    try:
        crit = float(cfg.get("thresholds", {}).get("age_sec", {}).get("crit"))
    except Exception:
        crit = None

    # 強制デフォルト（運用で困らない値）
    if warn is None:
        warn = 60.0
    if crit is None:
        crit = 300.0

    if crit < warn:
        # 設定ミスは“直すべきもの”として矯正（crit>=warnに丸める）
        crit = warn

    return warn, crit


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

    st = read_status()  # CollectorStatus
    raw_items = getattr(st, "items", None)

    if not raw_items:
        # items=None / [] を許容（“収集してない”状態）
        if st.mode != "RUNNING":
            reasons.append("collector is not running (status.items is empty)")
        return HealthSummary(
            updated_at=_now_iso(),
            counts={"OK": 0, "WARN": 0, "CRIT": 0},
            items=[],
            reasons=reasons,
        )

    items: List[HealthItem] = []
    counts = {"OK": 0, "WARN": 0, "CRIT": 0}

    for it in raw_items:
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
    if not (cfg.get("thresholds", {}).get("age_sec", {}).get("warn") is not None):
        reasons.append("monitoring.thresholds.age_sec.warn is missing -> default=60s")
    if not (cfg.get("thresholds", {}).get("age_sec", {}).get("crit") is not None):
        reasons.append("monitoring.thresholds.age_sec.crit is missing -> default=300s")

    return HealthSummary(
        updated_at=_now_iso(),
        counts=counts,
        items=items,
        reasons=reasons,
    )
