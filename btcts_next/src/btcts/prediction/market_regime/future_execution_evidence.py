# path: ./btcts_next/src/btcts/prediction/market_regime/future_execution_evidence.py
# desc: Pure MR-F9.1A immutable horizon-execution evidence contract. No reads, writes, UI, scheduler, broker, AutoTrade, promotion, or activation behavior.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping

from .future_forecast_contract import FutureForecastStatus, MarketRegimeFutureForecast
from .future_trace_identity import MarketRegimeFutureTraceIdentity, build_market_regime_future_trace_identity

MARKET_REGIME_FUTURE_EXECUTION_EVIDENCE_VERSION = (
    "prediction.market_regime.future_execution_evidence.mr_f9_1a.v1"
)


class FutureInferenceMode(str, Enum):
    FULL_INFERENCE = "FULL_INFERENCE"
    FALLBACK = "FALLBACK"
    ABSTAINED_WITHOUT_INFERENCE = "ABSTAINED_WITHOUT_INFERENCE"


class RawOutputSemantics(str, Enum):
    UNSPECIFIED = "UNSPECIFIED"
    SCORE = "SCORE"
    PROBABILITY = "PROBABILITY"


def _required_text(**values: str) -> None:
    missing = tuple(name for name, value in values.items() if not str(value).strip())
    if missing:
        raise ValueError("future_execution_evidence_required_identity_missing:" + ",".join(missing))


def _calculation_fingerprint(*, trace: MarketRegimeFutureTraceIdentity, inference_mode: FutureInferenceMode,
                             raw_output_semantics: RawOutputSemantics, raw_output: float | None,
                             fallback_reason: str, fallback_source_ref: str) -> str:
    basis = "|".join((
        trace.trace_id,
        inference_mode.value,
        raw_output_semantics.value,
        "" if raw_output is None else repr(float(raw_output)),
        fallback_reason,
        fallback_source_ref,
    ))
    return "market_regime_future_calculation:" + sha256(basis.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MarketRegimeFutureExecutionEvidence:
    trace_id: str
    prediction_origin: str
    generated_at: str
    target_horizon_sec: int
    model_id: str
    logic_version: str
    parameter_set_id: str
    feature_snapshot_ref: str
    target_definition_version: str
    forecast_status: FutureForecastStatus
    inference_mode: FutureInferenceMode
    raw_model_score_or_probability: float | None
    raw_output_semantics: RawOutputSemantics
    source_freshness_state: str
    source_age_sec: float | None
    abstention_decision: bool
    abstain_reason: str
    fallback_used: bool
    fallback_reason: str
    fallback_source_ref: str
    calculation_fingerprint: str
    contract_version: str = MARKET_REGIME_FUTURE_EXECUTION_EVIDENCE_VERSION

    def __post_init__(self) -> None:
        _required_text(
            trace_id=self.trace_id,
            prediction_origin=self.prediction_origin,
            generated_at=self.generated_at,
            model_id=self.model_id,
            logic_version=self.logic_version,
            parameter_set_id=self.parameter_set_id,
            feature_snapshot_ref=self.feature_snapshot_ref,
            target_definition_version=self.target_definition_version,
            source_freshness_state=self.source_freshness_state,
            calculation_fingerprint=self.calculation_fingerprint,
        )
        if int(self.target_horizon_sec) <= 0:
            raise ValueError("future_execution_evidence_horizon_invalid")
        if self.generated_at != self.prediction_origin:
            raise ValueError("future_execution_evidence_generated_at_origin_mismatch")
        if self.raw_model_score_or_probability is not None:
            value = float(self.raw_model_score_or_probability)
            if not 0.0 <= value <= 1.0:
                raise ValueError("future_execution_evidence_raw_output_out_of_range")
        if self.raw_output_semantics is RawOutputSemantics.PROBABILITY and self.raw_model_score_or_probability is None:
            raise ValueError("future_execution_evidence_probability_value_missing")
        if self.source_age_sec is not None and float(self.source_age_sec) < 0.0:
            raise ValueError("future_execution_evidence_source_age_negative")
        if self.abstention_decision != (self.forecast_status is FutureForecastStatus.ABSTAIN):
            raise ValueError("future_execution_evidence_abstention_status_mismatch")
        if self.abstention_decision and not self.abstain_reason.strip():
            raise ValueError("future_execution_evidence_abstain_reason_required")
        if not self.abstention_decision and self.abstain_reason:
            raise ValueError("future_execution_evidence_forecast_disallows_abstain_reason")
        if self.fallback_used != (self.inference_mode is FutureInferenceMode.FALLBACK):
            raise ValueError("future_execution_evidence_fallback_mode_mismatch")
        if self.fallback_used:
            if not self.fallback_reason.strip():
                raise ValueError("future_execution_evidence_fallback_reason_required")
            if not self.fallback_source_ref.strip():
                raise ValueError("future_execution_evidence_fallback_source_ref_required")
        elif self.fallback_reason or self.fallback_source_ref:
            raise ValueError("future_execution_evidence_non_fallback_disallows_fallback_fields")
        if self.inference_mode is FutureInferenceMode.ABSTAINED_WITHOUT_INFERENCE and not self.abstention_decision:
            raise ValueError("future_execution_evidence_abstained_mode_requires_abstention")

    def to_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "contract_version": self.contract_version,
            "trace_id": self.trace_id,
            "prediction_origin": self.prediction_origin,
            "generated_at": self.generated_at,
            "target_horizon_sec": int(self.target_horizon_sec),
            "model_id": self.model_id,
            "logic_version": self.logic_version,
            "parameter_set_id": self.parameter_set_id,
            "feature_snapshot_ref": self.feature_snapshot_ref,
            "target_definition_version": self.target_definition_version,
            "forecast_status": self.forecast_status.value,
            "inference_mode": self.inference_mode.value,
            "raw_model_score_or_probability": self.raw_model_score_or_probability,
            "raw_output_semantics": self.raw_output_semantics.value,
            "source_freshness_state": self.source_freshness_state,
            "source_age_sec": self.source_age_sec,
            "abstention_decision": self.abstention_decision,
            "abstain_reason": self.abstain_reason,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "fallback_source_ref": self.fallback_source_ref,
            "calculation_fingerprint": self.calculation_fingerprint,
            "shadow_only": True,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        })


