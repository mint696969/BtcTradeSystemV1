# path: ./btcts_next/src/btcts/prediction/market_regime/future_target_definition.py
# desc: Immutable MR-F5.2 target-definition policy for horizon-specific future MarketRegime outcomes. Pure contract only; no reads or writes.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC

MARKET_REGIME_FUTURE_TARGET_POLICY_VERSION = "prediction.market_regime.future_target_definition.mr_f5_2.v1"


class TargetObservationRule(str, Enum):
    POINT_IN_TIME_STATE = "POINT_IN_TIME_STATE"


class TargetPartialMatchRule(str, Enum):
    TRANSITION_ADJACENCY = "TRANSITION_ADJACENCY"


@dataclass(frozen=True)
class MarketRegimeFutureTargetDefinition:
    horizon_sec: int
    target_definition_version: str
    observation_rule: TargetObservationRule
    partial_match_rule: TargetPartialMatchRule
    origin_cutoff_inclusive: bool
    target_timestamp_offset_sec: int
    observation_tolerance_sec: int
    minimum_required_history_sec: int
    required_feature_families: Tuple[str, ...]
    optional_feature_families: Tuple[str, ...]
    missing_observation_outcome: str = "unknown"
    invalid_observation_outcome: str = "invalidated"
    allow_short_horizon_label_projection: bool = False
    require_exact_horizon_identity: bool = True
    require_source_timestamp_lte_origin: bool = True

    def __post_init__(self) -> None:
        horizon = int(self.horizon_sec)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError(f"unsupported_future_target_horizon_sec:{horizon}")
        expected_version = f"market_regime_target.{horizon}s.v1"
        if self.target_definition_version != expected_version:
            raise ValueError(
                "target_definition_version_horizon_mismatch:"
                f"expected={expected_version}:actual={self.target_definition_version}"
            )
        if not isinstance(self.observation_rule, TargetObservationRule):
            raise ValueError("observation_rule_invalid")
        if not isinstance(self.partial_match_rule, TargetPartialMatchRule):
            raise ValueError("partial_match_rule_invalid")
        if not self.origin_cutoff_inclusive:
            raise ValueError("origin_cutoff_must_be_inclusive")
        if int(self.target_timestamp_offset_sec) != horizon:
            raise ValueError("target_timestamp_offset_must_equal_horizon")
        if int(self.observation_tolerance_sec) < 0:
            raise ValueError("observation_tolerance_must_be_non_negative")
        if int(self.minimum_required_history_sec) <= 0:
            raise ValueError("minimum_required_history_must_be_positive")
        if not self.required_feature_families:
            raise ValueError("required_feature_families_missing")
        if any(not str(item).strip() for item in self.required_feature_families + self.optional_feature_families):
            raise ValueError("feature_family_name_invalid")
        if len(set(self.required_feature_families)) != len(self.required_feature_families):
            raise ValueError("required_feature_families_duplicate")
        if len(set(self.optional_feature_families)) != len(self.optional_feature_families):
            raise ValueError("optional_feature_families_duplicate")
        if set(self.required_feature_families) & set(self.optional_feature_families):
            raise ValueError("required_optional_feature_families_overlap")
        if self.missing_observation_outcome != "unknown":
            raise ValueError("missing_observation_outcome_must_be_unknown")
        if self.invalid_observation_outcome != "invalidated":
            raise ValueError("invalid_observation_outcome_must_be_invalidated")
        if self.allow_short_horizon_label_projection:
            raise ValueError("short_horizon_label_projection_forbidden")
        if not self.require_exact_horizon_identity:
            raise ValueError("exact_horizon_identity_required")
        if not self.require_source_timestamp_lte_origin:
            raise ValueError("source_timestamp_cutoff_guard_required")


_REQUIRED_COMMON = (
    "price_structure",
    "volatility",
    "liquidity",
    "source_quality",
)
_OPTIONAL_COMMON = (
    "orderflow",
    "microprice",
    "cross_venue",
    "change_point",
)


def _definition(horizon_sec: int) -> MarketRegimeFutureTargetDefinition:
    long_horizon = horizon_sec >= 21600
    required = _REQUIRED_COMMON + (("session_context",) if long_horizon else ())
    optional = _OPTIONAL_COMMON + (("macro_context",) if long_horizon else ())
    minimum_history = {
        300: 1800,
        900: 3600,
        1800: 7200,
        3600: 14400,
        21600: 86400,
        43200: 172800,
        86400: 259200,
    }[horizon_sec]
    tolerance = {
        300: 60,
        900: 120,
        1800: 180,
        3600: 300,
        21600: 900,
        43200: 1800,
        86400: 3600,
    }[horizon_sec]
    return MarketRegimeFutureTargetDefinition(
        horizon_sec=horizon_sec,
        target_definition_version=f"market_regime_target.{horizon_sec}s.v1",
        observation_rule=TargetObservationRule.POINT_IN_TIME_STATE,
        partial_match_rule=TargetPartialMatchRule.TRANSITION_ADJACENCY,
        origin_cutoff_inclusive=True,
        target_timestamp_offset_sec=horizon_sec,
        observation_tolerance_sec=tolerance,
        minimum_required_history_sec=minimum_history,
        required_feature_families=required,
        optional_feature_families=optional,
    )


def build_default_future_target_definitions() -> Tuple[MarketRegimeFutureTargetDefinition, ...]:
    return tuple(_definition(horizon) for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC)


def future_target_definitions_by_horizon() -> Dict[int, MarketRegimeFutureTargetDefinition]:
    return {item.horizon_sec: item for item in build_default_future_target_definitions()}


def validate_source_timestamp_for_origin(*, source_timestamp_epoch_sec: float, origin_timestamp_epoch_sec: float) -> None:
    if float(source_timestamp_epoch_sec) > float(origin_timestamp_epoch_sec):
        raise ValueError("lookahead_source_timestamp_after_origin")
