# path: ./btcts_next/src/btcts/autotrade/ledger/abstention.py
# desc: WAIT/NO_NEW_ENTRY abstention diagnostics and missed-opportunity records.

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Tuple


class AbstentionClass(str, Enum):
    SAFETY_BLOCKED = "safety_blocked"
    EDGE_BLOCKED = "edge_blocked"
    COST_BLOCKED = "cost_blocked"
    FORECAST_UNKNOWN = "forecast_unknown"
    COOLDOWN = "cooldown"
    MARGIN_CAUTION = "margin_caution"
    EXECUTION_STATE_NOT_CLEAN = "execution_state_not_clean"
    WAIT_NO_EDGE = "wait_no_edge"


SAFETY_BLOCK_REASONS = {
    "stale_input",
    "risk_entry_blocked_stale",
    "temporal_flow_unusable",
    "trade_unusable",
    "liquidity_unusable",
    "position_unknown",
    "order_state_unknown",
    "kill_switch_active",
}

EDGE_BLOCK_REASONS = {
    "low_confidence",
    "mixed_ground",
    "unknown_ground",
    "entry_quality_below_threshold",
    "forecast_not_aligned",
}

COST_BLOCK_REASONS = {
    "spread_too_wide",
    "expected_edge_below_cost",
}


@dataclass(frozen=True)
class AbstentionDiagnostic:
    decision_id: str
    action: str
    abstention_class: AbstentionClass
    reasons: Tuple[str, ...]
    safety_blocked: bool
    edge_blocked: bool
    tunable: bool

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["abstention_class"] = self.abstention_class.value
        return data


@dataclass(frozen=True)
class MissedOpportunityRecord:
    decision_id: str
    parameter_set_id: str
    snapshot_id: str
    forecast_id: str | None
    action: str
    side: str | None
    evaluation_horizon_sec: int
    actual_move: float | None
    cost_adjusted_move: float | None
    would_have_been_profitable: bool | None
    blocking_reasons: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def classify_abstention(*, decision_id: str, action: str, reasons: Tuple[str, ...], blocked_by: Tuple[str, ...]) -> AbstentionDiagnostic:
    all_reasons = tuple(dict.fromkeys(tuple(reasons) + tuple(blocked_by)))
    reason_set = set(all_reasons)

    if reason_set & SAFETY_BLOCK_REASONS:
        klass = AbstentionClass.SAFETY_BLOCKED
        safety = True
        edge = False
        tunable = False
    elif reason_set & COST_BLOCK_REASONS:
        klass = AbstentionClass.COST_BLOCKED
        safety = False
        edge = True
        tunable = True
    elif reason_set & EDGE_BLOCK_REASONS:
        klass = AbstentionClass.EDGE_BLOCKED
        safety = False
        edge = True
        tunable = True
    elif "forecast_unknown" in reason_set:
        klass = AbstentionClass.FORECAST_UNKNOWN
        safety = False
        edge = True
        tunable = True
    else:
        klass = AbstentionClass.WAIT_NO_EDGE
        safety = False
        edge = True
        tunable = True

    return AbstentionDiagnostic(
        decision_id=decision_id,
        action=action,
        abstention_class=klass,
        reasons=all_reasons,
        safety_blocked=safety,
        edge_blocked=edge,
        tunable=tunable,
    )
