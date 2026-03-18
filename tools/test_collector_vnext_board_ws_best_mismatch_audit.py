# path: ./tools/test_collector_vnext_board_ws_best_mismatch_audit.py
# desc: Audit bitFlyer board WS best-of-book mismatch cases against rebuild and continuity evidence.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import time
from typing import Any, Dict, List, Tuple, Optional

from btcts.collector_vnext.orderbook.book_rebuilder import OrderBookRebuilder
from btcts.collector_vnext.providers.bitflyer_ws_board import connect_and_stream_board


SYMBOL = "BTC_JPY"
SSL_VERIFY = False

MAX_SECONDS = 300.0
MAX_CASES = 20

STRONG_BEST_GAP_ABS = 1000.0
MIN_HEALTHY_OVERLAP = 0.8


def _normalize(side: Any, reverse: bool) -> List[Tuple[float, float]]:
    rows = []
    for r in side or []:
        try:
            rows.append((float(r["price"]), float(r["size"])))
        except Exception:
            continue
    rows.sort(key=lambda x: x[0], reverse=reverse)
    return rows


def _best(side: List[Tuple[float, float]]) -> Optional[float]:
    return side[0][0] if side else None


def _top_prices(side: List[Tuple[float, float]], n: int = 10) -> List[float]:
    return [p for p, _ in side[:n]]


def _price_set(side: List[Tuple[float, float]], n: int) -> set:
    return {p for p, _ in side[:n]}


def _overlap_ratio(a: set, b: set, n: int) -> float:
    if n == 0:
        return 0.0
    return len(a & b) / float(n)


def _classify_case(
    *,
    bid_overlap_top10: float,
    ask_overlap_top10: float,
    live_best_bid: Optional[float],
    snap_best_bid: Optional[float],
    live_best_ask: Optional[float],
    snap_best_ask: Optional[float],
) -> str:
    bid_gap_abs = None if live_best_bid is None or snap_best_bid is None else abs(live_best_bid - snap_best_bid)
    ask_gap_abs = None if live_best_ask is None or snap_best_ask is None else abs(live_best_ask - snap_best_ask)

    if bid_gap_abs is None and ask_gap_abs is None:
        return "unknown"

    overlaps_healthy = (
        bid_overlap_top10 >= MIN_HEALTHY_OVERLAP and
        ask_overlap_top10 >= MIN_HEALTHY_OVERLAP
    )

    if overlaps_healthy:
        strong_bid = bid_gap_abs is not None and bid_gap_abs > STRONG_BEST_GAP_ABS
        strong_ask = ask_gap_abs is not None and ask_gap_abs > STRONG_BEST_GAP_ABS
        if strong_bid or strong_ask:
            return "strong_timing_drift"
        return "small_timing_drift"

    if bid_overlap_top10 >= 0.6 or ask_overlap_top10 >= 0.6:
        return "mixed_local_drift"

    return "structural_drift_suspected"


def _audit_view_from_classification(classification: str) -> Dict[str, str]:
    if classification == "small_timing_drift":
        return {
            "audit_level": "INFO",
            "audit_decision": "allow",
            "audit_reason": "best mismatch is explainable by timing drift with healthy top10 overlap",
        }

    if classification == "strong_timing_drift":
        return {
            "audit_level": "WARN",
            "audit_decision": "observe",
            "audit_reason": "top10 overlap is healthy but best gap is large",
        }

    if classification == "mixed_local_drift":
        return {
            "audit_level": "WARN",
            "audit_decision": "observe",
            "audit_reason": "local drift is visible and requires continued monitoring",
        }

    if classification == "structural_drift_suspected":
        return {
            "audit_level": "ERROR",
            "audit_decision": "investigate",
            "audit_reason": "top10 overlap is too weak for timing-only explanation",
        }

    return {
        "audit_level": "WARN",
        "audit_decision": "unknown",
        "audit_reason": "classification is unknown",
    }


