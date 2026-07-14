# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_feature_shadow_ranking.py
# desc: MR-F6.13 explicit-policy evidence sufficiency and deterministic shadow ranking projection without selection.

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .features.current_l4_origin_feature_shadow_registry import (
    build_default_current_l4_origin_feature_shadow_registry,
)
from .future_mandatory_baseline_comparison import MANDATORY_BASELINE_IDS
from .future_origin_feature_shadow_aggregation import (
    MARKET_REGIME_ORIGIN_FEATURE_SHADOW_AGGREGATION_VERSION,
)

MARKET_REGIME_ORIGIN_FEATURE_SHADOW_RANKING_VERSION = (
    "prediction.market_regime.origin_feature_shadow_ranking.mr_f6_13.v1"
)

PARAMETER_SENSITIVE_BASELINE_IDS: Tuple[str, ...] = (
    "simple_ma_slope",
    "simple_volatility_threshold",
)


@dataclass(frozen=True)
class OriginFeatureShadowRankingPolicy:
    policy_id: str
    minimum_evaluation_slots: int
    minimum_observed_slots_per_baseline: int
    minimum_scored_slots_per_baseline: int
    minimum_coverage_rate: float
    required_baseline_ids: Tuple[str, ...] = PARAMETER_SENSITIVE_BASELINE_IDS

    def __post_init__(self) -> None:
        if not str(self.policy_id).strip():
            raise ValueError("origin_feature_shadow_ranking_policy_id_missing")
        for name, value in (
            ("minimum_evaluation_slots", self.minimum_evaluation_slots),
            ("minimum_observed_slots_per_baseline", self.minimum_observed_slots_per_baseline),
            ("minimum_scored_slots_per_baseline", self.minimum_scored_slots_per_baseline),
        ):
            if isinstance(value, bool) or int(value) <= 0:
                raise ValueError(f"origin_feature_shadow_ranking_policy_count_invalid:{name}")
        if int(self.minimum_scored_slots_per_baseline) > int(self.minimum_observed_slots_per_baseline):
            raise ValueError("origin_feature_shadow_ranking_policy_scored_exceeds_observed")
        coverage = float(self.minimum_coverage_rate)
        if not isfinite(coverage) or coverage < 0.0 or coverage > 1.0:
            raise ValueError("origin_feature_shadow_ranking_policy_coverage_invalid")
        required = tuple(str(item).strip() for item in self.required_baseline_ids)
        if required != PARAMETER_SENSITIVE_BASELINE_IDS:
            raise ValueError("origin_feature_shadow_ranking_policy_baseline_scope_invalid")
        object.__setattr__(self, "required_baseline_ids", required)

    def to_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "policy_id": self.policy_id,
            "minimum_evaluation_slots": int(self.minimum_evaluation_slots),
            "minimum_observed_slots_per_baseline": int(self.minimum_observed_slots_per_baseline),
            "minimum_scored_slots_per_baseline": int(self.minimum_scored_slots_per_baseline),
            "minimum_coverage_rate": float(self.minimum_coverage_rate),
            "required_baseline_ids": self.required_baseline_ids,
        })


def _validate_aggregation(aggregation: Mapping[str, Any]) -> None:
    if not isinstance(aggregation, Mapping):
        raise ValueError("origin_feature_shadow_ranking_aggregation_type_invalid")
    if aggregation.get("schema_version") != MARKET_REGIME_ORIGIN_FEATURE_SHADOW_AGGREGATION_VERSION:
        raise ValueError("origin_feature_shadow_ranking_aggregation_schema_mismatch")
    if aggregation.get("artifact_kind") != "origin_feature_shadow_multi_slot_aggregation":
        raise ValueError("origin_feature_shadow_ranking_artifact_kind_mismatch")
    if aggregation.get("aggregation_ready") is not True:
        raise ValueError("origin_feature_shadow_ranking_aggregation_not_ready")
    if aggregation.get("candidate_count") != 8 or aggregation.get("baseline_count") != 6:
        raise ValueError("origin_feature_shadow_ranking_matrix_shape_invalid")
    if aggregation.get("candidate_baseline_pair_count") != 48:
        raise ValueError("origin_feature_shadow_ranking_pair_count_invalid")
    if aggregation.get("ranking_performed") is not False:
        raise ValueError("origin_feature_shadow_ranking_pre_ranked_input_not_allowed")
    if aggregation.get("selection_performed") is not False or aggregation.get("selected_candidate_id") is not None:
        raise ValueError("origin_feature_shadow_ranking_selected_input_not_allowed")
    for field in (
        "writes_dhot",
        "scheduler_enabled",
        "live_parameter_apply_allowed",
        "auto_promotion_allowed",
        "canonical_replacement_allowed",
    ):
        if aggregation.get(field) is not False:
            raise ValueError(f"origin_feature_shadow_ranking_unsafe_input_flag:{field}")


def _expected_rate(numerator: int, denominator: int) -> float | None:
    return None if denominator <= 0 else round(numerator / denominator, 6)


