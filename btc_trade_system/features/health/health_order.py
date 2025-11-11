# path: btc_trade_system/features/health/health_order.py
# desc: Health の表示順（order）を settings_svc 経由で load/save する最小I/F。
#       current: btc_trade_system/config/health.yaml の "order" を使用（def は読み取り専用）。

from __future__ import annotations
from pathlib import Path
from typing import List
from btc_trade_system.features.settings import settings_svc

_AREA = "health"

def _uniq_clean(items: List[str]) -> List[str]:
    cleaned = [x.strip() for x in (items or []) if isinstance(x, str) and x.strip()]
    seen = set()
    out: List[str] = []
    for x in cleaned:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def load_order() -> List[str]:
    """
    現行設定（btc_trade_system/config/health.yaml）から order を読み出す。
    無ければ空配列。
    """
    data = settings_svc.load_yaml(_AREA) or {}
    order = data.get("order") or []
    if isinstance(order, list):
        return [str(x) for x in order if isinstance(x, str)]
    return []

def save_order(order: List[str]) -> Path:
    """
    order を差分保存する。ファイルI/Oは settings_svc に委譲（原子的保存／監査付き）。
    戻り値は current 側 health.yaml の見込みパス（表示用途）。
    """
    uniq = _uniq_clean(order)
    cur = settings_svc.load_yaml(_AREA) or {}
    cur["order"] = uniq
    settings_svc.save_yaml(_AREA, cur)

    # 表示用に current 側のパスを推定（settings_svc が外部配置を採る場合に配慮）
    try:
        from btc_trade_system.common import paths  # type: ignore
        base = Path(paths.config_dir())           # 共有設定ディレクトリ or リポ内
    except Exception:
        base = Path("btc_trade_system") / "config"
    return base / f"{_AREA}.yaml"
