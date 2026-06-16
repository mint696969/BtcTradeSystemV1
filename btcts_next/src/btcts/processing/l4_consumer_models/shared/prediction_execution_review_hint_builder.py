# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_execution_review_hint_builder.py
# desc: Thin read-only helper for PredictionExecutionReviewHint.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from btcts.processing.l4_consumer_models.contracts import PredictionExecutionReviewHint


@dataclass(frozen=True)
class ExecutionReviewHintBuildInput:
    scenario_ref: str
    direction_ref: str
    position_ref: str
    source_kind: str = "position_review_material"
    market_uid: str = "unknown"
    event_ts: str = "unknown"
    execution_context_ref: str = "execution_context.review_only.unknown"
    timing_hint: str = "review_only_wait_for_confirmation"
    urgency_hint: str = "low"
    passive_aggressive_hint: str = "passive_review_only"
    feasibility_hint: str = "feasible_for_review_only"
    invalidation_carry: str | None = None
    evidence_trace_refs: Sequence[str] = ()
    diagnostics: dict[str, Any] | None = None


def make_execution_review_hint(
    inp: ExecutionReviewHintBuildInput,
) -> PredictionExecutionReviewHint:
    return PredictionExecutionReviewHint(
        prediction_type="execution_review_hint",
        prediction_version="phase4a.execution_review_hint.v1",
        source_kind=inp.source_kind,
        market_uid=inp.market_uid,
        event_ts=inp.event_ts,
        scenario_ref=inp.scenario_ref,
        direction_ref=inp.direction_ref,
        position_ref=inp.position_ref,
        execution_context_ref=inp.execution_context_ref,
        timing_hint=inp.timing_hint,
        urgency_hint=inp.urgency_hint,
        passive_aggressive_hint=inp.passive_aggressive_hint,
        feasibility_hint=inp.feasibility_hint,
        invalidation_carry=inp.invalidation_carry,
        review_needed=True,
        evidence_trace_refs=tuple(inp.evidence_trace_refs),
        diagnostics={
            "builder_type": "execution_review_hint",
            "builder_stage": "thin_skeleton",
            "read_only_contract": True,
            "execution_side_effect_free": True,
            "not_execution_instruction": True,
            "broker_link_free": True,
            "account_side_effect_free": True,
            "not_final_trading_decision_owner": True,
            "not_runtime_wiring": True,
            "not_replay_wiring": True,
            "not_ui_wiring": True,
            **dict(inp.diagnostics or {}),
        },
    )


def execution_review_hint_to_snapshot(
    hint: PredictionExecutionReviewHint,
) -> dict[str, Any]:
    return {
        "prediction_type": hint.prediction_type,
        "prediction_version": hint.prediction_version,
        "source_kind": hint.source_kind,
        "market_uid": hint.market_uid,
        "event_ts": hint.event_ts,
        "scenario_ref": hint.scenario_ref,
        "direction_ref": hint.direction_ref,
        "position_ref": hint.position_ref,
        "execution_context_ref": hint.execution_context_ref,
        "timing_hint": hint.timing_hint,
        "urgency_hint": hint.urgency_hint,
        "passive_aggressive_hint": hint.passive_aggressive_hint,
        "feasibility_hint": hint.feasibility_hint,
        "invalidation_carry": hint.invalidation_carry,
        "review_needed": hint.review_needed,
        "evidence_trace_refs": list(hint.evidence_trace_refs),
        "diagnostics": dict(hint.diagnostics),
        "snapshot_stage": "execution_review_hint_read_only_local_snapshot",
        "read_only_contract": True,
        "execution_side_effect_free": True,
        "not_execution_instruction": True,
        "broker_link_free": True,
        "account_side_effect_free": True,
        "not_runtime_wiring": True,
        "not_replay_wiring": True,
        "not_ui_wiring": True,
    }
