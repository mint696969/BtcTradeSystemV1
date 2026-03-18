# path: ./btcts_next/src/btcts/market_engine/onboarding/bitflyer_review_policy.py
# desc: Review-only Layer3 policy draft for bitFlyer orderbook diff usage.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BitflyerReviewDecision:
    bucket: str
    reason: str
    top50_overlap_floor: float
    best_gap_ceiling: float
    dominant_gap_side: str


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_bitflyer_rebuild_case(case: dict[str, Any]) -> BitflyerReviewDecision:
    not_crossed_ok = bool(case.get("not_crossed_ok"))
    top_of_book_ok = bool(case.get("top_of_book_ok"))

    bid_overlap_top50 = _as_float(case.get("bid_overlap_top50")) or 0.0
    ask_overlap_top50 = _as_float(case.get("ask_overlap_top50")) or 0.0
    best_bid_gap_abs = _as_float(case.get("best_bid_gap_abs")) or 0.0
    best_ask_gap_abs = _as_float(case.get("best_ask_gap_abs")) or 0.0
    dominant_gap_side = str(case.get("dominant_gap_side") or "unknown")

    top50_overlap_floor = min(bid_overlap_top50, ask_overlap_top50)
    best_gap_ceiling = max(best_bid_gap_abs, best_ask_gap_abs)

    if not not_crossed_ok:
        return BitflyerReviewDecision(
            bucket="reanchor_required",
            reason="book crossed during rebuild review",
            top50_overlap_floor=top50_overlap_floor,
            best_gap_ceiling=best_gap_ceiling,
            dominant_gap_side=dominant_gap_side,
        )

    if top50_overlap_floor < 0.30:
        return BitflyerReviewDecision(
            bucket="reanchor_required",
            reason="structural overlap collapsed",
            top50_overlap_floor=top50_overlap_floor,
            best_gap_ceiling=best_gap_ceiling,
            dominant_gap_side=dominant_gap_side,
        )

    if top_of_book_ok:
        return BitflyerReviewDecision(
            bucket="allow_structural_use",
            reason="top of book matched and structure remained healthy",
            top50_overlap_floor=top50_overlap_floor,
            best_gap_ceiling=best_gap_ceiling,
            dominant_gap_side=dominant_gap_side,
        )

    if top50_overlap_floor >= 0.90 and best_gap_ceiling <= 1500.0:
        return BitflyerReviewDecision(
            bucket="allow_structural_use",
            reason="best mismatch is small while top50 structure remained very strong",
            top50_overlap_floor=top50_overlap_floor,
            best_gap_ceiling=best_gap_ceiling,
            dominant_gap_side=dominant_gap_side,
        )

    if top50_overlap_floor >= 0.60 and best_gap_ceiling <= 5000.0:
        return BitflyerReviewDecision(
            bucket="observe_only",
            reason="structure is partially healthy but exact best reconstruction is weak",
            top50_overlap_floor=top50_overlap_floor,
            best_gap_ceiling=best_gap_ceiling,
            dominant_gap_side=dominant_gap_side,
        )

    return BitflyerReviewDecision(
        bucket="reanchor_required",
        reason="gap/overlap quality is too weak for structural use",
        top50_overlap_floor=top50_overlap_floor,
        best_gap_ceiling=best_gap_ceiling,
        dominant_gap_side=dominant_gap_side,
    )