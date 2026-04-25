# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_tactic_operation_builder.py
# desc: Thin builder for Phase 4-A tactic operation record from tactic review record.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared._value_utils import safe_str
from btcts.processing.l4_consumer_models.shared.prediction_tactic_contract import (
    TacticParameterSetRef,
    TacticReviewRecord,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_operation_contract import (
    TacticOperationRecord,
)


@dataclass(frozen=True)
class PredictionTacticOperationBuildInput:
    review_record: TacticReviewRecord | None = None
    operation_ts: str | None = None
    operation_state: str | None = None
    operation_reason: str | None = None
    selected_parameter_set_ref: TacticParameterSetRef | None = None
    rollback_target_ref: str | None = None
    diagnostics: dict[str, Any] | None = None


def _resolve_operation_state(
    review_record: TacticReviewRecord | None,
    operation_state: str | None,
) -> str:
    provided = safe_str(operation_state)
    if provided is not None:
        return provided

    if review_record is None:
        return "hold"

    mapping = {
        "proposed": "propose",
        "adopted": "adopt",
        "held": "hold",
        "rejected": "reject",
        "rolled_back": "rollback",
        "superseded": "supersede",
    }
    return mapping.get(review_record.decision_state, "hold")


def _resolve_selected_parameter_set_ref(
    review_record: TacticReviewRecord | None,
    selected_parameter_set_ref: TacticParameterSetRef | None,
) -> TacticParameterSetRef:
    if selected_parameter_set_ref is not None:
        return selected_parameter_set_ref
    if review_record is not None:
        return review_record.selected_parameter_set_ref
    return TacticParameterSetRef()


def _resolve_operation_reason(
    review_record: TacticReviewRecord | None,
    operation_reason: str | None,
) -> str | None:
    provided = safe_str(operation_reason)
    if provided is not None:
        return provided
    if review_record is None:
        return None
    return review_record.decision_reason


def _resolve_rollback_target_ref(
    review_record: TacticReviewRecord | None,
    rollback_target_ref: str | None,
) -> str | None:
    provided = safe_str(rollback_target_ref)
    if provided is not None:
        return provided
    if review_record is None:
        return None
    return review_record.rollback_target_ref


def _build_operation_id(
    *,
    review_record: TacticReviewRecord | None,
    operation_state: str,
    operation_ts: str | None,
) -> str | None:
    if review_record is None:
        return None

    review_ref = safe_str(review_record.review_id)
    if review_ref is None:
        review_ref = safe_str(review_record.scenario_ref)

    if review_ref is None:
        return None

    if operation_ts is not None:
        return f"{review_ref}:{operation_state}:{operation_ts}"
    return f"{review_ref}:{operation_state}"


def build_prediction_tactic_operation_record(
    inp: PredictionTacticOperationBuildInput,
) -> TacticOperationRecord:
    review_record = inp.review_record
    operation_state = _resolve_operation_state(
        review_record,
        inp.operation_state,
    )
    selected_parameter_set_ref = _resolve_selected_parameter_set_ref(
        review_record,
        inp.selected_parameter_set_ref,
    )
    operation_reason = _resolve_operation_reason(
        review_record,
        inp.operation_reason,
    )
    rollback_target_ref = _resolve_rollback_target_ref(
        review_record,
        inp.rollback_target_ref,
    )
    parameter_trace = (
        {} if review_record is None else dict(review_record.parameter_trace)
    )
    adoption_ready = bool(parameter_trace.get("adoption_ready"))
    rollback_target_available = rollback_target_ref is not None

    return TacticOperationRecord(
        operation_id=_build_operation_id(
            review_record=review_record,
            operation_state=operation_state,
            operation_ts=inp.operation_ts,
        ),
        operation_ts=inp.operation_ts,
        market_uid=None if review_record is None else review_record.market_uid,
        scenario_ref=None if review_record is None else review_record.scenario_ref,
        proposal_ref=None if review_record is None else review_record.proposal_ref,
        review_ref=None if review_record is None else review_record.review_id,
        operation_state=operation_state,
        selected_tactic_key="observe_only"
        if review_record is None
        else review_record.selected_tactic_key,
        selected_parameter_set_ref=selected_parameter_set_ref,
        comparison_refs=()
        if review_record is None
        else review_record.comparison_refs,
        rollback_target_ref=rollback_target_ref,
        operation_reason=operation_reason,
        selection_trace={}
        if review_record is None
        else dict(review_record.selection_trace),
        parameter_trace=parameter_trace,
        diagnostics={
            "builder_type": "prediction_tactic_operation_record",
            "review_present": review_record is not None,
            "comparison_ref_count": 0
            if review_record is None
            else len(review_record.comparison_refs),
            "adoption_ready": adoption_ready,
            "rollback_target_available": rollback_target_available,
            "selected_set_id": selected_parameter_set_ref.set_id,
            **dict(inp.diagnostics or {}),
        },
    )