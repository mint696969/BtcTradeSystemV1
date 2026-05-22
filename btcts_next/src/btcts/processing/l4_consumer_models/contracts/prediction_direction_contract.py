# path: ./btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py
# desc: Read-only Direction prediction contract models.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class HorizonDirectionReading:
    """
    Direction reading for a specific horizon.

    Notes
    -----
    This is a read-only market interpretation contract.
    It is not an execution instruction.
    """

    horizon_key: str
    direction_bias: str
    confidence: float
    continuation_balance: float
    reversal_balance: float
    turning_point_risk: float
    invalidation_hint: str | None = None


@dataclass(frozen=True)
class PredictionDirectionOutput:
    """
    Phase 4-A Direction layer minimal contract skeleton.

    Boundary:
    - scenario downstream read model only
    - additive interpretation layer only
    - not position management
    - not execution instruction
    - not broker/order automation
    """

    prediction_type: str
    prediction_version: str

    source_kind: str
    market_uid: str
    event_ts: str

    scenario_ref: str

    primary_direction_bias: str

    horizon_direction_readings: Sequence[HorizonDirectionReading] = field(
        default_factory=tuple
    )

    continuation_reversal_balance: float = 0.0
    turning_point_risk: float = 0.0

    confidence: float = 0.0
    caution_level: str = "normal"

    invalidation_carry: str | None = None

    evidence_trace_refs: Sequence[str] = field(default_factory=tuple)

    diagnostics: Mapping[str, Any] = field(default_factory=dict)