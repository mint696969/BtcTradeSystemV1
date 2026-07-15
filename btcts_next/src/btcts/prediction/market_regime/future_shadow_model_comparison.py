# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_model_comparison.py
# desc: Pure MR-F8 immutable candidate/cohort comparison and human-gated decision contract.

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence, Tuple

from .future_mandatory_baseline_comparison import (
    MandatoryBaselineComparisonRow,
    summarize_mandatory_baseline_candidate,
)

MARKET_REGIME_SHADOW_MODEL_COMPARISON_VERSION = (
    "prediction.market_regime.shadow_model_comparison.mr_f8_2.v1"
)
_ALLOWED_ROLES = ("active", "shadow")
_ALLOWED_DECISIONS = ("winner", "tie", "insufficient_evidence")


@dataclass(frozen=True)
class FutureShadowCandidateIdentity:
    candidate_id: str
    model_id: str
    logic_version: str
    parameter_set_id: str
    target_definition_family: str
    source_contract_version: str
    registry_role: str

    def __post_init__(self) -> None:
        for name, value in (
            ("candidate_id", self.candidate_id),
            ("model_id", self.model_id),
            ("logic_version", self.logic_version),
            ("parameter_set_id", self.parameter_set_id),
            ("target_definition_family", self.target_definition_family),
            ("source_contract_version", self.source_contract_version),
        ):
            if not str(value).strip():
                raise ValueError(f"shadow_model_candidate_identity_missing:{name}")
        if self.registry_role not in _ALLOWED_ROLES:
            raise ValueError("shadow_model_candidate_registry_role_invalid")

    @property
    def immutable_key(self) -> Tuple[str, str, str, str, str, str]:
        return (
            self.candidate_id,
            self.model_id,
            self.logic_version,
            self.parameter_set_id,
            self.target_definition_family,
            self.source_contract_version,
        )

    def to_dict(self) -> Mapping[str, str]:
        return MappingProxyType({
            "candidate_id": self.candidate_id,
            "model_id": self.model_id,
            "logic_version": self.logic_version,
            "parameter_set_id": self.parameter_set_id,
            "target_definition_family": self.target_definition_family,
            "source_contract_version": self.source_contract_version,
            "registry_role": self.registry_role,
        })


@dataclass(frozen=True)
class FutureShadowComparisonCohort:
    cohort_id: str
    evaluation_window_ref: str
    oos_split_id: str
    oos_partition: str
    missing_data_policy_version: str
    condition_group_id: str

    def __post_init__(self) -> None:
        for name, value in (
            ("cohort_id", self.cohort_id),
            ("evaluation_window_ref", self.evaluation_window_ref),
            ("oos_split_id", self.oos_split_id),
            ("oos_partition", self.oos_partition),
            ("missing_data_policy_version", self.missing_data_policy_version),
            ("condition_group_id", self.condition_group_id),
        ):
            if not str(value).strip():
                raise ValueError(f"shadow_model_comparison_cohort_missing:{name}")
        if self.oos_partition not in ("validation", "test"):
            raise ValueError("shadow_model_comparison_oos_partition_invalid")


@dataclass(frozen=True)
class FutureShadowComparisonDecision:
    decision: str
    selected_candidate_id: str | None
    rollback_candidate_id: str
    rationale_codes: Tuple[str, ...]
    human_approval_required: bool = True
    approved_by: str | None = None
    approved_at: str | None = None
    live_parameter_apply_allowed: bool = False
    auto_promotion_allowed: bool = False

    def __post_init__(self) -> None:
        if self.decision not in _ALLOWED_DECISIONS:
            raise ValueError("shadow_model_comparison_decision_invalid")
        if self.decision == "winner" and not str(self.selected_candidate_id or "").strip():
            raise ValueError("shadow_model_comparison_winner_missing")
        if self.decision != "winner" and self.selected_candidate_id is not None:
            raise ValueError("shadow_model_comparison_nonwinner_selection_forbidden")
        if not str(self.rollback_candidate_id).strip():
            raise ValueError("shadow_model_comparison_rollback_candidate_missing")
        if not self.rationale_codes or any(not str(item).strip() for item in self.rationale_codes):
            raise ValueError("shadow_model_comparison_rationale_missing")
        if self.human_approval_required is not True:
            raise ValueError("shadow_model_comparison_human_gate_required")
        if (self.approved_by is None) != (self.approved_at is None):
            raise ValueError("shadow_model_comparison_partial_approval_identity")
        if self.live_parameter_apply_allowed is not False:
            raise ValueError("shadow_model_comparison_live_apply_forbidden")
        if self.auto_promotion_allowed is not False:
            raise ValueError("shadow_model_comparison_auto_promotion_forbidden")


