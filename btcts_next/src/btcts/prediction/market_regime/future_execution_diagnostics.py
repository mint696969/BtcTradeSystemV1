# path: ./btcts_next/src/btcts/prediction/market_regime/future_execution_diagnostics.py
# desc: MR-F9.7 pure multi-origin diagnostics for inference mode, fallback, abstention, freshness, and repeated raw outputs.

from __future__ import annotations

from collections import Counter, defaultdict
from types import MappingProxyType
from typing import Any, Mapping, Sequence

MARKET_REGIME_FUTURE_EXECUTION_DIAGNOSTICS_VERSION = (
    "prediction.market_regime.future_execution_diagnostics.mr_f9_7.v1"
)


def _sequence(value: Any, error: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(error)
    return value


def build_future_execution_diagnostics(
    *,
    execution_evidence_plans: Sequence[Mapping[str, Any]],
    evaluated_at: str,
) -> Mapping[str, Any]:
    plans = _sequence(execution_evidence_plans, "future_execution_diagnostics_plans_invalid")
    if not plans:
        raise ValueError("future_execution_diagnostics_plans_empty")
    if not str(evaluated_at).endswith("Z"):
        raise ValueError("future_execution_diagnostics_evaluated_at_invalid")

    origins: set[str] = set()
    suite_ids: set[str] = set()
    trace_ids: set[str] = set()
    rows: list[Mapping[str, Any]] = []
    slot_sets: list[frozenset[tuple[int, str]]] = []
    for index, plan in enumerate(plans):
        if not isinstance(plan, Mapping):
            raise ValueError(f"future_execution_diagnostics_plan_invalid:{index}")
        if plan.get("artifact_kind") != "future_shadow_origin_execution_evidence_set":
            raise ValueError("future_execution_diagnostics_plan_kind_invalid")
        origin = str(plan.get("generated_at") or "")
        suite_id = str(plan.get("suite_id") or "")
        if not origin.endswith("Z") or not suite_id:
            raise ValueError("future_execution_diagnostics_plan_identity_invalid")
        plan_rows = _sequence(plan.get("rows"), "future_execution_diagnostics_rows_invalid")
        if len(plan_rows) != int(plan.get("evidence_count") or 0):
            raise ValueError("future_execution_diagnostics_evidence_count_mismatch")
        local_ids = tuple(str(row.get("trace_id") or "") for row in plan_rows if isinstance(row, Mapping))
        if len(local_ids) != len(plan_rows) or any(not item for item in local_ids):
            raise ValueError("future_execution_diagnostics_trace_ids_invalid")
        if tuple(plan.get("trace_ids") or ()) != local_ids:
            raise ValueError("future_execution_diagnostics_trace_set_mismatch")
        if any(item in trace_ids for item in local_ids):
            raise ValueError("future_execution_diagnostics_duplicate_trace_id")
        local_slots: set[tuple[int, str]] = set()
        for row in plan_rows:
            row_origin = str(row.get("prediction_origin") or "")
            generated_at = str(row.get("generated_at") or "")
            horizon = int(row.get("target_horizon_sec") or 0)
            candidate = str(row.get("parameter_set_id") or "")
            if row_origin != origin or generated_at != origin:
                raise ValueError("future_execution_diagnostics_row_origin_mismatch")
            if horizon <= 0 or not candidate:
                raise ValueError("future_execution_diagnostics_row_identity_invalid")
            slot = (horizon, candidate)
            if slot in local_slots:
                raise ValueError("future_execution_diagnostics_duplicate_slot")
            local_slots.add(slot)
        origins.add(origin)
        suite_ids.add(suite_id)
        trace_ids.update(local_ids)
        rows.extend(plan_rows)
        slot_sets.append(frozenset(local_slots))

    if len(origins) != len(plans):
        raise ValueError("future_execution_diagnostics_duplicate_origin")
    if len(suite_ids) != len(plans):
        raise ValueError("future_execution_diagnostics_duplicate_suite_id")
    if len(set(slot_sets)) != 1:
        raise ValueError("future_execution_diagnostics_slot_set_mismatch")

    grouped: dict[tuple[int, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("future_execution_diagnostics_row_invalid")
        horizon = int(row.get("target_horizon_sec") or 0)
        candidate = str(row.get("parameter_set_id") or "")
        if horizon <= 0 or not candidate:
            raise ValueError("future_execution_diagnostics_row_identity_invalid")
        grouped[(horizon, candidate)].append(row)

    summaries = []
    for (horizon, candidate), items in sorted(grouped.items()):
        inference_counts = Counter(str(row.get("inference_mode") or "") for row in items)
        freshness_counts = Counter(str(row.get("source_freshness_state") or "") for row in items)
        raw_values = [row.get("raw_model_score_or_probability") for row in items]
        non_null_raw = [float(value) for value in raw_values if value is not None]
        semantics = {str(row.get("raw_output_semantics") or "") for row in items}
        if "" in semantics:
            raise ValueError("future_execution_diagnostics_raw_semantics_missing")
        fallback_count = sum(1 for row in items if row.get("fallback_used") is True)
        abstention_count = sum(1 for row in items if row.get("abstention_decision") is True)
        stale_count = sum(
            count for state, count in freshness_counts.items()
            if state.upper() != "FRESH"
        )
        repeated_raw_count = 0
        if non_null_raw:
            repeated_raw_count = len(non_null_raw) - len(set(non_null_raw))
        summaries.append(MappingProxyType({
            "target_horizon_sec": horizon,
            "parameter_set_id": candidate,
            "origin_count": len(items),
            "full_inference_rate": inference_counts.get("FULL_INFERENCE", 0) / len(items),
            "fallback_rate": fallback_count / len(items),
            "abstention_rate": abstention_count / len(items),
            "stale_or_nonfresh_rate": stale_count / len(items),
            "raw_output_present_rate": len(non_null_raw) / len(items),
            "raw_output_unique_count": len(set(non_null_raw)),
            "raw_output_repeat_count": repeated_raw_count,
            "fixed_raw_output_across_origins": (
                len(non_null_raw) == len(items) and len(set(non_null_raw)) == 1 and len(items) > 1
            ),
            "inference_mode_counts": MappingProxyType(dict(sorted(inference_counts.items()))),
            "freshness_state_counts": MappingProxyType(dict(sorted(freshness_counts.items()))),
            "raw_output_semantics": tuple(sorted(semantics)),
        }))

    horizon_counts = Counter(int(row.get("target_horizon_sec") or 0) for row in rows)
    expected_per_horizon = len(plans) * len({str(row.get("parameter_set_id") or "") for row in rows})
    incomplete_horizons = tuple(
        sorted(horizon for horizon, count in horizon_counts.items() if count != expected_per_horizon)
    )

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_EXECUTION_DIAGNOSTICS_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_execution_diagnostics_report",
        "evaluated_at": evaluated_at,
        "origin_count": len(origins),
        "suite_count": len(suite_ids),
        "trace_count": len(trace_ids),
        "candidate_count": len({str(row.get("parameter_set_id") or "") for row in rows}),
        "horizon_count": len(horizon_counts),
        "incomplete_horizons": incomplete_horizons,
        "summaries": tuple(summaries),
        "diagnostic_only": True,
        "probability_metrics_computed": False,
        "proposal_generated": False,
        "would_write": False,
        "safety": MappingProxyType({
            "read_only_inputs": True,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        }),
    })
