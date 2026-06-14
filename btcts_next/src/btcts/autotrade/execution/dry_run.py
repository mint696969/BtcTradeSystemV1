# path: ./btcts_next/src/btcts/autotrade/execution/dry_run.py
# desc: Armed dry-run execution validator. Never sends broker orders.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

from btcts.autotrade.execution.intents import OrderIntent
from btcts.autotrade.risk.safety_harness import KillSwitchState, RuntimeHealthState, evaluate_live_readiness


@dataclass(frozen=True)
class DryRunExecutionResult:
    intent_id: str
    decision_id: str
    accepted_for_dry_run: bool
    would_send_to_broker: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    mode: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_armed_dry_run_intent(
    intent: OrderIntent,
    *,
    kill_switch: KillSwitchState,
    runtime: RuntimeHealthState,
    active_parameter_set_id: str | None,
) -> DryRunExecutionResult:
    readiness = evaluate_live_readiness(
        kill_switch=kill_switch,
        runtime=runtime,
        active_parameter_set_id=active_parameter_set_id,
        mode="ARMED_DRY_RUN",
    )
    blocked: list[str] = list(readiness.blocked_by)
    warnings: list[str] = list(readiness.warnings)
    if not intent.risk_gate_allowed:
        blocked.append("risk_gate_not_allowed")
    if active_parameter_set_id is not None and intent.parameter_set_id != active_parameter_set_id:
        blocked.append("parameter_set_mismatch")

    return DryRunExecutionResult(
        intent_id=intent.intent_id,
        decision_id=intent.decision_id,
        accepted_for_dry_run=not blocked,
        would_send_to_broker=False,
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        mode="ARMED_DRY_RUN",
    )
