# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_origin_receipt.py
# desc: MR-F9.4 pure origin receipt binding seven trace plans to one execution-evidence persistence plan.

from __future__ import annotations

from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_execution_evidence_persistence import build_future_execution_evidence_persistence_plan

MARKET_REGIME_FUTURE_SHADOW_ORIGIN_RECEIPT_VERSION = (
    "prediction.market_regime.future_shadow_origin_receipt.mr_f9_4.v1"
)


def _receipt_id(*, suite_id: str, trace_ids: tuple[str, ...]) -> str:
    basis = "|".join((suite_id, *trace_ids))
    return "market_regime_mr_f9_origin_receipt:" + sha256(basis.encode("utf-8")).hexdigest()[:32]


def build_future_shadow_origin_receipt(*, origin_suite: Mapping[str, Any]) -> Mapping[str, Any]:
    if origin_suite.get("artifact_kind") != "future_shadow_origin_execution_suite":
        raise ValueError("future_shadow_origin_receipt_suite_kind_invalid")
    pair_plans = origin_suite.get("pair_plans")
    trace_plans = origin_suite.get("trace_persistence_plans")
    if not isinstance(pair_plans, Sequence) or isinstance(pair_plans, (str, bytes)):
        raise ValueError("future_shadow_origin_receipt_pair_plans_invalid")
    if not isinstance(trace_plans, Sequence) or isinstance(trace_plans, (str, bytes)):
        raise ValueError("future_shadow_origin_receipt_trace_plans_invalid")
    expected_pair_count = int(origin_suite.get("pair_count") or 0)
    if len(pair_plans) != expected_pair_count or len(trace_plans) != expected_pair_count:
        raise ValueError("future_shadow_origin_receipt_pair_count_mismatch")
    if any(not isinstance(plan, Mapping) for plan in trace_plans):
        raise ValueError("future_shadow_origin_receipt_trace_plan_invalid")

    trace_ids = tuple(sorted(
        str(trace_id)
        for plan in trace_plans
        for trace_id in tuple(plan.get("trace_ids") or ())
    ))
    suite_trace_ids = tuple(origin_suite.get("trace_ids") or ())
    if trace_ids != suite_trace_ids:
        raise ValueError("future_shadow_origin_receipt_trace_set_mismatch")
    if len(trace_ids) != int(origin_suite.get("evidence_count") or 0):
        raise ValueError("future_shadow_origin_receipt_trace_count_mismatch")
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_origin_receipt_duplicate_trace_id")
    if any(int(plan.get("trace_count") or 0) != len(tuple(plan.get("trace_ids") or ())) for plan in trace_plans):
        raise ValueError("future_shadow_origin_receipt_trace_plan_count_mismatch")

    execution_plan = build_future_execution_evidence_persistence_plan(origin_suite=origin_suite)
    if tuple(execution_plan.get("trace_ids") or ()) != trace_ids:
        raise ValueError("future_shadow_origin_receipt_execution_trace_set_mismatch")
    if int(execution_plan.get("evidence_count") or 0) != len(trace_ids):
        raise ValueError("future_shadow_origin_receipt_execution_count_mismatch")

    origins = {str(plan.get("generated_at") or "") for plan in trace_plans}
    origins.add(str(execution_plan.get("generated_at") or ""))
    origins.add(str(origin_suite.get("prediction_origin") or ""))
    if len(origins) != 1 or "" in origins:
        raise ValueError("future_shadow_origin_receipt_origin_mismatch")

    suite_id = str(origin_suite.get("suite_id") or "")
    if not suite_id:
        raise ValueError("future_shadow_origin_receipt_suite_id_missing")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_ORIGIN_RECEIPT_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_origin_receipt",
        "receipt_id": _receipt_id(suite_id=suite_id, trace_ids=trace_ids),
        "suite_id": suite_id,
        "prediction_origin": next(iter(origins)),
        "feature_snapshot_ref": str(origin_suite.get("feature_snapshot_ref") or ""),
        "horizon_count": int(origin_suite.get("horizon_count") or 0),
        "candidate_count": int(origin_suite.get("candidate_count") or 0),
        "pair_count": len(trace_plans),
        "trace_count": len(trace_ids),
        "execution_evidence_count": int(execution_plan["evidence_count"]),
        "trace_ids": trace_ids,
        "trace_persistence_plans": tuple(trace_plans),
        "execution_evidence_persistence_plan": MappingProxyType(dict(execution_plan)),
        "would_write": False,
        "safety": MappingProxyType({
            "pure": True,
            "trace_and_execution_sets_identical": True,
            "trace_plans_reused_without_reverse_projection": True,
            "writers_invoked": False,
            "writes_dhot": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        }),
    })
