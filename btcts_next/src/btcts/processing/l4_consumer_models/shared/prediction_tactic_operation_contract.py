# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_tactic_operation_contract.py
# desc: Shared Phase 4-A tactic operation contract for adoption / hold / reject / rollback handling.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    DEFAULT_PREDICTION_SYSTEM_VERSION,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_contract import (
    TacticParameterSetRef,
)

DEFAULT_TACTIC_OPERATION_VERSION = DEFAULT_PREDICTION_SYSTEM_VERSION


@dataclass(frozen=True)
class TacticOperationRecord:
    operation_type: str = "tactic_operation_record"
    operation_version: str = DEFAULT_TACTIC_OPERATION_VERSION
    operation_id: str | None = None
    operation_ts: str | None = None
    market_uid: str | None = None
    scenario_ref: str | None = None
    proposal_ref: str | None = None
    review_ref: str | None = None
    operation_state: str = "hold"
    selected_tactic_key: str = "observe_only"
    selected_parameter_set_ref: TacticParameterSetRef = field(
        default_factory=TacticParameterSetRef
    )
    comparison_refs: tuple[str, ...] = field(default_factory=tuple)
    rollback_target_ref: str | None = None
    operation_reason: str | None = None
    selection_trace: dict[str, Any] = field(default_factory=dict)
    parameter_trace: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)