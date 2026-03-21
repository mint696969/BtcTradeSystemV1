# path: ./btcts_next/src/btcts/market_engine/onboarding/bitflyer_review_policy.py
# desc: Compatibility wrapper for bitFlyer-specific review policy thresholds.

from __future__ import annotations

from btcts.market_engine.onboarding.review_policy import ReviewDecision, evaluate_rebuild_case


BITFLYER_REVIEW_POLICY = {
    "allow_structural_use": {
        "min_top50_overlap_floor": 0.90,
        "max_best_gap_abs": 1500.0,
        "requires_not_crossed": True,
    },
    "observe_only": {
        "min_top50_overlap_floor": 0.60,
        "max_best_gap_abs": 5000.0,
        "requires_not_crossed": True,
    },
    "reanchor_required": {
        "top50_overlap_below": 0.30,
        "crossed_book_forces_reanchor": True,
    },
}


BitflyerReviewDecision = ReviewDecision


def evaluate_bitflyer_rebuild_case(case: dict[str, object]) -> ReviewDecision:
    return evaluate_rebuild_case(case, policy=BITFLYER_REVIEW_POLICY)