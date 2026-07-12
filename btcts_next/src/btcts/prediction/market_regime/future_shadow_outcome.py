# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_outcome.py
# desc: Pure MR-F5.6 shadow future-outcome resolution contract and immutable evaluation-row projection. No reads or writes.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import MarketRegimeCode
from .future_forecast_contract import FutureForecastStatus
from .future_target_definition import future_target_definitions_by_horizon
from .future_trace_identity import MarketRegimeFutureTraceIdentity
from .transition_policy import evaluate_market_regime_transition

MARKET_REGIME_FUTURE_SHADOW_OUTCOME_VERSION = "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1"


class FutureShadowOutcomeStatus(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    INVALIDATED = "INVALIDATED"
    ABSTAINED = "ABSTAINED"
    CORRECT = "CORRECT"
    PARTIAL = "PARTIAL"
    INCORRECT = "INCORRECT"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("future_shadow_outcome_timestamp_missing")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception as exc:
        raise ValueError("future_shadow_outcome_timestamp_invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError("future_shadow_outcome_timestamp_timezone_missing")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class FutureShadowOutcomeEvidence:
    resolved_at: str
    observation_available: bool
    observed_at: str = ""
    observed_future_state: MarketRegimeCode = MarketRegimeCode.UNKNOWN
    invalidated: bool = False
    invalidation_reason: str = ""
    observation_source_ref: str = ""

    def __post_init__(self) -> None:
        resolved_at = _parse_utc(self.resolved_at)
        if self.resolved_at != _iso(resolved_at):
            raise ValueError("future_shadow_outcome_resolved_at_not_canonical_utc")
        if not isinstance(self.observed_future_state, MarketRegimeCode):
            raise ValueError("future_shadow_outcome_observed_state_invalid")
        if self.invalidated and not self.invalidation_reason.strip():
            raise ValueError("future_shadow_outcome_invalidation_reason_missing")
        if self.observation_available:
            observed_at = _parse_utc(self.observed_at)
            if self.observed_at != _iso(observed_at):
                raise ValueError("future_shadow_outcome_observed_at_not_canonical_utc")
            if observed_at > resolved_at:
                raise ValueError("future_shadow_outcome_observed_after_resolved")
            if not self.observation_source_ref.strip():
                raise ValueError("future_shadow_outcome_source_ref_missing")


@dataclass(frozen=True)
class MarketRegimeFutureShadowOutcome:
    trace: MarketRegimeFutureTraceIdentity
    status: FutureShadowOutcomeStatus
    reason: str
    resolved_at: str
    observed_at: str
    observed_future_state: MarketRegimeCode
    observation_source_ref: str
    contract_version: str = MARKET_REGIME_FUTURE_SHADOW_OUTCOME_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.status, FutureShadowOutcomeStatus):
            raise ValueError("future_shadow_outcome_status_invalid")
        if not self.reason.strip():
            raise ValueError("future_shadow_outcome_reason_missing")
        resolved_at = _parse_utc(self.resolved_at)
        if self.resolved_at != _iso(resolved_at):
            raise ValueError("future_shadow_outcome_resolved_at_not_canonical_utc")
        if self.observed_at:
            observed_at = _parse_utc(self.observed_at)
            if self.observed_at != _iso(observed_at):
                raise ValueError("future_shadow_outcome_observed_at_not_canonical_utc")
            if observed_at > resolved_at:
                raise ValueError("future_shadow_outcome_observed_after_resolved")
        if self.status in {FutureShadowOutcomeStatus.CORRECT, FutureShadowOutcomeStatus.PARTIAL, FutureShadowOutcomeStatus.INCORRECT}:
            if self.observed_future_state is MarketRegimeCode.UNKNOWN:
                raise ValueError("future_shadow_outcome_resolved_state_unknown")
            if not self.observed_at or not self.observation_source_ref:
                raise ValueError("future_shadow_outcome_resolved_evidence_missing")

    def to_evaluation_row(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "schema_version": self.contract_version,
            "artifact_family": "prediction/market_regime",
            "artifact_kind": "future_shadow_evaluation_row",
            "trace_id": self.trace.trace_id,
            "origin_timestamp": self.trace.origin_timestamp,
            "expiry_at": self.trace.expiry_at,
            "resolved_at": self.resolved_at,
            "target_horizon_sec": self.trace.target_horizon_sec,
            "target_horizon_key": self.trace.target_horizon_key,
            "target_definition_version": self.trace.target_definition_version,
            "model_id": self.trace.model_id,
            "logic_version": self.trace.logic_version,
            "parameter_set_id": self.trace.parameter_set_id,
            "feature_snapshot_ref": self.trace.feature_snapshot_ref,
            "forecast_status": self.trace.forecast_status.value,
            "predicted_future_state": self.trace.predicted_future_state.value,
            "observed_future_state": self.observed_future_state.value,
            "outcome_status": self.status.value,
            "outcome_reason": self.reason,
            "observed_at": self.observed_at,
            "observation_source_ref": self.observation_source_ref,
            "shadow_only": True,
            "canonical_replacement": False,
            "ledger_append_allowed": False,
        })


