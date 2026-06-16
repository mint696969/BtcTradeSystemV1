# path: ./btcts_next/src/btcts/autotrade/pipeline.py
# desc: AutoTrade end-to-end shadow/paper/armed-dry-run vertical slice. No broker execution.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from btcts.autotrade.config.models import ParameterSet, ParameterSetBundle
from btcts.autotrade.execution import OrderIntent, build_order_intent_from_decision, evaluate_armed_dry_run_intent
from btcts.autotrade.ledger import abstention_from_decision, outcome_from_decision, build_shadow_decision_record
from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.read_model import build_rule_based_forecast_5m
from btcts.autotrade.read_model.models import AutoTradeSnapshot
from btcts.autotrade.replay import PaperExecutionEngine
from btcts.autotrade.risk import KillSwitchState, RuntimeHealthState, evaluate_risk_gate
from btcts.autotrade.strategy import CandidateAction, build_action_candidate


@dataclass(frozen=True)
class AutoTradeVerticalSliceResult:
    mode: AutoTradeMode
    snapshot_id: str
    forecast_id: str
    candidate_action: str
    risk_allowed: bool
    shadow_decision_id: str
    order_intent: OrderIntent | None
    paper_order_status: str | None
    dry_run_accepted: bool | None
    would_send_to_broker: bool
    abstention_class: str | None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["mode"] = self.mode.value
        if self.order_intent is not None:
            data["order_intent"] = self.order_intent.to_dict()
        return data


def run_shadow_paper_dry_run_vertical_slice(
    *,
    snapshot: AutoTradeSnapshot,
    parameter_set: ParameterSet,
    mode: AutoTradeMode,
    parameter_bundle: ParameterSetBundle | None = None,
    paper_engine: PaperExecutionEngine | None = None,
    runtime: RuntimeHealthState | None = None,
    kill_switch: KillSwitchState | None = None,
    size: float = 0.01,
    price: float | None = None,
) -> AutoTradeVerticalSliceResult:
    if parameter_bundle is not None:
        parameter_set = parameter_bundle.trade_parameter_set
    forecast = build_rule_based_forecast_5m(snapshot, parameter_set)
    candidate = build_action_candidate(snapshot, forecast, parameter_set)
    risk = evaluate_risk_gate(snapshot, candidate, mode=mode)
    decision = build_shadow_decision_record(
        mode=mode,
        snapshot=snapshot,
        forecast_5m=forecast,
        candidate=candidate,
        risk_gate=risk,
        parameter_bundle=parameter_bundle,
    )
    outcome_from_decision(decision)
    abstention = abstention_from_decision(decision)

    entry_actions = {CandidateAction.ENTRY_BUY.value, CandidateAction.ENTRY_SELL.value}
    order_intent: OrderIntent | None = None
    paper_status: str | None = None
    dry_accepted: bool | None = None

    if decision.final_action in entry_actions and candidate.side is not None:
        order_intent = build_order_intent_from_decision(
            decision_id=decision.decision_id,
            snapshot_id=snapshot.snapshot_id,
            forecast_id=forecast.forecast_id,
            parameter_set_id=parameter_set.parameter_set_id,
            logic_version=parameter_set.logic_version,
            side=candidate.side,
            size=size,
            price=price if price is not None else snapshot.inputs.mid_price,
            reason_codes=candidate.reason_codes,
            risk_gate_allowed=risk.allowed,
            mode=mode.value,
        )

        if mode == AutoTradeMode.PAPER_OR_REPLAY:
            engine = paper_engine or PaperExecutionEngine()
            paper_order = engine.submit_intent(order_intent, ts=snapshot.created_at)
            paper_status = paper_order.status.value
        elif mode == AutoTradeMode.ARMED_DRY_RUN:
            dry_runtime = runtime or RuntimeHealthState(
                heartbeat_fresh=False,
                market_data_fresh=False,
                account_state_fresh=False,
                order_state_fresh=False,
                position_state_fresh=False,
                ledger_writable=False,
            )
            dry_kill = kill_switch or KillSwitchState(active=True, reason="default_fail_closed")
            dry = evaluate_armed_dry_run_intent(
                order_intent,
                kill_switch=dry_kill,
                runtime=dry_runtime,
                active_parameter_set_id=parameter_set.parameter_set_id,
            )
            dry_accepted = dry.accepted_for_dry_run

    return AutoTradeVerticalSliceResult(
        mode=mode,
        snapshot_id=snapshot.snapshot_id,
        forecast_id=forecast.forecast_id,
        candidate_action=candidate.action.value,
        risk_allowed=risk.allowed,
        shadow_decision_id=decision.decision_id,
        order_intent=order_intent,
        paper_order_status=paper_status,
        dry_run_accepted=dry_accepted,
        would_send_to_broker=False,
        abstention_class=abstention.abstention_class.value if abstention is not None else None,
    )