def _side_meta(
    *,
    bid_overlap_top10: float,
    ask_overlap_top10: float,
    best_bid_gap_abs: Optional[float],
    best_ask_gap_abs: Optional[float],
) -> Dict[str, Any]:
    healthy_bid_overlap = bid_overlap_top10 >= MIN_HEALTHY_OVERLAP
    healthy_ask_overlap = ask_overlap_top10 >= MIN_HEALTHY_OVERLAP

    strong_bid_gap = best_bid_gap_abs is not None and best_bid_gap_abs > STRONG_BEST_GAP_ABS
    strong_ask_gap = best_ask_gap_abs is not None and best_ask_gap_abs > STRONG_BEST_GAP_ABS

    affected_sides: List[str] = []

    if (best_bid_gap_abs is not None and best_bid_gap_abs > 0) or not healthy_bid_overlap:
        affected_sides.append("bid")

    if (best_ask_gap_abs is not None and best_ask_gap_abs > 0) or not healthy_ask_overlap:
        affected_sides.append("ask")

    if not affected_sides:
        sides_affected = "none"
    elif len(affected_sides) == 1:
        sides_affected = affected_sides[0]
    else:
        sides_affected = "both"

    dominant_side = "none"
    if sides_affected == "bid":
        dominant_side = "bid"
    elif sides_affected == "ask":
        dominant_side = "ask"
    elif sides_affected == "both":
        bid_score = (0.0 if healthy_bid_overlap else (MIN_HEALTHY_OVERLAP - bid_overlap_top10)) + float(best_bid_gap_abs or 0.0)
        ask_score = (0.0 if healthy_ask_overlap else (MIN_HEALTHY_OVERLAP - ask_overlap_top10)) + float(best_ask_gap_abs or 0.0)
        if bid_score > ask_score:
            dominant_side = "bid"
        elif ask_score > bid_score:
            dominant_side = "ask"
        else:
            dominant_side = "balanced"

    return {
        "healthy_bid_overlap": healthy_bid_overlap,
        "healthy_ask_overlap": healthy_ask_overlap,
        "strong_bid_gap": strong_bid_gap,
        "strong_ask_gap": strong_ask_gap,
        "sides_affected": sides_affected,
        "dominant_side": dominant_side,
    }


def observe():
    rebuilder = OrderBookRebuilder()

    cases = []
    diffs_since_snapshot = 0
    last_snapshot_payload = None

    stream = connect_and_stream_board(
        symbol=SYMBOL,
        ssl_verify=SSL_VERIFY,
    )

    started = time.time()

    for msg in stream:
        kind = "snapshot" if "snapshot" in (msg.channel or "").lower() else "diff"
        payload = msg.payload or {}

        if kind == "diff":
            if rebuilder.snapshot_loaded:
                diffs_since_snapshot += 1
            rebuilder.apply_event({
                "event_type": "delta",
                "bids": payload.get("bids") or [],
                "asks": payload.get("asks") or [],
            })

        else:
            snap_bids = _normalize(payload.get("bids"), True)
            snap_asks = _normalize(payload.get("asks"), False)

            if not rebuilder.snapshot_loaded:
                rebuilder.apply_event({
                    "event_type": "snapshot",
                    "bids": payload.get("bids") or [],
                    "asks": payload.get("asks") or [],
                })
                last_snapshot_payload = payload
                diffs_since_snapshot = 0
                continue

            # ---- live book ----
            live_bids = sorted(
                [(float(p), float(s)) for p, s in rebuilder.book.bids.items()],
                key=lambda x: x[0],
                reverse=True,
            )
            live_asks = sorted(
                [(float(p), float(s)) for p, s in rebuilder.book.asks.items()],
                key=lambda x: x[0],
                reverse=False,
            )

            live_best_bid = rebuilder.best_bid()
            live_best_ask = rebuilder.best_ask()
            snap_best_bid = _best(snap_bids)
            snap_best_ask = _best(snap_asks)

            bid_mismatch = live_best_bid != snap_best_bid
            ask_mismatch = live_best_ask != snap_best_ask

            if bid_mismatch or ask_mismatch:
                bid_overlap_top10 = _overlap_ratio(
                    _price_set(live_bids, 10),
                    _price_set(snap_bids, 10),
                    10,
                )
                ask_overlap_top10 = _overlap_ratio(
                    _price_set(live_asks, 10),
                    _price_set(snap_asks, 10),
                    10,
                )

                classification = _classify_case(
                    bid_overlap_top10=bid_overlap_top10,
                    ask_overlap_top10=ask_overlap_top10,
                    live_best_bid=live_best_bid,
                    snap_best_bid=snap_best_bid,
                    live_best_ask=live_best_ask,
                    snap_best_ask=snap_best_ask,
                )
                audit_view = _audit_view_from_classification(classification)

                best_bid_gap_abs = None if live_best_bid is None or snap_best_bid is None else abs(live_best_bid - snap_best_bid)
                best_ask_gap_abs = None if live_best_ask is None or snap_best_ask is None else abs(live_best_ask - snap_best_ask)

                side_meta = _side_meta(
                    bid_overlap_top10=bid_overlap_top10,
                    ask_overlap_top10=ask_overlap_top10,
                    best_bid_gap_abs=best_bid_gap_abs,
                    best_ask_gap_abs=best_ask_gap_abs,
                )

                case = {
                    "diffs_applied": diffs_since_snapshot,

                    "live_best_bid": live_best_bid,
                    "snap_best_bid": snap_best_bid,
                    "live_best_ask": live_best_ask,
                    "snap_best_ask": snap_best_ask,

                    "bid_diff": None if live_best_bid is None or snap_best_bid is None else live_best_bid - snap_best_bid,
                    "ask_diff": None if live_best_ask is None or snap_best_ask is None else live_best_ask - snap_best_ask,
                    "best_bid_gap_abs": best_bid_gap_abs,
                    "best_ask_gap_abs": best_ask_gap_abs,

                    "live_bid_top10": _top_prices(live_bids, 10),
                    "snap_bid_top10": _top_prices(snap_bids, 10),
                    "live_ask_top10": _top_prices(live_asks, 10),
                    "snap_ask_top10": _top_prices(snap_asks, 10),

                    "bid_overlap_top10": bid_overlap_top10,
                    "ask_overlap_top10": ask_overlap_top10,

                    "healthy_bid_overlap": side_meta["healthy_bid_overlap"],
                    "healthy_ask_overlap": side_meta["healthy_ask_overlap"],
                    "strong_bid_gap": side_meta["strong_bid_gap"],
                    "strong_ask_gap": side_meta["strong_ask_gap"],
                    "sides_affected": side_meta["sides_affected"],
                    "dominant_side": side_meta["dominant_side"],

                    "classification": classification,
                    "audit_level": audit_view["audit_level"],
                    "audit_decision": audit_view["audit_decision"],
                    "audit_reason": audit_view["audit_reason"],
                }

                if classification == "small_timing_drift":
                    case["hint"] = "best_only_shift_or_timing"
                elif classification == "strong_timing_drift":
                    case["hint"] = "strong_timing_drift"
                elif classification == "structural_drift_suspected":
                    case["hint"] = "possible_content_drift"
                else:
                    case["hint"] = "mixed"

                cases.append(case)

                if len(cases) >= MAX_CASES:
                    break

            # snapshot rebase
            rebuilder.apply_event({
                "event_type": "snapshot",
                "bids": payload.get("bids") or [],
                "asks": payload.get("asks") or [],
            })
            diffs_since_snapshot = 0

        if (time.time() - started) > MAX_SECONDS:
            break

    classification_counts: Dict[str, int] = {}
    audit_level_counts: Dict[str, int] = {}
    audit_decision_counts: Dict[str, int] = {}
    dominant_side_counts: Dict[str, int] = {}
    sides_affected_counts: Dict[str, int] = {}

    for case in cases:
        classification = str(case.get("classification") or "unknown")
        classification_counts[classification] = classification_counts.get(classification, 0) + 1

        audit_level = str(case.get("audit_level") or "unknown")
        audit_level_counts[audit_level] = audit_level_counts.get(audit_level, 0) + 1

        audit_decision = str(case.get("audit_decision") or "unknown")
        audit_decision_counts[audit_decision] = audit_decision_counts.get(audit_decision, 0) + 1

        dominant_side = str(case.get("dominant_side") or "unknown")
        dominant_side_counts[dominant_side] = dominant_side_counts.get(dominant_side, 0) + 1

        sides_affected = str(case.get("sides_affected") or "unknown")
        sides_affected_counts[sides_affected] = sides_affected_counts.get(sides_affected, 0) + 1

    return {
        "ok": True,
        "case_count": len(cases),
        "summary": {
            "classification_counts": classification_counts,
            "audit_level_counts": audit_level_counts,
            "audit_decision_counts": audit_decision_counts,
            "dominant_side_counts": dominant_side_counts,
            "sides_affected_counts": sides_affected_counts,
            "strong_best_gap_threshold": STRONG_BEST_GAP_ABS,
            "min_healthy_overlap": MIN_HEALTHY_OVERLAP,
        },
        "cases": cases,
    }


def main():
    print(json.dumps(observe(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()