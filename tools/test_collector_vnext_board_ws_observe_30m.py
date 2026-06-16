# path: ./tools/test_collector_vnext_board_ws_observe_30m.py
# desc: Observe a single WS board stream for 30 minutes and compare diff-applied state against later snapshots.

import json
import math
import os
import ssl
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import websocket


WS_URL = "wss://ws.lightstream.bitflyer.com/json-rpc"
SYMBOL = "BTC_JPY"
SNAPSHOT_CHANNEL = f"lightning_board_snapshot_{SYMBOL}"
DIFF_CHANNEL = f"lightning_board_{SYMBOL}"

MAX_SECONDS = 1800.0
MAX_COMPARE_COUNT = 200
MAX_MESSAGES = 20000
SSL_VERIFY = os.getenv("BTCTS_WS_SSL_VERIFY", "0").strip().lower() not in {"0", "false", "no"}

TOP_LEVELS = [10, 20, 50, 100]
DISTANCE_BUCKETS_BPS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def subscribe_message(channel: str) -> str:
    return json.dumps(
        {
            "method": "subscribe",
            "params": {
                "channel": channel,
            },
        }
    )


def round_bps(distance_ratio: float) -> float:
    return distance_ratio * 10000.0


def bucket_bps(value_bps: float) -> str:
    for limit in DISTANCE_BUCKETS_BPS:
        if value_bps <= limit:
            return f"<= {limit}bps"
    return "> 1000bps"


def safe_mean(values: Iterable[float]) -> Optional[float]:
    values = list(values)
    if not values:
        return None
    return sum(values) / len(values)


def top_prices(
    levels_map: Dict[float, float],
    side: str,
    top_n: int,
) -> List[Tuple[float, float]]:
    items = [(price, size) for price, size in levels_map.items() if size > 0]
    if side == "bid":
        items.sort(key=lambda x: x[0], reverse=True)
    else:
        items.sort(key=lambda x: x[0])
    return items[:top_n]


def best_price(levels_map: Dict[float, float], side: str) -> Optional[float]:
    top1 = top_prices(levels_map, side, 1)
    return top1[0][0] if top1 else None


def parse_levels(levels: Any) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    if not isinstance(levels, list):
        return out
    for item in levels:
        if not isinstance(item, dict):
            continue
        price = item.get("price")
        size = item.get("size")
        try:
            p = float(price)
            s = float(size)
        except (TypeError, ValueError):
            continue
        out.append((p, s))
    return out


def message_kind(channel: str) -> str:
    if channel == SNAPSHOT_CHANNEL:
        return "snapshot"
    if channel == DIFF_CHANNEL:
        return "diff"
    return "unknown"


def snapshot_to_maps(board: Dict[str, Any]) -> Dict[str, Dict[float, float]]:
    bids = {price: size for price, size in parse_levels(board.get("bids")) if size > 0}
    asks = {price: size for price, size in parse_levels(board.get("asks")) if size > 0}
    return {"bid": bids, "ask": asks}


def apply_diff_inplace(book: Dict[str, Dict[float, float]], board: Dict[str, Any]) -> None:
    for side_key, ws_key in (("bid", "bids"), ("ask", "asks")):
        side_map = book[side_key]
        for price, size in parse_levels(board.get(ws_key)):
            if size <= 0:
                side_map.pop(price, None)
            else:
                side_map[price] = size


def compare_top_levels(
    live_side: Dict[float, float],
    snap_side: Dict[float, float],
    side: str,
    top_n: int,
) -> Dict[str, Any]:
    live_top = top_prices(live_side, side, top_n)
    snap_top = top_prices(snap_side, side, top_n)

    live_pairs = [(p, round(s, 12)) for p, s in live_top]
    snap_pairs = [(p, round(s, 12)) for p, s in snap_top]

    match_count = 0
    for idx in range(min(len(live_pairs), len(snap_pairs))):
        if live_pairs[idx] == snap_pairs[idx]:
            match_count += 1

    ratio = match_count / max(len(snap_pairs), 1)
    return {
        "match_count": match_count,
        "ratio": ratio,
        "live_count": len(live_pairs),
        "snapshot_count": len(snap_pairs),
    }


