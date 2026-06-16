# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_tactic_review_builder.py
# desc: Thin builder for Phase 4-A tactic review record from tactic proposal output.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared._value_utils import safe_str
from btcts.processing.l4_consumer_models.shared.prediction_tactic_contract import (
    ScenarioTacticProposalOutput,
    TacticParameterSetRef,
    TacticReviewRecord,
)


@dataclass(frozen=True)
class PredictionTacticReviewBuildInput:
    proposal_output: ScenarioTacticProposalOutput | None = None
    review_ts: str | None = None
    decision_state: str = "proposed"
    decision_reason: str | None = None
    selected_tactic_key: str | None = None
    selected_parameter_set_ref: TacticParameterSetRef | None = None
    comparison_refs: tuple[str, ...] | None = None
    rollback_target_ref: str | None = None
    operator_note: str | None = None
    replay_followup_required: bool | None = None
    diagnostics: dict[str, Any] | None = None


def _resolve_selected_tactic_key(
    proposal_output: ScenarioTacticProposalOutput | None,
    selected_tactic_key: str | None,
) -> str:
    provided = safe_str(selected_tactic_key)
    if provided is not None:
        return provided
    if proposal_output is None:
        return "observe_only"
    return proposal_output.primary_tactic_key


def _resolve_selected_parameter_set_ref(
    proposal_output: ScenarioTacticProposalOutput | None,
    selected_parameter_set_ref: TacticParameterSetRef | None,
) -> TacticParameterSetRef:
    if selected_parameter_set_ref is not None:
        return selected_parameter_set_ref
    if proposal_output is not None:
        return proposal_output.active_parameter_set_ref
    return TacticParameterSetRef()


def _resolve_comparison_refs(
    proposal_output: ScenarioTacticProposalOutput | None,
    comparison_refs: tuple[str, ...] | None,
) -> tuple[str, ...]:
    if comparison_refs:
        return comparison_refs
    if proposal_output is None:
        return ()

    refs: list[str] = []
    for item in proposal_output.comparison_set_refs:
        refs.append(item.set_id)
    return tuple(refs)


def _resolve_rollback_target_ref(
    *,
    proposal_output: ScenarioTacticProposalOutput | None,
    rollback_target_ref: str | None,
    selected_parameter_set_ref: TacticParameterSetRef,
) -> str | None:
    provided = safe_str(rollback_target_ref)
    if provided is not None:
        return provided

    parent = safe_str(selected_parameter_set_ref.rollback_parent_set_id)
    if parent is not None:
        return parent

    baseline = safe_str(selected_parameter_set_ref.baseline_ref)
    if baseline is not None:
        return baseline

    if proposal_output is None:
        return None

    first_ref = next(iter(proposal_output.comparison_set_refs), None)
    if first_ref is None:
        return None
    return first_ref.set_id


def _resolve_replay_followup_required(
    *,
    proposal_output: ScenarioTacticProposalOutput | None,
    decision_state: str,
    replay_followup_required: bool | None,
) -> bool:
    if replay_followup_required is not None:
        return bool(replay_followup_required)

    if proposal_output is None:
        return False

    if decision_state in {"adopted", "rolled_back"}:
        return True
    return proposal_output.review_needed


def _build_review_id(
    *,
    proposal_output: ScenarioTacticProposalOutput | None,
    selected_tactic_key: str,
    review_ts: str | None,
) -> str | None:
    if proposal_output is None:
        return None

    scenario_ref = safe_str(proposal_output.scenario_ref) or "unknown_scenario"
    if review_ts is not None:
        return f"{scenario_ref}:{selected_tactic_key}:{review_ts}"
    return f"{scenario_ref}:{selected_tactic_key}"


def _build_proposal_ref(
    proposal_output: ScenarioTacticProposalOutput | None,
) -> str | None:
    if proposal_output is None:
        return None

    scenario_ref = safe_str(proposal_output.scenario_ref) or "unknown_scenario"
    return f"proposal:{scenario_ref}"


def _resolve_trace_payload(
    proposal_output: ScenarioTacticProposalOutput | None,
    key: str,
) -> dict[str, Any]:
    if proposal_output is None:
        return {}

    diagnostics_value = proposal_output.diagnostics.get(key)
    if isinstance(diagnostics_value, dict):
        return dict(diagnostics_value)

    if key == "selection_trace":
        explanation_value = proposal_output.explanation_trace.get("selection_trace")
        if isinstance(explanation_value, dict):
            return dict(explanation_value)

    return {}


def build_prediction_tactic_review_record(
    inp: PredictionTacticReviewBuildInput,
) -> TacticReviewRecord:
    proposal_output = inp.proposal_output
    decision_state = safe_str(inp.decision_state) or "proposed"
    selected_tactic_key = _resolve_selected_tactic_key(
        proposal_output,
        inp.selected_tactic_key,
    )
    selected_parameter_set_ref = _resolve_selected_parameter_set_ref(
        proposal_output,
        inp.selected_parameter_set_ref,
    )
    comparison_refs = _resolve_comparison_refs(
        proposal_output,
        inp.comparison_refs,
    )
    rollback_target_ref = _resolve_rollback_target_ref(
        proposal_output=proposal_output,
        rollback_target_ref=inp.rollback_target_ref,
        selected_parameter_set_ref=selected_parameter_set_ref,
    )

    selection_trace = _resolve_trace_payload(proposal_output, "selection_trace")
    parameter_trace = _resolve_trace_payload(proposal_output, "parameter_trace")
    adoption_ready = bool(parameter_trace.get("adoption_ready"))
    rollback_target_available = rollback_target_ref is not None

    return TacticReviewRecord(
        review_id=_build_review_id(
            proposal_output=proposal_output,
            selected_tactic_key=selected_tactic_key,
            review_ts=inp.review_ts,
        ),
        review_ts=inp.review_ts,
        market_uid=None if proposal_output is None else proposal_output.market_uid,
        scenario_ref=None if proposal_output is None else proposal_output.scenario_ref,
        proposal_ref=_build_proposal_ref(proposal_output),
        selected_tactic_key=selected_tactic_key,
        selected_parameter_set_ref=selected_parameter_set_ref,
        decision_state=decision_state,
        decision_reason=inp.decision_reason,
        comparison_refs=comparison_refs,
        rollback_target_ref=rollback_target_ref,
        operator_note=inp.operator_note,
        replay_followup_required=_resolve_replay_followup_required(
            proposal_output=proposal_output,
            decision_state=decision_state,
            replay_followup_required=inp.replay_followup_required,
        ),
        selection_trace=selection_trace,
        parameter_trace=parameter_trace,
        diagnostics={
            "builder_type": "prediction_tactic_review_record",
            "proposal_present": proposal_output is not None,
            "comparison_ref_count": len(comparison_refs),
            "selection_trace_present": bool(selection_trace),
            "parameter_trace_present": bool(parameter_trace),
            "adoption_ready": adoption_ready,
            "rollback_target_available": rollback_target_available,
            "selected_set_id": selected_parameter_set_ref.set_id,
            **dict(inp.diagnostics or {}),
        },
    )