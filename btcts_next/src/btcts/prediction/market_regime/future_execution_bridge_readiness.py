# path: ./btcts_next/src/btcts/prediction/market_regime/future_execution_bridge_readiness.py
# desc: MR-F9.10 read-only audit of whether an existing MarketRegime trace row contains enough explicit truth to build paired future execution evidence.

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC

MARKET_REGIME_FUTURE_EXECUTION_BRIDGE_READINESS_VERSION = (
    "prediction.market_regime.future_execution_bridge_readiness.mr_f9_10.v1"
)

_REQUIRED_SAFETY_FALSE = (
    "scheduler_enabled",
    "broker_private_api_allowed",
    "autotrade_trigger_allowed",
    "order_intent_submitted",
    "trade_ledger_append_allowed",
    "would_send_to_broker",
)


def _sequence(value: Any, error: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(error)
    return value


def audit_market_regime_trace_for_future_execution_bridge(
    *,
    trace_row: Mapping[str, Any],
    expected_active_parameter_set_id: str,
    expected_shadow_parameter_set_id: str,
) -> Mapping[str, Any]:
    if not isinstance(trace_row, Mapping):
        raise ValueError("future_execution_bridge_trace_invalid")
    if trace_row.get("artifact_kind") != "trace_row":
        raise ValueError("future_execution_bridge_trace_kind_invalid")
    if trace_row.get("prediction_family_id") != "market_regime":
        raise ValueError("future_execution_bridge_family_invalid")

    active_id = str(expected_active_parameter_set_id or "").strip()
    shadow_id = str(expected_shadow_parameter_set_id or "").strip()
    if not active_id or not shadow_id:
        raise ValueError("future_execution_bridge_candidate_identity_missing")
    if active_id == shadow_id:
        raise ValueError("future_execution_bridge_candidate_identity_duplicate")

    blockers: list[str] = []
    warnings: list[str] = []

    generated_at = str(trace_row.get("generated_at") or "")
    run_id = str(trace_row.get("run_id") or "")
    if not generated_at:
        blockers.append("prediction_origin_missing")
    if not run_id:
        blockers.append("run_id_missing")

    safety = trace_row.get("safety")
    if not isinstance(safety, Mapping):
        blockers.append("trace_safety_missing")
        safety = {}
    for key in _REQUIRED_SAFETY_FALSE:
        if safety.get(key) is not False:
            blockers.append(f"unsafe_trace_flag:{key}")

    prediction_summary = trace_row.get("prediction_summary")
    if not isinstance(prediction_summary, Mapping):
        raise ValueError("future_execution_bridge_prediction_summary_invalid")
    horizons = _sequence(
        prediction_summary.get("horizons"),
        "future_execution_bridge_horizons_invalid",
    )
    if any(not isinstance(row, Mapping) for row in horizons):
        raise ValueError("future_execution_bridge_horizon_row_invalid")

    canonical = tuple(sorted(int(item) for item in FUTURE_MARKET_REGIME_HORIZONS_SEC))
    observed_future = tuple(sorted({
        int(row.get("horizon_sec") or 0)
        for row in horizons
        if int(row.get("horizon_sec") or 0) > 0
    }))
    if observed_future != canonical:
        blockers.append("canonical_future_horizon_set_missing")

    future_rows = tuple(
        row
        for row in horizons
        if int(row.get("horizon_sec") or 0) > 0
    )
    observed_slots = tuple(
        (
            int(row.get("horizon_sec") or 0),
            str(row.get("parameter_set_id") or ""),
        )
        for row in future_rows
    )
    if len(observed_slots) != len(set(observed_slots)):
        blockers.append("duplicate_future_candidate_slot")
    expected_slots = {
        (horizon, candidate)
        for horizon in canonical
        for candidate in (active_id, shadow_id)
    }
    observed_slot_set = set(observed_slots)
    missing_slots = tuple(sorted(expected_slots - observed_slot_set))
    unexpected_slots = tuple(sorted(observed_slot_set - expected_slots))
    if missing_slots:
        blockers.append("expected_future_candidate_slots_missing")
    if unexpected_slots:
        blockers.append("unexpected_future_candidate_slots_present")

    parameter_ids = {
        str(row.get("parameter_set_id") or "")
        for row in horizons
        if int(row.get("horizon_sec") or 0) > 0
    }
    if "" in parameter_ids:
        blockers.append("parameter_set_identity_missing")
        parameter_ids.discard("")
    if active_id not in parameter_ids:
        blockers.append("expected_active_candidate_missing")
    if shadow_id not in parameter_ids:
        blockers.append("expected_shadow_candidate_missing")
    if parameter_ids == {active_id}:
        blockers.append("active_only_runtime_trace")
    if len(parameter_ids) < 2:
        blockers.append("paired_candidate_execution_missing")

    required_explicit_fields = (
        "inference_mode",
        "raw_model_score_or_probability",
        "raw_output_semantics",
        "source_freshness_state",
        "source_age_sec",
        "abstention_decision",
        "abstain_reason",
        "fallback_used",
        "fallback_reason",
        "fallback_source_ref",
        "feature_snapshot_ref",
        "target_definition_version",
        "forecast_status",
        "model_id",
        "logic_version",
    )
    missing_fields = tuple(sorted({
        field
        for field in required_explicit_fields
        if any(field not in row for row in horizons if int(row.get("horizon_sec") or 0) > 0)
    }))
    blockers.extend(f"explicit_field_missing:{field}" for field in missing_fields)

    legacy_confidence_present = any(
        "confidence_percent" in row
        for row in horizons
        if int(row.get("horizon_sec") or 0) > 0
    )
    if legacy_confidence_present:
        warnings.append("legacy_confidence_is_not_raw_probability")
    if any(
        str(row.get("freshness_state") or "")
        for row in horizons
        if int(row.get("horizon_sec") or 0) > 0
    ):
        warnings.append("legacy_freshness_state_requires_explicit_bridge_mapping")

    source_refs = trace_row.get("source_refs")
    if not isinstance(source_refs, Mapping) or not source_refs:
        blockers.append("feature_source_refs_missing")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers
    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_EXECUTION_BRIDGE_READINESS_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_execution_bridge_readiness_report",
        "run_id": run_id,
        "prediction_origin": generated_at,
        "expected_active_parameter_set_id": active_id,
        "expected_shadow_parameter_set_id": shadow_id,
        "observed_parameter_set_ids": tuple(sorted(parameter_ids)),
        "canonical_horizons_sec": canonical,
        "observed_future_horizons_sec": observed_future,
        "expected_slot_count": len(expected_slots),
        "observed_slot_count": len(observed_slot_set),
        "missing_slots": missing_slots,
        "unexpected_slots": unexpected_slots,
        "bridge_ready": ready,
        "blocker_count": len(unique_blockers),
        "blockers": unique_blockers,
        "warning_count": len(unique_warnings),
        "warnings": unique_warnings,
        "facts_inferred_from_legacy_display": False,
        "legacy_confidence_promoted_to_probability": False,
        "would_build_evidence": ready,
        "would_write": False,
        "safety": MappingProxyType({
            "read_only_input": True,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_trace_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
        }),
    })
