# path: ./btcts_next/src/btcts/market_engine/profiles/bitflyer.py
# desc: bitFlyer exchange profile for Market Engine orderbook assembly and continuity policy.

from __future__ import annotations

from dataclasses import replace
from typing import Any

from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.processing.l3_market_semantics.continuity.models import SeriesState
from btcts.market_engine.profiles.base import ExchangeProfile
from btcts.market_engine.types import BoundaryReason


def _payload(normalized_event: dict[str, Any]) -> dict[str, Any]:
    payload = normalized_event.get("payload")
    return payload if isinstance(payload, dict) else {}


def _levels(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


def _normalize_bids(levels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[float, dict[str, Any]] = {}
    for item in levels:
        try:
            price = float(item["price"])
            size = float(item["size"])
        except Exception:
            continue
        if size <= 0:
            deduped.pop(price, None)
            continue
        deduped[price] = {"price": price, "size": size}
    return [deduped[p] for p in sorted(deduped.keys(), reverse=True)]


def _normalize_asks(levels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[float, dict[str, Any]] = {}
    for item in levels:
        try:
            price = float(item["price"])
            size = float(item["size"])
        except Exception:
            continue
        if size <= 0:
            deduped.pop(price, None)
            continue
        deduped[price] = {"price": price, "size": size}
    return [deduped[p] for p in sorted(deduped.keys())]


def _best_bid(levels: list[dict[str, Any]]) -> float | None:
    if not levels:
        return None
    try:
        return float(levels[0]["price"])
    except Exception:
        return None


def _best_ask(levels: list[dict[str, Any]]) -> float | None:
    if not levels:
        return None
    try:
        return float(levels[0]["price"])
    except Exception:
        return None


def _spread(best_bid: float | None, best_ask: float | None) -> float | None:
    if best_bid is None or best_ask is None:
        return None
    return best_ask - best_bid


def _mid_price(best_bid: float | None, best_ask: float | None) -> float | None:
    if best_bid is None or best_ask is None:
        return None
    return (best_bid + best_ask) / 2.0


class BitflyerProfile(ExchangeProfile):
    profile_name = "bitflyer"

    min_healthy_overlap_top10 = 0.8
    strong_best_gap_abs = 1000.0
    dominant_drift_side = "ask"
    small_timing_drift_decision = "allow"
    strong_timing_drift_decision = "observe"

    review_allow_top50_floor = 0.90
    review_observe_top50_floor = 0.60
    review_reanchor_top50_floor = 0.30

    review_allow_best_gap_abs = 1500.0
    review_observe_best_gap_abs = 5000.0

    anchor_truth_mode = "snapshot"
    diff_usage_mode = "conditional_structural_use"

    def classify_event(self, normalized_event: dict[str, Any]) -> str:
        record_type = str(normalized_event.get("record_type") or "")
        payload = _payload(normalized_event)
        event_type = str(payload.get("event_type") or "")

        if record_type.startswith("stream."):
            return "boundary"
        if record_type == "market.orderbook.snapshot":
            return "snapshot"
        if record_type == "market.orderbook.diff":
            return "diff"
        if record_type == "market.trade":
            return "trade"
        if event_type:
            return event_type
        return "unknown"

    def message_family(self, normalized_event: dict[str, Any]) -> str:
        return str(normalized_event.get("record_type") or "unknown")

    def is_boundary_event(self, normalized_event: dict[str, Any]) -> bool:
        record_type = str(normalized_event.get("record_type") or "")
        if record_type.startswith("stream."):
            return True

        payload = _payload(normalized_event)
        continuity_state = str(payload.get("continuity_state") or "")
        return continuity_state == "gap_detected"

    def boundary_reason(self, normalized_event: dict[str, Any]) -> BoundaryReason:
        record_type = str(normalized_event.get("record_type") or "")
        payload = _payload(normalized_event)
        continuity_state = str(payload.get("continuity_state") or "")

        if record_type == "stream.started":
            return BoundaryReason.STREAM_STARTED
        if record_type == "stream.gap_detected" or continuity_state == "gap_detected":
            return BoundaryReason.GAP_DETECTED
        if record_type == "stream.resync_started":
            return BoundaryReason.RESYNC_STARTED
        if record_type == "stream.resync_completed":
            return BoundaryReason.RESYNC_COMPLETED
        return BoundaryReason.NONE

    def is_anchor_candidate(self, normalized_event: dict[str, Any]) -> bool:
        record_type = str(normalized_event.get("record_type") or "")
        if record_type != "market.orderbook.snapshot":
            return False

        payload = _payload(normalized_event)
        event_type = str(payload.get("event_type") or "")
        return event_type in {"snapshot", ""}

    def can_attach_diff(
        self,
        book_state: BookState,
        normalized_event: dict[str, Any],
        series_state: SeriesState,
    ) -> bool:
        if str(normalized_event.get("record_type") or "") != "market.orderbook.diff":
            return False

        if book_state.anchor_event_id is None:
            return False

        payload = _payload(normalized_event)
        continuity_state = str(payload.get("continuity_state") or "")
        if continuity_state != "continuous":
            return False

        if series_state.boundary_reason == BoundaryReason.GAP_DETECTED:
            return False

        return True

    def apply_anchor(self, book_state: BookState, normalized_event: dict[str, Any]) -> BookState:
        payload = _payload(normalized_event)
        bids = _levels(payload.get("bids"))
        asks = _levels(payload.get("asks"))

        updated = replace(book_state)
        updated.bids_near = _normalize_bids(bids)
        updated.asks_near = _normalize_asks(asks)
        updated.bids_far = []
        updated.asks_far = []
        updated.best_bid = _best_bid(updated.bids_near)
        updated.best_ask = _best_ask(updated.asks_near)
        updated.spread = _spread(updated.best_bid, updated.best_ask)
        updated.mid_price = _mid_price(updated.best_bid, updated.best_ask)
        updated.continuity_state = str(payload.get("continuity_state") or "")
        return updated

    def apply_diff(self, book_state: BookState, normalized_event: dict[str, Any]) -> BookState:
        payload = _payload(normalized_event)
        bids = _levels(payload.get("bids"))
        asks = _levels(payload.get("asks"))

        updated = replace(book_state)

        merged_bids = list(updated.bids_near)
        merged_asks = list(updated.asks_near)

        if bids:
            merged_bids = list(bids) + merged_bids
        if asks:
            merged_asks = list(asks) + merged_asks

        updated.bids_near = _normalize_bids(merged_bids)
        updated.asks_near = _normalize_asks(merged_asks)

        updated.best_bid = _best_bid(updated.bids_near)
        updated.best_ask = _best_ask(updated.asks_near)
        updated.spread = _spread(updated.best_bid, updated.best_ask)
        updated.mid_price = _mid_price(updated.best_bid, updated.best_ask)
        updated.continuity_state = str(payload.get("continuity_state") or "")
        return updated

    def build_zone_policy(self, book_state: BookState) -> dict[str, Any]:
        return {
            "near_levels": 50,
            "far_levels": 200,
        }

    def validate_rebuild_state(self, book_state: BookState) -> bool:
        # Runtime semantic minimum:
        # - both sides must exist
        # - crossed book is never acceptable
        #
        # Intentionally not enforced here:
        # - exact best-of-book match to a future snapshot
        # - structural overlap thresholds
        # - venue review bucket decisions
        #
        # Those belong to Layer3 review/onboarding policy, where bitFlyer diff
        # is treated as conditional structural-use evidence rather than strict
        # deterministic next-snapshot truth.
        if book_state.best_bid is None or book_state.best_ask is None:
            return False
        if book_state.best_bid > book_state.best_ask:
            return False
        return True

    def review_policy(self) -> dict[str, Any]:
        return {
            "anchor_truth_mode": self.anchor_truth_mode,
            "diff_usage_mode": self.diff_usage_mode,
            "notes": [
                "snapshot is the safer runtime truth anchor",
                "diff is treated as conditional structural-use evidence",
                "best mismatch alone does not imply structural failure",
            ],
            "allow_structural_use": {
                "min_top50_overlap_floor": self.review_allow_top50_floor,
                "max_best_gap_abs": self.review_allow_best_gap_abs,
                "requires_not_crossed": True,
            },
            "observe_only": {
                "min_top50_overlap_floor": self.review_observe_top50_floor,
                "max_best_gap_abs": self.review_observe_best_gap_abs,
                "requires_not_crossed": True,
            },
            "reanchor_required": {
                "top50_overlap_below": self.review_reanchor_top50_floor,
                "crossed_book_forces_reanchor": True,
            },
        }

    def audit_policy(self) -> dict[str, Any]:
        review_policy = self.review_policy()
        return {
            "min_healthy_overlap_top10": self.min_healthy_overlap_top10,
            "strong_best_gap_abs": self.strong_best_gap_abs,
            "dominant_drift_side": self.dominant_drift_side,
            "small_timing_drift_decision": self.small_timing_drift_decision,
            "strong_timing_drift_decision": self.strong_timing_drift_decision,
            "anchor_truth_mode": self.anchor_truth_mode,
            "diff_usage_mode": self.diff_usage_mode,
            "review_notes": review_policy.get("notes"),
            "review_allow_top50_floor": self.review_allow_top50_floor,
            "review_observe_top50_floor": self.review_observe_top50_floor,
            "review_reanchor_top50_floor": self.review_reanchor_top50_floor,
            "review_allow_best_gap_abs": self.review_allow_best_gap_abs,
            "review_observe_best_gap_abs": self.review_observe_best_gap_abs,
        }

    def orderbook_semantic_policy(self) -> dict[str, Any]:
        return {
            "pressure_threshold": 0.20,
            "wall_ratio_threshold": 0.30,
            "wall_near_rank_threshold": 5,
            "pull_threshold": 0.20,
            "pull_near_levels": 3,
            "strong_pull_threshold": 0.40,
        }

    def build_snapshot_drift_review_summary(
        self,
        normalized_events: list[dict[str, Any]],
        *,
        profile_name_hint: str,
    ) -> dict[str, Any] | None:
        from btcts.market_engine.onboarding.bitflyer_snapshot_drift_review import (
            build_bitflyer_snapshot_drift_review_summary,
        )

        return build_bitflyer_snapshot_drift_review_summary(
            normalized_events,
            profile_name_hint=profile_name_hint,
            review_policy=self.review_policy(),
        )

    def build_rebuild_review(
        self,
        *,
        normalized_events: list[dict[str, Any]],
        profile_name_hint: str,
    ) -> dict[str, Any] | None:
        from btcts.market_engine.onboarding.bitflyer_rebuild_review import (
            build_bitflyer_rebuild_review,
        )

        return build_bitflyer_rebuild_review(
            normalized_events=normalized_events,
            profile_name_hint=profile_name_hint,
            review_policy=self.review_policy(),
        )