def diff_price_distances_bps(
    lhs: Dict[float, float],
    rhs: Dict[float, float],
    best_ref: Optional[float],
) -> List[float]:
    if best_ref is None or best_ref <= 0:
        return []
    lhs_prices = {p for p, s in lhs.items() if s > 0}
    rhs_prices = {p for p, s in rhs.items() if s > 0}
    out: List[float] = []
    for price in sorted(lhs_prices ^ rhs_prices):
        out.append(round_bps(abs(price - best_ref) / best_ref))
    return out


def classify_side_weaker(compare: Dict[str, Any], top_n: int) -> Optional[str]:
    bid_ratio = compare[f"top{top_n}_bid_ratio"]
    ask_ratio = compare[f"top{top_n}_ask_ratio"]
    if bid_ratio == ask_ratio:
        return None
    return "ask" if ask_ratio < bid_ratio else "bid"


@dataclass
class CompareRecord:
    compare_no: int
    snapshot_from_index: int
    snapshot_to_index: int
    diffs_applied: int
    best_bid_match: bool
    best_ask_match: bool
    top10_bid_ratio: float
    top10_ask_ratio: float
    top20_bid_ratio: float
    top20_ask_ratio: float
    top50_bid_ratio: float
    top50_ask_ratio: float
    top100_bid_ratio: float
    top100_ask_ratio: float
    only_in_live_bid_levels: int
    only_in_live_ask_levels: int
    only_in_snapshot_bid_levels: int
    only_in_snapshot_ask_levels: int
    live_only_bid_distance_bps_avg: Optional[float]
    live_only_ask_distance_bps_avg: Optional[float]
    snapshot_only_bid_distance_bps_avg: Optional[float]
    snapshot_only_ask_distance_bps_avg: Optional[float]
    max_mismatch_distance_bps: Optional[float]
    ask_weaker_than_bid_top50: bool
    ask_weaker_than_bid_top100: bool


