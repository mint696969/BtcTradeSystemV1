# path: ./tools/test_collector_vnext_board_ws_best_mismatch_trace.py
# desc: Trace bitFlyer board WS best-of-book mismatch sequences for manual diagnosis.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

from btcts.collector_vnext.orderbook.book_rebuilder import OrderBookRebuilder
from btcts.collector_vnext.providers.bitflyer_ws_board import connect_and_stream_board


SYMBOL = os.getenv("BTCTS_WS_TRACE_SYMBOL", "BTC_JPY")
SSL_VERIFY = os.getenv("BTCTS_WS_TRACE_SSL_VERIFY", "0") == "1"
MAX_SECONDS = float(os.getenv("BTCTS_WS_TRACE_SECONDS", "300"))
MAX_CASES = int(os.getenv("BTCTS_WS_TRACE_CASES", "10"))
TRACE_BACK_EVENTS = int(os.getenv("BTCTS_WS_TRACE_BACK_EVENTS", "12"))
TRACE_FORWARD_EVENTS = int(os.getenv("BTCTS_WS_TRACE_FORWARD_EVENTS", "6"))
STRONG_BEST_GAP_ABS = float(os.getenv("BTCTS_WS_TRACE_STRONG_BEST_GAP_ABS", "1000"))
MIN_HEALTHY_OVERLAP = float(os.getenv("BTCTS_WS_TRACE_MIN_HEALTHY_OVERLAP", "0.8"))


def _normalize_side(side: Any, reverse: bool) -> List[Tuple[float, float]]:
    rows: List[Tuple[float, float]] = []
    for row in side or []:
        if not isinstance(row, dict):
            continue
        try:
            price = float(row["price"])
            size = float(row["size"])
        except (KeyError, TypeError, ValueError):
            continue
        rows.append((price, size))
    rows.sort(key=lambda x: x[0], reverse=reverse)
    return rows


def _best_price(side: List[Tuple[float, float]]) -> Optional[float]:
    if not side:
        return None
    return side[0][0]


def _top_prices(side: List[Tuple[float, float]], n: int = 10) -> List[float]:
    return [price for price, _ in side[:max(n, 0)]]


def _price_set(side: List[Tuple[float, float]], n: int) -> set:
    return {price for price, _ in side[:max(n, 0)]}


def _overlap_ratio(a: set, b: set, n: int) -> float:
    if n <= 0:
        return 0.0
    return len(a & b) / float(n)


def _kind_from_channel(channel: str) -> str:
    text = str(channel or "").lower()
    if "snapshot" in text:
        return "snapshot"
    return "diff"


def _event_from_payload(kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "event_type": kind,
        "bids": payload.get("bids") or [],
        "asks": payload.get("asks") or [],
    }


def _compact_diff_rows(rows: Any, limit: int = 8) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        try:
            out.append(
                {
                    "price": float(row["price"]),
                    "size": float(row["size"]),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue
        if len(out) >= limit:
            break
    return out


def _message_trace_entry(
    msg_no: int,
    kind: str,
    received_ts: Optional[str],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "msg_no": msg_no,
        "kind": kind,
        "received_ts": received_ts,
        "bid_count": len(payload.get("bids") or []),
        "ask_count": len(payload.get("asks") or []),
        "bids_head": _compact_diff_rows(payload.get("bids")),
        "asks_head": _compact_diff_rows(payload.get("asks")),
    }


def _live_book_sides(rebuilder: OrderBookRebuilder) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    live_bids = sorted(
        [(float(price), float(size)) for price, size in rebuilder.book.bids.items()],
        key=lambda x: x[0],
        reverse=True,
    )
    live_asks = sorted(
        [(float(price), float(size)) for price, size in rebuilder.book.asks.items()],
        key=lambda x: x[0],
        reverse=False,
    )
    return live_bids, live_asks


def _price_index(side: List[Tuple[float, float]], price: Optional[float]) -> Optional[int]:
    if price is None:
        return None
    for idx, (row_price, _) in enumerate(side):
        if row_price == price:
            return idx
    return None


def _classify_case(
    *,
    bid_overlap_top10: float,
    ask_overlap_top10: float,
    live_best_ask: Optional[float],
    snap_best_ask: Optional[float],
) -> str:
    if live_best_ask is None or snap_best_ask is None:
        return "unknown"

    best_gap_abs = abs(live_best_ask - snap_best_ask)

    if ask_overlap_top10 >= MIN_HEALTHY_OVERLAP:
        if best_gap_abs <= STRONG_BEST_GAP_ABS:
            return "small_timing_drift"
        return "strong_timing_drift"

    if bid_overlap_top10 >= MIN_HEALTHY_OVERLAP and ask_overlap_top10 >= 0.6:
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


def _summary_from_cases(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not cases:
        return {
            "case_count": 0,
            "classification_counts": {},
            "audit_level_counts": {},
            "audit_decision_counts": {},
        }

    classification_counts: Dict[str, int] = {}
    audit_level_counts: Dict[str, int] = {}
    audit_decision_counts: Dict[str, int] = {}
    ask_overlaps: List[float] = []
    best_gap_abs_values: List[float] = []

    for case in cases:
        cls = str(case.get("classification") or "unknown")
        classification_counts[cls] = classification_counts.get(cls, 0) + 1

        audit_level = str(case.get("audit_level") or "unknown")
        audit_level_counts[audit_level] = audit_level_counts.get(audit_level, 0) + 1

        audit_decision = str(case.get("audit_decision") or "unknown")
        audit_decision_counts[audit_decision] = audit_decision_counts.get(audit_decision, 0) + 1

        ask_overlap = case.get("ask_overlap_top10")
        if isinstance(ask_overlap, (int, float)):
            ask_overlaps.append(float(ask_overlap))

        best_gap_abs = case.get("best_ask_gap_abs")
        if isinstance(best_gap_abs, (int, float)):
            best_gap_abs_values.append(float(best_gap_abs))

    return {
        "case_count": len(cases),
        "classification_counts": classification_counts,
        "audit_level_counts": audit_level_counts,
        "audit_decision_counts": audit_decision_counts,
        "ask_overlap_top10_avg": round(sum(ask_overlaps) / len(ask_overlaps), 6) if ask_overlaps else 0.0,
        "best_ask_gap_abs_avg": round(sum(best_gap_abs_values) / len(best_gap_abs_values), 6) if best_gap_abs_values else 0.0,
        "strong_best_gap_threshold": STRONG_BEST_GAP_ABS,
        "min_healthy_overlap": MIN_HEALTHY_OVERLAP,
    }


def observe_trace() -> Dict[str, Any]:
    rebuilder = OrderBookRebuilder()
    cases: List[Dict[str, Any]] = []

    message_count = 0
    snapshot_count = 0
    diff_count = 0
    diffs_since_snapshot = 0

    recent_events: Deque[Dict[str, Any]] = deque(maxlen=max(TRACE_BACK_EVENTS, 1))
    pending_forward_capture: Optional[Dict[str, Any]] = None

    stream = connect_and_stream_board(
        symbol=SYMBOL,
        ssl_verify=SSL_VERIFY,
    )

    started = time.time()

    for msg in stream:
        message_count += 1
        payload = msg.payload or {}
        kind = _kind_from_channel(msg.channel)
        trace_entry = _message_trace_entry(
            msg_no=message_count,
            kind=kind,
            received_ts=msg.received_ts,
            payload=payload,
        )

        if pending_forward_capture is not None:
            pending_forward_capture["forward_events"].append(trace_entry)
            if len(pending_forward_capture["forward_events"]) >= TRACE_FORWARD_EVENTS:
                cases.append(pending_forward_capture)
                pending_forward_capture = None
                if len(cases) >= MAX_CASES:
                    break

        if kind == "diff":
            diff_count += 1
            if rebuilder.snapshot_loaded:
                diffs_since_snapshot += 1

            rebuilder.apply_event(_event_from_payload("delta", payload))
            recent_events.append(trace_entry)

        else:
            snapshot_count += 1

            snap_bids = _normalize_side(payload.get("bids"), reverse=True)
            snap_asks = _normalize_side(payload.get("asks"), reverse=False)

            if not rebuilder.snapshot_loaded:
                rebuilder.apply_event(_event_from_payload("snapshot", payload))
                recent_events.append(trace_entry)
                diffs_since_snapshot = 0
                continue

            live_bids, live_asks = _live_book_sides(rebuilder)

            live_best_bid = rebuilder.best_bid()
            live_best_ask = rebuilder.best_ask()
            snap_best_bid = _best_price(snap_bids)
            snap_best_ask = _best_price(snap_asks)

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

            ask_mismatch = live_best_ask != snap_best_ask

            if ask_mismatch and pending_forward_capture is None:
                target_prices = []
                if live_best_ask is not None:
                    target_prices.append(live_best_ask)
                if snap_best_ask is not None and snap_best_ask not in target_prices:
                    target_prices.append(snap_best_ask)

                best_ask_gap_abs = None
                if live_best_ask is not None and snap_best_ask is not None:
                    best_ask_gap_abs = abs(live_best_ask - snap_best_ask)

                classification = _classify_case(
                    bid_overlap_top10=bid_overlap_top10,
                    ask_overlap_top10=ask_overlap_top10,
                    live_best_ask=live_best_ask,
                    snap_best_ask=snap_best_ask,
                )
                audit_view = _audit_view_from_classification(classification)

                pending_forward_capture = {
                    "case_no": len(cases) + 1,
                    "message_no": message_count,
                    "snapshot_received_ts": msg.received_ts,
                    "diffs_since_snapshot": diffs_since_snapshot,
                    "live_best_bid": live_best_bid,
                    "live_best_ask": live_best_ask,
                    "snap_best_bid": snap_best_bid,
                    "snap_best_ask": snap_best_ask,
                    "best_ask_gap_abs": best_ask_gap_abs,
                    "bid_overlap_top10": bid_overlap_top10,
                    "ask_overlap_top10": ask_overlap_top10,
                    "live_best_ask_index_top10": _price_index(live_asks[:10], live_best_ask),
                    "snap_best_ask_index_top10": _price_index(snap_asks[:10], snap_best_ask),
                    "live_ask_top10": _top_prices(live_asks, 10),
                    "snap_ask_top10": _top_prices(snap_asks, 10),
                    "classification": classification,
                    "audit_level": audit_view["audit_level"],
                    "audit_decision": audit_view["audit_decision"],
                    "audit_reason": audit_view["audit_reason"],
                    "target_prices": target_prices,
                    "back_events": list(recent_events),
                    "snapshot_event": trace_entry,
                    "forward_events": [],
                }

            rebuilder.apply_event(_event_from_payload("snapshot", payload))
            recent_events.append(trace_entry)
            diffs_since_snapshot = 0

        if (time.time() - started) >= MAX_SECONDS:
            break

    if pending_forward_capture is not None and len(cases) < MAX_CASES:
        cases.append(pending_forward_capture)

    return {
        "ok": True,
        "symbol": SYMBOL,
        "ssl_verify": SSL_VERIFY,
        "elapsed_sec": round(time.time() - started, 3),
        "message_count": message_count,
        "snapshot_count": snapshot_count,
        "diff_count": diff_count,
        "case_count": len(cases),
        "summary": _summary_from_cases(cases),
        "cases": cases,
    }


def main() -> None:
    print(json.dumps(observe_trace(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()