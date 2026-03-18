# path: ./btcts_next/src/btcts/market_engine/onboarding/bitflyer_rebuild_review.py
# desc: Shared rebuild review helper for bitFlyer onboarding/review flows.

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any

from btcts.collector_vnext.orderbook.book_rebuilder import OrderBookRebuilder
from btcts.market_engine.onboarding.bitflyer_review_policy import evaluate_bitflyer_rebuild_case
from btcts.market_engine.onboarding.rebuild_validator import RebuildValidator
from btcts.market_engine.onboarding.stream_classifier import StreamClassifier


@dataclass(frozen=True)
class BitflyerRebuildCompareCase:
    compare_no: int
    diffs_applied: int
    top_of_book_ok: bool
    not_crossed_ok: bool
    assembled_best_bid: float | None
    assembled_best_ask: float | None
    reference_best_bid: float | None
    reference_best_ask: float | None
    best_bid_gap_abs: float | None
    best_ask_gap_abs: float | None
    dominant_gap_side: str
    review_bucket: str
    review_reason: str
    bid_overlap_top10: float
    ask_overlap_top10: float
    bid_overlap_top50: float
    ask_overlap_top50: float


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


def _logical_stream_group_key(
    *,
    classifier: StreamClassifier,
    event: dict[str, Any],
) -> str:
    classified = classifier.classify(event)
    stream_session_id = classified.stream_session_id or "missing"

    normalized = stream_session_id
    normalized = re.sub(r"-\d{8}T\d{6}Z-[0-9a-f]+$", "", normalized)
    normalized = normalized.replace("-board_snapshot", "-board")
    normalized = normalized.replace("-board_ws", "-board")
    return normalized


def _event_sort_key(
    *,
    classifier: StreamClassifier,
    event: dict[str, Any],
) -> tuple[str, int, int, str]:
    classified = classifier.classify(event)

    payload_dict = _payload(event)
    event_ts = str(
        event.get("event_ts")
        or event.get("collector_ts")
        or event.get("ingest_ts")
        or payload_dict.get("event_ts")
        or ""
    )

    family_rank_map = {
        "boundary": 0,
        "snapshot": 1,
        "diff": 2,
    }
    family_rank = family_rank_map.get(classified.family, 9)

    seq = classified.sequence_id
    seq_key = seq if isinstance(seq, int) else 10**18

    record_id = str(event.get("record_id") or "")
    return (event_ts, family_rank, seq_key, record_id)


def _best_from_side(side: Any, *, reverse: bool) -> float | None:
    best: float | None = None
    rows = side if isinstance(side, list) else []

    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            price = float(row["price"])
        except (KeyError, TypeError, ValueError):
            continue

        if best is None:
            best = price
            continue

        if reverse:
            if price > best:
                best = price
        else:
            if price < best:
                best = price

    return best


def _top_prices(side: Any, *, reverse: bool, limit: int) -> list[float]:
    rows = side if isinstance(side, list) else []
    prices: list[float] = []

    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            price = float(row["price"])
        except (KeyError, TypeError, ValueError):
            continue
        prices.append(price)

    prices.sort(reverse=reverse)
    return prices[:limit]


