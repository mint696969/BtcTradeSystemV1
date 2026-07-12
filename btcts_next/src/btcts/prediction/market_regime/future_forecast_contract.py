# path: ./btcts_next/src/btcts/prediction/market_regime/future_forecast_contract.py
# desc: Immutable pure contract for horizon-specific future MarketRegime forecasts. No reads, writes, UI, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, Mapping, Tuple

from .contracts import MarketRegimeCode
from .horizon_policy import build_default_horizon_policy

MARKET_REGIME_FUTURE_FORECAST_CONTRACT_VERSION = "prediction.market_regime.future_forecast_contract.mr_f5_1.v1"
FUTURE_MARKET_REGIME_HORIZONS_SEC: Tuple[int, ...] = tuple(
    int(horizon.horizon_sec)
    for horizon in build_default_horizon_policy().horizons
    if int(horizon.horizon_sec) > 0
)


class FutureForecastStatus(str, Enum):
    FORECAST = "FORECAST"
    ABSTAIN = "ABSTAIN"


@dataclass(frozen=True)
class FutureTransitionStep:
    regime: MarketRegimeCode
    earliest_offset_sec: int = 0
    reason_codes: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if int(self.earliest_offset_sec) < 0:
            raise ValueError("earliest_offset_sec_must_be_non_negative")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "regime": self.regime.value,
            "earliest_offset_sec": int(self.earliest_offset_sec),
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True)
class MarketRegimeFutureForecast:
    origin_timestamp: str
    origin_current_state: MarketRegimeCode
    target_horizon_sec: int
    predicted_future_state: MarketRegimeCode
    status: FutureForecastStatus
    transition_path_candidate: Tuple[FutureTransitionStep, ...]
    raw_model_score_or_probability: float | None
    feature_snapshot_ref: str
    model_id: str
    logic_version: str
    parameter_set_id: str
    target_definition_version: str
    invalidation_conditions: Tuple[str, ...] = ()
    abstain_reason: str = ""
    calibrated_reliability: float | None = None
    calibrated_probability_claim: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        horizon = int(self.target_horizon_sec)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError(f"unsupported_future_horizon_sec:{horizon}")
        required_text = {
            "origin_timestamp": self.origin_timestamp,
            "feature_snapshot_ref": self.feature_snapshot_ref,
            "model_id": self.model_id,
            "logic_version": self.logic_version,
            "parameter_set_id": self.parameter_set_id,
            "target_definition_version": self.target_definition_version,
        }
        missing = tuple(name for name, value in required_text.items() if not str(value).strip())
        if missing:
            raise ValueError("required_identity_missing:" + ",".join(missing))
        expected_target_definition_version = f"market_regime_target.{horizon}s.v1"
        if self.target_definition_version != expected_target_definition_version:
            raise ValueError(
                "target_definition_version_horizon_mismatch:"
                f"expected={expected_target_definition_version}:actual={self.target_definition_version}"
            )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        if self.calibrated_probability_claim:
            raise ValueError("calibrated_probability_claim_not_allowed_before_mr_f7")
        if self.calibrated_reliability is not None:
            raise ValueError("calibrated_reliability_not_allowed_before_mr_f7")
        if self.raw_model_score_or_probability is not None:
            score = float(self.raw_model_score_or_probability)
            if not 0.0 <= score <= 1.0:
                raise ValueError("raw_model_score_or_probability_out_of_range")
        if self.status is FutureForecastStatus.ABSTAIN:
            if self.predicted_future_state is not MarketRegimeCode.UNKNOWN:
                raise ValueError("abstain_requires_unknown_future_state")
            if not self.abstain_reason.strip():
                raise ValueError("abstain_reason_required")
            if self.transition_path_candidate:
                raise ValueError("abstain_transition_path_must_be_empty")
        else:
            if self.predicted_future_state is MarketRegimeCode.UNKNOWN:
                raise ValueError("forecast_requires_non_unknown_future_state")
            if self.abstain_reason:
                raise ValueError("forecast_abstain_reason_must_be_empty")
            if not self.transition_path_candidate:
                raise ValueError("forecast_transition_path_required")
            if self.transition_path_candidate[-1].regime is not self.predicted_future_state:
                raise ValueError("transition_path_terminal_state_mismatch")
            offsets = tuple(int(step.earliest_offset_sec) for step in self.transition_path_candidate)
            if offsets != tuple(sorted(offsets)):
                raise ValueError("transition_path_offsets_must_be_monotonic")
            if offsets[-1] > horizon:
                raise ValueError("transition_path_exceeds_target_horizon")

    @property
    def target_horizon_key(self) -> str:
        return f"{int(self.target_horizon_sec)}s"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_version": MARKET_REGIME_FUTURE_FORECAST_CONTRACT_VERSION,
            "origin_timestamp": self.origin_timestamp,
            "origin_current_state": self.origin_current_state.value,
            "target_horizon_sec": int(self.target_horizon_sec),
            "target_horizon_key": self.target_horizon_key,
            "predicted_future_state": self.predicted_future_state.value,
            "status": self.status.value,
            "transition_path_candidate": [step.to_dict() for step in self.transition_path_candidate],
            "raw_model_score_or_probability": self.raw_model_score_or_probability,
            "calibrated_reliability": self.calibrated_reliability,
            "calibrated_probability_claim": self.calibrated_probability_claim,
            "invalidation_conditions": list(self.invalidation_conditions),
            "feature_snapshot_ref": self.feature_snapshot_ref,
            "model_id": self.model_id,
            "logic_version": self.logic_version,
            "parameter_set_id": self.parameter_set_id,
            "target_definition_version": self.target_definition_version,
            "abstain_reason": self.abstain_reason,
            "metadata": dict(self.metadata),
        }


def validate_future_forecast_set(forecasts: Tuple[MarketRegimeFutureForecast, ...]) -> None:
    horizons = tuple(int(item.target_horizon_sec) for item in forecasts)
    if len(horizons) != len(set(horizons)):
        raise ValueError("duplicate_future_horizon")
    if tuple(sorted(horizons)) != tuple(sorted(FUTURE_MARKET_REGIME_HORIZONS_SEC)):
        raise ValueError("future_horizon_coverage_mismatch")
