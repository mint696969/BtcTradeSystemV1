# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_tactic_contract.py
# desc: Shared Phase 4-A tactic proposal contract for scenario-driven operating stance and parameter-set review.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    DEFAULT_PREDICTION_SYSTEM_VERSION,
)

DEFAULT_TACTIC_PROPOSAL_VERSION = DEFAULT_PREDICTION_SYSTEM_VERSION


@dataclass(frozen=True)
class TacticParameterSetRef:
    ref_type: str = "tactic_parameter_set_ref"
    ref_version: str = DEFAULT_TACTIC_PROPOSAL_VERSION
    set_id: str = "default"
    set_version: str = "v1"
    profile_kind: str = "baseline"
    baseline_ref: str | None = None
    overlay_refs: tuple[str, ...] = field(default_factory=tuple)
    rollback_parent_set_id: str | None = None
    comparison_group: str | None = None
    is_active_candidate: bool = False
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScenarioTacticCandidate:
    tactic_key: str
    tactic_label: str = "unknown"
    stance_bias: str = "unknown"
    readiness: str = "hold"
    priority: int = 100
    parameter_set_ref: TacticParameterSetRef = field(
        default_factory=TacticParameterSetRef
    )
    reason_refs: tuple[str, ...] = field(default_factory=tuple)
    caution_flags: tuple[str, ...] = field(default_factory=tuple)
    invalidation_watch: str = "unknown"
    switch_alignment: str = "unknown"
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScenarioTacticProposalOutput:
    proposal_type: str = "scenario_tactic_proposal_output"
    proposal_version: str = DEFAULT_TACTIC_PROPOSAL_VERSION
    source_kind: str = "prediction_scenario_output"
    market_uid: str | None = None
    event_ts: str | None = None
    scenario_ref: str | None = None
    scenario_regime: str = "unknown"
    primary_tactic_key: str = "observe_only"
    proposal_state: str = "hold"
    candidate_tactics: tuple[ScenarioTacticCandidate, ...] = field(
        default_factory=tuple
    )
    active_parameter_set_ref: TacticParameterSetRef = field(
        default_factory=TacticParameterSetRef
    )
    comparison_set_refs: tuple[TacticParameterSetRef, ...] = field(
        default_factory=tuple
    )
    rollback_ready: bool = False
    review_needed: bool = True
    explanation_trace: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TacticReviewRecord:
    review_type: str = "tactic_review_record"
    review_version: str = DEFAULT_TACTIC_PROPOSAL_VERSION
    review_id: str | None = None
    review_ts: str | None = None
    market_uid: str | None = None
    scenario_ref: str | None = None
    proposal_ref: str | None = None
    selected_tactic_key: str = "observe_only"
    selected_parameter_set_ref: TacticParameterSetRef = field(
        default_factory=TacticParameterSetRef
    )
    decision_state: str = "proposed"
    decision_reason: str | None = None
    comparison_refs: tuple[str, ...] = field(default_factory=tuple)
    rollback_target_ref: str | None = None
    operator_note: str | None = None
    replay_followup_required: bool = False
    selection_trace: dict[str, Any] = field(default_factory=dict)
    parameter_trace: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)