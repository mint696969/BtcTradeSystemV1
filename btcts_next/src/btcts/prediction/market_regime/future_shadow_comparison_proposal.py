# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_comparison_proposal.py
# desc: MR-F8.5 pure multi-slot comparison assembly and human-gated winner/tie/insufficient proposal generation.

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence, Tuple

from .future_mandatory_baseline_comparison import MandatoryBaselineComparisonRow
from .future_shadow_model_comparison import (
    FutureShadowCandidateIdentity,
    FutureShadowComparisonCohort,
    FutureShadowComparisonDecision,
    build_future_shadow_model_comparison,
)

MARKET_REGIME_FUTURE_SHADOW_PROPOSAL_VERSION = (
    "prediction.market_regime.future_shadow_comparison_proposal.mr_f8_5.v1"
)


@dataclass(frozen=True)
class FutureShadowProposalPolicy:
    minimum_observed_slots: int = 30
    minimum_coverage_rate: float = 0.20
    minimum_accuracy_delta: float = 0.02
    maximum_brier_regression: float = 0.01
    maximum_ece_regression: float = 0.02
    maximum_unknown_rate_increase: float = 0.05

    def __post_init__(self) -> None:
        if int(self.minimum_observed_slots) <= 0:
            raise ValueError("shadow_proposal_minimum_observed_slots_invalid")
        for name, value in (
            ("minimum_coverage_rate", self.minimum_coverage_rate),
            ("minimum_accuracy_delta", self.minimum_accuracy_delta),
            ("maximum_brier_regression", self.maximum_brier_regression),
            ("maximum_ece_regression", self.maximum_ece_regression),
            ("maximum_unknown_rate_increase", self.maximum_unknown_rate_increase),
        ):
            number = float(value)
            if not 0.0 <= number <= 1.0:
                raise ValueError(f"shadow_proposal_policy_invalid:{name}")


def _summary_map(comparison: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(item["candidate_id"]): item for item in comparison["candidate_summaries"]}


def _metric(summary: Mapping[str, Any], name: str) -> float | None:
    value = summary.get(name)
    return None if value is None else float(value)


def _condition_summaries(
    *,
    identities: Sequence[FutureShadowCandidateIdentity],
    cohort: FutureShadowComparisonCohort,
    rows: Tuple[MandatoryBaselineComparisonRow, ...],
    condition_rows: Mapping[str, Sequence[MandatoryBaselineComparisonRow]],
    rollback_candidate_id: str,
) -> Tuple[Mapping[str, Any], ...]:
    payloads = []
    for condition_id, subset in sorted(condition_rows.items()):
        safe_id = str(condition_id).strip()
        if not safe_id:
            raise ValueError("shadow_proposal_condition_id_missing")
        subset_tuple = tuple(subset)
        if any(row not in rows for row in subset_tuple):
            raise ValueError("shadow_proposal_condition_row_outside_cohort")
        condition_cohort = FutureShadowComparisonCohort(
            cohort_id=f"{cohort.cohort_id}:{safe_id}",
            evaluation_window_ref=cohort.evaluation_window_ref,
            oos_split_id=cohort.oos_split_id,
            oos_partition=cohort.oos_partition,
            missing_data_policy_version=cohort.missing_data_policy_version,
            condition_group_id=safe_id,
        )
        decision = FutureShadowComparisonDecision(
            decision="insufficient_evidence",
            selected_candidate_id=None,
            rollback_candidate_id=rollback_candidate_id,
            rationale_codes=("condition_summary_only",),
        )
        payloads.append(build_future_shadow_model_comparison(
            identities=identities,
            cohort=condition_cohort,
            rows=subset_tuple,
            decision=decision,
        ))
    return tuple(payloads)


