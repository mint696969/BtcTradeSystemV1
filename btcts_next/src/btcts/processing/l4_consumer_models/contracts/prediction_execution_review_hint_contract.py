# path: ./btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_execution_review_hint_contract.py
# desc: Read-only Execution review hint contract models.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class PredictionExecutionReviewHint:
    """
    Phase 4-A Execution review hint minimal contract skeleton.

    Boundary:
    - review-only timing / urgency / feasibility material
    - additive read model only
    - not live order placement
    - not broker adapter operation
    - not account mutation
    - not final autonomous trading decision
    """

    prediction_type: str
    prediction_version: str

    source_kind: str
    market_uid: str
    event_ts: str

    scenario_ref: str
    direction_ref: str
    position_ref: str
    execution_context_ref: str

    timing_hint: str
    urgency_hint: str
    passive_aggressive_hint: str
    feasibility_hint: str
    invalidation_carry: str | None = None

    review_needed: bool = True

    evidence_trace_refs: Sequence[str] = field(default_factory=tuple)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
