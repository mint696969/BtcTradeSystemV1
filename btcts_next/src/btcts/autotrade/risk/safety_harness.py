# path: ./btcts_next/src/btcts/autotrade/risk/safety_harness.py
# desc: AutoTrade live readiness and safety harness contracts.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class KillSwitchState:
    active: bool
    reason: str | None = None
    source: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeHealthState:
    heartbeat_fresh: bool
    market_data_fresh: bool
    account_state_fresh: bool
    order_state_fresh: bool
    position_state_fresh: bool
    ledger_writable: bool
    broker_reachable: bool = False
    reconciliation_clean: bool = False

    def freshness_ok(self) -> bool:
        return (
            self.heartbeat_fresh
            and self.market_data_fresh
            and self.account_state_fresh
            and self.order_state_fresh
            and self.position_state_fresh
            and self.ledger_writable
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["freshness_ok"] = self.freshness_ok()
        return data


@dataclass(frozen=True)
class LiveReadinessResult:
    ready: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_live_readiness(*, kill_switch: KillSwitchState, runtime: RuntimeHealthState, active_parameter_set_id: str | None, mode: str) -> LiveReadinessResult:
    blocked: list[str] = []
    warnings: list[str] = []

    if kill_switch.active:
        blocked.append("kill_switch_active")
    if active_parameter_set_id is None:
        blocked.append("active_parameter_set_missing")
    if not runtime.heartbeat_fresh:
        blocked.append("heartbeat_stale")
    if not runtime.market_data_fresh:
        blocked.append("market_data_stale")
    if not runtime.account_state_fresh:
        blocked.append("account_state_stale")
    if not runtime.order_state_fresh:
        blocked.append("order_state_stale")
    if not runtime.position_state_fresh:
        blocked.append("position_state_stale")
    if not runtime.ledger_writable:
        blocked.append("ledger_not_writable")
    if mode in {"LIVE_MIN_SIZE", "LIVE_CONTROLLED"} and not runtime.reconciliation_clean:
        blocked.append("reconciliation_not_clean")
    if not runtime.broker_reachable:
        warnings.append("broker_not_reachable_or_not_checked")

    return LiveReadinessResult(ready=not blocked, blocked_by=tuple(blocked), warnings=tuple(warnings))