def build_future_shadow_comparison_proposal(
    *,
    identities: Sequence[FutureShadowCandidateIdentity],
    cohort: FutureShadowComparisonCohort,
    rows: Iterable[MandatoryBaselineComparisonRow],
    rollback_candidate_id: str,
    policy: FutureShadowProposalPolicy = FutureShadowProposalPolicy(),
    condition_rows: Mapping[str, Sequence[MandatoryBaselineComparisonRow]] | None = None,
) -> Mapping[str, Any]:
    safe_rows = tuple(rows)
    provisional = FutureShadowComparisonDecision(
        decision="insufficient_evidence",
        selected_candidate_id=None,
        rollback_candidate_id=rollback_candidate_id,
        rationale_codes=("proposal_pending",),
    )
    comparison = build_future_shadow_model_comparison(
        identities=identities,
        cohort=cohort,
        rows=safe_rows,
        decision=provisional,
    )
    summaries = _summary_map(comparison)
    active_id = str(comparison["active_candidate_id"])
    shadow_ids = tuple(item.candidate_id for item in identities if item.registry_role == "shadow")
    if len(shadow_ids) != 1:
        raise ValueError("shadow_proposal_exactly_one_shadow_required")
    shadow_id = shadow_ids[0]
    active = summaries.get(active_id)
    shadow = summaries.get(shadow_id)
    blockers = list(comparison["comparison_blockers"])
    rationale: list[str] = []
    decision = "insufficient_evidence"
    selected: str | None = None

    if active is None or shadow is None:
        blockers.append("candidate_summary_missing")
    else:
        observed = min(int(active["observed_rows"]), int(shadow["observed_rows"]))
        if observed < int(policy.minimum_observed_slots):
            blockers.append("minimum_observed_slots_not_met")
        for candidate_id, summary in ((active_id, active), (shadow_id, shadow)):
            coverage = _metric(summary, "coverage_rate")
            if coverage is None or coverage < policy.minimum_coverage_rate:
                blockers.append(f"minimum_coverage_not_met:{candidate_id}")
        required_metrics = ("accuracy", "brier_score", "expected_calibration_error", "unknown_rate")
        if any(_metric(active, name) is None or _metric(shadow, name) is None for name in required_metrics):
            blockers.append("required_metric_missing")

    if not blockers and active is not None and shadow is not None:
        accuracy_delta = float(shadow["accuracy"]) - float(active["accuracy"])
        brier_delta = float(shadow["brier_score"]) - float(active["brier_score"])
        ece_delta = float(shadow["expected_calibration_error"]) - float(active["expected_calibration_error"])
        unknown_delta = float(shadow["unknown_rate"]) - float(active["unknown_rate"])
        safety_ok = (
            brier_delta <= policy.maximum_brier_regression
            and ece_delta <= policy.maximum_ece_regression
            and unknown_delta <= policy.maximum_unknown_rate_increase
        )
        if accuracy_delta >= policy.minimum_accuracy_delta and safety_ok:
            decision = "winner"
            selected = shadow_id
            rationale.extend(("shadow_accuracy_gain_met", "risk_regression_within_policy"))
        elif accuracy_delta <= -policy.minimum_accuracy_delta:
            decision = "winner"
            selected = active_id
            rationale.append("active_accuracy_advantage_preserved")
        else:
            decision = "tie"
            rationale.append("accuracy_delta_below_materiality_threshold")
            if not safety_ok:
                rationale.append("shadow_risk_regression_exceeds_policy")
    else:
        rationale.extend(blockers or ("insufficient_evidence",))

    decision_contract = FutureShadowComparisonDecision(
        decision=decision,
        selected_candidate_id=selected,
        rollback_candidate_id=rollback_candidate_id,
        rationale_codes=tuple(dict.fromkeys(rationale)),
    )
    final_comparison = build_future_shadow_model_comparison(
        identities=identities,
        cohort=cohort,
        rows=safe_rows,
        decision=decision_contract,
    )
    conditions = _condition_summaries(
        identities=identities,
        cohort=cohort,
        rows=safe_rows,
        condition_rows=condition_rows or {},
        rollback_candidate_id=rollback_candidate_id,
    )
    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_PROPOSAL_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_comparison_proposal",
        "comparison": final_comparison,
        "condition_summaries": conditions,
        "proposal": MappingProxyType({
            "decision": decision,
            "selected_candidate_id": selected,
            "rollback_candidate_id": rollback_candidate_id,
            "rationale_codes": tuple(dict.fromkeys(rationale)),
            "comparison_blockers": tuple(dict.fromkeys(blockers)),
            "human_approval_required": True,
            "approved_by": None,
            "approved_at": None,
            "proposal_is_not_runtime_activation": True,
        }),
        "policy": MappingProxyType({
            "minimum_observed_slots": policy.minimum_observed_slots,
            "minimum_coverage_rate": policy.minimum_coverage_rate,
            "minimum_accuracy_delta": policy.minimum_accuracy_delta,
            "maximum_brier_regression": policy.maximum_brier_regression,
            "maximum_ece_regression": policy.maximum_ece_regression,
            "maximum_unknown_rate_increase": policy.maximum_unknown_rate_increase,
        }),
        "safety": MappingProxyType({
            "read_only_inputs": True,
            "writes_dhot": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        }),
    })