def _validate_pair_summary(
    row: Mapping[str, Any],
    *,
    evaluation_slot_count: int,
) -> None:
    counts: dict[str, int] = {}
    for field in (
        "slot_count",
        "observed_slot_count",
        "scored_slot_count",
        "hit_count",
        "unknown_count",
    ):
        value = row.get(field)
        if isinstance(value, bool):
            raise ValueError(f"origin_feature_shadow_ranking_count_invalid:{field}")
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"origin_feature_shadow_ranking_count_invalid:{field}") from exc
        if parsed < 0 or parsed != value:
            raise ValueError(f"origin_feature_shadow_ranking_count_invalid:{field}")
        counts[field] = parsed

    if counts["slot_count"] != evaluation_slot_count:
        raise ValueError("origin_feature_shadow_ranking_slot_count_mismatch")
    if not (
        counts["hit_count"] <= counts["scored_slot_count"]
        <= counts["observed_slot_count"]
        <= counts["slot_count"]
    ):
        raise ValueError("origin_feature_shadow_ranking_count_order_invalid")
    if counts["unknown_count"] != counts["observed_slot_count"] - counts["scored_slot_count"]:
        raise ValueError("origin_feature_shadow_ranking_unknown_count_mismatch")

    expected = {
        "coverage_rate": _expected_rate(counts["scored_slot_count"], counts["observed_slot_count"]),
        "accuracy": _expected_rate(counts["hit_count"], counts["scored_slot_count"]),
        "unknown_rate": _expected_rate(counts["unknown_count"], counts["observed_slot_count"]),
    }
    for field, expected_value in expected.items():
        actual = row.get(field)
        if expected_value is None:
            if actual is not None:
                raise ValueError(f"origin_feature_shadow_ranking_metric_mismatch:{field}")
            continue
        actual_value = _finite_metric(row, field)
        if actual_value != expected_value:
            raise ValueError(f"origin_feature_shadow_ranking_metric_mismatch:{field}")


def _finite_metric(row: Mapping[str, Any], field: str) -> float | None:
    value = row.get(field)
    if value is None:
        return None
    result = float(value)
    if not isfinite(result) or result < 0.0 or result > 1.0:
        raise ValueError(f"origin_feature_shadow_ranking_metric_invalid:{field}")
    return result


def _candidate_projection(
    *,
    candidate_id: str,
    baseline_rows: Mapping[str, Mapping[str, Any]],
    evaluation_slot_count: int,
    policy: OriginFeatureShadowRankingPolicy,
) -> Mapping[str, Any]:
    blockers: list[str] = []
    if evaluation_slot_count < int(policy.minimum_evaluation_slots):
        blockers.append("minimum_evaluation_slots_not_met")

    sensitive_rows = []
    for baseline_id in policy.required_baseline_ids:
        row = baseline_rows.get(baseline_id)
        if row is None:
            blockers.append(f"required_baseline_missing:{baseline_id}")
            continue
        observed = int(row.get("observed_slot_count") or 0)
        scored = int(row.get("scored_slot_count") or 0)
        slot_count = int(row.get("slot_count") or 0)
        if slot_count != evaluation_slot_count:
            raise ValueError("origin_feature_shadow_ranking_slot_count_mismatch")
        if observed < int(policy.minimum_observed_slots_per_baseline):
            blockers.append(f"minimum_observed_slots_not_met:{baseline_id}")
        if scored < int(policy.minimum_scored_slots_per_baseline):
            blockers.append(f"minimum_scored_slots_not_met:{baseline_id}")
        coverage = _finite_metric(row, "coverage_rate")
        accuracy = _finite_metric(row, "accuracy")
        if coverage is None or coverage < float(policy.minimum_coverage_rate):
            blockers.append(f"minimum_coverage_rate_not_met:{baseline_id}")
        if accuracy is None:
            blockers.append(f"accuracy_unavailable:{baseline_id}")
        sensitive_rows.append(row)

    sufficient = not blockers and len(sensitive_rows) == len(policy.required_baseline_ids)
    accuracies = tuple(float(row["accuracy"]) for row in sensitive_rows if row.get("accuracy") is not None)
    coverages = tuple(float(row["coverage_rate"]) for row in sensitive_rows if row.get("coverage_rate") is not None)
    scored_counts = tuple(int(row["scored_slot_count"]) for row in sensitive_rows)
    metric_key = None
    if sufficient:
        metric_key = (
            round(sum(accuracies) / len(accuracies), 6),
            round(min(accuracies), 6),
            round(sum(coverages) / len(coverages), 6),
            min(scored_counts),
        )
    return MappingProxyType({
        "candidate_id": candidate_id,
        "evidence_sufficient": sufficient,
        "evidence_blockers": tuple(blockers),
        "sensitive_baseline_summaries": tuple(sensitive_rows),
        "mean_accuracy": None if not accuracies else round(sum(accuracies) / len(accuracies), 6),
        "minimum_accuracy": None if not accuracies else round(min(accuracies), 6),
        "mean_coverage_rate": None if not coverages else round(sum(coverages) / len(coverages), 6),
        "minimum_scored_slots": None if not scored_counts else min(scored_counts),
        "ranking_metric_key": metric_key,
    })


