# path: ./btcts_next/src/btcts/processing/l3_market_semantics/zone/zone_engine.py
# desc: Hybrid near/far zone engine for assembled market truth and density metadata.

from __future__ import annotations

from dataclasses import replace
from typing import Any

from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.market_engine.types import ZoneScope


def _levels(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


class ZoneEngine:
    def split_book(
        self,
        *,
        book_state: BookState,
        zone_policy: dict[str, Any],
    ) -> BookState:
        near_levels = int(zone_policy.get("near_levels", 50) or 50)
        far_levels = int(zone_policy.get("far_levels", 200) or 200)

        bids_full = _levels(book_state.bids_near) + _levels(book_state.bids_far)
        asks_full = _levels(book_state.asks_near) + _levels(book_state.asks_far)

        next_book = replace(book_state)
        next_book.bids_near = bids_full[:near_levels]
        next_book.asks_near = asks_full[:near_levels]
        next_book.bids_far = bids_full[near_levels:near_levels + far_levels]
        next_book.asks_far = asks_full[near_levels:near_levels + far_levels]
        return next_book

    def zone_metadata(
        self,
        *,
        book_state: BookState,
        zone_policy: dict[str, Any],
    ) -> dict[str, Any]:
        near_levels = int(zone_policy.get("near_levels", 50) or 50)
        far_levels = int(zone_policy.get("far_levels", 200) or 200)

        return {
            "mode": "hybrid",
            "near_scope": ZoneScope.NEAR.value,
            "far_scope": ZoneScope.FAR.value,
            "near_levels": near_levels,
            "far_levels": far_levels,
            "bids_near_count": len(book_state.bids_near),
            "asks_near_count": len(book_state.asks_near),
            "bids_far_count": len(book_state.bids_far),
            "asks_far_count": len(book_state.asks_far),
            "density_difference_visible": True,
        }

    def apply(
        self,
        *,
        book_state: BookState,
        zone_policy: dict[str, Any],
    ) -> tuple[BookState, dict[str, Any]]:
        zoned = self.split_book(book_state=book_state, zone_policy=zone_policy)
        metadata = self.zone_metadata(book_state=zoned, zone_policy=zone_policy)
        return zoned, metadata