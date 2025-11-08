# path: ./btc_trade_system/features/health/health_svc.py
# desc: collector の status.json を読み、OK/WARN/CRIT を判定して UI/通知向けサマリを返す共通サービス。

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from btc_trade_system.features.settings import settings_svc as _SET
from btc_trade_system.features.health.health_order import load_order as _load_order

DEFAULT_WARN = 3.0
DEFAULT_CRIT = 10.0

@dataclass
class ItemView:
    exchange: str
    topic: str
    last_ok: Optional[str]
    age_sec: float
    cause: Optional[str]
    retries: int
    notes: Optional[str]
    level: str  # "OK" | "WARN" | "CRIT"

@dataclass
class HealthSummary:
    updated_at: Optional[str]
    items: List[ItemView]
    counts: Dict[str, int]  # {'OK': n1, 'WARN': n2, 'CRIT': n3}

# == パス解決 ==

def _data_dir() -> Path:
    p = os.environ.get("BTC_TS_DATA_DIR") or os.environ.get("DATA")
    if p:
        return Path(p)
    # 開発フォールバック：リポ直下 data/
    return Path(__file__).resolve().parents[3] / "data"

def _status_path() -> Path:
    return _data_dir() / "collector" / "status.json"

# == 設定読取り ==
# 既存の _load_thresholds() を丸ごと置換
def _load_thresholds() -> Tuple[float, float, List[str]]:
    """
    (warn, crit, order) を返す。
    - warn/crit は settings_svc.load_yaml("monitoring") の後勝ちマージ結果から取得
    - order は health_order.load_order() に委譲
    """
    mon = _SET.load_yaml("monitoring") or {}

    # 期待パス: thresholds.default.age_sec.{warn, crit}
    thr = (((mon.get("thresholds") or {}).get("default") or {}).get("age_sec") or {})
    warn = float(thr.get("warn", DEFAULT_WARN))
    crit = float(thr.get("crit", DEFAULT_CRIT))

    try:
        order = list(_load_order())
    except Exception:
        order = []

    return warn, crit, order

def _judge_level(age_sec: float, warn: float, crit: float) -> str:
    if age_sec >= crit:
        return "CRIT"
    if age_sec >= warn:
        return "WARN"
    return "OK"

# == 健全性判定（再利用向け） ==

def eval_with_thresholds(snapshot: dict, thresholds: Tuple[float, float]) -> dict:
    """
    与えられた snapshot(dict) に warn/crit を適用し、各要素へ level を付与して返す。
    thresholds = (warn, crit)
    戻り値: {"items": [...], "counts": {...}}
    """
    warn, crit = thresholds
    items = []
    counts = {"OK": 0, "WARN": 0, "CRIT": 0}

    for it in snapshot.get("items", []):
        age = float(it.get("age_sec", 0.0))
        level = _judge_level(age, warn, crit)
        it["level"] = level
        items.append(it)
        counts[level] = counts.get(level, 0) + 1

    return {"items": items, "counts": counts, "updated_at": snapshot.get("updated_at")}

# == パブリックI/F ==

def read_health() -> HealthSummary:
    """
    collector/status.json を読み、OK/WARN/CRIT を付けた一覧と件数を返す。
    UI/ヘッダー/通知から共通利用することを想定。
    """
    p = _status_path()
    if not p.exists():
        return HealthSummary(updated_at=None, items=[], counts={"OK": 0, "WARN": 0, "CRIT": 0})

    raw = json.loads(p.read_text(encoding="utf-8"))
    warn, crit, order = _load_thresholds()

    items: List[ItemView] = []
    for it in raw.get("items", []):
        age = float(it.get("age_sec", 0.0))
        items.append(ItemView(
            exchange=str(it.get("exchange")),
            topic=str(it.get("topic")),
            last_ok=it.get("last_ok"),
            age_sec=age,
            cause=it.get("cause"),
            retries=int(it.get("retries", 0)),
            notes=it.get("notes"),
            level=_judge_level(age, warn, crit),
        ))

    # 並び順：設定 order > exchange/topic
    def _key(iv: ItemView):
        k = f"{iv.exchange}/{iv.topic}"
        return (0, order.index(k)) if (order and k in order) else (1, iv.exchange, iv.topic)

    items.sort(key=_key)

    counts = {"OK": 0, "WARN": 0, "CRIT": 0}
    for iv in items:
        counts[iv.level] = counts.get(iv.level, 0) + 1

    return HealthSummary(
        updated_at=raw.get("updated_at"),
        items=items,
        counts=counts,
    )

# --- compat shim for legacy imports -----------------------------------------
def evaluate(snapshot, thresholds):
    """
    互換I/F: 旧UIが import していた evaluate を提供する。
    実体は eval_with_thresholds のエイリアス。
    """
    return eval_with_thresholds(snapshot, thresholds)
