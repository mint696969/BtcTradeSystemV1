# path: ./btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_position_review_hint_contract.py
# desc: Read-only Position review hint contract models.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class PredictionPositionReviewHint:
    """
    Phase 4-A Position review hint minimal contract skeleton.

    Boundary:
    - review-only management material
    - additive read model only
    - not live position mutation
    - not execution instruction
    - not broker/order automation
    - not final trading decision owner
    """

    prediction_type: str
    prediction_version: str

    source_kind: str
    market_uid: str
    event_ts: str

    scenario_ref: str
    direction_ref: str
    position_context_ref: str

    position_state_reading: str
    management_hint: str
    exposure_risk_hint: str
    invalidation_response_hint: str | None = None

    review_needed: bool = True

    evidence_trace_refs: Sequence[str] = field(default_factory=tuple)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