def build_origin_feature_shadow_ranking(
    *,
    aggregation: Mapping[str, Any],
    policy: OriginFeatureShadowRankingPolicy,
) -> Mapping[str, Any]:
    _validate_aggregation(aggregation)
    if not isinstance(policy, OriginFeatureShadowRankingPolicy):
        raise ValueError("origin_feature_shadow_ranking_policy_type_invalid")

    candidate_ids = aggregation.get("candidate_ids")
    pair_summaries = aggregation.get("pair_summaries")
    if not isinstance(candidate_ids, (tuple, list)) or len(candidate_ids) != 8:
        raise ValueError("origin_feature_shadow_ranking_candidate_ids_invalid")
    canonical_candidate_ids = tuple(
        item.candidate_id
        for item in build_default_current_l4_origin_feature_shadow_registry()
    )
    normalized_candidate_ids = tuple(str(item).strip() for item in candidate_ids)
    if normalized_candidate_ids != canonical_candidate_ids:
        raise ValueError("origin_feature_shadow_ranking_candidate_registry_not_canonical")
    if not isinstance(pair_summaries, (tuple, list)) or len(pair_summaries) != 48:
        raise ValueError("origin_feature_shadow_ranking_pair_summaries_invalid")

    by_candidate: dict[str, dict[str, Mapping[str, Any]]] = {item: {} for item in normalized_candidate_ids}
    for row in pair_summaries:
        if not isinstance(row, Mapping):
            raise ValueError("origin_feature_shadow_ranking_pair_summary_type_invalid")
        candidate_id = str(row.get("candidate_id") or "").strip()
        baseline_id = str(row.get("baseline_id") or "").strip()
        if candidate_id not in by_candidate:
            raise ValueError("origin_feature_shadow_ranking_unknown_candidate")
        if baseline_id not in MANDATORY_BASELINE_IDS:
            raise ValueError("origin_feature_shadow_ranking_unknown_baseline")
        if baseline_id in by_candidate[candidate_id]:
            raise ValueError("origin_feature_shadow_ranking_duplicate_candidate_baseline_pair")
        by_candidate[candidate_id][baseline_id] = row

    evaluation_slot_count = int(aggregation.get("evaluation_slot_count") or 0)
    if evaluation_slot_count <= 0:
        raise ValueError("origin_feature_shadow_ranking_evaluation_slot_count_invalid")
    for candidate_id, baseline_rows in by_candidate.items():
        if tuple(baseline_rows) != MANDATORY_BASELINE_IDS:
            raise ValueError(
                f"origin_feature_shadow_ranking_baseline_matrix_incomplete:{candidate_id}"
            )
        for row in baseline_rows.values():
            _validate_pair_summary(row, evaluation_slot_count=evaluation_slot_count)
    projections = tuple(
        _candidate_projection(
            candidate_id=candidate_id,
            baseline_rows=by_candidate[candidate_id],
            evaluation_slot_count=evaluation_slot_count,
            policy=policy,
        )
        for candidate_id in candidate_ids
    )
    sufficient = tuple(item for item in projections if item["evidence_sufficient"])
    metric_groups: dict[tuple[float, float, float, int], list[Mapping[str, Any]]] = {}
    for item in sufficient:
        key = item["ranking_metric_key"]
        assert isinstance(key, tuple)
        metric_groups.setdefault(key, []).append(item)

    ranked_groups = []
    for rank, metric_key in enumerate(sorted(metric_groups, reverse=True), start=1):
        members = tuple(sorted(
            (str(item["candidate_id"]) for item in metric_groups[metric_key]),
        ))
        ranked_groups.append(MappingProxyType({
            "metric_rank": rank,
            "ranking_metric_key": metric_key,
            "candidate_ids": members,
            "tie": len(members) > 1,
            "human_review_required": True,
            "selection_allowed": False,
        }))

    global_blockers = []
    if not sufficient:
        global_blockers.append("no_candidate_meets_evidence_sufficiency")
    elif len(sufficient) < 2:
        global_blockers.append("fewer_than_two_sufficient_candidates")
    comparison_ready = len(sufficient) >= 2

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_FEATURE_SHADOW_RANKING_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "origin_feature_shadow_evidence_sufficiency_and_ranking",
        "comparison_contract": aggregation["comparison_contract"],
        "ranking_policy": policy.to_dict(),
        "candidate_count": len(projections),
        "evidence_sufficient_candidate_count": len(sufficient),
        "comparison_ready": comparison_ready,
        "comparison_blockers": tuple(global_blockers),
        "candidate_projections": projections,
        "ranked_metric_groups": tuple(ranked_groups),
        "ranking_performed": comparison_ready,
        "ranking_scope": PARAMETER_SENSITIVE_BASELINE_IDS,
        "winner_declared": False,
        "selection_performed": False,
        "selected_candidate_id": None,
        "promotion_candidates": (),
        "writes_dhot": False,
        "scheduler_enabled": False,
        "human_gate_required": True,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })
