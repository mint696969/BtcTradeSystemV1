# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_tactic_parameter_sets.py
# desc: Thin parameter-set resolution helper for Phase 4-A tactic proposal builders.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    PredictionScenarioOutput,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_contract import (
    TacticParameterSetRef,
)


@dataclass(frozen=True)
class ResolvedTacticParameterSetBundle:
    active_parameter_set_ref: TacticParameterSetRef
    comparison_set_refs: tuple[TacticParameterSetRef, ...]
    rollback_ready: bool
    parameter_trace: dict[str, Any]


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _build_default_active_parameter_set_ref(
    scenario_output: PredictionScenarioOutput | None,
) -> TacticParameterSetRef:
    market_uid = "global"
    if scenario_output is not None and scenario_output.market_uid:
        market_uid = scenario_output.market_uid.replace(".", "_")

    return TacticParameterSetRef(
        set_id=f"{market_uid}_phase4a_default",
        set_version="v1",
        profile_kind="baseline",
        comparison_group="phase4a_entry",
        is_active_candidate=True,
    )


def _normalize_active_parameter_set_ref(
    scenario_output: PredictionScenarioOutput | None,
    active_parameter_set_ref: TacticParameterSetRef | None,
) -> TacticParameterSetRef:
    if active_parameter_set_ref is not None:
        return active_parameter_set_ref
    return _build_default_active_parameter_set_ref(scenario_output)


def _build_default_comparison_set_refs(
    active_parameter_set_ref: TacticParameterSetRef,
) -> tuple[TacticParameterSetRef, ...]:
    refs: list[TacticParameterSetRef] = []

    baseline_ref_id = _safe_str(active_parameter_set_ref.baseline_ref)
    if baseline_ref_id and baseline_ref_id != active_parameter_set_ref.set_id:
        refs.append(
            TacticParameterSetRef(
                set_id=baseline_ref_id,
                set_version=active_parameter_set_ref.set_version,
                profile_kind="baseline",
                comparison_group=active_parameter_set_ref.comparison_group,
            )
        )

    refs.append(active_parameter_set_ref)
    return tuple(refs)


def _normalize_comparison_set_refs(
    active_parameter_set_ref: TacticParameterSetRef,
    comparison_set_refs: tuple[TacticParameterSetRef, ...] | None,
) -> tuple[TacticParameterSetRef, ...]:
    if comparison_set_refs:
        return comparison_set_refs
    return _build_default_comparison_set_refs(active_parameter_set_ref)


def _build_parameter_trace(
    active_parameter_set_ref: TacticParameterSetRef,
    comparison_set_refs: tuple[TacticParameterSetRef, ...],
) -> dict[str, Any]:
    return {
        "active_set_id": active_parameter_set_ref.set_id,
        "active_set_version": active_parameter_set_ref.set_version,
        "profile_kind": active_parameter_set_ref.profile_kind,
        "baseline_ref": active_parameter_set_ref.baseline_ref,
        "overlay_refs": active_parameter_set_ref.overlay_refs,
        "comparison_group": active_parameter_set_ref.comparison_group,
        "rollback_parent_set_id": active_parameter_set_ref.rollback_parent_set_id,
        "comparison_set_ids": tuple(item.set_id for item in comparison_set_refs),
        "comparison_count": len(comparison_set_refs),
    }


def resolve_tactic_parameter_set_bundle(
    *,
    scenario_output: PredictionScenarioOutput | None,
    active_parameter_set_ref: TacticParameterSetRef | None,
    comparison_set_refs: tuple[TacticParameterSetRef, ...] | None,
) -> ResolvedTacticParameterSetBundle:
    normalized_active_ref = _normalize_active_parameter_set_ref(
        scenario_output,
        active_parameter_set_ref,
    )
    normalized_comparison_refs = _normalize_comparison_set_refs(
        normalized_active_ref,
        comparison_set_refs,
    )

    return ResolvedTacticParameterSetBundle(
        active_parameter_set_ref=normalized_active_ref,
        comparison_set_refs=normalized_comparison_refs,
        rollback_ready=bool(
            normalized_active_ref.rollback_parent_set_id
            or normalized_active_ref.baseline_ref
        ),
        parameter_trace=_build_parameter_trace(
            normalized_active_ref,
            normalized_comparison_refs,
        ),
    )