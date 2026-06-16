# path: ./btcts_next/src/btcts/processing/l3_market_semantics/continuity/models/trust_state.py
# desc: Trust state model for Market Engine assembly outputs and transitions.

from __future__ import annotations

from dataclasses import dataclass

from btcts.market_engine.types import BoundaryReason, TrustState as TrustStateValue


@dataclass(frozen=True)
class TrustStateModel:
    state: TrustStateValue
    reason: BoundaryReason = BoundaryReason.NONE
    trusted: bool = False
    provisional: bool = False
    broken: bool = False
    quarantined: bool = False

    @classmethod
    def trusted_state(cls, reason: BoundaryReason = BoundaryReason.NONE) -> "TrustStateModel":
        return cls(
            state=TrustStateValue.TRUSTED,
            reason=reason,
            trusted=True,
            provisional=False,
            broken=False,
            quarantined=False,
        )

    @classmethod
    def provisional_state(cls, reason: BoundaryReason) -> "TrustStateModel":
        return cls(
            state=TrustStateValue.PROVISIONAL,
            reason=reason,
            trusted=False,
            provisional=True,
            broken=False,
            quarantined=False,
        )

    @classmethod
    def broken_state(cls, reason: BoundaryReason) -> "TrustStateModel":
        return cls(
            state=TrustStateValue.BROKEN,
            reason=reason,
            trusted=False,
            provisional=False,
            broken=True,
            quarantined=False,
        )

    @classmethod
    def quarantined_state(cls, reason: BoundaryReason) -> "TrustStateModel":
        return cls(
            state=TrustStateValue.QUARANTINED,
            reason=reason,
            trusted=False,
            provisional=False,
            broken=False,
            quarantined=True,
        )