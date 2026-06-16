# path: ./btcts_next/src/btcts/autotrade/strategy/models.py
# desc: AutoTrade deterministic action candidate models.

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Tuple


class CandidateAction(str, Enum):
    ENTRY_BUY = "ENTRY_BUY"
    ENTRY_SELL = "ENTRY_SELL"
    WAIT = "WAIT"
    WATCH_BUY = "WATCH_BUY"
    WATCH_SELL = "WATCH_SELL"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    EXIT = "EXIT"
    CANCEL_ORDER = "CANCEL_ORDER"
    REPRICE_ORDER = "REPRICE_ORDER"
    NO_NEW_ENTRY = "NO_NEW_ENTRY"
    HALT = "HALT"


class StrategyProfile(str, Enum):
    STALE_GUARD = "stale_guard"
    LOW_CONFIDENCE = "low_confidence"
    NORMAL_MIXED = "normal_mixed"
    BUY_LEANING_MEDIUM = "buy_leaning_medium"
    SELL_LEANING_MEDIUM = "sell_leaning_medium"
    WIDE_SPREAD = "wide_spread"
    TRAP_CAUTION = "trap_caution"
    FORECAST_VOLATILITY_GUARD = "forecast_volatility_guard"


@dataclass(frozen=True)
class ActionCandidate:
    candidate_id: str
    snapshot_id: str
    forecast_id: str | None
    parameter_set_id: str
    logic_version: str
    action: CandidateAction
    strategy_profile: StrategyProfile
    side: str | None = None
    entry_quality: int = 0
    reason_codes: Tuple[str, ...] = ()
    blocked_hint: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["action"] = self.action.value
        data["strategy_profile"] = self.strategy_profile.value
        return data
