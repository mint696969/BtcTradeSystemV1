# path: ./tools/test_collector_vnext_board_ws_rebuild.py
# desc: Rebuild board state from WS events and verify snapshot-diff reconstruction behavior.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from btcts.collector_vnext.orderbook.book_rebuilder import OrderBookRebuilder
from btcts.collector_vnext.providers.bitflyer_ws_board import connect_and_stream_board
from btcts.collector_vnext.providers.bitflyer_ws_board import (
    BoardMessage,
    connect_and_stream_board,
)

SYMBOL = "BTC_JPY"
SSL_VERIFY = False

MAX_COMPARE_COUNT = 6
MAX_SECONDS = 120.0
TOP_LEVELS = (10, 50)


@dataclass
class SnapshotDigest:
    index: int
    received_ts: str
    best_bid: Optional[float]
    best_ask: Optional[float]
    bid_levels: int
    ask_levels: int


@dataclass
class CompareResult:
    compare_no: int
    snapshot_from_index: int
    snapshot_to_index: int
    diffs_applied: int
    best_bid_match: bool
    best_ask_match: bool
    top10_bid_match_count: int
    top10_ask_match_count: int
    top50_bid_match_count: int
    top50_ask_match_count: int
    top10_bid_ratio: float
    top10_ask_ratio: float
    top50_bid_ratio: float
    top50_ask_ratio: float
    only_in_live_bid_levels: int
    only_in_live_ask_levels: int
    only_in_snapshot_bid_levels: int
    only_in_snapshot_ask_levels: int


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


def _side_to_map(side: List[Tuple[float, float]]) -> Dict[float, float]:
    return {price: size for price, size in side}


def _best_price(side: List[Tuple[float, float]], reverse: bool) -> Optional[float]:
    if not side:
        return None
    prices = [price for price, _ in side]
    return max(prices) if reverse else min(prices)


def _top_match_count(
    live_side: List[Tuple[float, float]],
    snap_side: List[Tuple[float, float]],
    top_n: int,
) -> int:
    live_top = live_side[: max(top_n, 0)]
    snap_top = snap_side[: max(top_n, 0)]

    match_count = 0
    for live_row, snap_row in zip(live_top, snap_top):
        if live_row[0] == snap_row[0] and live_row[1] == snap_row[1]:
            match_count += 1
    return match_count


def _safe_ratio(match_count: int, top_n: int) -> float:
    if top_n <= 0:
        return 0.0
    return match_count / float(top_n)


def _diff_level_gap_counts(
    live_side: List[Tuple[float, float]],
    snap_side: List[Tuple[float, float]],
) -> Tuple[int, int]:
    live_prices = {price for price, _ in live_side}
    snap_prices = {price for price, _ in snap_side}
    only_in_live = len(live_prices - snap_prices)
    only_in_snapshot = len(snap_prices - live_prices)
    return only_in_live, only_in_snapshot


