# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_runtime_preflight_bridge.py
# desc: MR-F8.7 pure bridge from validated MR-F6 runtime inputs to paired shadow preflight reports without writes.

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from .future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from .future_origin_evidence_adapter import build_market_regime_origin_evidence_bundles
from .future_origin_feature_runtime_bundle import (
    MARKET_REGIME_ORIGIN_FEATURE_RUNTIME_BUNDLE_VERSION,
)
from .contracts import MarketRegimeCode
from .future_horizon_conditioning import condition_horizon_regime_scores
from .future_shadow_adapter import MarketRegimeFutureShadowPacket
from .future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from .future_shadow_candidate_registry import build_default_future_shadow_candidate_registry
from .future_shadow_pair_trace_plan import build_future_shadow_pair_trace_plan

MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION = (
    "prediction.market_regime.future_shadow_runtime_preflight_bridge.mr_f8_7.v1"
)


def _origin_epoch(value: str) -> float:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("mr_f8_runtime_bridge_origin_timestamp_invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError("mr_f8_runtime_bridge_origin_timestamp_timezone_missing")
    return parsed.astimezone(timezone.utc).timestamp()


def _validate_runtime_bundle(runtime_bundle: Mapping[str, Any]) -> Any:
    if not isinstance(runtime_bundle, Mapping):
        raise ValueError("mr_f8_runtime_bridge_runtime_bundle_invalid")
    if runtime_bundle.get("schema_version") != MARKET_REGIME_ORIGIN_FEATURE_RUNTIME_BUNDLE_VERSION:
        raise ValueError("mr_f8_runtime_bridge_runtime_bundle_schema_invalid")
    if runtime_bundle.get("artifact_kind") != "future_origin_feature_runtime_bundle_readiness":
        raise ValueError("mr_f8_runtime_bridge_runtime_bundle_kind_invalid")
    if runtime_bundle.get("runtime_source_ready") is not True:
        raise ValueError("mr_f8_runtime_bridge_runtime_source_not_ready")
    if runtime_bundle.get("source_quality_ready") is not True:
        raise ValueError("mr_f8_runtime_bridge_source_quality_not_ready")
    if runtime_bundle.get("blockers") != ():
        raise ValueError("mr_f8_runtime_bridge_runtime_blockers_present")
    for field in (
        "semantic_substitution_used",
        "candidate_selection_performed",
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "live_parameter_apply_allowed",
        "auto_promotion_allowed",
        "canonical_replacement_allowed",
    ):
        if runtime_bundle.get(field) is not False:
            raise ValueError(f"mr_f8_runtime_bridge_unsafe_runtime_flag:{field}")
    feature_inputs = runtime_bundle.get("feature_inputs")
    if feature_inputs is None:
        raise ValueError("mr_f8_runtime_bridge_feature_inputs_missing")
    return feature_inputs


def build_future_shadow_runtime_preflight_report(
    *,
    packet: MarketRegimeFutureShadowPacket,
    signal_score_report: Mapping[str, Any],
    runtime_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:
    if not isinstance(packet, MarketRegimeFutureShadowPacket):
        raise ValueError("mr_f8_runtime_bridge_packet_invalid")
    feature_inputs = _validate_runtime_bundle(runtime_bundle)
    if runtime_bundle.get("feature_bundle_generated_at") != packet.generated_at:
        raise ValueError("mr_f8_runtime_bridge_origin_mismatch")
    if runtime_bundle.get("feature_snapshot_ref") != packet.feature_snapshot_ref:
        raise ValueError("mr_f8_runtime_bridge_snapshot_mismatch")

    bundles = build_market_regime_origin_evidence_bundles(
        packet=packet,
        signal_score_report=signal_score_report,
        feature_inputs=feature_inputs,
    )
    pairs = []
    candidates = build_default_future_shadow_candidate_registry()
    predecessor_scores_by_candidate: dict[str, Mapping[MarketRegimeCode, float]] = {}
    predecessor_forecast_by_candidate: dict[str, Any] = {}
    seen_bundle_ids: set[str] = set()
    for bundle in bundles:
        bundle_id = str(bundle.get("bundle_id") or "")
        if not bundle_id or bundle_id in seen_bundle_ids:
            raise ValueError("mr_f8_runtime_bridge_bundle_identity_invalid")
        seen_bundle_ids.add(bundle_id)
        evidence = FutureBaselineEvidence(
            origin_timestamp=str(bundle["prediction_origin"]),
            origin_current_state=packet.origin_current_state,
            target_horizon_sec=int(bundle["target_horizon_sec"]),
            feature_snapshot_ref=str(bundle["feature_snapshot_ref"]),
            regime_scores={
                MarketRegimeCode(str(state)): float(value)
                for state, value in bundle["candidate_probability_by_state"].items()
            },
            available_feature_families=(
                "price_structure",
                "volatility",
                "liquidity",
                "source_quality",
                "microprice",
                "session_context",
            ),
            source_timestamp_epoch_sec=feature_inputs.source_timestamp_epoch_sec,
            origin_timestamp_epoch_sec=_origin_epoch(packet.generated_at),
        )
        local_scores = dict(evidence.regime_scores)
        conditioned_forecasts = []
        for candidate in candidates:
            candidate_scores = local_scores
            conditioning = None
            predecessor_scores = predecessor_scores_by_candidate.get(candidate.parameter_set_id)
            predecessor_forecast = predecessor_forecast_by_candidate.get(candidate.parameter_set_id)
            if predecessor_scores is not None and predecessor_forecast is not None:
                candidate_scores, conditioning = condition_horizon_regime_scores(
                    local_scores=local_scores,
                    predecessor_scores=predecessor_scores,
                    predecessor_forecast=predecessor_forecast,
                    transition_prior_fraction_of_top=candidate.transition_prior_fraction_of_top,
                )
            candidate_evidence = FutureBaselineEvidence(
                origin_timestamp=evidence.origin_timestamp,
                origin_current_state=evidence.origin_current_state,
                target_horizon_sec=evidence.target_horizon_sec,
                feature_snapshot_ref=evidence.feature_snapshot_ref,
                regime_scores=candidate_scores,
                available_feature_families=evidence.available_feature_families,
                source_timestamp_epoch_sec=evidence.source_timestamp_epoch_sec,
                origin_timestamp_epoch_sec=evidence.origin_timestamp_epoch_sec,
            )
            forecast = forecast_future_market_regime_baseline(candidate_evidence, candidate=candidate)
            if conditioning is not None:
                forecast = replace(
                    forecast,
                    metadata={**dict(forecast.metadata), "horizon_conditioning": dict(conditioning)},
                )
            conditioned_forecasts.append(forecast)
            predecessor_scores_by_candidate[candidate.parameter_set_id] = candidate_scores
            predecessor_forecast_by_candidate[candidate.parameter_set_id] = forecast

        pair = build_future_shadow_candidate_pair(
            evidence=evidence,
            candidates=candidates,
            precomputed_forecasts=tuple(conditioned_forecasts),
        )
        trace_plan = build_future_shadow_pair_trace_plan(pair=pair)
        pairs.append(MappingProxyType({
            "source_bundle_id": bundle_id,
            "origin_evidence_bundle": bundle,
            **dict(pair),
            "trace_plan": trace_plan,
        }))

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_runtime_preflight_report",
        "prediction_origin": packet.generated_at,
        "feature_snapshot_ref": packet.feature_snapshot_ref,
        "pair_count": len(pairs),
        "pairs": tuple(pairs),
        "runtime_source_ready": True,
        "preflight_only": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "canonical_replacement_allowed": False,
    })