def observe_board_ws() -> Dict[str, Any]:
    started_at = time.time()

    ws = websocket.create_connection(
        WS_URL,
        timeout=60,
        sslopt=(
            {"cert_reqs": ssl.CERT_REQUIRED, "check_hostname": True}
            if SSL_VERIFY
            else {"cert_reqs": ssl.CERT_NONE, "check_hostname": False}
        ),
    )
    ws.send(subscribe_message(SNAPSHOT_CHANNEL))
    ws.send(subscribe_message(DIFF_CHANNEL))

    message_count = 0
    snapshot_count = 0
    diff_count = 0
    diffs_before_first_snapshot = 0
    first_snapshot_index: Optional[int] = None

    current_book = {"bid": {}, "ask": {}}
    anchored = False
    last_snapshot_index: Optional[int] = None
    diffs_since_last_snapshot = 0

    compare_records: List[Dict[str, Any]] = []

    order_counter = Counter()
    update_density_counter = Counter()
    update_density_counter_by_side = {"bid": Counter(), "ask": Counter()}
    update_distance_samples_bps = {"bid": [], "ask": []}

    snapshot_gap_diff_counts: List[int] = []
    first_orders: List[str] = []

    while True:
        if (time.time() - started_at) >= MAX_SECONDS:
            break
        if len(compare_records) >= MAX_COMPARE_COUNT:
            break
        if message_count >= MAX_MESSAGES:
            break

        raw = ws.recv()
        message_count += 1

        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue

        params = obj.get("params")
        if not isinstance(params, dict):
            continue

        channel = params.get("channel")
        kind = message_kind(str(channel or ""))
        if kind == "unknown":
            continue

        board = params.get("message")
        if not isinstance(board, dict):
            continue
        order_counter[kind] += 1

        if len(first_orders) < 20:
            first_orders.append(kind)

        if kind == "snapshot":
            snapshot_count += 1
            snapshot_maps = snapshot_to_maps(board)

            if first_snapshot_index is None:
                first_snapshot_index = message_count
                anchored = True
                current_book = snapshot_maps
                last_snapshot_index = message_count
                snapshot_gap_diff_counts.append(diffs_since_last_snapshot)
                diffs_since_last_snapshot = 0
                continue

            if anchored:
                live_bid_best = best_price(current_book["bid"], "bid")
                live_ask_best = best_price(current_book["ask"], "ask")
                snap_bid_best = best_price(snapshot_maps["bid"], "bid")
                snap_ask_best = best_price(snapshot_maps["ask"], "ask")

                top_cmp: Dict[str, Any] = {}
                for n in TOP_LEVELS:
                    bid_cmp = compare_top_levels(current_book["bid"], snapshot_maps["bid"], "bid", n)
                    ask_cmp = compare_top_levels(current_book["ask"], snapshot_maps["ask"], "ask", n)
                    top_cmp[f"top{n}_bid_ratio"] = bid_cmp["ratio"]
                    top_cmp[f"top{n}_ask_ratio"] = ask_cmp["ratio"]

                live_only_bid_bps = diff_price_distances_bps(current_book["bid"], snapshot_maps["bid"], live_bid_best)
                live_only_ask_bps = diff_price_distances_bps(current_book["ask"], snapshot_maps["ask"], live_ask_best)
                snap_only_bid_bps = diff_price_distances_bps(snapshot_maps["bid"], current_book["bid"], snap_bid_best)
                snap_only_ask_bps = diff_price_distances_bps(snapshot_maps["ask"], current_book["ask"], snap_ask_best)

                all_mismatch_bps = (
                    live_only_bid_bps + live_only_ask_bps + snap_only_bid_bps + snap_only_ask_bps
                )

                compare = {
                    "compare_no": len(compare_records) + 1,
                    "snapshot_from_index": last_snapshot_index,
                    "snapshot_to_index": message_count,
                    "diffs_applied": diffs_since_last_snapshot,
                    "best_bid_match": live_bid_best == snap_bid_best,
                    "best_ask_match": live_ask_best == snap_ask_best,
                    **top_cmp,
                    "only_in_live_bid_levels": len(live_only_bid_bps),
                    "only_in_live_ask_levels": len(live_only_ask_bps),
                    "only_in_snapshot_bid_levels": len(snap_only_bid_bps),
                    "only_in_snapshot_ask_levels": len(snap_only_ask_bps),
                    "live_only_bid_distance_bps_avg": safe_mean(live_only_bid_bps),
                    "live_only_ask_distance_bps_avg": safe_mean(live_only_ask_bps),
                    "snapshot_only_bid_distance_bps_avg": safe_mean(snap_only_bid_bps),
                    "snapshot_only_ask_distance_bps_avg": safe_mean(snap_only_ask_bps),
                    "max_mismatch_distance_bps": max(all_mismatch_bps) if all_mismatch_bps else None,
                }
                compare["ask_weaker_than_bid_top50"] = compare["top50_ask_ratio"] < compare["top50_bid_ratio"]
                compare["ask_weaker_than_bid_top100"] = compare["top100_ask_ratio"] < compare["top100_bid_ratio"]
                compare_records.append(compare)

            current_book = snapshot_maps
            last_snapshot_index = message_count
            snapshot_gap_diff_counts.append(diffs_since_last_snapshot)
            diffs_since_last_snapshot = 0
            continue

        # diff
        diff_count += 1
        if first_snapshot_index is None:
            diffs_before_first_snapshot += 1
            continue

        diffs_since_last_snapshot += 1

        live_bid_best = best_price(current_book["bid"], "bid")
        live_ask_best = best_price(current_book["ask"], "ask")

        for side, ws_key, best_ref in (
            ("bid", "bids", live_bid_best),
            ("ask", "asks", live_ask_best),
        ):
            for price, _size in parse_levels(board.get(ws_key)):
                if best_ref is not None and best_ref > 0:
                    distance_bps = round_bps(abs(price - best_ref) / best_ref)
                    bucket = bucket_bps(distance_bps)
                    update_density_counter[bucket] += 1
                    update_density_counter_by_side[side][bucket] += 1
                    update_distance_samples_bps[side].append(distance_bps)

        apply_diff_inplace(current_book, board)

    ws.close()

    compare_count = len(compare_records)

    summary = {
        "best_bid_match_rate": safe_mean([1.0 if c["best_bid_match"] else 0.0 for c in compare_records]),
        "best_ask_match_rate": safe_mean([1.0 if c["best_ask_match"] else 0.0 for c in compare_records]),
        "top10_bid_avg_ratio": safe_mean([c["top10_bid_ratio"] for c in compare_records]),
        "top10_ask_avg_ratio": safe_mean([c["top10_ask_ratio"] for c in compare_records]),
        "top20_bid_avg_ratio": safe_mean([c["top20_bid_ratio"] for c in compare_records]),
        "top20_ask_avg_ratio": safe_mean([c["top20_ask_ratio"] for c in compare_records]),
        "top50_bid_avg_ratio": safe_mean([c["top50_bid_ratio"] for c in compare_records]),
        "top50_ask_avg_ratio": safe_mean([c["top50_ask_ratio"] for c in compare_records]),
        "top100_bid_avg_ratio": safe_mean([c["top100_bid_ratio"] for c in compare_records]),
        "top100_ask_avg_ratio": safe_mean([c["top100_ask_ratio"] for c in compare_records]),
        "avg_diffs_applied_per_compare": safe_mean([c["diffs_applied"] for c in compare_records]),
        "ask_side_weaker_than_bid_top50_count": sum(1 for c in compare_records if c["ask_weaker_than_bid_top50"]),
        "ask_side_weaker_than_bid_top100_count": sum(1 for c in compare_records if c["ask_weaker_than_bid_top100"]),
        "avg_live_only_bid_distance_bps": safe_mean(
            [c["live_only_bid_distance_bps_avg"] for c in compare_records if c["live_only_bid_distance_bps_avg"] is not None]
        ),
        "avg_live_only_ask_distance_bps": safe_mean(
            [c["live_only_ask_distance_bps_avg"] for c in compare_records if c["live_only_ask_distance_bps_avg"] is not None]
        ),
        "avg_snapshot_only_bid_distance_bps": safe_mean(
            [c["snapshot_only_bid_distance_bps_avg"] for c in compare_records if c["snapshot_only_bid_distance_bps_avg"] is not None]
        ),
        "avg_snapshot_only_ask_distance_bps": safe_mean(
            [c["snapshot_only_ask_distance_bps_avg"] for c in compare_records if c["snapshot_only_ask_distance_bps_avg"] is not None]
        ),
        "max_observed_mismatch_distance_bps": max(
            [c["max_mismatch_distance_bps"] for c in compare_records if c["max_mismatch_distance_bps"] is not None],
            default=None,
        ),
        "snapshot_gap_diff_avg": safe_mean(snapshot_gap_diff_counts[1:] if len(snapshot_gap_diff_counts) > 1 else snapshot_gap_diff_counts),
    }

    worst_cases = sorted(
        compare_records,
        key=lambda c: (
            c["top50_bid_ratio"] + c["top50_ask_ratio"] + c["top100_bid_ratio"] + c["top100_ask_ratio"]
        ),
    )[:12]

    result = {
        "symbol": "BTC_JPY",
        "channels": {
            "snapshot": SNAPSHOT_CHANNEL,
            "diff": DIFF_CHANNEL,
        },
        "ssl_verify": SSL_VERIFY,
        "started_at": utc_now_iso(),
        "max_seconds": MAX_SECONDS,
        "max_compare_count": MAX_COMPARE_COUNT,
        "message_count": message_count,
        "snapshot_count": snapshot_count,
        "diff_count": diff_count,
        "diffs_before_first_snapshot": diffs_before_first_snapshot,
        "first_snapshot_index": first_snapshot_index,
        "first_orders": first_orders,
        "compare_count": compare_count,
        "summary": summary,
        "update_density_all": dict(update_density_counter),
        "update_density_by_side": {
            "bid": dict(update_density_counter_by_side["bid"]),
            "ask": dict(update_density_counter_by_side["ask"]),
        },
        "update_distance_samples_summary_bps": {
            "bid_avg": safe_mean(update_distance_samples_bps["bid"]),
            "ask_avg": safe_mean(update_distance_samples_bps["ask"]),
            "bid_median": statistics.median(update_distance_samples_bps["bid"]) if update_distance_samples_bps["bid"] else None,
            "ask_median": statistics.median(update_distance_samples_bps["ask"]) if update_distance_samples_bps["ask"] else None,
        },
        "snapshot_gap_diff_counts": snapshot_gap_diff_counts,
        "worst_cases": worst_cases,
        "compare_results": compare_records,
        "ok": True,
    }
    return result


def main() -> None:
    result = observe_board_ws()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()