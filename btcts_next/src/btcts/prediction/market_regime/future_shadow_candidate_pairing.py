# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_candidate_pairing.py
# desc: MR-F8.3 pure paired-forecast generation for all registered future candidates from one immutable evidence slot.

from __future__ import annotations

from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Sequence, Tuple

from .future_baseline_model import (
    MARKET_REGIME_FUTURE_BASELINE_LOGIC_VERSION,
    MARKET_REGIME_FUTURE_BASELINE_MODEL_ID,
    FutureBaselineEvidence,
    forecast_future_market_regime_baseline,
)
from .future_forecast_contract import MarketRegimeFutureForecast
from .future_shadow_candidate_registry import (
    FutureShadowCandidateParameters,
    build_default_future_shadow_candidate_registry,
    validate_future_shadow_candidate_registry,
)
from .future_shadow_model_comparison import FutureShadowCandidateIdentity

MARKET_REGIME_FUTURE_SHADOW_PAIRING_VERSION = (
    "prediction.market_regime.future_shadow_candidate_pairing.mr_f8_3.v1"
)
SOURCE_CONTRACT_VERSION = "prediction.market_regime.future_baseline_evidence.mr_f5_3.v1"


def _slot_key(evidence: FutureBaselineEvidence) -> Tuple[str, str, int, str]:
    return (
        evidence.origin_timestamp,
        evidence.feature_snapshot_ref,
        int(evidence.target_horizon_sec),
        f"market_regime_target.{int(evidence.target_horizon_sec)}s.v1",
    )


def _pair_id(evidence: FutureBaselineEvidence, candidate_ids: Sequence[str]) -> str:
    basis = "|".join((*map(str, _slot_key(evidence)), *candidate_ids))
    return "market_regime_mr_f8_pair:" + sha256(basis.encode("utf-8")).hexdigest()


def _identity(candidate: FutureShadowCandidateParameters) -> FutureShadowCandidateIdentity:
    role = "active" if candidate.registry_state == "active" else "shadow"
    return FutureShadowCandidateIdentity(
        candidate_id=candidate.parameter_set_id,
        model_id=MARKET_REGIME_FUTURE_BASELINE_MODEL_ID,
        logic_version=MARKET_REGIME_FUTURE_BASELINE_LOGIC_VERSION,
        parameter_set_id=candidate.parameter_set_id,
        target_definition_family="market_regime_target.*.v1",
        source_contract_version=SOURCE_CONTRACT_VERSION,
        registry_role=role,
    )


def _forecast_payload(forecast: MarketRegimeFutureForecast) -> Mapping[str, Any]:
    return MappingProxyType({
        "model_id": forecast.model_id,
        "logic_version": forecast.logic_version,
        "parameter_set_id": forecast.parameter_set_id,
        "origin_timestamp": forecast.origin_timestamp,
        "feature_snapshot_ref": forecast.feature_snapshot_ref,
        "target_horizon_sec": forecast.target_horizon_sec,
        "target_definition_version": forecast.target_definition_version,
        "forecast_status": forecast.status.value,
        "predicted_future_state": forecast.predicted_future_state.value,
        "raw_model_score_or_probability": forecast.raw_model_score_or_probability,
        "abstain_reason": forecast.abstain_reason,
        "invalidation_conditions": forecast.invalidation_conditions,
        "shadow_only": True,
        "canonical_replacement": False,
    })


def build_future_shadow_candidate_pair(
    *,
    evidence: FutureBaselineEvidence,
    candidates: Sequence[FutureShadowCandidateParameters] | None = None,
) -> Mapping[str, Any]:
    registry = tuple(candidates or build_default_future_shadow_candidate_registry())
    validation = validate_future_shadow_candidate_registry(registry)
    if validation["ok"] is not True:
        raise ValueError("future_shadow_candidate_pair_registry_invalid:" + ",".join(validation["failures"]))
    if any(item.registry_state not in ("active", "shadow") for item in registry):
        raise ValueError("future_shadow_candidate_pair_noncomparison_registry_state")

    identities = tuple(_identity(item) for item in registry)
    forecasts = tuple(forecast_future_market_regime_baseline(evidence, candidate=item) for item in registry)
    expected_slot = _slot_key(evidence)
    observed_slots = {
        (
            item.origin_timestamp,
            item.feature_snapshot_ref,
            int(item.target_horizon_sec),
            item.target_definition_version,
        )
        for item in forecasts
    }
    if observed_slots != {expected_slot}:
        raise ValueError("future_shadow_candidate_pair_slot_identity_mismatch")
    if tuple(item.parameter_set_id for item in forecasts) != tuple(item.parameter_set_id for item in registry):
        raise ValueError("future_shadow_candidate_pair_parameter_identity_mismatch")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_PAIRING_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_candidate_pair",
        "pair_id": _pair_id(evidence, tuple(item.parameter_set_id for item in registry)),
        "slot_identity": MappingProxyType({
            "origin_timestamp": evidence.origin_timestamp,
            "feature_snapshot_ref": evidence.feature_snapshot_ref,
            "target_horizon_sec": int(evidence.target_horizon_sec),
            "target_definition_version": expected_slot[3],
        }),
        "candidate_count": len(registry),
        "candidate_identities": tuple(item.to_dict() for item in identities),
        "forecasts": tuple(_forecast_payload(item) for item in forecasts),
        "comparison_ready_for_outcome_join": True,
        "safety": MappingProxyType({
            "pure": True,
            "read_only_inputs": True,
            "writes_dhot": False,
            "shadow_only": True,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        }),
    })