def build_future_shadow_model_comparison(
    *,
    identities: Sequence[FutureShadowCandidateIdentity],
    cohort: FutureShadowComparisonCohort,
    rows: Iterable[MandatoryBaselineComparisonRow],
    decision: FutureShadowComparisonDecision,
) -> Mapping[str, Any]:
    safe_identities = tuple(identities)
    if len(safe_identities) < 2:
        raise ValueError("shadow_model_comparison_fewer_than_two_candidates")
    if sum(1 for item in safe_identities if item.registry_role == "active") != 1:
        raise ValueError("shadow_model_comparison_active_candidate_count_not_one")
    candidate_ids = tuple(item.candidate_id for item in safe_identities)
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("shadow_model_comparison_duplicate_candidate_id")
    if len({item.immutable_key for item in safe_identities}) != len(safe_identities):
        raise ValueError("shadow_model_comparison_duplicate_immutable_identity")
    if decision.rollback_candidate_id not in candidate_ids:
        raise ValueError("shadow_model_comparison_rollback_candidate_unknown")
    if decision.selected_candidate_id is not None and decision.selected_candidate_id not in candidate_ids:
        raise ValueError("shadow_model_comparison_selected_candidate_unknown")

    safe_rows = tuple(rows)
    if not safe_rows:
        raise ValueError("shadow_model_comparison_rows_empty")
    by_candidate: dict[str, list[MandatoryBaselineComparisonRow]] = {item: [] for item in candidate_ids}
    slot_sets: dict[str, set[tuple[str, str, str, int, str, str]]] = {item: set() for item in candidate_ids}
    seen_trace_ids: set[str] = set()
    unknown_candidates: set[str] = set()
    wrong_window: set[str] = set()
    for row in safe_rows:
        if not isinstance(row, MandatoryBaselineComparisonRow):
            raise ValueError("shadow_model_comparison_row_type_invalid")
        if row.trace_id in seen_trace_ids:
            raise ValueError("shadow_model_comparison_duplicate_trace_id")
        seen_trace_ids.add(row.trace_id)
        if row.candidate_id not in by_candidate:
            unknown_candidates.add(row.candidate_id)
            continue
        if row.evaluation_window_ref != cohort.evaluation_window_ref:
            wrong_window.add(row.candidate_id)
        if row.comparison_key in slot_sets[row.candidate_id]:
            raise ValueError(f"shadow_model_comparison_duplicate_slot:{row.candidate_id}")
        by_candidate[row.candidate_id].append(row)
        slot_sets[row.candidate_id].add(row.comparison_key)

    reference_id = next(item.candidate_id for item in safe_identities if item.registry_role == "active")
    reference_slots = slot_sets[reference_id]
    missing_candidates = tuple(item for item in candidate_ids if not by_candidate[item])
    mismatch_candidates = tuple(item for item in candidate_ids if slot_sets[item] != reference_slots)
    blockers: list[str] = []
    if unknown_candidates:
        blockers.append("unknown_candidate_rows")
    if wrong_window:
        blockers.append("evaluation_window_mismatch")
    if missing_candidates:
        blockers.append("candidate_rows_missing")
    if not reference_slots:
        blockers.append("comparison_cohort_empty")
    if mismatch_candidates:
        blockers.append("identical_cohort_contract_mismatch")

    comparison_ready = not blockers
    if not comparison_ready and decision.decision != "insufficient_evidence":
        raise ValueError("shadow_model_comparison_unready_decision_must_be_insufficient")

    summaries = tuple(
        summarize_mandatory_baseline_candidate(
            candidate_id=candidate_id,
            rows=tuple(by_candidate[candidate_id]),
            total_slots=max(1, len(reference_slots)),
        )
        for candidate_id in candidate_ids
        if by_candidate[candidate_id]
    )
    return MappingProxyType({
        "schema_version": MARKET_REGIME_SHADOW_MODEL_COMPARISON_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "shadow_model_and_parameter_set_comparison",
        "cohort": MappingProxyType({
            "cohort_id": cohort.cohort_id,
            "evaluation_window_ref": cohort.evaluation_window_ref,
            "oos_split_id": cohort.oos_split_id,
            "oos_partition": cohort.oos_partition,
            "missing_data_policy_version": cohort.missing_data_policy_version,
            "condition_group_id": cohort.condition_group_id,
        }),
        "candidate_identities": tuple(item.to_dict() for item in safe_identities),
        "active_candidate_id": reference_id,
        "candidate_count": len(candidate_ids),
        "comparison_slot_count": len(reference_slots),
        "comparison_ready": comparison_ready,
        "comparison_blockers": tuple(blockers),
        "missing_candidate_ids": missing_candidates,
        "cohort_mismatch_candidate_ids": mismatch_candidates,
        "unknown_row_candidate_ids": tuple(sorted(unknown_candidates)),
        "wrong_window_candidate_ids": tuple(sorted(wrong_window)),
        "candidate_summaries": summaries,
        "decision": MappingProxyType({
            "decision": decision.decision,
            "selected_candidate_id": decision.selected_candidate_id,
            "rollback_candidate_id": decision.rollback_candidate_id,
            "rationale_codes": decision.rationale_codes,
            "human_approval_required": True,
            "approved_by": decision.approved_by,
            "approved_at": decision.approved_at,
        }),
        "safety": MappingProxyType({
            "read_only_inputs": True,
            "writes_dhot": False,
            "shadow_only": True,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        }),
    })
