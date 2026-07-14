# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_writer_preflight.py
# desc: MR-F6.16 pure bridge from one explicit runtime feature bundle to an immutable seven-horizon writer preflight.

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_origin_evidence_adapter import (
    MarketRegimeOriginFeatureInputs,
    build_market_regime_origin_evidence_bundles,
)
from .future_origin_evidence_writer import (
    MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
    build_origin_evidence_write_plan,
    preflight_origin_evidence_write,
)
from .future_origin_feature_runtime_bundle import (
    MARKET_REGIME_ORIGIN_FEATURE_RUNTIME_BUNDLE_VERSION,
)
from .future_shadow_adapter import MarketRegimeFutureShadowPacket

MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_PREFLIGHT_VERSION = (
    "prediction.market_regime.origin_evidence_writer_preflight.mr_f6_16.v1"
)


def _validate_runtime_bundle(runtime_bundle: Mapping[str, Any]) -> MarketRegimeOriginFeatureInputs:
    if not isinstance(runtime_bundle, Mapping):
        raise ValueError("origin_evidence_writer_preflight_runtime_bundle_type_invalid")
    if runtime_bundle.get("schema_version") != MARKET_REGIME_ORIGIN_FEATURE_RUNTIME_BUNDLE_VERSION:
        raise ValueError("origin_evidence_writer_preflight_runtime_bundle_schema_mismatch")
    if runtime_bundle.get("artifact_kind") != "future_origin_feature_runtime_bundle_readiness":
        raise ValueError("origin_evidence_writer_preflight_runtime_bundle_kind_mismatch")
    if runtime_bundle.get("runtime_source_ready") is not True:
        raise ValueError("origin_evidence_writer_preflight_runtime_bundle_not_ready")
    if runtime_bundle.get("source_quality_ready") is not True:
        raise ValueError("origin_evidence_writer_preflight_source_quality_not_ready")
    blockers = runtime_bundle.get("blockers")
    if blockers != ():
        raise ValueError("origin_evidence_writer_preflight_runtime_blockers_present")
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
            raise ValueError(f"origin_evidence_writer_preflight_unsafe_runtime_flag:{field}")
    if runtime_bundle.get("explicit_candidate_required") is not True:
        raise ValueError("origin_evidence_writer_preflight_explicit_candidate_contract_missing")
    candidate_id = str(runtime_bundle.get("shadow_candidate_id") or "").strip()
    parameter_set_id = str(runtime_bundle.get("parameter_set_id") or "").strip()
    if not candidate_id or parameter_set_id != candidate_id:
        raise ValueError("origin_evidence_writer_preflight_candidate_parameter_identity_mismatch")
    feature_inputs = runtime_bundle.get("feature_inputs")
    if not isinstance(feature_inputs, MarketRegimeOriginFeatureInputs):
        raise ValueError("origin_evidence_writer_preflight_feature_inputs_invalid")
    return feature_inputs


def build_origin_evidence_writer_preflight(
    *,
    packet: MarketRegimeFutureShadowPacket,
    signal_score_report: Mapping[str, Any],
    runtime_bundle: Mapping[str, Any],
    generated_at: str,
    writer_id: str,
    writer_contract_version: str,
    executed_at: str,
    approval: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    if not isinstance(packet, MarketRegimeFutureShadowPacket):
        raise ValueError("origin_evidence_writer_preflight_packet_invalid")
    feature_inputs = _validate_runtime_bundle(runtime_bundle)
    if packet.generated_at != generated_at:
        raise ValueError("origin_evidence_writer_preflight_generated_at_origin_mismatch")
    if runtime_bundle.get("feature_bundle_generated_at") != packet.generated_at:
        raise ValueError("origin_evidence_writer_preflight_runtime_origin_mismatch")
    if runtime_bundle.get("feature_snapshot_ref") != packet.feature_snapshot_ref:
        raise ValueError("origin_evidence_writer_preflight_runtime_snapshot_mismatch")

    bundles = build_market_regime_origin_evidence_bundles(
        packet=packet,
        signal_score_report=signal_score_report,
        feature_inputs=feature_inputs,
    )
    if len(bundles) != len(FUTURE_MARKET_REGIME_HORIZONS_SEC):
        raise RuntimeError("origin_evidence_writer_preflight_bundle_count_invalid")
    horizons = tuple(int(item["target_horizon_sec"]) for item in bundles)
    if horizons != FUTURE_MARKET_REGIME_HORIZONS_SEC:
        raise RuntimeError("origin_evidence_writer_preflight_horizon_order_invalid")
    origins = tuple(dict.fromkeys(str(item["prediction_origin"]) for item in bundles))
    snapshot_refs = tuple(dict.fromkeys(str(item["feature_snapshot_ref"]) for item in bundles))
    if origins != (packet.generated_at,):
        raise RuntimeError("origin_evidence_writer_preflight_origin_batch_not_immutable")
    if snapshot_refs != (packet.feature_snapshot_ref,):
        raise RuntimeError("origin_evidence_writer_preflight_snapshot_batch_not_immutable")

    plan = build_origin_evidence_write_plan(
        generated_at=generated_at,
        writer_id=writer_id,
        writer_contract_version=writer_contract_version,
        bundles=bundles,
        maximum_batch_rows=len(FUTURE_MARKET_REGIME_HORIZONS_SEC),
    )

    approval_present = approval is not None
    writer_preflight = None
    blockers = []
    if not approval_present:
        blockers.append("operator_approval_missing")
    else:
        writer_preflight = preflight_origin_evidence_write(
            plan=plan,
            approval=approval,
            bundles=bundles,
            executed_at=executed_at,
        )
        if writer_preflight.get("preflight_only") is not True:
            raise RuntimeError("origin_evidence_writer_preflight_execution_boundary_breached")
        if writer_preflight.get("would_write") is not False:
            raise RuntimeError("origin_evidence_writer_preflight_would_write_invalid")

    preflight_ready = writer_preflight is not None
    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_PREFLIGHT_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_single_batch_writer_preflight",
        "prediction_origin": packet.generated_at,
        "feature_snapshot_ref": packet.feature_snapshot_ref,
        "shadow_candidate_id": runtime_bundle["shadow_candidate_id"],
        "origin_feature_parameter_set_id": runtime_bundle["parameter_set_id"],
        "forecast_parameter_set_ids": tuple(dict.fromkeys(
            str(item["parameter_set_id"]) for item in bundles
        )),
        "target_horizons_sec": horizons,
        "bundle_count": len(bundles),
        "bundle_ids": tuple(item["bundle_id"] for item in bundles),
        "write_plan": plan,
        "approval_present": approval_present,
        "writer_preflight": writer_preflight,
        "preflight_ready": preflight_ready,
        "blockers": tuple(blockers),
        "writer_contract_schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
        "single_origin_batch": True,
        "preflight_only": True,
        "write_allowed": False,
        "would_write": False,
        "writer_invoked": False,
        "write_execution_performed": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "counts_as_real_shadow_evidence": False,
        "candidate_selection_performed": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })
