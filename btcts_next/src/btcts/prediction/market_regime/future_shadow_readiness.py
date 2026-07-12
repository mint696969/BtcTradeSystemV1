# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_readiness.py
# desc: Pure MR-F5.8 read-only projection and MarketRegime family-completion readiness audit for shadow future evaluation summaries.

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .future_shadow_evaluation import MARKET_REGIME_FUTURE_SHADOW_EVALUATION_VERSION

MARKET_REGIME_FUTURE_SHADOW_READINESS_VERSION = "prediction.market_regime.future_shadow_readiness.mr_f5_8.v1"
_REQUIRED_CHECKPOINTS = (
    "MR_F5_1_FUTURE_FORECAST_CONTRACT_AND_LEGACY_PATH_AUDIT_ACCEPTED",
    "MR_F5_2_TARGET_DEFINITION_AND_FEATURE_AVAILABILITY_ACCEPTED",
    "MR_F5_3_TRANSPARENT_BASELINE_MODEL_ACCEPTED",
    "MR_F5_4_EXPLICIT_EVIDENCE_ADAPTER_AND_SHADOW_PACKET_ACCEPTED",
    "MR_F5_5_SHADOW_TRACE_AND_OUTCOME_IDENTITY_ACCEPTED",
    "MR_F5_6_SHADOW_OUTCOME_RESOLUTION_AND_EVALUATION_ROW_ACCEPTED",
    "MR_F5_7_SHADOW_EVALUATION_AGGREGATION_AND_CANDIDATE_COMPARISON_ACCEPTED",
)


@dataclass(frozen=True)
class MarketRegimeFamilyCompletionEvidence:
    accepted_checkpoints: Tuple[str, ...]
    representative_feature_availability_proven: bool
    shadow_observation_window_completed: bool
    shadow_evaluation_row_count: int
    comparison_ready: bool
    canonical_migration_review_completed: bool = False

    def __post_init__(self) -> None:
        raw_checkpoints = tuple(str(item).strip() for item in self.accepted_checkpoints)
        if any(not item for item in raw_checkpoints):
            raise ValueError("future_shadow_readiness_checkpoint_invalid")
        checkpoints = tuple(dict.fromkeys(raw_checkpoints))
        object.__setattr__(self, "accepted_checkpoints", checkpoints)
        for field_name in (
            "representative_feature_availability_proven",
            "shadow_observation_window_completed",
            "comparison_ready",
            "canonical_migration_review_completed",
        ):
            if type(getattr(self, field_name)) is not bool:
                raise ValueError(f"future_shadow_readiness_boolean_invalid:{field_name}")
        if isinstance(self.shadow_evaluation_row_count, bool):
            raise ValueError("future_shadow_readiness_row_count_invalid")
        if int(self.shadow_evaluation_row_count) < 0:
            raise ValueError("future_shadow_readiness_row_count_invalid")


def _validate_summary(summary: Mapping[str, Any]) -> None:
    if summary.get("schema_version") != MARKET_REGIME_FUTURE_SHADOW_EVALUATION_VERSION:
        raise ValueError("future_shadow_readiness_summary_schema_invalid")
    if summary.get("artifact_family") != "prediction/market_regime":
        raise ValueError("future_shadow_readiness_summary_family_invalid")
    if summary.get("artifact_kind") != "future_shadow_evaluation_summary":
        raise ValueError("future_shadow_readiness_summary_kind_invalid")
    safety = summary.get("safety") if isinstance(summary.get("safety"), Mapping) else {}
    required_true = ("shadow_only", "read_only_inputs", "human_gate_required")
    required_false = (
        "writes_dhot",
        "ledger_append_allowed",
        "parameter_auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "canonical_replacement",
    )
    for key in required_true:
        if safety.get(key) is not True:
            raise ValueError(f"future_shadow_readiness_safety_{key}_invalid")
    for key in required_false:
        if safety.get(key) is not False:
            raise ValueError(f"future_shadow_readiness_safety_{key}_invalid")
    if tuple(summary.get("promotion_candidates") or ()):
        raise ValueError("future_shadow_readiness_promotion_candidates_not_empty")


def build_market_regime_future_shadow_readiness(
    *,
    evaluation_summary: Mapping[str, Any],
    completion_evidence: MarketRegimeFamilyCompletionEvidence,
) -> Mapping[str, Any]:
    if not isinstance(evaluation_summary, Mapping):
        raise ValueError("future_shadow_readiness_summary_not_mapping")
    _validate_summary(evaluation_summary)

    blockers: list[str] = []
    accepted = set(completion_evidence.accepted_checkpoints)
    missing_checkpoints = tuple(item for item in _REQUIRED_CHECKPOINTS if item not in accepted)
    if missing_checkpoints:
        blockers.append("required_mr_f5_checkpoints_missing")
    if not completion_evidence.representative_feature_availability_proven:
        blockers.append("representative_feature_availability_not_proven")
    if not completion_evidence.shadow_observation_window_completed:
        blockers.append("shadow_observation_window_not_completed")
    if int(completion_evidence.shadow_evaluation_row_count) <= 0:
        blockers.append("shadow_evaluation_rows_absent")
    if int(evaluation_summary.get("row_count") or 0) != int(completion_evidence.shadow_evaluation_row_count):
        blockers.append("shadow_evaluation_row_count_mismatch")
    if bool(evaluation_summary.get("comparison_ready")) != bool(completion_evidence.comparison_ready):
        blockers.append("comparison_ready_evidence_mismatch")
    if not completion_evidence.comparison_ready:
        blockers.append("shadow_candidate_comparison_not_ready")
    if not completion_evidence.canonical_migration_review_completed:
        blockers.append("canonical_migration_review_not_completed")

    family_ready = not blockers
    candidate_items = tuple(evaluation_summary.get("candidate_summaries") or ())
    if int(evaluation_summary.get("candidate_count") or 0) != len(candidate_items):
        raise ValueError("future_shadow_readiness_candidate_count_mismatch")
    if any(not isinstance(item, Mapping) for item in candidate_items):
        raise ValueError("future_shadow_readiness_candidate_summary_invalid")
    candidate_rows = tuple(
        MappingProxyType({
            "candidate_key": str(item.get("candidate_key") or ""),
            "model_id": str(item.get("model_id") or ""),
            "logic_version": str(item.get("logic_version") or ""),
            "parameter_set_id": str(item.get("parameter_set_id") or ""),
            "scored_rows": int(item.get("scored_rows") or 0),
            "weighted_score": item.get("weighted_score"),
            "insufficient_sample": bool(item.get("insufficient_sample")),
        })
        for item in candidate_items
    )

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_READINESS_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_readiness_read_model",
        "current_gate": "MR_F5_8_READ_ONLY_COMPARISON_PROJECTION_AND_FAMILY_COMPLETION_READINESS_AUDITED",
        "family_completion_gate": "MARKET_REGIME_READY_FOR_NEXT_FAMILY",
        "family_ready_for_next_family": family_ready,
        "next_prediction_family": "trend_bias" if family_ready else "",
        "blockers": tuple(blockers),
        "missing_required_checkpoints": missing_checkpoints,
        "accepted_checkpoint_count": len(accepted.intersection(_REQUIRED_CHECKPOINTS)),
        "required_checkpoint_count": len(_REQUIRED_CHECKPOINTS),
        "shadow_evaluation_row_count": int(evaluation_summary.get("row_count") or 0),
        "candidate_count": int(evaluation_summary.get("candidate_count") or 0),
        "comparable_candidate_count": int(evaluation_summary.get("comparable_candidate_count") or 0),
        "comparison_ready": bool(evaluation_summary.get("comparison_ready")),
        "comparison_blockers": tuple(evaluation_summary.get("comparison_blockers") or ()),
        "candidate_projection": candidate_rows,
        "recommendations": tuple(evaluation_summary.get("recommendations") or ()),
        "promotion_candidates": (),
        "decision": "ready_for_next_family" if family_ready else "continue_market_regime_shadow_evidence",
        "safety": MappingProxyType({
            "read_only_projection": True,
            "shadow_only": True,
            "writes_dhot": False,
            "ledger_append_allowed": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "canonical_replacement": False,
            "ui_change": False,
            "human_gate_required": True,
        }),
    })