def resolve_market_regime_future_shadow_outcome(*, trace: MarketRegimeFutureTraceIdentity, evidence: FutureShadowOutcomeEvidence) -> MarketRegimeFutureShadowOutcome:
    resolved_at = _parse_utc(evidence.resolved_at)
    expiry = _parse_utc(trace.expiry_at)
    if resolved_at < expiry:
        return MarketRegimeFutureShadowOutcome(trace, FutureShadowOutcomeStatus.UNRESOLVED, "target_horizon_not_expired", evidence.resolved_at, "", MarketRegimeCode.UNKNOWN, "")
    if trace.forecast_status is FutureForecastStatus.ABSTAIN:
        return MarketRegimeFutureShadowOutcome(trace, FutureShadowOutcomeStatus.ABSTAINED, "forecast_abstained", evidence.resolved_at, "", MarketRegimeCode.UNKNOWN, "")
    if evidence.invalidated:
        return MarketRegimeFutureShadowOutcome(trace, FutureShadowOutcomeStatus.INVALIDATED, evidence.invalidation_reason, evidence.resolved_at, evidence.observed_at, evidence.observed_future_state, evidence.observation_source_ref)
    if not evidence.observation_available:
        return MarketRegimeFutureShadowOutcome(trace, FutureShadowOutcomeStatus.UNRESOLVED, "observation_unavailable", evidence.resolved_at, "", MarketRegimeCode.UNKNOWN, "")
    observed_at = _parse_utc(evidence.observed_at)
    definition = future_target_definitions_by_horizon()[trace.target_horizon_sec]
    delta = (observed_at - expiry).total_seconds()
    if delta < 0:
        return MarketRegimeFutureShadowOutcome(trace, FutureShadowOutcomeStatus.UNRESOLVED, "observation_before_target_timestamp", evidence.resolved_at, evidence.observed_at, evidence.observed_future_state, evidence.observation_source_ref)
    if delta > definition.observation_tolerance_sec:
        return MarketRegimeFutureShadowOutcome(trace, FutureShadowOutcomeStatus.INVALIDATED, "observation_outside_target_tolerance", evidence.resolved_at, evidence.observed_at, evidence.observed_future_state, evidence.observation_source_ref)
    if evidence.observed_future_state is MarketRegimeCode.UNKNOWN:
        return MarketRegimeFutureShadowOutcome(trace, FutureShadowOutcomeStatus.UNRESOLVED, "observed_future_state_unknown", evidence.resolved_at, evidence.observed_at, evidence.observed_future_state, evidence.observation_source_ref)
    if evidence.observed_future_state is trace.predicted_future_state:
        status, reason = FutureShadowOutcomeStatus.CORRECT, "observed_state_matches_prediction"
    else:
        transition = evaluate_market_regime_transition(
            previous_regime=trace.predicted_future_state.value,
            candidate_regime=evidence.observed_future_state.value,
            previous_state_age_sec=999999,
            candidate_score=1.0,
            runner_up_score=0.0,
            change_point_evidence_score=1.0,
        )
        if bool(transition["transition_allowed"]):
            status, reason = FutureShadowOutcomeStatus.PARTIAL, "observed_state_transition_adjacent"
        else:
            status, reason = FutureShadowOutcomeStatus.INCORRECT, "observed_state_differs"
    return MarketRegimeFutureShadowOutcome(trace, status, reason, evidence.resolved_at, evidence.observed_at, evidence.observed_future_state, evidence.observation_source_ref)
