# # path: ./btc_trade_system/features/dash/presets.py
# desc: ダッシュボード/監査UIの期間・レベル・色などのプリセットを一元管理する小モジュール。

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

# 期間プリセット（UIのドロップダウンと providers.audit の既定値で共通利用）
LOOKBACKS: List[str] = ["15m", "1h", "6h", "24h", "7d"]

# 監査レベル（並び順の定義）
LEVELS_ORDER: List[str] = ["OK", "INFO", "WARN", "CRIT", "ERROR"]

# UIのレベル色（monitoring.yaml と被せる場合は、UI側で monitoring.yaml を優先し、未定義だけここで補完）
LEVEL_COLORS: Dict[str, str] = {
    "OK": "#00B050",
    "WARN": "#FFCC00",
    "CRIT": "#C00000",
    "INFO": "#2F5597",
    "ERROR": "#C00000",
}

@dataclass(frozen=True)
class Preset:
    key: str
    label: str

def get_lookbacks() -> List[Preset]:
    """UI向け：表示ラベルとキーを揃えたリストを返す"""
    return [Preset(k, k) for k in LOOKBACKS]

def is_valid_lookback(value: str) -> bool:
    """入力バリデーション用"""
    return value in LOOKBACKS

def get_levels_order() -> List[str]:
    return LEVELS_ORDER[:]

def level_color(level: str) -> str:
    return LEVEL_COLORS.get(level.upper(), "#808080")
