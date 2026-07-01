# path: ./btcts_next/src/btcts/prediction/market_regime/horizon_policy.py
# desc: Horizon and cadence policy for market-regime prediction. Pure policy; no scheduling side effects.

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Tuple

MARKET_REGIME_HORIZON_POLICY_VERSION = "prediction.market_regime.horizon_policy.ps_q27g.v1"


class MarketRegimeHorizonGroup(str, Enum):
    CURRENT = "current"
    SHORT = "short"
    MID = "mid"
    MEDIUM_LONG = "medium_long"
    LONG = "long"


@dataclass(frozen=True)
class MarketRegimeHorizon:
    label: str
    horizon_sec: int
    group: MarketRegimeHorizonGroup
    normal_refresh_sec: int
    stale_caution_sec: int
    event_refresh_allowed: bool
    role: str

    @property
    def horizon_key(self) -> str:
        return "current" if int(self.horizon_sec) == 0 else f"{int(self.horizon_sec)}s"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["group"] = self.group.value
        data["horizon_key"] = self.horizon_key
        return data


@dataclass(frozen=True)
class MarketRegimeHorizonPolicy:
    policy_id: str
    version: str
    horizons: Tuple[MarketRegimeHorizon, ...]
    observation_clock_note: str = "current nowcast may refresh faster than prediction horizons"
    strategy_clock_note: str = "tactical state must debounce prediction changes"
    read_only: bool = True
    scheduler_enabled: bool = False
    producer_enabled: bool = False

    def horizon_by_label(self, label: str) -> MarketRegimeHorizon:
        for horizon in self.horizons:
            if horizon.label == label:
                return horizon
        raise KeyError(label)

    def horizon_by_seconds(self, seconds: int) -> MarketRegimeHorizon:
        for horizon in self.horizons:
            if int(horizon.horizon_sec) == int(seconds):
                return horizon
        raise KeyError(seconds)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "horizons": [horizon.to_dict() for horizon in self.horizons],
            "observation_clock_note": self.observation_clock_note,
            "strategy_clock_note": self.strategy_clock_note,
            "read_only": self.read_only,
            "scheduler_enabled": self.scheduler_enabled,
            "producer_enabled": self.producer_enabled,
        }


def build_default_horizon_policy() -> MarketRegimeHorizonPolicy:
    return MarketRegimeHorizonPolicy(
        policy_id="market_regime_horizon_policy.v1",
        version=MARKET_REGIME_HORIZON_POLICY_VERSION,
        horizons=(
            MarketRegimeHorizon("現在", 0, MarketRegimeHorizonGroup.CURRENT, 3, 15, True, "fast_nowcast_observation"),
            MarketRegimeHorizon("5分後", 300, MarketRegimeHorizonGroup.SHORT, 30, 120, True, "short_horizon_regime"),
            MarketRegimeHorizon("15分後", 900, MarketRegimeHorizonGroup.SHORT, 60, 300, True, "short_structure_regime"),
            MarketRegimeHorizon("30分後", 1800, MarketRegimeHorizonGroup.MID, 120, 600, True, "range_breakout_transition"),
            MarketRegimeHorizon("60分後", 3600, MarketRegimeHorizonGroup.MID, 300, 900, True, "medium_regime"),
            MarketRegimeHorizon("6時間後", 21600, MarketRegimeHorizonGroup.MEDIUM_LONG, 900, 3600, False, "medium_long_regime"),
            MarketRegimeHorizon("12時間後", 43200, MarketRegimeHorizonGroup.MEDIUM_LONG, 1800, 7200, False, "medium_long_regime"),
            MarketRegimeHorizon("24時間後", 86400, MarketRegimeHorizonGroup.LONG, 3600, 14400, False, "broad_context_regime"),
        ),
    )
