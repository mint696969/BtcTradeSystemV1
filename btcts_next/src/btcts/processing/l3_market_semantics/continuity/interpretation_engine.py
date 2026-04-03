# path: ./btcts_next/src/btcts/processing/l3_market_semantics/continuity/interpretation_engine.py
# desc: Layer3 continuity and structural-use interpretation engine.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.market_engine.types import BoundaryReason, TrustState


@dataclass(frozen=True)
class InterpretationDecision:
    bucket: str
    reason: str
    policy: dict[str, Any]


class InterpretationEngine:
    def evaluate(
        self,
        *,
        trust_state: TrustState,
        boundary_reason: BoundaryReason,
        continuity_state: str | None,
        review_policy: dict[str, Any],
    ) -> InterpretationDecision:
        dangerous_boundaries = {
            BoundaryReason.GAP_DETECTED,
            BoundaryReason.RESYNC_STARTED,
            BoundaryReason.INVALID_DIFF_ATTACH,
        }

        if trust_state != TrustState.TRUSTED:
            return InterpretationDecision(
                bucket="reanchor_required",
                reason="trust_state is not trusted",
                policy=review_policy,
            )

        if boundary_reason in dangerous_boundaries:
            return InterpretationDecision(
                bucket="reanchor_required",
                reason=f"boundary_reason={boundary_reason.value}",
                policy=review_policy,
            )

        if continuity_state not in {None, "", "continuous"}:
            return InterpretationDecision(
                bucket="reanchor_required",
                reason=f"continuity_state={continuity_state}",
                policy=review_policy,
            )

        return InterpretationDecision(
            bucket="allow_structural_use",
            reason="trusted state with continuous series",
            policy=review_policy,
        )