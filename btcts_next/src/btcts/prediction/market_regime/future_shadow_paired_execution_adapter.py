# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_paired_execution_adapter.py
# desc: MR-F9.11 pure active/shadow seven-horizon adapter from one feature snapshot plus explicit execution facts to immutable execution plans.

from __future__ import annotations

from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .contracts import MarketRegimeCode
from .future_shadow_adapter import build_market_regime_future_shadow_packet
from .future_shadow_candidate_registry import (
    FutureShadowCandidateParameters,
    build_default_future_shadow_candidate_registry,
    validate_future_shadow_candidate_registry,
)
from .future_shadow_pair_execution_plan import FutureExecutionFacts, build_future_shadow_pair_execution_plan
from .future_trace_identity import build_market_regime_future_trace_identity

MARKET_REGIME_FUTURE_SHADOW_PAIRED_EXECUTION_ADAPTER_VERSION = (
    "prediction.market_regime.future_shadow_paired_execution_adapter.mr_f9_11.v1"
)


def _pair_id(*, origin: str, snapshot: str, horizon: int, candidate_ids: Sequence[str]) -> str:
    basis = "|".join((origin, snapshot, str(int(horizon)), *candidate_ids))
    return "market_regime_mr_f9_runtime_pair:" + sha256(basis.encode("utf-8")).hexdigest()


def _forecast_row(forecast: Any) -> Mapping[str, Any]:
    trace = build_market_regime_future_trace_identity(forecast)
    return MappingProxyType({
        "trace_id": trace.trace_id,
        "expiry_at": trace.expiry_at,
        "model_id": forecast.model_id,
        "logic_version": forecast.logic_version,
        "parameter_set_id": forecast.parameter_set_id,
        "origin_timestamp": forecast.origin_timestamp,
        "feature_snapshot_ref": forecast.feature_snapshot_ref,
        "target_horizon_sec": int(forecast.target_horizon_sec),
        "target_definition_version": forecast.target_definition_version,
        "forecast_status": forecast.status.value,
        "predicted_future_state": forecast.predicted_future_state.value,
        "raw_model_score_or_probability": forecast.raw_model_score_or_probability,
        "abstain_reason": forecast.abstain_reason,
        "invalidation_conditions": tuple(forecast.invalidation_conditions),
        "shadow_only": True,
        "canonical_replacement": False,
    })


def build_future_shadow_paired_execution_adapter(
    *,
    feature_bundle: Any,
    signal_score_report: Mapping[str, Any],
    origin_current_state: MarketRegimeCode,
    origin_timestamp_epoch_sec: float,
    source_timestamp_epoch_sec: float,
    facts_by_slot: Mapping[tuple[int, str], FutureExecutionFacts],
    candidates: Sequence[FutureShadowCandidateParameters] | None = None,
) -> Mapping[str, Any]:
    registry = tuple(candidates or build_default_future_shadow_candidate_registry())
    validation = validate_future_shadow_candidate_registry(registry)
    if validation["ok"] is not True:
        raise ValueError("future_shadow_paired_execution_registry_invalid:" + ",".join(validation["failures"]))
    if len(registry) != 2:
        raise ValueError("future_shadow_paired_execution_candidate_pair_count_invalid")
    states = tuple(item.registry_state for item in registry)
    if sorted(states) != ["active", "shadow"]:
        raise ValueError("future_shadow_paired_execution_registry_state_invalid")
    registry = tuple(sorted(registry, key=lambda item: 0 if item.registry_state == "active" else 1))
    if not isinstance(facts_by_slot, Mapping):
        raise ValueError("future_shadow_paired_execution_facts_invalid")

    packets = tuple(
        build_market_regime_future_shadow_packet(
            feature_bundle=feature_bundle,
            signal_score_report=signal_score_report,
            origin_current_state=origin_current_state,
            origin_timestamp_epoch_sec=origin_timestamp_epoch_sec,
            source_timestamp_epoch_sec=source_timestamp_epoch_sec,
            candidate=candidate,
        )
        for candidate in registry
    )
    origins = {packet.generated_at for packet in packets}
    snapshots = {packet.feature_snapshot_ref for packet in packets}
    if len(origins) != 1 or len(snapshots) != 1:
        raise ValueError("future_shadow_paired_execution_packet_identity_mismatch")

    candidate_ids = tuple(item.parameter_set_id for item in registry)
    by_slot = {
        (int(forecast.target_horizon_sec), forecast.parameter_set_id): forecast
        for packet in packets
        for forecast in packet.forecasts
    }
    expected_slots = {
        (int(forecast.target_horizon_sec), candidate_id)
        for forecast in packets[0].forecasts
        for candidate_id in candidate_ids
    }
    observed_slots = set(by_slot)
    if observed_slots != expected_slots:
        raise ValueError("future_shadow_paired_execution_forecast_slot_set_mismatch")
    fact_slots = set(facts_by_slot)
    missing_facts = tuple(sorted(expected_slots - fact_slots))
    extra_facts = tuple(sorted(fact_slots - expected_slots))
    if missing_facts:
        raise ValueError("future_shadow_paired_execution_facts_missing:" + repr(missing_facts))
    if extra_facts:
        raise ValueError("future_shadow_paired_execution_facts_extra:" + repr(extra_facts))
    if any(not isinstance(facts_by_slot[slot], FutureExecutionFacts) for slot in expected_slots):
        raise ValueError("future_shadow_paired_execution_fact_contract_invalid")

    pair_plans = []
    evidence_rows = []
    trace_ids = set()
    for horizon in sorted({slot[0] for slot in expected_slots}):
        forecasts = tuple(_forecast_row(by_slot[(horizon, candidate_id)]) for candidate_id in candidate_ids)
        pair = MappingProxyType({
            "artifact_kind": "future_shadow_candidate_pair",
            "pair_id": _pair_id(
                origin=packets[0].generated_at,
                snapshot=packets[0].feature_snapshot_ref,
                horizon=horizon,
                candidate_ids=candidate_ids,
            ),
            "forecasts": forecasts,
        })
        facts_by_trace_id = {}
        for row in forecasts:
            trace_id = str(row["trace_id"])
            if trace_id in trace_ids:
                raise ValueError("future_shadow_paired_execution_trace_id_duplicate")
            trace_ids.add(trace_id)
            facts_by_trace_id[trace_id] = facts_by_slot[(horizon, str(row["parameter_set_id"]))]
        plan = build_future_shadow_pair_execution_plan(pair=pair, facts_by_trace_id=facts_by_trace_id)
        pair_plans.append(plan)
        evidence_rows.extend(plan["rows"])

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_PAIRED_EXECUTION_ADAPTER_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_paired_execution_adapter_report",
        "prediction_origin": packets[0].generated_at,
        "feature_snapshot_ref": packets[0].feature_snapshot_ref,
        "candidate_ids": candidate_ids,
        "pair_count": len(pair_plans),
        "trace_count": len(trace_ids),
        "evidence_count": len(evidence_rows),
        "pair_plans": tuple(pair_plans),
        "evidence_rows": tuple(evidence_rows),
        "would_write": False,
        "safety": MappingProxyType({
            "pure": True,
            "facts_are_explicit": True,
            "facts_inferred_from_display": False,
            "legacy_confidence_promoted_to_probability": False,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
        }),
    })
