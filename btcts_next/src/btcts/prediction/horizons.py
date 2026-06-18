# path: ./btcts_next/src/btcts/prediction/horizons.py
# desc: Horizon contracts for market prediction. Defines micro, primary trade, and context layers without execution behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Tuple


class HorizonLayer(str, Enum):
    EXECUTION_MICRO = "execution_micro"
    PRIMARY_TRADE = "primary_trade"
    CONTEXT = "context"


EXECUTION_MICRO_HORIZONS_SEC: Tuple[int, ...] = (15, 30, 60, 180)
PRIMARY_TRADE_HORIZONS_SEC: Tuple[int, ...] = (300, 900, 1800)
CONTEXT_HORIZONS_SEC: Tuple[int, ...] = (3600, 14400, 86400)


@dataclass(frozen=True)
class PredictionHorizon:
    horizon_sec: int
    layer: HorizonLayer
    label: str
    role: str
    hard_blocker_by_default: bool = False

    @property
    def horizon_key(self) -> str:
        return f"{int(self.horizon_sec)}s"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["layer"] = self.layer.value
        data["horizon_key"] = self.horizon_key
        return data


def _label(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds == 86400:
        return "1d"
    if seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    return f"{seconds}s"


def _role(layer: HorizonLayer) -> str:
    if layer == HorizonLayer.EXECUTION_MICRO:
        return "entry_timing_and_execution_veto"
    if layer == HorizonLayer.PRIMARY_TRADE:
        return "main_trade_thesis"
    return "higher_timeframe_context"


def build_default_horizons() -> Tuple[PredictionHorizon, ...]:
    items: list[PredictionHorizon] = []
    for seconds in EXECUTION_MICRO_HORIZONS_SEC:
        items.append(PredictionHorizon(seconds, HorizonLayer.EXECUTION_MICRO, _label(seconds), _role(HorizonLayer.EXECUTION_MICRO)))
    for seconds in PRIMARY_TRADE_HORIZONS_SEC:
        items.append(PredictionHorizon(seconds, HorizonLayer.PRIMARY_TRADE, _label(seconds), _role(HorizonLayer.PRIMARY_TRADE)))
    for seconds in CONTEXT_HORIZONS_SEC:
        items.append(PredictionHorizon(seconds, HorizonLayer.CONTEXT, _label(seconds), _role(HorizonLayer.CONTEXT), hard_blocker_by_default=False))
    return tuple(items)


def horizon_by_seconds(seconds: int) -> PredictionHorizon:
    for horizon in build_default_horizons():
        if horizon.horizon_sec == int(seconds):
            return horizon
    raise KeyError(f"unsupported prediction horizon: {seconds}")
