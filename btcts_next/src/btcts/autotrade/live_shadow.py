# path: ./btcts_next/src/btcts/autotrade/live_shadow.py
# desc: AutoTrade market-state live snapshot to shadow decision ledger vertical slice. No broker execution.

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict

from btcts.autotrade.config.models import ParameterSet
from btcts.autotrade.ledger import ShadowDecisionRecord, append_decision_jsonl, build_shadow_decision_record
from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.read_model import build_rule_based_forecast_5m, load_latest_snapshot_from_market_state
from btcts.autotrade.read_model.live_input_adapter import LiveInputAdapterDiagnostics
from btcts.autotrade.read_model.models import AutoTradeSnapshot
from btcts.autotrade.risk import evaluate_risk_gate
from btcts.autotrade.runtime_paths import decision_ledger_path
from btcts.autotrade.strategy import build_action_candidate


@dataclass(frozen=True)
class ShadowDecisionVerticalResult:
    snapshot_id: str | None
    forecast_id: str | None
    decision_id: str | None
    candidate_action: str | None
    risk_allowed: bool
    appended: bool
    ledger_path: Path
    blocked_by: tuple[str, ...]
    would_send_to_broker: bool = False
    decision: ShadowDecisionRecord | None = None
    diagnostics: LiveInputAdapterDiagnostics | None = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["ledger_path"] = str(self.ledger_path)
        if self.decision is not None:
            data["decision"] = self.decision.to_dict()
        if self.diagnostics is not None:
            data["diagnostics"] = self.diagnostics.to_dict()
        return data


def default_shadow_decision_ledger_path(*, ensure: bool = True) -> Path:
    return decision_ledger_path("shadow_decisions.jsonl", ensure=ensure)


def run_shadow_decision_from_snapshot(
    *,
    snapshot: AutoTradeSnapshot,
    parameter_set: ParameterSet,
    ledger_path: Path | None = None,
    persist: bool = True,
) -> ShadowDecisionVerticalResult:
    path = ledger_path or default_shadow_decision_ledger_path(ensure=persist)
    forecast = build_rule_based_forecast_5m(snapshot, parameter_set)
    candidate = build_action_candidate(snapshot, forecast, parameter_set)
    risk = evaluate_risk_gate(snapshot, candidate, mode=AutoTradeMode.SHADOW)
    decision = build_shadow_decision_record(
        mode=AutoTradeMode.SHADOW,
        snapshot=snapshot,
        forecast_5m=forecast,
        candidate=candidate,
        risk_gate=risk,
    )
    appended = False
    if persist:
        append_decision_jsonl(path, decision)
        appended = True
    return ShadowDecisionVerticalResult(
        snapshot_id=snapshot.snapshot_id,
        forecast_id=forecast.forecast_id,
        decision_id=decision.decision_id,
        candidate_action=candidate.action.value,
        risk_allowed=risk.allowed,
        appended=appended,
        ledger_path=path,
        blocked_by=tuple(dict.fromkeys(tuple(forecast.blocked_by) + tuple(candidate.blocked_hint) + tuple(risk.blocked_by))),
        would_send_to_broker=False,
        decision=decision,
        diagnostics=None,
    )


def run_latest_market_state_shadow_decision(
    *,
    parameter_set: ParameterSet,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
    ledger_path: Path | None = None,
    persist: bool = True,
) -> ShadowDecisionVerticalResult:
    path = ledger_path or default_shadow_decision_ledger_path(ensure=persist)
    snapshot, diagnostics = load_latest_snapshot_from_market_state(
        parameter_set=parameter_set,
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type=state_type,
    )
    if snapshot is None:
        return ShadowDecisionVerticalResult(
            snapshot_id=None,
            forecast_id=None,
            decision_id=None,
            candidate_action=None,
            risk_allowed=False,
            appended=False,
            ledger_path=path,
            blocked_by=tuple(diagnostics.blocked_by or ("market_state_snapshot_missing",)),
            would_send_to_broker=False,
            decision=None,
            diagnostics=diagnostics,
        )
    result = run_shadow_decision_from_snapshot(
        snapshot=snapshot,
        parameter_set=parameter_set,
        ledger_path=path,
        persist=persist,
    )
    return ShadowDecisionVerticalResult(
        snapshot_id=result.snapshot_id,
        forecast_id=result.forecast_id,
        decision_id=result.decision_id,
        candidate_action=result.candidate_action,
        risk_allowed=result.risk_allowed,
        appended=result.appended,
        ledger_path=result.ledger_path,
        blocked_by=result.blocked_by,
        would_send_to_broker=False,
        decision=result.decision,
        diagnostics=diagnostics,
    )
