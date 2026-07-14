# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_collection_plan.py
# desc: MR-F6.14 read-only operational evidence collection readiness plan without writer activation.

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence, Tuple

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_origin_evidence_runtime_source import (
    MARKET_REGIME_ORIGIN_EVIDENCE_RUNTIME_SOURCE_VERSION,
)
from .future_origin_evidence_writer import ORIGIN_EVIDENCE_NAMESPACE

MARKET_REGIME_ORIGIN_EVIDENCE_COLLECTION_PLAN_VERSION = (
    "prediction.market_regime.origin_evidence_collection_plan.mr_f6_14.v1"
)


@dataclass(frozen=True)
class OriginEvidenceCollectionPolicy:
    policy_id: str
    minimum_origin_batches: int
    minimum_observed_slots_per_horizon: int
    required_horizons_sec: Tuple[int, ...] = FUTURE_MARKET_REGIME_HORIZONS_SEC

    def __post_init__(self) -> None:
        if not str(self.policy_id).strip():
            raise ValueError("origin_evidence_collection_policy_id_missing")
        for name, value in (
            ("minimum_origin_batches", self.minimum_origin_batches),
            ("minimum_observed_slots_per_horizon", self.minimum_observed_slots_per_horizon),
        ):
            if type(value) is not int or value <= 0:
                raise ValueError(f"origin_evidence_collection_policy_count_invalid:{name}")
        horizons = tuple(int(item) for item in self.required_horizons_sec)
        if horizons != FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError("origin_evidence_collection_policy_horizons_invalid")
        object.__setattr__(self, "required_horizons_sec", horizons)

    def to_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "policy_id": self.policy_id,
            "minimum_origin_batches": int(self.minimum_origin_batches),
            "minimum_observed_slots_per_horizon": int(self.minimum_observed_slots_per_horizon),
            "required_horizons_sec": self.required_horizons_sec,
        })


