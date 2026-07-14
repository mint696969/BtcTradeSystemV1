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
    calibration_display_confidence: float | None = None
    calibrated_probability_claim: bool = False
    calibration_state: str = "UNCALIBRATED"
    calibration_sample_count: int = 0
    calibration_maturity: str = ""
    calibration_cap_reasons: Tuple[str, ...] = ()
    calibration_estimator_version: str = ""
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
        allowed_states = {"UNCALIBRATED", "INSUFFICIENT_SAMPLE", "PROVISIONAL", "CAPPED", "CALIBRATED"}
        if self.calibration_state not in allowed_states:
            raise ValueError("calibration_state_invalid")
        if int(self.calibration_sample_count) < 0:
            raise ValueError("calibration_sample_count_must_be_non_negative")
        if self.calibrated_reliability is not None:
            reliability = float(self.calibrated_reliability)
            if not 0.0 <= reliability <= 1.0:
                raise ValueError("calibrated_reliability_out_of_range")
            if not self.calibration_estimator_version.strip():
                raise ValueError("calibration_estimator_version_required")
            if not self.calibration_maturity.strip():
                raise ValueError("calibration_maturity_required")
        if self.calibration_display_confidence is not None:
            display_confidence = float(self.calibration_display_confidence)
            if not 0.0 <= display_confidence <= 1.0:
                raise ValueError("calibration_display_confidence_out_of_range")
            if self.calibrated_reliability is None:
                raise ValueError("calibration_display_confidence_requires_reliability")
            if display_confidence > float(self.calibrated_reliability):
                raise ValueError("calibration_display_confidence_exceeds_reliability")
        if self.calibrated_probability_claim:
            if self.status is not FutureForecastStatus.FORECAST:
                raise ValueError("calibrated_probability_claim_requires_forecast")
            if self.calibrated_reliability is None:
                raise ValueError("calibrated_probability_claim_requires_reliability")
            if self.calibration_state != "CALIBRATED":
                raise ValueError("calibrated_probability_claim_requires_calibrated_state")
            if self.calibration_maturity != "MATURE":
                raise ValueError("calibrated_probability_claim_requires_mature_sample")
            if int(self.calibration_sample_count) <= 0:
                raise ValueError("calibrated_probability_claim_requires_samples")
            if self.calibration_cap_reasons:
                raise ValueError("calibrated_probability_claim_disallows_caps")
        if self.calibration_state == "CALIBRATED" and not self.calibrated_probability_claim:
            raise ValueError("calibrated_state_requires_probability_claim")
        if self.calibration_state == "CAPPED" and not self.calibration_cap_reasons:
            raise ValueError("capped_state_requires_cap_reasons")
        if self.calibration_state != "CAPPED" and self.calibration_cap_reasons:
            raise ValueError("cap_reasons_require_capped_state")
        if self.calibration_state == "INSUFFICIENT_SAMPLE":
            if self.calibrated_reliability is not None or self.calibration_display_confidence is not None:
                raise ValueError("insufficient_sample_disallows_calibration_values")
            if int(self.calibration_sample_count) != 0:
                raise ValueError("insufficient_sample_requires_zero_samples")
        if self.calibration_state == "UNCALIBRATED":
            if self.calibrated_reliability is not None or self.calibration_display_confidence is not None:
                raise ValueError("uncalibrated_state_disallows_calibration_values")
            if self.calibration_maturity:
                raise ValueError("uncalibrated_state_disallows_maturity")
            if int(self.calibration_sample_count) != 0:
                raise ValueError("uncalibrated_state_requires_zero_samples")
        if self.calibration_state == "PROVISIONAL":
            if self.calibrated_reliability is None:
                raise ValueError("provisional_state_requires_reliability")
            if self.calibration_maturity not in {"SPARSE", "PROVISIONAL"}:
                raise ValueError("provisional_state_requires_non_mature_sample")
            if int(self.calibration_sample_count) <= 0:
                raise ValueError("provisional_state_requires_samples")
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
            "calibration_display_confidence": self.calibration_display_confidence,
            "calibrated_probability_claim": self.calibrated_probability_claim,
            "calibration_state": self.calibration_state,
            "calibration_sample_count": int(self.calibration_sample_count),
            "calibration_maturity": self.calibration_maturity,
            "calibration_cap_reasons": list(self.calibration_cap_reasons),
            "calibration_estimator_version": self.calibration_estimator_version,
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
