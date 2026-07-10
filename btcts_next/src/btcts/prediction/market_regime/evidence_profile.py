# path: ./btcts_next/src/btcts/prediction/market_regime/evidence_profile.py
# desc: MarketRegime default evidence profile adapter. Pure/read-only; no runtime read/write, prediction, broker, AutoTrade, or parameter apply.

from __future__ import annotations

from math import floor
from typing import Any, Iterable

from btcts.prediction.evidence_sources import (
    build_prediction_evidence_source_descriptor,
    build_prediction_evidence_source_weight_profile,
)

from .contracts import FeatureGroup
from .horizon_policy import MarketRegimeHorizon, MarketRegimeHorizonGroup, build_default_horizon_policy
from .parameter_set_registry import MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID
from .source_priority_policy import HorizonSourcePriority, build_default_source_priority_policy

MARKET_REGIME_EVIDENCE_PROFILE_VERSION = "prediction.market_regime.evidence_profile.2026_07_10.v1"

_COMMON_HORIZON_GROUP_BY_MARKET_REGIME_GROUP = {
    MarketRegimeHorizonGroup.CURRENT: "nowcast",
    MarketRegimeHorizonGroup.SHORT: "short_horizon",
    MarketRegimeHorizonGroup.MID: "mid_horizon",
    MarketRegimeHorizonGroup.MEDIUM_LONG: "long_horizon",
    MarketRegimeHorizonGroup.LONG: "long_horizon",
}

_SOURCE_ID_BY_FEATURE_GROUP = {
    FeatureGroup.SOURCE_QUALITY: "market_regime.source_quality",
    FeatureGroup.LIQUIDITY: "market_regime.liquidity",
    FeatureGroup.ORDERFLOW: "market_regime.orderflow",
    FeatureGroup.PRICE_STRUCTURE: "market_regime.price_structure",
    FeatureGroup.VOLATILITY: "market_regime.volatility",
    FeatureGroup.CROSS_VENUE: "market_regime.cross_venue",
}


def market_regime_common_horizon_group(group: MarketRegimeHorizonGroup | str) -> str:
    normalized = group if isinstance(group, MarketRegimeHorizonGroup) else MarketRegimeHorizonGroup(str(group))
    return _COMMON_HORIZON_GROUP_BY_MARKET_REGIME_GROUP[normalized]


def market_regime_evidence_source_id(feature_group: FeatureGroup | str) -> str:
    normalized = feature_group if isinstance(feature_group, FeatureGroup) else FeatureGroup(str(feature_group))
    return _SOURCE_ID_BY_FEATURE_GROUP[normalized]


def _integer_weight_percentages(priority: HorizonSourcePriority) -> tuple[int, ...]:
    """Convert valid policy float weights into deterministic integer percentages totaling 100."""

    groups = tuple(priority.ordered_feature_groups)
    if not groups:
        raise ValueError(f"source priority has no feature groups: {priority.group.value}")
    if len(groups) != len(set(groups)):
        raise ValueError(f"source priority has duplicate feature groups: {priority.group.value}")

    raw: list[float] = []
    for group in groups:
        if group not in priority.weights:
            raise ValueError(f"source priority weight missing: {priority.group.value}:{group.value}")
        weight = float(priority.weights[group])
        if weight <= 0.0:
            raise ValueError(f"source priority weight must be positive: {priority.group.value}:{group.value}")
        raw.append(weight * 100.0)

    if sum(raw) <= 0:
        raise ValueError(f"source priority has no positive weights: {priority.group.value}")
    normalized = [value * 100.0 / sum(raw) for value in raw]
    base = [floor(value) for value in normalized]
    remainder = 100 - sum(base)
    order = sorted(range(len(normalized)), key=lambda index: (-(normalized[index] - base[index]), index))
    for index in order[:remainder]:
        base[index] += 1
    return tuple(int(value) for value in base)


def _source_role(priority_rank: int) -> str:
    return "primary" if priority_rank == 1 else "supporting"


def _build_sources(priority: HorizonSourcePriority) -> list[dict[str, Any]]:
    weights = _integer_weight_percentages(priority)
    sources: list[dict[str, Any]] = []
    for index, feature_group in enumerate(priority.ordered_feature_groups):
        priority_rank = index + 1
        sources.append(build_prediction_evidence_source_descriptor(
            source_id=market_regime_evidence_source_id(feature_group),
            role=_source_role(priority_rank),
            source_kind="derived_feature_group",
            weight_percent=weights[index],
            priority_rank=priority_rank,
            default_reliability_percent=50,
            default_signal_strength_percent=50,
            default_freshness_percent=100,
            default_quality_percent=100,
            default_direction="unknown",
            learned_from_outcomes=False,
            min_required=False,
            missing_policy="degrade_confidence",
            tunable=True,
            source_ref=f"market_regime.feature_group:{feature_group.value}",
            rationale=f"MarketRegime {priority.group.value} source-priority policy rank {priority_rank}",
        ))
    return sources


def build_market_regime_default_evidence_profile(
    *,
    horizon_sec: int,
    parameter_set_id: str = MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID,
) -> dict[str, Any]:
    """Build the default MarketRegime evidence profile for one configured horizon."""

    horizon_policy = build_default_horizon_policy()
    horizon = horizon_policy.horizon_by_seconds(int(horizon_sec))
    source_policy = build_default_source_priority_policy()
    priority = source_policy.priority_for_group(horizon.group)
    profile = build_prediction_evidence_source_weight_profile(
        prediction_family_id="market_regime",
        family_part_role="primary_context",
        horizon_key=horizon.horizon_key,
        horizon_group=market_regime_common_horizon_group(horizon.group),
        parameter_set_id=str(parameter_set_id),
        sources=_build_sources(priority),
        profile_id=f"market_regime:{horizon.horizon_key}:{parameter_set_id}:default_evidence_profile",
        notes=[
            f"adapter_version={MARKET_REGIME_EVIDENCE_PROFILE_VERSION}",
            f"horizon_policy_version={horizon_policy.version}",
            f"source_priority_policy_version={source_policy.version}",
            "neutral defaults only; runtime freshness, quality, direction, and learned reliability are not applied in MR-VS1",
            "missing-source blockers and currentness gates are deferred to MR-VS2",
        ],
    )
    profile["market_regime_evidence_profile_version"] = MARKET_REGIME_EVIDENCE_PROFILE_VERSION
    profile["market_regime_horizon_group"] = horizon.group.value
    profile["market_regime_horizon_label"] = horizon.label
    profile["source_priority_policy_id"] = source_policy.policy_id
    profile["source_priority_policy_version"] = source_policy.version
    profile["horizon_policy_id"] = horizon_policy.policy_id
    profile["horizon_policy_version"] = horizon_policy.version
    return profile


def build_all_market_regime_default_evidence_profiles(
    *,
    parameter_set_id: str = MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID,
    horizons: Iterable[MarketRegimeHorizon] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Build deterministic default profiles for all configured MarketRegime horizons."""

    selected = tuple(horizons) if horizons is not None else build_default_horizon_policy().horizons
    return tuple(
        build_market_regime_default_evidence_profile(
            horizon_sec=horizon.horizon_sec,
            parameter_set_id=parameter_set_id,
        )
        for horizon in selected
    )