def _snapshot_digest(index: int, payload: Dict[str, Any], received_ts: str) -> SnapshotDigest:
    bids = _normalize_side(payload.get("bids"), reverse=True)
    asks = _normalize_side(payload.get("asks"), reverse=False)

    return SnapshotDigest(
        index=index,
        received_ts=received_ts,
        best_bid=_best_price(bids, reverse=True),
        best_ask=_best_price(asks, reverse=False),
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

    top10_bid_match_count = _top_match_count(live_bids, snap_bids, 10)
    top10_ask_match_count = _top_match_count(live_asks, snap_asks, 10)
    top50_bid_match_count = _top_match_count(live_bids, snap_bids, 50)
    top50_ask_match_count = _top_match_count(live_asks, snap_asks, 50)

    only_in_live_bid_levels, only_in_snapshot_bid_levels = _diff_level_gap_counts(live_bids, snap_bids)
    only_in_live_ask_levels, only_in_snapshot_ask_levels = _diff_level_gap_counts(live_asks, snap_asks)

    live_best_bid = rebuilder.best_bid()
    live_best_ask = rebuilder.best_ask()
    snap_best_bid = _best_price(snap_bids, reverse=True)
    snap_best_ask = _best_price(snap_asks, reverse=False)

    return CompareResult(
        compare_no=compare_no,
        snapshot_from_index=from_snapshot.index,
        snapshot_to_index=to_snapshot.index,
        diffs_applied=diffs_applied,
        best_bid_match=(live_best_bid == snap_best_bid),
        best_ask_match=(live_best_ask == snap_best_ask),
        top10_bid_match_count=top10_bid_match_count,
        top10_ask_match_count=top10_ask_match_count,
        top50_bid_match_count=top50_bid_match_count,
        top50_ask_match_count=top50_ask_match_count,
        top10_bid_ratio=_safe_ratio(top10_bid_match_count, 10),
        top10_ask_ratio=_safe_ratio(top10_ask_match_count, 10),
        top50_bid_ratio=_safe_ratio(top50_bid_match_count, 50),
        top50_ask_ratio=_safe_ratio(top50_ask_match_count, 50),
        only_in_live_bid_levels=only_in_live_bid_levels,
        only_in_live_ask_levels=only_in_live_ask_levels,
        only_in_snapshot_bid_levels=only_in_snapshot_bid_levels,
        only_in_snapshot_ask_levels=only_in_snapshot_ask_levels,
    )


def _avg(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def observe_rebuild_accuracy(
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
    last_snapshot_digest: Optional[SnapshotDigest] = None

    started = time.time()

    stream = connect_and_stream_board(
        symbol=symbol,
        ssl_verify=ssl_verify,
    )

    for msg in stream:
        message_count += 1
        received_ts = msg.received_ts or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        channel = msg.channel
        payload = msg.payload or {}
        kind = _kind_from_channel(channel)

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

            if not rebuilder.snapshot_loaded or last_snapshot_digest is None:
                rebuilder.apply_event(_event_from_payload("snapshot", payload))
                last_snapshot_digest = current_digest
                diffs_since_last_snapshot = 0
            else:
                compare_no = len(compare_results) + 1
                compare_result = _compare_live_vs_snapshot(
                    compare_no=compare_no,
                    from_snapshot=last_snapshot_digest,
                    to_snapshot=current_digest,
                    rebuilder=rebuilder,
                    snapshot_payload=payload,
                    diffs_applied=diffs_since_last_snapshot,
                )
                compare_results.append(compare_result)

                rebuilder.apply_event(_event_from_payload("snapshot", payload))
                last_snapshot_digest = current_digest
                diffs_since_last_snapshot = 0

        if len(compare_results) >= max_compare_count:
            break

        if (time.time() - started) >= max_seconds:
            break

    compare_dicts = [asdict(item) for item in compare_results]

    summary = {
        "best_bid_match_rate": _avg([1.0 if x.best_bid_match else 0.0 for x in compare_results]),
        "best_ask_match_rate": _avg([1.0 if x.best_ask_match else 0.0 for x in compare_results]),
        "top10_bid_avg_ratio": _avg([x.top10_bid_ratio for x in compare_results]),
        "top10_ask_avg_ratio": _avg([x.top10_ask_ratio for x in compare_results]),
        "top50_bid_avg_ratio": _avg([x.top50_bid_ratio for x in compare_results]),
        "top50_ask_avg_ratio": _avg([x.top50_ask_ratio for x in compare_results]),
        "avg_diffs_applied_per_compare": _avg([float(x.diffs_applied) for x in compare_results]),
    }

    return {
        "symbol": symbol,
        "ssl_verify": ssl_verify,
        "max_compare_count": max_compare_count,
        "max_seconds": max_seconds,
        "message_count": message_count,
        "snapshot_count": snapshot_count,
        "diff_count": diff_count,
        "diffs_before_first_snapshot": diffs_before_first_snapshot,
        "compare_count": len(compare_results),
        "compare_results": compare_dicts,
        "summary": summary,
        "ok": True,
    }


def main() -> None:
    result = observe_rebuild_accuracy()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()