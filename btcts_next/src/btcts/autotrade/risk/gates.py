# path: ./btcts_next/src/btcts/autotrade/risk/gates.py
# desc: Fail-closed risk gates for AutoTrade action candidates.

from __future__ import annotations

from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.read_model.models import AutoTradeSnapshot
from btcts.autotrade.strategy.models import ActionCandidate, CandidateAction
from btcts.autotrade.strategy import reason_codes as rc
from .models import RiskGateResult

ENTRY_ACTIONS = {CandidateAction.ENTRY_BUY, CandidateAction.ENTRY_SELL}
WATCH_ACTIONS = {CandidateAction.WATCH_BUY, CandidateAction.WATCH_SELL}


def evaluate_risk_gate(snapshot: AutoTradeSnapshot, candidate: ActionCandidate, *, mode: AutoTradeMode) -> RiskGateResult:
    blocked: list[str] = []
    warnings: list[str] = []

    if candidate.action in ENTRY_ACTIONS:
        if snapshot.stale_reasons or not snapshot.usability.live_inputs_usable:
            blocked.append(rc.RISK_ENTRY_BLOCKED_STALE)
        if candidate.entry_quality <= 0:
            blocked.append(rc.RISK_ENTRY_BLOCKED_LOW_QUALITY)
        if mode == AutoTradeMode.SHADOW:
            warnings.append(rc.RISK_NO_REAL_ORDERS_IN_SHADOW)
            # Shadow can allow the decision logically, but executable remains false.
            return RiskGateResult(allowed=not blocked, executable=False, blocked_by=tuple(dict.fromkeys(blocked)), warnings=tuple(warnings))
        if mode not in {AutoTradeMode.PAPER_OR_REPLAY, AutoTradeMode.ARMED_DRY_RUN, AutoTradeMode.LIVE_MIN_SIZE, AutoTradeMode.LIVE_CONTROLLED}:
            blocked.append("mode_not_entry_capable")

    if candidate.action in WATCH_ACTIONS:
        return RiskGateResult(allowed=True, executable=False, blocked_by=(), warnings=tuple(warnings))

    if candidate.action in {CandidateAction.NO_NEW_ENTRY, CandidateAction.WAIT}:
        return RiskGateResult(allowed=False, executable=False, blocked_by=tuple(candidate.blocked_hint), warnings=tuple(warnings))

    return RiskGateResult(allowed=not blocked, executable=False, blocked_by=tuple(dict.fromkeys(blocked)), warnings=tuple(warnings))
