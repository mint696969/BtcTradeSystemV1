# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_origin_execution_suite.py
# desc: Pure MR-F9.2 origin-level assembly for all canonical horizons and both active/shadow candidates.

from __future__ import annotations

from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping

from .future_baseline_model import FutureBaselineEvidence
from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from .future_shadow_pair_execution_plan import FutureExecutionFacts, build_future_shadow_pair_execution_plan
from .future_shadow_pair_trace_plan import build_future_shadow_pair_trace_plan

MARKET_REGIME_FUTURE_SHADOW_ORIGIN_EXECUTION_SUITE_VERSION = (
    "prediction.market_regime.future_shadow_origin_execution_suite.mr_f9_2.v1"
)


def _suite_id(*, origin: str, snapshot: str, trace_ids: tuple[str, ...]) -> str:
    basis = "|".join((origin, snapshot, *trace_ids))
    return "market_regime_mr_f9_origin_suite:" + sha256(basis.encode("utf-8")).hexdigest()


def build_future_shadow_origin_execution_suite(
    *,
    evidence_by_horizon: Mapping[int, FutureBaselineEvidence],
    facts_by_trace_id: Mapping[str, FutureExecutionFacts],
) -> Mapping[str, Any]:
    expected = tuple(int(item) for item in FUTURE_MARKET_REGIME_HORIZONS_SEC)
    observed = tuple(sorted(int(item) for item in evidence_by_horizon.keys()))
    if observed != tuple(sorted(expected)):
        raise ValueError(
            "future_shadow_origin_execution_horizon_set_mismatch:"
            f"expected={','.join(map(str, expected))}:observed={','.join(map(str, observed))}"
        )
    if any(not isinstance(evidence_by_horizon[item], FutureBaselineEvidence) for item in expected):
        raise ValueError("future_shadow_origin_execution_evidence_contract_invalid")

    origins = {evidence_by_horizon[item].origin_timestamp for item in expected}
    snapshots = {evidence_by_horizon[item].feature_snapshot_ref for item in expected}
    if len(origins) != 1:
        raise ValueError("future_shadow_origin_execution_origin_mismatch")
    if len(snapshots) != 1:
        raise ValueError("future_shadow_origin_execution_snapshot_mismatch")

    pair_plans = []
    trace_plans = []
    all_trace_ids: list[str] = []
    used_fact_ids: set[str] = set()
    candidate_sets: set[tuple[str, ...]] = set()
    for horizon in expected:
        evidence = evidence_by_horizon[horizon]
        if int(evidence.target_horizon_sec) != horizon:
            raise ValueError("future_shadow_origin_execution_horizon_identity_mismatch")
        pair = build_future_shadow_candidate_pair(evidence=evidence)
        trace_plan = build_future_shadow_pair_trace_plan(pair=pair)
        pair_trace_ids = tuple(str(row["trace_id"]) for row in pair["forecasts"])
        if tuple(trace_plan["trace_ids"]) != tuple(sorted(pair_trace_ids)):
            raise ValueError("future_shadow_origin_execution_trace_plan_set_mismatch")
        local_facts = {
            trace_id: facts_by_trace_id[trace_id]
            for trace_id in pair_trace_ids
            if trace_id in facts_by_trace_id
        }
        plan = build_future_shadow_pair_execution_plan(pair=pair, facts_by_trace_id=local_facts)
        if tuple(plan["trace_ids"]) != tuple(trace_plan["trace_ids"]):
            raise ValueError("future_shadow_origin_execution_pair_trace_set_mismatch")
        pair_plans.append(plan)
        trace_plans.append(trace_plan)
        all_trace_ids.extend(plan["trace_ids"])
        used_fact_ids.update(plan["trace_ids"])
        candidate_sets.add(tuple(sorted(str(row["parameter_set_id"]) for row in plan["rows"])))

    extra = tuple(sorted(set(str(item) for item in facts_by_trace_id.keys()) - used_fact_ids))
    if extra:
        raise ValueError("future_shadow_origin_execution_facts_extra:" + ",".join(extra))
    if len(candidate_sets) != 1:
        raise ValueError("future_shadow_origin_execution_candidate_set_mismatch")
    if len(all_trace_ids) != len(set(all_trace_ids)):
        raise ValueError("future_shadow_origin_execution_duplicate_trace_id")
    if len(pair_plans) != len(expected) or len(trace_plans) != len(expected):
        raise ValueError("future_shadow_origin_execution_pair_count_invalid")
    candidate_count = len(next(iter(candidate_sets)))
    expected_evidence_count = len(expected) * candidate_count
    actual_evidence_count = sum(int(plan["evidence_count"]) for plan in pair_plans)
    if actual_evidence_count != expected_evidence_count:
        raise ValueError("future_shadow_origin_execution_evidence_count_invalid")

    origin = next(iter(origins))
    snapshot = next(iter(snapshots))
    trace_ids = tuple(sorted(all_trace_ids))
    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_ORIGIN_EXECUTION_SUITE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_origin_execution_suite",
        "suite_id": _suite_id(origin=origin, snapshot=snapshot, trace_ids=trace_ids),
        "prediction_origin": origin,
        "feature_snapshot_ref": snapshot,
        "horizons_sec": expected,
        "horizon_count": len(expected),
        "candidate_count": candidate_count,
        "pair_count": len(pair_plans),
        "evidence_count": actual_evidence_count,
        "trace_ids": trace_ids,
        "trace_persistence_plans": tuple(trace_plans),
        "pair_plans": tuple(pair_plans),
        "would_write": False,
        "safety": MappingProxyType({
            "pure": True,
            "all_horizons_required": True,
            "same_origin_required": True,
            "same_snapshot_required": True,
            "facts_are_explicit": True,
            "trace_plans_from_forecast_pairs": True,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        }),
    })
