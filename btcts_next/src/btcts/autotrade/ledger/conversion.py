# path: ./btcts_next/src/btcts/autotrade/ledger/conversion.py
# desc: Convert shadow decision records into performance/diagnostic records.

from __future__ import annotations

from btcts.autotrade.ledger.abstention import AbstentionDiagnostic, classify_abstention
from btcts.autotrade.ledger.decision_log import ShadowDecisionRecord
from btcts.autotrade.ledger.performance import DecisionOutcomeRecord


def outcome_from_decision(record: ShadowDecisionRecord, *, realized_pnl: float | None = None, fees: float = 0.0, slippage: float = 0.0, outcome_label: str = "unresolved") -> DecisionOutcomeRecord:
    forecast = record.forecast_5m
    return DecisionOutcomeRecord(
        decision_id=record.decision_id,
        parameter_set_id=record.candidate.parameter_set_id,
        logic_version=record.candidate.logic_version,
        action=record.candidate.action.value,
        side=record.candidate.side,
        base_ground_direction=record.snapshot.ground.direction.value,
        base_ground_confidence=record.snapshot.ground.confidence.value,
        forecast_direction=forecast.forecast_direction.value if forecast is not None else None,
        forecast_confidence=forecast.confidence.value if forecast is not None else None,
        strategy_profile=record.candidate.strategy_profile.value,
        entry_quality=record.candidate.entry_quality,
        reason_codes=record.candidate.reason_codes,
        blocked_by=record.risk_gate.blocked_by,
        realized_pnl=realized_pnl,
        fees=fees,
        slippage=slippage,
        outcome_label=outcome_label,
    )


def abstention_from_decision(record: ShadowDecisionRecord) -> AbstentionDiagnostic | None:
    if record.final_action not in {"WAIT", "NO_NEW_ENTRY"} and record.risk_gate.allowed:
        return None
    return classify_abstention(
        decision_id=record.decision_id,
        action=record.final_action,
        reasons=record.candidate.reason_codes,
        blocked_by=record.risk_gate.blocked_by,
    )