def build_market_regime_future_execution_evidence(
    forecast: MarketRegimeFutureForecast,
    *,
    inference_mode: FutureInferenceMode,
    raw_output_semantics: RawOutputSemantics = RawOutputSemantics.UNSPECIFIED,
    source_freshness_state: str,
    source_age_sec: float | None,
    fallback_reason: str = "",
    fallback_source_ref: str = "",
) -> MarketRegimeFutureExecutionEvidence:
    trace = build_market_regime_future_trace_identity(forecast)
    fallback_used = inference_mode is FutureInferenceMode.FALLBACK
    fingerprint = _calculation_fingerprint(
        trace=trace,
        inference_mode=inference_mode,
        raw_output_semantics=raw_output_semantics,
        raw_output=forecast.raw_model_score_or_probability,
        fallback_reason=fallback_reason,
        fallback_source_ref=fallback_source_ref,
    )
    return MarketRegimeFutureExecutionEvidence(
        trace_id=trace.trace_id,
        prediction_origin=trace.origin_timestamp,
        generated_at=trace.origin_timestamp,
        target_horizon_sec=trace.target_horizon_sec,
        model_id=trace.model_id,
        logic_version=trace.logic_version,
        parameter_set_id=trace.parameter_set_id,
        feature_snapshot_ref=trace.feature_snapshot_ref,
        target_definition_version=trace.target_definition_version,
        forecast_status=trace.forecast_status,
        inference_mode=inference_mode,
        raw_model_score_or_probability=forecast.raw_model_score_or_probability,
        raw_output_semantics=raw_output_semantics,
        source_freshness_state=source_freshness_state,
        source_age_sec=source_age_sec,
        abstention_decision=forecast.status is FutureForecastStatus.ABSTAIN,
        abstain_reason=forecast.abstain_reason,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        fallback_source_ref=fallback_source_ref,
        calculation_fingerprint=fingerprint,
    )
