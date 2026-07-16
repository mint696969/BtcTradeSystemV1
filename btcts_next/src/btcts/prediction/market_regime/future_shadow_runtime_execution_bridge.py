# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_runtime_execution_bridge.py
# desc: MR-F9.12 pure bridge from validated MR-F8 runtime preflight pairs plus explicit trace facts to immutable execution plans.

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_shadow_pair_execution_plan import (
    FutureExecutionFacts,
    build_future_shadow_pair_execution_plan,
)
from .future_shadow_runtime_preflight_bridge import (
    MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION,
)

MARKET_REGIME_FUTURE_SHADOW_RUNTIME_EXECUTION_BRIDGE_VERSION = (
    "prediction.market_regime.future_shadow_runtime_execution_bridge.mr_f9_12.v1"
)


def _pairs(value: Any) -> Sequence[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("mr_f9_runtime_execution_bridge_pairs_invalid")
    if any(not isinstance(item, Mapping) for item in value):
        raise ValueError("mr_f9_runtime_execution_bridge_pair_invalid")
    return value


def build_future_shadow_runtime_execution_bridge(
    *,
    preflight_report: Mapping[str, Any],
    facts_by_trace_id: Mapping[str, FutureExecutionFacts],
) -> Mapping[str, Any]:
    if not isinstance(preflight_report, Mapping):
        raise ValueError("mr_f9_runtime_execution_bridge_preflight_invalid")
    if (
        preflight_report.get("schema_version")
        != MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION
    ):
        raise ValueError("mr_f9_runtime_execution_bridge_preflight_schema_invalid")
    if preflight_report.get("artifact_kind") != "future_shadow_runtime_preflight_report":
        raise ValueError("mr_f9_runtime_execution_bridge_preflight_kind_invalid")
    if preflight_report.get("runtime_source_ready") is not True:
        raise ValueError("mr_f9_runtime_execution_bridge_runtime_source_not_ready")
    if preflight_report.get("preflight_only") is not True:
        raise ValueError("mr_f9_runtime_execution_bridge_preflight_only_required")
    for field in (
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "canonical_replacement_allowed",
    ):
        if preflight_report.get(field) is not False:
            raise ValueError(f"mr_f9_runtime_execution_bridge_unsafe_preflight_flag:{field}")
    if not isinstance(facts_by_trace_id, Mapping):
        raise ValueError("mr_f9_runtime_execution_bridge_facts_invalid")

    pairs = tuple(_pairs(preflight_report.get("pairs")))
    if int(preflight_report.get("pair_count") or 0) != len(pairs):
        raise ValueError("mr_f9_runtime_execution_bridge_pair_count_mismatch")
    if len(pairs) != len(FUTURE_MARKET_REGIME_HORIZONS_SEC):
        raise ValueError("mr_f9_runtime_execution_bridge_pair_count_invalid")

    prediction_origin = str(preflight_report.get("prediction_origin") or "")
    feature_snapshot_ref = str(preflight_report.get("feature_snapshot_ref") or "")
    if not prediction_origin or not feature_snapshot_ref:
        raise ValueError("mr_f9_runtime_execution_bridge_report_identity_missing")

    expected_horizons = tuple(sorted(int(item) for item in FUTURE_MARKET_REGIME_HORIZONS_SEC))
    observed_horizons: list[int] = []
    expected_trace_ids: list[str] = []
    candidate_sets: list[tuple[str, ...]] = []
    source_bundle_ids: list[str] = []
    pair_ids: list[str] = []

    for pair in pairs:
        if pair.get("artifact_kind") != "future_shadow_candidate_pair":
            raise ValueError("mr_f9_runtime_execution_bridge_pair_kind_invalid")
        slot = pair.get("slot_identity")
        forecasts = pair.get("forecasts")
        trace_plan = pair.get("trace_plan")
        if not isinstance(slot, Mapping):
            raise ValueError("mr_f9_runtime_execution_bridge_slot_identity_missing")
        if not isinstance(forecasts, Sequence) or isinstance(forecasts, (str, bytes)):
            raise ValueError("mr_f9_runtime_execution_bridge_forecasts_invalid")
        if len(forecasts) != 2 or any(not isinstance(row, Mapping) for row in forecasts):
            raise ValueError("mr_f9_runtime_execution_bridge_candidate_pair_invalid")
        if not isinstance(trace_plan, Mapping):
            raise ValueError("mr_f9_runtime_execution_bridge_trace_plan_missing")
        if trace_plan.get("artifact_kind") != "future_shadow_pair_trace_plan":
            raise ValueError("mr_f9_runtime_execution_bridge_trace_plan_kind_invalid")
        persistence = trace_plan.get("persistence_plan")
        if not isinstance(persistence, Mapping) or persistence.get("would_write") is not False:
            raise ValueError("mr_f9_runtime_execution_bridge_trace_plan_write_enabled")

        horizon = int(slot.get("target_horizon_sec") or 0)
        forecast_horizons = {int(row.get("target_horizon_sec") or 0) for row in forecasts}
        forecast_origins = {str(row.get("origin_timestamp") or "") for row in forecasts}
        forecast_snapshots = {str(row.get("feature_snapshot_ref") or "") for row in forecasts}
        if forecast_horizons != {horizon}:
            raise ValueError("mr_f9_runtime_execution_bridge_slot_forecast_horizon_mismatch")
        if forecast_origins != {prediction_origin}:
            raise ValueError("mr_f9_runtime_execution_bridge_report_origin_mismatch")
        if forecast_snapshots != {feature_snapshot_ref}:
            raise ValueError("mr_f9_runtime_execution_bridge_report_snapshot_mismatch")
        observed_horizons.append(horizon)
        pair_id = str(pair.get("pair_id") or "")
        source_bundle_id = str(pair.get("source_bundle_id") or "")
        if not pair_id or not source_bundle_id:
            raise ValueError("mr_f9_runtime_execution_bridge_pair_identity_missing")
        pair_ids.append(pair_id)
        source_bundle_ids.append(source_bundle_id)

        forecast_trace_ids = tuple(str(row.get("trace_id") or "") for row in forecasts)
        forecast_candidate_ids = tuple(str(row.get("parameter_set_id") or "") for row in forecasts)
        if any(not item for item in forecast_trace_ids + forecast_candidate_ids):
            raise ValueError("mr_f9_runtime_execution_bridge_forecast_identity_missing")
        if len(set(forecast_trace_ids)) != 2 or len(set(forecast_candidate_ids)) != 2:
            raise ValueError("mr_f9_runtime_execution_bridge_forecast_identity_duplicate")
        if set(trace_plan.get("trace_ids") or ()) != set(forecast_trace_ids):
            raise ValueError("mr_f9_runtime_execution_bridge_trace_plan_identity_mismatch")
        expected_trace_ids.extend(forecast_trace_ids)
        candidate_sets.append(tuple(sorted(forecast_candidate_ids)))

    if tuple(sorted(observed_horizons)) != expected_horizons:
        raise ValueError("mr_f9_runtime_execution_bridge_horizon_set_invalid")
    if len(set(pair_ids)) != len(pair_ids):
        raise ValueError("mr_f9_runtime_execution_bridge_pair_id_duplicate")
    if len(set(source_bundle_ids)) != len(source_bundle_ids):
        raise ValueError("mr_f9_runtime_execution_bridge_source_bundle_id_duplicate")
    if len(set(expected_trace_ids)) != len(expected_trace_ids):
        raise ValueError("mr_f9_runtime_execution_bridge_trace_id_duplicate")
    if len(set(candidate_sets)) != 1:
        raise ValueError("mr_f9_runtime_execution_bridge_candidate_set_mismatch")

    expected_trace_set = set(expected_trace_ids)
    fact_trace_set = {str(item) for item in facts_by_trace_id}
    missing_facts = tuple(sorted(expected_trace_set - fact_trace_set))
    extra_facts = tuple(sorted(fact_trace_set - expected_trace_set))
    if missing_facts:
        raise ValueError("mr_f9_runtime_execution_bridge_facts_missing:" + repr(missing_facts))
    if extra_facts:
        raise ValueError("mr_f9_runtime_execution_bridge_facts_extra:" + repr(extra_facts))
    if any(not isinstance(facts_by_trace_id[trace_id], FutureExecutionFacts) for trace_id in expected_trace_ids):
        raise ValueError("mr_f9_runtime_execution_bridge_fact_contract_invalid")

    plans = tuple(
        build_future_shadow_pair_execution_plan(
            pair=pair,
            facts_by_trace_id={
                str(row["trace_id"]): facts_by_trace_id[str(row["trace_id"])]
                for row in pair["forecasts"]
            },
        )
        for pair in pairs
    )
    evidence_rows = tuple(row for plan in plans for row in plan["rows"])
    if len(plans) != 7 or len(evidence_rows) != 14:
        raise ValueError("mr_f9_runtime_execution_bridge_output_count_invalid")
    output_horizons = tuple(sorted({int(row["target_horizon_sec"]) for row in evidence_rows}))
    if output_horizons != expected_horizons:
        raise ValueError("mr_f9_runtime_execution_bridge_output_horizon_set_invalid")
    if {str(row["prediction_origin"]) for row in evidence_rows} != {prediction_origin}:
        raise ValueError("mr_f9_runtime_execution_bridge_output_origin_mismatch")
    if {str(row["feature_snapshot_ref"]) for row in evidence_rows} != {feature_snapshot_ref}:
        raise ValueError("mr_f9_runtime_execution_bridge_output_snapshot_mismatch")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_RUNTIME_EXECUTION_BRIDGE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_runtime_execution_bridge_report",
        "prediction_origin": prediction_origin,
        "feature_snapshot_ref": feature_snapshot_ref,
        "candidate_ids": candidate_sets[0],
        "pair_count": len(plans),
        "trace_count": len(expected_trace_ids),
        "evidence_count": len(evidence_rows),
        "pair_plans": plans,
        "evidence_rows": evidence_rows,
        "source_bundle_ids": tuple(source_bundle_ids),
        "facts_are_explicit": True,
        "facts_inferred_from_preflight": False,
        "would_write": False,
        "safety": MappingProxyType({
            "pure": True,
            "read_only_input": True,
            "facts_are_explicit": True,
            "facts_inferred_from_preflight": False,
            "legacy_confidence_promoted_to_probability": False,
            "writer_invoked": False,
            "writes_dhot": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
        }),
    })
