# path: ./btcts_next/src/btcts/market_engine/onboarding/bitflyer_snapshot_drift_review.py
# desc: Snapshot-to-snapshot drift review helper for bitFlyer onboarding summary.

from __future__ import annotations

import re
from collections import defaultdict
from statistics import mean
from typing import Any

from btcts.market_engine.onboarding.review_policy import evaluate_rebuild_case
from btcts.market_engine.onboarding.stream_classifier import StreamClassifier


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
) -> tuple[int, str, str]:
    classified = classifier.classify(event)

    seq = classified.sequence_id
    seq_key = seq if isinstance(seq, int) else 10**18

    payload = event.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}

    event_ts = str(
        event.get("event_ts")
        or event.get("collector_ts")
        or event.get("ingest_ts")
        or payload_dict.get("event_ts")
        or ""
    )

    record_id = str(event.get("record_id") or "")
    return (seq_key, event_ts, record_id)


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


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


def _best_from_side(side: Any, *, reverse: bool) -> float | None:
    prices = _top_prices(side, reverse=reverse, limit=1)
    return prices[0] if prices else None


def _gap_abs(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return abs(float(a) - float(b))


def build_bitflyer_snapshot_drift_review_summary(
    normalized_events: list[dict[str, Any]],
    *,
    profile_name_hint: str,
    review_policy: dict[str, Any],
) -> dict[str, Any] | None:
    if profile_name_hint != "bitflyer":
        return None

    classifier = StreamClassifier()

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in normalized_events:
        group_key = _logical_stream_group_key(classifier=classifier, event=event)
        grouped[group_key].append(event)

    board_groups = {
        key: sorted(
            value,
            key=lambda item: _event_sort_key(classifier=classifier, event=item),
        )
        for key, value in grouped.items()
        if "-bitflyer-board" in key or key.endswith("-board")
    }
    if not board_groups:
        return None

    logical_group_key = sorted(board_groups.keys())[0]
    events = board_groups[logical_group_key]

    compare_cases: list[dict[str, Any]] = []
    previous_snapshot: dict[str, Any] | None = None
    diffs_since_anchor = 0

    for event in events:
        classified = classifier.classify(event)

        if classified.family == "boundary":
            continue

        if classified.family == "snapshot":
            if previous_snapshot is not None and diffs_since_anchor > 0:
                previous_payload = _payload(previous_snapshot)
                current_payload = _payload(event)

                prev_best_bid = _best_from_side(previous_payload.get("bids"), reverse=True)
                prev_best_ask = _best_from_side(previous_payload.get("asks"), reverse=False)
                curr_best_bid = _best_from_side(current_payload.get("bids"), reverse=True)
                curr_best_ask = _best_from_side(current_payload.get("asks"), reverse=False)

                bid_overlap_top50 = _overlap_ratio(
                    _top_prices(previous_payload.get("bids"), reverse=True, limit=50),
                    _top_prices(current_payload.get("bids"), reverse=True, limit=50),
                )
                ask_overlap_top50 = _overlap_ratio(
                    _top_prices(previous_payload.get("asks"), reverse=False, limit=50),
                    _top_prices(current_payload.get("asks"), reverse=False, limit=50),
                )

                best_bid_gap_abs = _gap_abs(prev_best_bid, curr_best_bid)
                best_ask_gap_abs = _gap_abs(prev_best_ask, curr_best_ask)

                dominant_gap_side = "balanced"
                bid_gap = best_bid_gap_abs if best_bid_gap_abs is not None else -1.0
                ask_gap = best_ask_gap_abs if best_ask_gap_abs is not None else -1.0
                if bid_gap > ask_gap:
                    dominant_gap_side = "bid"
                elif ask_gap > bid_gap:
                    dominant_gap_side = "ask"

                not_crossed_ok = (
                    prev_best_bid is not None
                    and prev_best_ask is not None
                    and prev_best_bid <= prev_best_ask
                )
                top_of_book_ok = prev_best_bid == curr_best_bid and prev_best_ask == curr_best_ask

                review_decision = evaluate_rebuild_case(
                    {
                        "top_of_book_ok": top_of_book_ok,
                        "not_crossed_ok": not_crossed_ok,
                        "best_bid_gap_abs": best_bid_gap_abs,
                        "best_ask_gap_abs": best_ask_gap_abs,
                        "dominant_gap_side": dominant_gap_side,
                        "bid_overlap_top50": bid_overlap_top50,
                        "ask_overlap_top50": ask_overlap_top50,
                    },
                    policy=review_policy,
                )

                compare_cases.append(
                    {
                        "diffs_applied": diffs_since_anchor,
                        "top_of_book_ok": top_of_book_ok,
                        "not_crossed_ok": not_crossed_ok,
                        "best_bid_gap_abs": best_bid_gap_abs,
                        "best_ask_gap_abs": best_ask_gap_abs,
                        "dominant_gap_side": dominant_gap_side,
                        "bid_overlap_top50": bid_overlap_top50,
                        "ask_overlap_top50": ask_overlap_top50,
                        "review_bucket": review_decision.bucket,
                        "review_reason": review_decision.reason,
                        "top50_overlap_floor": review_decision.top50_overlap_floor,
                        "best_gap_ceiling": review_decision.best_gap_ceiling,
                    }
                )

            previous_snapshot = event
            diffs_since_anchor = 0
            continue

        if classified.family == "diff" and previous_snapshot is not None:
            diffs_since_anchor += 1
            continue

    if not compare_cases:
        return {
            "logical_group_key": logical_group_key,
            "case_count": 0,
            "review_bucket_counts": {
                "allow_structural_use": 0,
                "observe_only": 0,
                "reanchor_required": 0,
            },
            "sample_cases": [],
        }

    return {
        "logical_group_key": logical_group_key,
        "case_count": len(compare_cases),
        "review_bucket_counts": {
            "allow_structural_use": sum(
                1 for case in compare_cases if case["review_bucket"] == "allow_structural_use"
            ),
            "observe_only": sum(
                1 for case in compare_cases if case["review_bucket"] == "observe_only"
            ),
            "reanchor_required": sum(
                1 for case in compare_cases if case["review_bucket"] == "reanchor_required"
            ),
        },
        "top50_overlap_floor_avg": mean(case["top50_overlap_floor"] for case in compare_cases),
        "best_gap_ceiling_avg": mean(case["best_gap_ceiling"] for case in compare_cases),
        "sample_cases": compare_cases[:5],
    }