def _overlap_ratio(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    sa = set(a)
    sb = set(b)
    return len(sa & sb) / float(len(sa | sb))


def _book_side_prices(
    rebuilder: OrderBookRebuilder,
    *,
    reverse: bool,
    limit: int,
) -> list[float]:
    side_map = rebuilder.book.bids if reverse else rebuilder.book.asks

    prices: list[float] = []
    for price in side_map.keys():
        try:
            prices.append(float(price))
        except (TypeError, ValueError):
            continue

    prices.sort(reverse=reverse)
    return prices[:limit]


def _reference_snapshot_from_event(event: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(event)
    return {
        "best_bid": _best_from_side(payload.get("bids"), reverse=True),
        "best_ask": _best_from_side(payload.get("asks"), reverse=False),
    }


def _rebuilder_event_from_canonical(event: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(event)
    record_type = str(event.get("record_type") or "")

    if record_type == "market.orderbook.snapshot":
        event_type = "snapshot"
    elif record_type == "market.orderbook.diff":
        event_type = "delta"
    else:
        raise ValueError(f"unsupported orderbook record_type: {record_type}")

    return {
        "event_type": event_type,
        "bids": payload.get("bids") or [],
        "asks": payload.get("asks") or [],
    }


def _gap_abs(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return abs(float(a) - float(b))


def _dominant_gap_side(
    best_bid_gap_abs: float | None,
    best_ask_gap_abs: float | None,
) -> str:
    bid_gap = best_bid_gap_abs if best_bid_gap_abs is not None else -1.0
    ask_gap = best_ask_gap_abs if best_ask_gap_abs is not None else -1.0

    if bid_gap < 0.0 and ask_gap < 0.0:
        return "unknown"
    if bid_gap > ask_gap:
        return "bid"
    if ask_gap > bid_gap:
        return "ask"
    return "balanced"


def _avg(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _strength_score(case: BitflyerRebuildCompareCase) -> float:
    return (
        (1.0 if case.top_of_book_ok else 0.0) * 2.0
        + (1.0 if case.not_crossed_ok else 0.0) * 0.5
        + case.bid_overlap_top10
        + case.ask_overlap_top10
        + case.bid_overlap_top50
        + case.ask_overlap_top50
    )


def _resilience_score(case: BitflyerRebuildCompareCase) -> float:
    return (
        (1.0 if case.not_crossed_ok else 0.0)
        + case.bid_overlap_top50
        + case.ask_overlap_top50
    )


def _bucket_for_diffs(n: int) -> str:
    if n <= 1:
        return "1"
    if n <= 3:
        return "2-3"
    if n <= 7:
        return "4-7"
    if n <= 15:
        return "8-15"
    if n <= 31:
        return "16-31"
    return "32+"


def build_bitflyer_rebuild_review(
    *,
    normalized_events: list[dict[str, Any]],
    profile_name_hint: str,
) -> dict[str, Any]:
    classifier = StreamClassifier()
    validator = RebuildValidator()

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in normalized_events:
        group_key = _logical_stream_group_key(classifier=classifier, event=row)
        grouped.setdefault(group_key, []).append(row)

    board_groups = {
        key: sorted(value, key=lambda item: _event_sort_key(classifier=classifier, event=item))
        for key, value in grouped.items()
        if "-bitflyer-board" in key or key.endswith("-board")
    }

    if not board_groups:
        raise RuntimeError("no board logical stream group found in onboarding input")

    logical_group_key = sorted(board_groups.keys())[0]
    events = board_groups[logical_group_key]

    snapshot_count = 0
    diff_count = 0
    boundary_count = 0
    compare_cases: list[BitflyerRebuildCompareCase] = []

    rebuilder = OrderBookRebuilder()
    active_anchor_loaded = False
    diffs_since_anchor = 0

    for event in events:
        classified = classifier.classify(event)

        if classified.family == "boundary":
            boundary_count += 1
            continue

        if classified.family == "snapshot":
            snapshot_count += 1

            if not active_anchor_loaded:
                rebuilder.apply_event(_rebuilder_event_from_canonical(event))
                active_anchor_loaded = True
                diffs_since_anchor = 0
                continue

            if diffs_since_anchor > 0:
                reference_snapshot = _reference_snapshot_from_event(event)
                assembled_book = {
                    "best_bid": rebuilder.best_bid(),
                    "best_ask": rebuilder.best_ask(),
                }

                top_of_book_result = validator.validate_top_of_book(
                    assembled_book=assembled_book,
                    reference_snapshot=reference_snapshot,
                )
                not_crossed_result = validator.validate_not_crossed(
                    assembled_book=assembled_book,
                )

                assembled_bids = _book_side_prices(rebuilder, reverse=True, limit=50)
                assembled_asks = _book_side_prices(rebuilder, reverse=False, limit=50)

                ref_payload = _payload(event)
                ref_bids = _top_prices(ref_payload.get("bids"), reverse=True, limit=50)
                ref_asks = _top_prices(ref_payload.get("asks"), reverse=False, limit=50)

                bid_overlap_top10 = _overlap_ratio(assembled_bids[:10], ref_bids[:10])
                ask_overlap_top10 = _overlap_ratio(assembled_asks[:10], ref_asks[:10])
                bid_overlap_top50 = _overlap_ratio(assembled_bids, ref_bids)
                ask_overlap_top50 = _overlap_ratio(assembled_asks, ref_asks)

                best_bid_gap_abs = _gap_abs(
                    assembled_book.get("best_bid"),
                    reference_snapshot.get("best_bid"),
                )
                best_ask_gap_abs = _gap_abs(
                    assembled_book.get("best_ask"),
                    reference_snapshot.get("best_ask"),
                )
                dominant_gap_side = _dominant_gap_side(
                    best_bid_gap_abs,
                    best_ask_gap_abs,
                )

                review_decision = evaluate_bitflyer_rebuild_case(
                    {
                        "top_of_book_ok": top_of_book_result.ok,
                        "not_crossed_ok": not_crossed_result.ok,
                        "best_bid_gap_abs": best_bid_gap_abs,
                        "best_ask_gap_abs": best_ask_gap_abs,
                        "dominant_gap_side": dominant_gap_side,
                        "bid_overlap_top50": bid_overlap_top50,
                        "ask_overlap_top50": ask_overlap_top50,
                    }
                )

                compare_cases.append(
                    BitflyerRebuildCompareCase(
                        compare_no=len(compare_cases) + 1,
                        diffs_applied=diffs_since_anchor,
                        top_of_book_ok=top_of_book_result.ok,
                        not_crossed_ok=not_crossed_result.ok,
                        assembled_best_bid=assembled_book.get("best_bid"),
                        assembled_best_ask=assembled_book.get("best_ask"),
                        reference_best_bid=reference_snapshot.get("best_bid"),
                        reference_best_ask=reference_snapshot.get("best_ask"),
                        best_bid_gap_abs=best_bid_gap_abs,
                        best_ask_gap_abs=best_ask_gap_abs,
                        dominant_gap_side=dominant_gap_side,
                        review_bucket=review_decision.bucket,
                        review_reason=review_decision.reason,
                        bid_overlap_top10=bid_overlap_top10,
                        ask_overlap_top10=ask_overlap_top10,
                        bid_overlap_top50=bid_overlap_top50,
                        ask_overlap_top50=ask_overlap_top50,
                    )
                )

            rebuilder.apply_event(_rebuilder_event_from_canonical(event))
            diffs_since_anchor = 0
            continue

        if classified.family == "diff":
            diff_count += 1
            rebuilder.apply_event(_rebuilder_event_from_canonical(event))
            if rebuilder.snapshot_loaded:
                diffs_since_anchor += 1
            continue

    buckets: dict[str, list[BitflyerRebuildCompareCase]] = {}
    for case in compare_cases:
        key = _bucket_for_diffs(case.diffs_applied)
        buckets.setdefault(key, []).append(case)

    diff_length_distribution: dict[str, dict[str, float]] = {}
    for key, cases in buckets.items():
        diff_length_distribution[key] = {
            "cases": len(cases),
            "best_bid_match_rate": _avg([1.0 if c.assembled_best_bid == c.reference_best_bid else 0.0 for c in cases]),
            "best_ask_match_rate": _avg([1.0 if c.assembled_best_ask == c.reference_best_ask else 0.0 for c in cases]),
            "avg_bid_overlap_top10": _avg([c.bid_overlap_top10 for c in cases]),
            "avg_ask_overlap_top10": _avg([c.ask_overlap_top10 for c in cases]),
            "avg_bid_overlap_top50": _avg([c.bid_overlap_top50 for c in cases]),
            "avg_ask_overlap_top50": _avg([c.ask_overlap_top50 for c in cases]),
            "not_crossed_rate": _avg([1.0 if c.not_crossed_ok else 0.0 for c in cases]),
        }

    strongest_cases = sorted(compare_cases, key=_strength_score, reverse=True)[:5]
    weakest_cases = sorted(compare_cases, key=_strength_score)[:5]
    resilient_but_not_best_cases = [
        case
        for case in sorted(compare_cases, key=_resilience_score, reverse=True)
        if not case.top_of_book_ok and case.not_crossed_ok
    ][:5]

    summary = {
        "cases_with_diffs": len(compare_cases),
        "best_bid_match_rate": _avg([1.0 if case.assembled_best_bid == case.reference_best_bid else 0.0 for case in compare_cases]),
        "best_ask_match_rate": _avg([1.0 if case.assembled_best_ask == case.reference_best_ask else 0.0 for case in compare_cases]),
        "top_of_book_ok_rate": _avg([1.0 if case.top_of_book_ok else 0.0 for case in compare_cases]),
        "not_crossed_pass_rate": _avg([1.0 if case.not_crossed_ok else 0.0 for case in compare_cases]),
        "avg_diffs_applied_per_compare": _avg([float(case.diffs_applied) for case in compare_cases]),
        "avg_bid_overlap_top10": _avg([case.bid_overlap_top10 for case in compare_cases]),
        "avg_ask_overlap_top10": _avg([case.ask_overlap_top10 for case in compare_cases]),
        "avg_bid_overlap_top50": _avg([case.bid_overlap_top50 for case in compare_cases]),
        "avg_ask_overlap_top50": _avg([case.ask_overlap_top50 for case in compare_cases]),
        "avg_best_bid_gap_abs": _avg([case.best_bid_gap_abs for case in compare_cases if case.best_bid_gap_abs is not None]),
        "avg_best_ask_gap_abs": _avg([case.best_ask_gap_abs for case in compare_cases if case.best_ask_gap_abs is not None]),
        "dominant_gap_side_counts": {
            "bid": sum(1 for case in compare_cases if case.dominant_gap_side == "bid"),
            "ask": sum(1 for case in compare_cases if case.dominant_gap_side == "ask"),
            "balanced": sum(1 for case in compare_cases if case.dominant_gap_side == "balanced"),
            "unknown": sum(1 for case in compare_cases if case.dominant_gap_side == "unknown"),
        },
        "review_bucket_counts": {
            "allow_structural_use": sum(1 for case in compare_cases if case.review_bucket == "allow_structural_use"),
            "observe_only": sum(1 for case in compare_cases if case.review_bucket == "observe_only"),
            "reanchor_required": sum(1 for case in compare_cases if case.review_bucket == "reanchor_required"),
        },
        "diff_length_distribution": diff_length_distribution,
    }

    return {
        "ok": True,
        "profile_name_hint": profile_name_hint,
        "logical_group_key": logical_group_key,
        "total_group_events": len(events),
        "snapshot_count": snapshot_count,
        "diff_count": diff_count,
        "boundary_count": boundary_count,
        "compare_count": len(compare_cases),
        "cases": [asdict(case) for case in compare_cases],
        "summary": summary,
        "representative_cases": {
            "strongest": [asdict(case) for case in strongest_cases],
            "weakest": [asdict(case) for case in weakest_cases],
            "resilient_but_not_best": [asdict(case) for case in resilient_but_not_best_cases],
        },
    }