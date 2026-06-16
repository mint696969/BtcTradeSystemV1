# path: ./btcts_next/src/btcts/autotrade/modes.py
# desc: AutoTrade mode state machine and human-control policy.

from __future__ import annotations

from enum import Enum
from typing import Final, FrozenSet, Tuple


class AutoTradeMode(str, Enum):
    OFF = "OFF"
    SHADOW = "SHADOW"
    PAPER_OR_REPLAY = "PAPER_OR_REPLAY"
    ARMED_DRY_RUN = "ARMED_DRY_RUN"
    LIVE_MIN_SIZE = "LIVE_MIN_SIZE"
    LIVE_CONTROLLED = "LIVE_CONTROLLED"
    HALTED = "HALTED"


class HumanControlMode(str, Enum):
    MANUAL_APPROVE = "manual_approve"
    AUTO_ALLOWED = "auto_allowed"


DANGEROUS_MODES: Final[FrozenSet[AutoTradeMode]] = frozenset(
    {
        AutoTradeMode.LIVE_MIN_SIZE,
        AutoTradeMode.LIVE_CONTROLLED,
    }
)

SAFE_DOWNGRADE_TARGETS: Final[FrozenSet[AutoTradeMode]] = frozenset(
    {
        AutoTradeMode.OFF,
        AutoTradeMode.SHADOW,
        AutoTradeMode.HALTED,
    }
)

ALLOWED_HUMAN_ESCALATIONS: Final[dict[AutoTradeMode, Tuple[AutoTradeMode, ...]]] = {
    AutoTradeMode.OFF: (AutoTradeMode.SHADOW,),
    AutoTradeMode.SHADOW: (AutoTradeMode.PAPER_OR_REPLAY, AutoTradeMode.OFF),
    AutoTradeMode.PAPER_OR_REPLAY: (AutoTradeMode.ARMED_DRY_RUN, AutoTradeMode.SHADOW, AutoTradeMode.OFF),
    AutoTradeMode.ARMED_DRY_RUN: (AutoTradeMode.LIVE_MIN_SIZE, AutoTradeMode.PAPER_OR_REPLAY, AutoTradeMode.OFF),
    AutoTradeMode.LIVE_MIN_SIZE: (AutoTradeMode.LIVE_CONTROLLED, AutoTradeMode.ARMED_DRY_RUN, AutoTradeMode.OFF),
    AutoTradeMode.LIVE_CONTROLLED: (AutoTradeMode.LIVE_MIN_SIZE, AutoTradeMode.ARMED_DRY_RUN, AutoTradeMode.OFF),
    AutoTradeMode.HALTED: (AutoTradeMode.OFF, AutoTradeMode.SHADOW),
}


def requires_human_confirmation(current: AutoTradeMode, target: AutoTradeMode) -> bool:
    if target in DANGEROUS_MODES:
        return True
    if current == AutoTradeMode.HALTED and target != AutoTradeMode.OFF:
        return True
    return target not in SAFE_DOWNGRADE_TARGETS


def is_transition_allowed(current: AutoTradeMode, target: AutoTradeMode, *, human_confirmed: bool) -> bool:
    if current == target:
        return True
    allowed = target in ALLOWED_HUMAN_ESCALATIONS.get(current, ())
    if not allowed:
        return False
    if requires_human_confirmation(current, target) and not human_confirmed:
        return False
    return True


def default_human_control_for_mode(mode: AutoTradeMode) -> HumanControlMode:
    if mode in {AutoTradeMode.LIVE_MIN_SIZE, AutoTradeMode.LIVE_CONTROLLED}:
        return HumanControlMode.MANUAL_APPROVE
    return HumanControlMode.AUTO_ALLOWED
