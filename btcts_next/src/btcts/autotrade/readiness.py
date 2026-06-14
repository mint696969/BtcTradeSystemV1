# path: ./btcts_next/src/btcts/autotrade/readiness.py
# desc: Read-only AutoTrade live readiness preflight. No mode changes, no broker execution.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

from btcts.autotrade.health import AutoTradeRuntimeHealthSnapshot, build_autotrade_runtime_health_snapshot
from btcts.autotrade.modes import AutoTradeMode, DANGEROUS_MODES, is_transition_allowed, requires_human_confirmation


@dataclass(frozen=True)
class AutoTradeReadinessResult:
    current_mode: AutoTradeMode
    target_mode: AutoTradeMode
    ready: bool
    transition_allowed: bool
    human_confirmation_required: bool
    human_confirmed: bool
    allow_warnings: bool
    health: AutoTradeRuntimeHealthSnapshot
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    would_send_to_broker: bool = False
    read_only: bool = True
    mode_changed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["current_mode"] = self.current_mode.value
        data["target_mode"] = self.target_mode.value
        data["health"] = self.health.to_dict()
        return data


def _coerce_mode(value: AutoTradeMode | str) -> AutoTradeMode:
    if isinstance(value, AutoTradeMode):
        return value
    return AutoTradeMode(str(value))


def evaluate_autotrade_live_readiness(
    *,
    current_mode: AutoTradeMode | str,
    target_mode: AutoTradeMode | str,
    human_confirmed: bool = False,
    allow_warnings: bool = False,
    max_observer_run_age_sec: float = 120.0,
    max_lines: int | None = 1000,
) -> AutoTradeReadinessResult:
    current = _coerce_mode(current_mode)
    target = _coerce_mode(target_mode)
    health = build_autotrade_runtime_health_snapshot(
        max_observer_run_age_sec=max_observer_run_age_sec,
        max_lines=max_lines,
    )
    blocked: list[str] = []
    warnings: list[str] = list(health.warnings)

    transition_allowed = is_transition_allowed(current, target, human_confirmed=human_confirmed)
    confirmation_required = requires_human_confirmation(current, target)
    if not transition_allowed:
        blocked.append("mode_transition_not_allowed_or_unconfirmed")
    if confirmation_required and not human_confirmed:
        blocked.append("human_confirmation_required")

    if health.blocked_by:
        blocked.append("runtime_health_blocked")
        blocked.extend(health.blocked_by)
    if target in DANGEROUS_MODES and not health.runtime.live_ready:
        blocked.append("autotrade_runtime_not_live_ready")
    if target in DANGEROUS_MODES and not health.observer_run_fresh:
        blocked.append("observer_run_not_fresh_for_live_target")
    latest_observer_blocked_by = tuple(health.observer_runs.latest_blocked_by or ())
    if target in DANGEROUS_MODES and latest_observer_blocked_by:
        blocked.append("observer_run_latest_blocked_for_live_target")
        blocked.extend(latest_observer_blocked_by)
    if health.warnings and not allow_warnings:
        blocked.append("runtime_health_warnings_present")

    blocked_tuple = tuple(dict.fromkeys(blocked))
    warnings_tuple = tuple(dict.fromkeys(warnings))
    return AutoTradeReadinessResult(
        current_mode=current,
        target_mode=target,
        ready=not blocked_tuple,
        transition_allowed=transition_allowed,
        human_confirmation_required=confirmation_required,
        human_confirmed=bool(human_confirmed),
        allow_warnings=bool(allow_warnings),
        health=health,
        blocked_by=blocked_tuple,
        warnings=warnings_tuple,
        would_send_to_broker=False,
        read_only=True,
        mode_changed=False,
    )
