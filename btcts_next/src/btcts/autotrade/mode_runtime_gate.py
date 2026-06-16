# path: ./btcts_next/src/btcts/autotrade/mode_runtime_gate.py
# desc: Read-only AutoTrade runtime capability gate derived from mode_state. No runner execution, no broker execution.

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.execution import current_mode_state
from btcts.autotrade.modes import AutoTradeMode


@dataclass(frozen=True)
class ModeRuntimeGate:
    current_mode: AutoTradeMode
    source_command_id: str | None
    changed_at: str | None
    allow_observer_cycle: bool
    allow_shadow_decision_append: bool
    allow_forecast_outcome_resolution: bool
    allow_paper_order: bool
    allow_armed_dry_run: bool
    allow_live_order_capability: bool
    live_requires_readiness_risk_execution_safety: bool
    blocked_by: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["current_mode"] = self.current_mode.value
        return data


OBSERVER_MODES = frozenset(
    {
        AutoTradeMode.SHADOW,
        AutoTradeMode.PAPER_OR_REPLAY,
        AutoTradeMode.ARMED_DRY_RUN,
        AutoTradeMode.LIVE_MIN_SIZE,
        AutoTradeMode.LIVE_CONTROLLED,
    }
)
PAPER_MODES = frozenset(
    {
        AutoTradeMode.PAPER_OR_REPLAY,
        AutoTradeMode.ARMED_DRY_RUN,
        AutoTradeMode.LIVE_MIN_SIZE,
        AutoTradeMode.LIVE_CONTROLLED,
    }
)
ARMED_DRY_RUN_MODES = frozenset(
    {
        AutoTradeMode.ARMED_DRY_RUN,
        AutoTradeMode.LIVE_MIN_SIZE,
        AutoTradeMode.LIVE_CONTROLLED,
    }
)
LIVE_ORDER_CAPABILITY_MODES = frozenset(
    {
        AutoTradeMode.LIVE_MIN_SIZE,
        AutoTradeMode.LIVE_CONTROLLED,
    }
)


def _blocked_for_mode(mode: AutoTradeMode) -> tuple[str, ...]:
    if mode == AutoTradeMode.OFF:
        return ("mode_off",)
    if mode == AutoTradeMode.HALTED:
        return ("mode_halted",)
    return ()


def build_mode_runtime_gate(path: Path | None = None, *, max_lines: int | None = 1000) -> ModeRuntimeGate:
    state = current_mode_state(path, max_lines=max_lines)
    mode = state.current_mode
    observer_allowed = mode in OBSERVER_MODES
    paper_allowed = mode in PAPER_MODES
    dry_allowed = mode in ARMED_DRY_RUN_MODES
    live_capability = mode in LIVE_ORDER_CAPABILITY_MODES
    blocked = list(_blocked_for_mode(mode))
    warnings: list[str] = []
    if live_capability:
        warnings.append("live_order_capability_requires_readiness_risk_execution_safety")
    return ModeRuntimeGate(
        current_mode=mode,
        source_command_id=state.source_command_id,
        changed_at=state.changed_at,
        allow_observer_cycle=observer_allowed,
        allow_shadow_decision_append=observer_allowed,
        allow_forecast_outcome_resolution=observer_allowed,
        allow_paper_order=paper_allowed,
        allow_armed_dry_run=dry_allowed,
        allow_live_order_capability=live_capability,
        live_requires_readiness_risk_execution_safety=True,
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        read_only=True,
        would_send_to_broker=False,
    )
