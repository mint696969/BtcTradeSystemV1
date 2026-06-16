# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_position_review_hint_builder.py
# desc: Thin read-only helper for PredictionPositionReviewHint.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from btcts.processing.l4_consumer_models.contracts import PredictionPositionReviewHint


@dataclass(frozen=True)
class PositionReviewHintBuildInput:
    scenario_ref: str
    direction_ref: str
    source_kind: str = "direction_review_material"
    market_uid: str = "unknown"
    event_ts: str = "unknown"
    position_context_ref: str = "position_context.review_only.unknown"
    position_state_reading: str = "flat_or_no_live_claim"
    management_hint: str = "review_only_wait"
    exposure_risk_hint: str = "unknown"
    invalidation_response_hint: str | None = None
    evidence_trace_refs: Sequence[str] = ()
    diagnostics: dict[str, Any] | None = None


def make_position_review_hint(
    inp: PositionReviewHintBuildInput,
) -> PredictionPositionReviewHint:
    return PredictionPositionReviewHint(
        prediction_type="position_review_hint",
        prediction_version="phase4a.position_review_hint.v1",
        source_kind=inp.source_kind,
        market_uid=inp.market_uid,
        event_ts=inp.event_ts,
        scenario_ref=inp.scenario_ref,
        direction_ref=inp.direction_ref,
        position_context_ref=inp.position_context_ref,
        position_state_reading=inp.position_state_reading,
        management_hint=inp.management_hint,
        exposure_risk_hint=inp.exposure_risk_hint,
        invalidation_response_hint=inp.invalidation_response_hint,
        review_needed=True,
        evidence_trace_refs=tuple(inp.evidence_trace_refs),
        diagnostics={
            "builder_type": "position_review_hint",
            "builder_stage": "thin_skeleton",
            "read_only_contract": True,
            "not_live_position_mutation": True,
            "not_execution_instruction": True,
            "not_broker_or_order_automation": True,
            "not_final_trading_decision_owner": True,
            "not_runtime_wiring": True,
            "not_replay_wiring": True,
            "not_ui_wiring": True,
            **dict(inp.diagnostics or {}),
        },
    )


def position_review_hint_to_snapshot(
    hint: PredictionPositionReviewHint,
) -> dict[str, Any]:
    return {
        "prediction_type": hint.prediction_type,
        "prediction_version": hint.prediction_version,
        "source_kind": hint.source_kind,
        "market_uid": hint.market_uid,
        "event_ts": hint.event_ts,
        "scenario_ref": hint.scenario_ref,
        "direction_ref": hint.direction_ref,
        "position_context_ref": hint.position_context_ref,
        "position_state_reading": hint.position_state_reading,
        "management_hint": hint.management_hint,
        "exposure_risk_hint": hint.exposure_risk_hint,
        "invalidation_response_hint": hint.invalidation_response_hint,
        "review_needed": hint.review_needed,
        "evidence_trace_refs": list(hint.evidence_trace_refs),
        "diagnostics": dict(hint.diagnostics),
        "snapshot_stage": "position_review_hint_read_only_local_snapshot",
        "read_only_contract": True,
        "not_live_position_mutation": True,
        "not_execution_instruction": True,
        "not_broker_or_order_automation": True,
        "not_runtime_wiring": True,
        "not_replay_wiring": True,
        "not_ui_wiring": True,
    }
