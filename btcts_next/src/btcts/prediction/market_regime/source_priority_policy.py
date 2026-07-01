# path: ./btcts_next/src/btcts/prediction/market_regime/source_priority_policy.py
# desc: Per-horizon source priority policy for market-regime inference. Pure policy; tunable by versioned proposal only.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .contracts import FeatureGroup
from .horizon_policy import MarketRegimeHorizonGroup

MARKET_REGIME_SOURCE_PRIORITY_POLICY_VERSION = "prediction.market_regime.source_priority_policy.ps_q27g.v1"


@dataclass(frozen=True)
class HorizonSourcePriority:
    group: MarketRegimeHorizonGroup
    ordered_feature_groups: Tuple[FeatureGroup, ...]
    weights: Mapping[FeatureGroup, float] = field(default_factory=dict)

    def weight_for(self, feature_group: FeatureGroup | str) -> float:
        normalized = feature_group if isinstance(feature_group, FeatureGroup) else FeatureGroup(str(feature_group))
        return float(self.weights.get(normalized, 0.0))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group": self.group.value,
            "ordered_feature_groups": [group.value for group in self.ordered_feature_groups],
            "weights": {group.value: float(weight) for group, weight in self.weights.items()},
        }


@dataclass(frozen=True)
class SourcePriorityPolicy:
    policy_id: str
    version: str
    priorities: Tuple[HorizonSourcePriority, ...]
    live_parameter_apply_allowed: bool = False
    human_review_required_before_apply: bool = True
    read_only: bool = True
    non_executing: bool = True

    def priority_for_group(self, group: MarketRegimeHorizonGroup | str) -> HorizonSourcePriority:
        normalized = group if isinstance(group, MarketRegimeHorizonGroup) else MarketRegimeHorizonGroup(str(group))
        for priority in self.priorities:
            if priority.group == normalized:
                return priority
        raise KeyError(str(group))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "priorities": [priority.to_dict() for priority in self.priorities],
            "live_parameter_apply_allowed": self.live_parameter_apply_allowed,
            "human_review_required_before_apply": self.human_review_required_before_apply,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
        }


def _priority(group: MarketRegimeHorizonGroup, ordered: Tuple[FeatureGroup, ...], weights: Tuple[float, ...]) -> HorizonSourcePriority:
    return HorizonSourcePriority(group=group, ordered_feature_groups=ordered, weights=dict(zip(ordered, weights)))


def build_default_source_priority_policy() -> SourcePriorityPolicy:
    return SourcePriorityPolicy(
        policy_id="market_regime_source_priority.v1",
        version=MARKET_REGIME_SOURCE_PRIORITY_POLICY_VERSION,
        priorities=(
            _priority(
                MarketRegimeHorizonGroup.CURRENT,
                (FeatureGroup.SOURCE_QUALITY, FeatureGroup.LIQUIDITY, FeatureGroup.ORDERFLOW, FeatureGroup.PRICE_STRUCTURE),
                (0.30, 0.25, 0.25, 0.20),
            ),
            _priority(
                MarketRegimeHorizonGroup.SHORT,
                (FeatureGroup.LIQUIDITY, FeatureGroup.ORDERFLOW, FeatureGroup.VOLATILITY, FeatureGroup.CROSS_VENUE, FeatureGroup.SOURCE_QUALITY),
                (0.25, 0.25, 0.20, 0.15, 0.15),
            ),
            _priority(
                MarketRegimeHorizonGroup.MID,
                (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.ORDERFLOW, FeatureGroup.CROSS_VENUE, FeatureGroup.SOURCE_QUALITY),
                (0.30, 0.25, 0.15, 0.15, 0.15),
            ),
            _priority(
                MarketRegimeHorizonGroup.MEDIUM_LONG,
                (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.CROSS_VENUE, FeatureGroup.SOURCE_QUALITY, FeatureGroup.LIQUIDITY),
                (0.35, 0.25, 0.20, 0.15, 0.05),
            ),
            _priority(
                MarketRegimeHorizonGroup.LONG,
                (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.CROSS_VENUE, FeatureGroup.SOURCE_QUALITY),
                (0.35, 0.30, 0.20, 0.15),
            ),
        ),
    )