def build_origin_evidence_collection_plan(
    *,
    generated_at: str,
    policy: OriginEvidenceCollectionPolicy,
    runtime_source_readiness: Mapping[str, Any],
    existing_artifact_relpaths: Sequence[str],
    observed_slot_count_by_horizon: Mapping[int, int],
    operator_approval_present: bool = False,
) -> Mapping[str, Any]:
    if not str(generated_at).strip():
        raise ValueError("origin_evidence_collection_plan_generated_at_missing")
    if not isinstance(policy, OriginEvidenceCollectionPolicy):
        raise ValueError("origin_evidence_collection_plan_policy_type_invalid")
    if not isinstance(runtime_source_readiness, Mapping):
        raise ValueError("origin_evidence_collection_plan_runtime_readiness_type_invalid")
    if runtime_source_readiness.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_RUNTIME_SOURCE_VERSION:
        raise ValueError("origin_evidence_collection_plan_runtime_readiness_schema_mismatch")
    if runtime_source_readiness.get("artifact_kind") != "future_origin_evidence_runtime_source_readiness":
        raise ValueError("origin_evidence_collection_plan_runtime_readiness_kind_mismatch")
    for field in (
        "semantic_substitution_used",
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "canonical_replacement",
        "live_parameter_apply_allowed",
    ):
        if runtime_source_readiness.get(field) is not False:
            raise ValueError(f"origin_evidence_collection_plan_unsafe_runtime_flag:{field}")
    if not isinstance(operator_approval_present, bool):
        raise ValueError("origin_evidence_collection_plan_operator_approval_flag_invalid")
    if isinstance(existing_artifact_relpaths, (str, bytes)) or not isinstance(existing_artifact_relpaths, Sequence):
        raise ValueError("origin_evidence_collection_plan_artifact_inventory_invalid")
    if not isinstance(observed_slot_count_by_horizon, Mapping):
        raise ValueError("origin_evidence_collection_plan_observation_inventory_invalid")

    relpaths = tuple(str(item).replace("\\", "/").strip("/") for item in existing_artifact_relpaths)
    if any(not item for item in relpaths):
        raise ValueError("origin_evidence_collection_plan_artifact_relpath_invalid")
    if len(relpaths) != len(set(relpaths)):
        raise ValueError("origin_evidence_collection_plan_duplicate_artifact_relpath")
    foreign = tuple(item for item in relpaths if not item.startswith(ORIGIN_EVIDENCE_NAMESPACE + "/"))
    if foreign:
        raise ValueError("origin_evidence_collection_plan_foreign_artifact_path")

    normalized_observed_counts: dict[int, int] = {}
    for raw_horizon, raw_count in observed_slot_count_by_horizon.items():
        if type(raw_horizon) is not int or type(raw_count) is not int or raw_count < 0:
            raise ValueError("origin_evidence_collection_plan_observation_inventory_invalid")
        normalized_observed_counts[raw_horizon] = raw_count
    if tuple(normalized_observed_counts) != policy.required_horizons_sec:
        raise ValueError("origin_evidence_collection_plan_observation_horizons_mismatch")

    raw_runtime_ready = runtime_source_readiness.get("runtime_source_ready")
    if not isinstance(raw_runtime_ready, bool):
        raise ValueError("origin_evidence_collection_plan_runtime_ready_flag_invalid")
    raw_runtime_blockers = runtime_source_readiness.get("blockers", ())
    if isinstance(raw_runtime_blockers, (str, bytes)) or not isinstance(raw_runtime_blockers, Sequence):
        raise ValueError("origin_evidence_collection_plan_runtime_blockers_invalid")
    runtime_blockers = tuple(str(item).strip() for item in raw_runtime_blockers)
    if any(not item for item in runtime_blockers):
        raise ValueError("origin_evidence_collection_plan_runtime_blocker_empty")
    runtime_ready = raw_runtime_ready
    if runtime_ready and runtime_blockers:
        raise ValueError("origin_evidence_collection_plan_ready_runtime_has_blockers")
    blockers = []
    if not runtime_ready:
        blockers.append("runtime_source_not_ready")
        blockers.extend(f"runtime:{item}" for item in runtime_blockers)
    if not relpaths:
        blockers.append("origin_evidence_namespace_empty")
    if not operator_approval_present:
        blockers.append("operator_approval_missing")

    collection_start_ready = runtime_ready and operator_approval_present
    origin_batch_sufficient = len(relpaths) >= int(policy.minimum_origin_batches)
    if collection_start_ready and not origin_batch_sufficient:
        blockers.append("minimum_origin_batches_not_met")

    horizon_requirements = tuple(MappingProxyType({
        "target_horizon_sec": horizon,
        "minimum_observed_slots": int(policy.minimum_observed_slots_per_horizon),
        "observed_slot_count": normalized_observed_counts[horizon],
        "requirement_met": (
            normalized_observed_counts[horizon]
            >= int(policy.minimum_observed_slots_per_horizon)
        ),
        "target_definition_version": f"market_regime_target.{horizon}s.v1",
    }) for horizon in policy.required_horizons_sec)
    insufficient_horizons = tuple(
        item["target_horizon_sec"]
        for item in horizon_requirements
        if not item["requirement_met"]
    )
    blockers.extend(
        f"minimum_observed_slots_not_met:{horizon}"
        for horizon in insufficient_horizons
    )
    evaluation_ready = (
        collection_start_ready
        and origin_batch_sufficient
        and not insufficient_horizons
    )

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_COLLECTION_PLAN_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_collection_readiness_plan",
        "generated_at": generated_at,
        "namespace": ORIGIN_EVIDENCE_NAMESPACE,
        "collection_policy": policy.to_dict(),
        "runtime_source_ready": runtime_ready,
        "runtime_blockers": runtime_blockers,
        "existing_artifact_count": len(relpaths),
        "existing_artifact_relpaths": relpaths,
        "observed_slot_count_by_horizon": MappingProxyType(normalized_observed_counts),
        "operator_approval_present": operator_approval_present,
        "collection_start_ready": collection_start_ready,
        "evaluation_ready": evaluation_ready,
        "blockers": tuple(dict.fromkeys(blockers)),
        "horizon_requirements": horizon_requirements,
        "historical_backfill_allowed": False,
        "same_window_required": True,
        "append_only_required": True,
        "writer_activation_performed": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "winner_declared": False,
        "selection_performed": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })
