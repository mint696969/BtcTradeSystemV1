# path: ./tools/test_collector_vnext_board_ws_compare_diagnose.py
# desc: Diagnose whether WS board rebuild mismatches are caused by positional comparison or true content drift.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import time
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from btcts.collector_vnext.orderbook.book_rebuilder import OrderBookRebuilder
from btcts.collector_vnext.providers.bitflyer_ws_board import connect_and_stream_board


SYMBOL = os.getenv("BTCTS_WS_COMPARE_SYMBOL", "BTC_JPY")
SSL_VERIFY = os.getenv("BTCTS_WS_COMPARE_SSL_VERIFY", "0") == "1"
MAX_SECONDS = float(os.getenv("BTCTS_WS_COMPARE_SECONDS", "300"))
MAX_COMPARE_COUNT = int(os.getenv("BTCTS_WS_COMPARE_COUNT", "50"))
TOP_LEVELS = (10, 20, 50, 100)
WORST_CASE_KEEP = 12


@dataclass
class SnapshotDigest:
    index: int
    received_ts: str
    best_bid: Optional[float]
    best_ask: Optional[float]
    bid_levels: int
    ask_levels: int


@dataclass
class SideCompare:
    positional_exact_count: int
    positional_exact_ratio: float

    set_exact_count: int
    set_exact_ratio: float

    price_overlap_count: int
    price_overlap_ratio: float

    same_price_size_mismatch_count: int
    same_price_size_mismatch_ratio: float

    only_in_live_price_count: int
    only_in_snapshot_price_count: int


@dataclass
class CompareResult:
    compare_no: int
    snapshot_from_index: int
    snapshot_to_index: int
    diffs_applied: int

    best_bid_match: bool
    best_ask_match: bool

    bid_top10: Dict[str, float]
    ask_top10: Dict[str, float]
    bid_top20: Dict[str, float]
    ask_top20: Dict[str, float]
    bid_top50: Dict[str, float]
    ask_top50: Dict[str, float]
    bid_top100: Dict[str, float]
    ask_top100: Dict[str, float]

    live_best_bid: Optional[float]
    live_best_ask: Optional[float]
    snap_best_bid: Optional[float]
    snap_best_ask: Optional[float]

    positional_minus_set_gap_top10_bid: float
    positional_minus_set_gap_top10_ask: float
    positional_minus_set_gap_top50_bid: float
    positional_minus_set_gap_top50_ask: float

    diagnosis_hint: str


def _utc_now_text() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _kind_from_channel(channel: str) -> str:
    text = str(channel or "").lower()
    if "snapshot" in text:
        return "snapshot"
    return "diff"


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


def _safe_ratio(count: int, top_n: int) -> float:
    if top_n <= 0:
        return 0.0
    return count / float(top_n)


def _top_positional_exact_count(
    live_side: List[Tuple[float, float]],
    snap_side: List[Tuple[float, float]],
    top_n: int,
) -> int:
    live_top = live_side[:max(top_n, 0)]
    snap_top = snap_side[:max(top_n, 0)]
    match_count = 0
    for live_row, snap_row in zip(live_top, snap_top):
        if live_row[0] == snap_row[0] and live_row[1] == snap_row[1]:
            match_count += 1
    return match_count


def _top_side_compare(
    live_side: List[Tuple[float, float]],
    snap_side: List[Tuple[float, float]],
    top_n: int,
) -> SideCompare:
    live_top = live_side[:max(top_n, 0)]
    snap_top = snap_side[:max(top_n, 0)]

    positional_exact_count = _top_positional_exact_count(live_side, snap_side, top_n)

    live_by_price = {price: size for price, size in live_top}
    snap_by_price = {price: size for price, size in snap_top}

    live_prices = set(live_by_price.keys())
    snap_prices = set(snap_by_price.keys())
    overlap_prices = live_prices & snap_prices

    set_exact_count = sum(
        1
        for price in overlap_prices
        if live_by_price.get(price) == snap_by_price.get(price)
    )
    price_overlap_count = len(overlap_prices)
    same_price_size_mismatch_count = sum(
        1
        for price in overlap_prices
        if live_by_price.get(price) != snap_by_price.get(price)
    )

    only_in_live_price_count = len(live_prices - snap_prices)
    only_in_snapshot_price_count = len(snap_prices - live_prices)

    return SideCompare(
        positional_exact_count=positional_exact_count,
        positional_exact_ratio=_safe_ratio(positional_exact_count, top_n),
        set_exact_count=set_exact_count,
        set_exact_ratio=_safe_ratio(set_exact_count, top_n),
        price_overlap_count=price_overlap_count,
        price_overlap_ratio=_safe_ratio(price_overlap_count, top_n),
        same_price_size_mismatch_count=same_price_size_mismatch_count,
        same_price_size_mismatch_ratio=_safe_ratio(same_price_size_mismatch_count, top_n),
        only_in_live_price_count=only_in_live_price_count,
        only_in_snapshot_price_count=only_in_snapshot_price_count,
    )


def _snapshot_digest(index: int, payload: Dict[str, Any], received_ts: str) -> SnapshotDigest:
    bids = _normalize_side(payload.get("bids"), reverse=True)
    asks = _normalize_side(payload.get("asks"), reverse=False)
    return SnapshotDigest(
        index=index,
        received_ts=received_ts,
        best_bid=_best_price(bids),
        best_ask=_best_price(asks),
        bid_levels=len(bids),
        ask_levels=len(asks),
    )


def _event_from_payload(kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "event_type": kind,
        "bids": payload.get("bids") or [],
        "asks": payload.get("asks") or [],
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


def _hint_from_side_compares(
    bid10: SideCompare,
    ask10: SideCompare,
    bid50: SideCompare,
    ask50: SideCompare,
) -> str:
    positional_gap = max(
        bid10.set_exact_ratio - bid10.positional_exact_ratio,
        ask10.set_exact_ratio - ask10.positional_exact_ratio,
        bid50.set_exact_ratio - bid50.positional_exact_ratio,
        ask50.set_exact_ratio - ask50.positional_exact_ratio,
    )

    price_overlap_strong = min(
        bid10.price_overlap_ratio,
        ask10.price_overlap_ratio,
    ) >= 0.7

    if positional_gap >= 0.4 and price_overlap_strong:
        return "positional_bias_suspected"

    if max(bid10.price_overlap_ratio, ask10.price_overlap_ratio) < 0.3 and max(bid50.price_overlap_ratio, ask50.price_overlap_ratio) < 0.3:
        return "true_content_drift_suspected"

    if (
        bid10.price_overlap_ratio >= 0.7
        and ask10.price_overlap_ratio >= 0.7
        and (
            bid10.same_price_size_mismatch_ratio >= 0.3
            or ask10.same_price_size_mismatch_ratio >= 0.3
        )
    ):
        return "size_mismatch_bias_suspected"

    return "mixed_or_inconclusive"


def _side_compare_dict(item: SideCompare) -> Dict[str, float]:
    return {
        "positional_exact_count": item.positional_exact_count,
        "positional_exact_ratio": item.positional_exact_ratio,
        "set_exact_count": item.set_exact_count,
        "set_exact_ratio": item.set_exact_ratio,
        "price_overlap_count": item.price_overlap_count,
        "price_overlap_ratio": item.price_overlap_ratio,
        "same_price_size_mismatch_count": item.same_price_size_mismatch_count,
        "same_price_size_mismatch_ratio": item.same_price_size_mismatch_ratio,
        "only_in_live_price_count": item.only_in_live_price_count,
        "only_in_snapshot_price_count": item.only_in_snapshot_price_count,
    }


def _compare_live_vs_snapshot(
    compare_no: int,
    from_snapshot: SnapshotDigest,
    to_snapshot: SnapshotDigest,
    rebuilder: OrderBookRebuilder,
    snapshot_payload: Dict[str, Any],
    diffs_applied: int,
) -> CompareResult:
    live_bids, live_asks = _live_book_sides(rebuilder)
    snap_bids = _normalize_side(snapshot_payload.get("bids"), reverse=True)
    snap_asks = _normalize_side(snapshot_payload.get("asks"), reverse=False)

    bid10 = _top_side_compare(live_bids, snap_bids, 10)
    ask10 = _top_side_compare(live_asks, snap_asks, 10)
    bid20 = _top_side_compare(live_bids, snap_bids, 20)
    ask20 = _top_side_compare(live_asks, snap_asks, 20)
    bid50 = _top_side_compare(live_bids, snap_bids, 50)
    ask50 = _top_side_compare(live_asks, snap_asks, 50)
    bid100 = _top_side_compare(live_bids, snap_bids, 100)
    ask100 = _top_side_compare(live_asks, snap_asks, 100)

    live_best_bid = rebuilder.best_bid()
    live_best_ask = rebuilder.best_ask()
    snap_best_bid = _best_price(snap_bids)
    snap_best_ask = _best_price(snap_asks)

    best_bid_match = live_best_bid == snap_best_bid
    best_ask_match = live_best_ask == snap_best_ask

    return CompareResult(
        compare_no=compare_no,
        snapshot_from_index=from_snapshot.index,
        snapshot_to_index=to_snapshot.index,
        diffs_applied=diffs_applied,
        best_bid_match=best_bid_match,
        best_ask_match=best_ask_match,
        bid_top10=_side_compare_dict(bid10),
        ask_top10=_side_compare_dict(ask10),
        bid_top20=_side_compare_dict(bid20),
        ask_top20=_side_compare_dict(ask20),
        bid_top50=_side_compare_dict(bid50),
        ask_top50=_side_compare_dict(ask50),
        bid_top100=_side_compare_dict(bid100),
        ask_top100=_side_compare_dict(ask100),
        live_best_bid=live_best_bid,
        live_best_ask=live_best_ask,
        snap_best_bid=snap_best_bid,
        snap_best_ask=snap_best_ask,
        positional_minus_set_gap_top10_bid=round(bid10.positional_exact_ratio - bid10.set_exact_ratio, 6),
        positional_minus_set_gap_top10_ask=round(ask10.positional_exact_ratio - ask10.set_exact_ratio, 6),
        positional_minus_set_gap_top50_bid=round(bid50.positional_exact_ratio - bid50.set_exact_ratio, 6),
        positional_minus_set_gap_top50_ask=round(ask50.positional_exact_ratio - ask50.set_exact_ratio, 6),
        diagnosis_hint=_hint_from_side_compares(bid10, ask10, bid50, ask50),
    )


def _avg(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def _hist(values: List[str]) -> Dict[str, int]:
    c = Counter(values)
    return {str(k): int(v) for k, v in sorted(c.items(), key=lambda x: x[0])}


def _summary(compare_results: List[CompareResult]) -> Dict[str, Any]:
    if not compare_results:
        return {
            "compare_count": 0,
            "hint_counts": {},
        }

    return {
        "compare_count": len(compare_results),
        "best_bid_match_rate": _avg([1.0 if x.best_bid_match else 0.0 for x in compare_results]),
        "best_ask_match_rate": _avg([1.0 if x.best_ask_match else 0.0 for x in compare_results]),

        "bid_top10_positional_avg": _avg([x.bid_top10["positional_exact_ratio"] for x in compare_results]),
        "bid_top10_set_avg": _avg([x.bid_top10["set_exact_ratio"] for x in compare_results]),
        "bid_top10_price_overlap_avg": _avg([x.bid_top10["price_overlap_ratio"] for x in compare_results]),

        "ask_top10_positional_avg": _avg([x.ask_top10["positional_exact_ratio"] for x in compare_results]),
        "ask_top10_set_avg": _avg([x.ask_top10["set_exact_ratio"] for x in compare_results]),
        "ask_top10_price_overlap_avg": _avg([x.ask_top10["price_overlap_ratio"] for x in compare_results]),

        "bid_top50_positional_avg": _avg([x.bid_top50["positional_exact_ratio"] for x in compare_results]),
        "bid_top50_set_avg": _avg([x.bid_top50["set_exact_ratio"] for x in compare_results]),
        "bid_top50_price_overlap_avg": _avg([x.bid_top50["price_overlap_ratio"] for x in compare_results]),

        "ask_top50_positional_avg": _avg([x.ask_top50["positional_exact_ratio"] for x in compare_results]),
        "ask_top50_set_avg": _avg([x.ask_top50["set_exact_ratio"] for x in compare_results]),
        "ask_top50_price_overlap_avg": _avg([x.ask_top50["price_overlap_ratio"] for x in compare_results]),

        "size_mismatch_bid_top10_avg": _avg([x.bid_top10["same_price_size_mismatch_ratio"] for x in compare_results]),
        "size_mismatch_ask_top10_avg": _avg([x.ask_top10["same_price_size_mismatch_ratio"] for x in compare_results]),

        "hint_counts": _hist([x.diagnosis_hint for x in compare_results]),
        "positional_bias_suspected_count": sum(1 for x in compare_results if x.diagnosis_hint == "positional_bias_suspected"),
        "true_content_drift_suspected_count": sum(1 for x in compare_results if x.diagnosis_hint == "true_content_drift_suspected"),
    }


def observe_compare_diagnose(
    symbol: str = SYMBOL,
    ssl_verify: bool = SSL_VERIFY,
    max_compare_count: int = MAX_COMPARE_COUNT,
    max_seconds: float = MAX_SECONDS,
) -> Dict[str, Any]:
    rebuilder = OrderBookRebuilder()

    compare_results: List[CompareResult] = []
    message_count = 0
    snapshot_count = 0
    diff_count = 0
    diffs_before_first_snapshot = 0
    diffs_since_last_snapshot = 0
    first_snapshot_index: Optional[int] = None
    last_snapshot_digest: Optional[SnapshotDigest] = None

    started = time.time()
    stream = connect_and_stream_board(symbol=symbol, ssl_verify=ssl_verify)

    for msg in stream:
        message_count += 1
        received_ts = msg.received_ts or _utc_now_text()
        payload = msg.payload or {}
        kind = _kind_from_channel(msg.channel)

        if kind == "diff":
            diff_count += 1
            if not rebuilder.snapshot_loaded:
                diffs_before_first_snapshot += 1
            else:
                diffs_since_last_snapshot += 1
            rebuilder.apply_event(_event_from_payload("delta", payload))

        elif kind == "snapshot":
            snapshot_count += 1
            current_digest = _snapshot_digest(
                index=message_count,
                payload=payload,
                received_ts=received_ts,
            )

            if first_snapshot_index is None:
                first_snapshot_index = message_count

            if not rebuilder.snapshot_loaded or last_snapshot_digest is None:
                rebuilder.apply_event(_event_from_payload("snapshot", payload))
                last_snapshot_digest = current_digest
                diffs_since_last_snapshot = 0
            else:
                compare_no = len(compare_results) + 1
                compare_results.append(
                    _compare_live_vs_snapshot(
                        compare_no=compare_no,
                        from_snapshot=last_snapshot_digest,
                        to_snapshot=current_digest,
                        rebuilder=rebuilder,
                        snapshot_payload=payload,
                        diffs_applied=diffs_since_last_snapshot,
                    )
                )
                rebuilder.apply_event(_event_from_payload("snapshot", payload))
                last_snapshot_digest = current_digest
                diffs_since_last_snapshot = 0

        if len(compare_results) >= max_compare_count:
            break
        if (time.time() - started) >= max_seconds:
            break

    elapsed_sec = round(time.time() - started, 3)
    compare_dicts = [asdict(x) for x in compare_results]
    worst_cases = sorted(
        compare_dicts,
        key=lambda x: (
            x["bid_top10"]["positional_exact_ratio"]
            + x["ask_top10"]["positional_exact_ratio"]
            + x["bid_top50"]["positional_exact_ratio"]
            + x["ask_top50"]["positional_exact_ratio"]
        )
    )[:WORST_CASE_KEEP]

    return {
        "ok": True,
        "gate_type": "ws_board_compare_diagnose",
        "symbol": symbol,
        "ssl_verify": ssl_verify,
        "elapsed_sec": elapsed_sec,
        "max_seconds": max_seconds,
        "max_compare_count": max_compare_count,
        "message_count": message_count,
        "snapshot_count": snapshot_count,
        "diff_count": diff_count,
        "first_snapshot_index": first_snapshot_index,
        "diffs_before_first_snapshot": diffs_before_first_snapshot,
        "compare_count": len(compare_results),
        "summary": _summary(compare_results),
        "worst_cases": worst_cases,
        "compare_results": compare_dicts,
    }


def main() -> None:
    result = observe_compare_diagnose()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()