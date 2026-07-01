# path: ./btcts_next/src/btcts/prediction/market_regime/freshness_policy.py
# desc: Freshness policy for market-regime horizon outputs. Pure policy; no clock loop or scheduler behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

from .contracts import FreshnessState
from .horizon_policy import MarketRegimeHorizonPolicy, build_default_horizon_policy

MARKET_REGIME_FRESHNESS_POLICY_VERSION = "prediction.market_regime.freshness_policy.ps_q27g.v1"


@dataclass(frozen=True)
class FreshnessThreshold:
    horizon_sec: int
    live_max_age_sec: int
    warm_max_age_sec: int
    stale_after_sec: int

    def state_for_age(self, age_sec: float | int | None) -> FreshnessState:
        if age_sec is None:
            return FreshnessState.MISSING
        age = float(age_sec)
        if age < 0:
            return FreshnessState.MISSING
        if age <= self.live_max_age_sec:
            return FreshnessState.LIVE
        if age <= self.warm_max_age_sec:
            return FreshnessState.WARM
        if age <= self.stale_after_sec:
            return FreshnessState.STALE
        return FreshnessState.MISSING

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketRegimeFreshnessPolicy:
    policy_id: str
    version: str
    thresholds: Tuple[FreshnessThreshold, ...]
    read_only: bool = True
    scheduler_enabled: bool = False
    producer_enabled: bool = False

    def threshold_for_horizon(self, horizon_sec: int) -> FreshnessThreshold:
        for threshold in self.thresholds:
            if int(threshold.horizon_sec) == int(horizon_sec):
                return threshold
        raise KeyError(horizon_sec)

    def state_for_age(self, *, horizon_sec: int, age_sec: float | int | None) -> FreshnessState:
        return self.threshold_for_horizon(horizon_sec).state_for_age(age_sec)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "thresholds": [threshold.to_dict() for threshold in self.thresholds],
            "read_only": self.read_only,
            "scheduler_enabled": self.scheduler_enabled,
            "producer_enabled": self.producer_enabled,
        }


def build_default_freshness_policy(horizon_policy: MarketRegimeHorizonPolicy | None = None) -> MarketRegimeFreshnessPolicy:
    policy = horizon_policy or build_default_horizon_policy()
    thresholds = tuple(
        FreshnessThreshold(
            horizon_sec=horizon.horizon_sec,
            live_max_age_sec=horizon.normal_refresh_sec,
            warm_max_age_sec=horizon.stale_caution_sec,
            stale_after_sec=horizon.stale_caution_sec * 2,
        )
        for horizon in policy.horizons
    )
    return MarketRegimeFreshnessPolicy(
        policy_id="market_regime_freshness_policy.v1",
        version=MARKET_REGIME_FRESHNESS_POLICY_VERSION,
        thresholds=thresholds,
    )
