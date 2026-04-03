# path: ./btcts_next/src/btcts/processing/l3_market_semantics/continuity/trust_engine.py
# desc: Trust evaluation engine for continuity and assembled market-state semantics.

from __future__ import annotations

from btcts.market_engine.assembler.models.book_state import BookState
from btcts.market_engine.assembler.models.series_state import SeriesState
from btcts.market_engine.assembler.models.trust_state import TrustStateModel
from btcts.market_engine.types import BoundaryReason, TrustState


class TrustEngine:
    def evaluate(
        self,
        book_state: BookState,
        series_state: SeriesState,
        *,
        profile_valid: bool,
        has_anchor: bool,
        invalid_diff_attach: bool = False,
    ) -> TrustStateModel:
        if invalid_diff_attach:
            return TrustStateModel.broken_state(BoundaryReason.INVALID_DIFF_ATTACH)

        if not has_anchor:
            return TrustStateModel.provisional_state(
                series_state.boundary_reason if series_state.boundary_reason != BoundaryReason.NONE else BoundaryReason.UNKNOWN
            )

        if not profile_valid:
            return TrustStateModel.quarantined_state(
                series_state.boundary_reason if series_state.boundary_reason != BoundaryReason.NONE else BoundaryReason.PROFILE_RULE
            )

        if series_state.trust_state == TrustState.BROKEN:
            return TrustStateModel.broken_state(series_state.boundary_reason)

        if series_state.trust_state == TrustState.QUARANTINED:
            return TrustStateModel.quarantined_state(series_state.boundary_reason)

        if series_state.trust_state == TrustState.PROVISIONAL:
            return TrustStateModel.provisional_state(
                series_state.boundary_reason if series_state.boundary_reason != BoundaryReason.NONE else book_state.boundary_reason
            )

        return TrustStateModel.trusted_state(
            series_state.boundary_reason if series_state.boundary_reason != BoundaryReason.NONE else book_state.boundary_reason
        )

    def apply(
        self,
        book_state: BookState,
        series_state: SeriesState,
        *,
        profile_valid: bool,
        has_anchor: bool,
        invalid_diff_attach: bool = False,
    ) -> BookState:
        trust = self.evaluate(
            book_state,
            series_state,
            profile_valid=profile_valid,
            has_anchor=has_anchor,
            invalid_diff_attach=invalid_diff_attach,
        )
        book_state.trust_state = trust.state
        book_state.boundary_reason = trust.reason
        return book_state