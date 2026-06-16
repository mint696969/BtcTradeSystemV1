# path: ./tools/test_collector_vnext_board_ws_pair_observe_30m.py
# desc: Observe paired WS snapshot and diff channels for 30 minutes and measure reconstruction agreement.

import json
import os
import ssl
import statistics
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import websocket


WS_URL = "wss://ws.lightstream.bitflyer.com/json-rpc"
SNAPSHOT_CHANNEL = "lightning_board_snapshot_BTC_JPY"
DIFF_CHANNEL = "lightning_board_BTC_JPY"
SYMBOL = "BTC_JPY"

MAX_SECONDS = 1800.0
MAX_MESSAGES = 50000
MAX_COMPARE_COUNT = 300
SSL_VERIFY = os.getenv("BTCTS_WS_SSL_VERIFY", "0").strip().lower() not in {"0", "false", "no"}

TOP_LEVELS = [10, 20, 50, 100]
DISTANCE_BUCKETS_BPS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_mean(values: Iterable[Optional[float]]) -> Optional[float]:
    xs = [x for x in values if x is not None]
    if not xs:
        return None
    return sum(xs) / len(xs)


def round_bps(distance_ratio: float) -> float:
    return distance_ratio * 10000.0


def bucket_bps(value_bps: float) -> str:
    for limit in DISTANCE_BUCKETS_BPS:
        if value_bps <= limit:
            return f"<= {limit}bps"
    return "> 1000bps"


def parse_levels(levels: Any) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    if not isinstance(levels, list):
        return out
    for item in levels:
        if not isinstance(item, dict):
            continue
        try:
            price = float(item.get("price"))
            size = float(item.get("size"))
        except (TypeError, ValueError):
            continue
        out.append((price, size))
    return out


def levels_to_maps(board: Dict[str, Any]) -> Dict[str, Dict[float, float]]:
    return {
        "bid": {p: s for p, s in parse_levels(board.get("bids")) if s > 0},
        "ask": {p: s for p, s in parse_levels(board.get("asks")) if s > 0},
    }


def best_price(levels_map: Dict[float, float], side: str) -> Optional[float]:
    if not levels_map:
        return None
    return max(levels_map.keys()) if side == "bid" else min(levels_map.keys())


def top_prices(levels_map: Dict[float, float], side: str, top_n: int) -> List[Tuple[float, float]]:
    items = [(p, s) for p, s in levels_map.items() if s > 0]
    items.sort(key=lambda x: x[0], reverse=(side == "bid"))
    return items[:top_n]


def apply_diff_inplace(book: Dict[str, Dict[float, float]], diff_board: Dict[str, Any]) -> None:
    for side, ws_key in (("bid", "bids"), ("ask", "asks")):
        side_map = book[side]
        for price, size in parse_levels(diff_board.get(ws_key)):
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
    for i in range(min(len(live_pairs), len(snap_pairs))):
        if live_pairs[i] == snap_pairs[i]:
            match_count += 1

    return {
        "match_count": match_count,
        "ratio": match_count / max(len(snap_pairs), 1),
    }


def symmetric_distance_bps(
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


def connect_ws() -> websocket.WebSocket:
    ws = websocket.create_connection(
        WS_URL,
        timeout=60,
        sslopt=(
            {"cert_reqs": ssl.CERT_REQUIRED, "check_hostname": True}
            if SSL_VERIFY
            else {"cert_reqs": ssl.CERT_NONE, "check_hostname": False}
        ),
    )
    ws.send(json.dumps({"method": "subscribe", "params": {"channel": SNAPSHOT_CHANNEL}}))
    ws.send(json.dumps({"method": "subscribe", "params": {"channel": DIFF_CHANNEL}}))
    return ws


def recv_channel_message(ws: websocket.WebSocket) -> Tuple[str, Dict[str, Any]]:
    while True:
        raw = ws.recv()
        obj = json.loads(raw)
        params = obj.get("params")
        if not isinstance(params, dict):
            continue
        channel = params.get("channel")
        message = params.get("message")
        if not isinstance(channel, str) or not isinstance(message, dict):
            continue
        if channel not in {SNAPSHOT_CHANNEL, DIFF_CHANNEL}:
            continue
        return channel, message


def main() -> None:
    started_at = time.time()
    ws = connect_ws()

    message_count = 0
    snapshot_count = 0
    diff_count = 0
    compare_count = 0

    first_snapshot_index: Optional[int] = None
    diffs_before_first_snapshot = 0

    live_book: Optional[Dict[str, Dict[float, float]]] = None
    last_snapshot_book: Optional[Dict[str, Dict[float, float]]] = None
    last_snapshot_index: Optional[int] = None
    diffs_since_snapshot = 0

    diff_density_all = Counter()
    diff_density_by_side = {"bid": Counter(), "ask": Counter()}
    diff_distance_samples_bps = {"bid": [], "ask": []}
    snapshot_gap_diff_counts: List[int] = []

    compare_results: List[Dict[str, Any]] = []
    first_orders: List[str] = []

    try:
        while True:
            if (time.time() - started_at) >= MAX_SECONDS:
                break
            if message_count >= MAX_MESSAGES:
                break
            if compare_count >= MAX_COMPARE_COUNT:
                break

            channel, message = recv_channel_message(ws)
            message_count += 1

            kind = "snapshot" if channel == SNAPSHOT_CHANNEL else "diff"
            if len(first_orders) < 30:
                first_orders.append(kind)

            if kind == "snapshot":
                snapshot_count += 1
                snapshot_book = levels_to_maps(message)

                if first_snapshot_index is None:
                    first_snapshot_index = message_count
                    live_book = {
                        "bid": dict(snapshot_book["bid"]),
                        "ask": dict(snapshot_book["ask"]),
                    }
                    last_snapshot_book = snapshot_book
                    last_snapshot_index = message_count
                    snapshot_gap_diff_counts.append(diffs_since_snapshot)
                    diffs_since_snapshot = 0
                    continue

                assert live_book is not None
                assert last_snapshot_book is not None
                assert last_snapshot_index is not None

                live_bid_best = best_price(live_book["bid"], "bid")
                live_ask_best = best_price(live_book["ask"], "ask")
                snap_bid_best = best_price(snapshot_book["bid"], "bid")
                snap_ask_best = best_price(snapshot_book["ask"], "ask")

                record: Dict[str, Any] = {
                    "compare_no": compare_count + 1,
                    "elapsed_sec": round(time.time() - started_at, 3),
                    "snapshot_from_index": last_snapshot_index,
                    "snapshot_to_index": message_count,
                    "diffs_applied": diffs_since_snapshot,
                    "live_best_bid": live_bid_best,
                    "live_best_ask": live_ask_best,
                    "snapshot_best_bid": snap_bid_best,
                    "snapshot_best_ask": snap_ask_best,
                    "best_bid_match": live_bid_best == snap_bid_best,
                    "best_ask_match": live_ask_best == snap_ask_best,
                }

                for n in TOP_LEVELS:
                    bid_cmp = compare_top_levels(live_book["bid"], snapshot_book["bid"], "bid", n)
                    ask_cmp = compare_top_levels(live_book["ask"], snapshot_book["ask"], "ask", n)
                    record[f"top{n}_bid_match_count"] = bid_cmp["match_count"]
                    record[f"top{n}_ask_match_count"] = ask_cmp["match_count"]
                    record[f"top{n}_bid_ratio"] = bid_cmp["ratio"]
                    record[f"top{n}_ask_ratio"] = ask_cmp["ratio"]

                live_only_bid = symmetric_distance_bps(live_book["bid"], snapshot_book["bid"], live_bid_best)
                live_only_ask = symmetric_distance_bps(live_book["ask"], snapshot_book["ask"], live_ask_best)
                snap_only_bid = symmetric_distance_bps(snapshot_book["bid"], live_book["bid"], snap_bid_best)
                snap_only_ask = symmetric_distance_bps(snapshot_book["ask"], live_book["ask"], snap_ask_best)

                all_mismatch = live_only_bid + live_only_ask + snap_only_bid + snap_only_ask

                record["only_in_live_bid_levels"] = len(live_only_bid)
                record["only_in_live_ask_levels"] = len(live_only_ask)
                record["only_in_snapshot_bid_levels"] = len(snap_only_bid)
                record["only_in_snapshot_ask_levels"] = len(snap_only_ask)
                record["live_only_bid_distance_bps_avg"] = safe_mean(live_only_bid)
                record["live_only_ask_distance_bps_avg"] = safe_mean(live_only_ask)
                record["snapshot_only_bid_distance_bps_avg"] = safe_mean(snap_only_bid)
                record["snapshot_only_ask_distance_bps_avg"] = safe_mean(snap_only_ask)
                record["max_mismatch_distance_bps"] = max(all_mismatch) if all_mismatch else None
                record["ask_weaker_than_bid_top50"] = record["top50_ask_ratio"] < record["top50_bid_ratio"]
                record["ask_weaker_than_bid_top100"] = record["top100_ask_ratio"] < record["top100_bid_ratio"]

                compare_results.append(record)
                compare_count += 1

                live_book = {
                    "bid": dict(snapshot_book["bid"]),
                    "ask": dict(snapshot_book["ask"]),
                }
                last_snapshot_book = snapshot_book
                last_snapshot_index = message_count
                snapshot_gap_diff_counts.append(diffs_since_snapshot)
                diffs_since_snapshot = 0
                continue

            # diff
            diff_count += 1
            if first_snapshot_index is None:
                diffs_before_first_snapshot += 1
                continue

            assert live_book is not None
            diffs_since_snapshot += 1

            live_bid_best = best_price(live_book["bid"], "bid")
            live_ask_best = best_price(live_book["ask"], "ask")

            for side, ws_key, best_ref in (
                ("bid", "bids", live_bid_best),
                ("ask", "asks", live_ask_best),
            ):
                for price, _size in parse_levels(message.get(ws_key)):
                    if best_ref is None or best_ref <= 0:
                        continue
                    distance_bps = round_bps(abs(price - best_ref) / best_ref)
                    bucket = bucket_bps(distance_bps)
                    diff_density_all[bucket] += 1
                    diff_density_by_side[side][bucket] += 1
                    diff_distance_samples_bps[side].append(distance_bps)

            apply_diff_inplace(live_book, message)

    finally:
        try:
            ws.close()
        except Exception:
            pass

    summary = {
        "best_bid_match_rate": safe_mean([1.0 if c["best_bid_match"] else 0.0 for c in compare_results]),
        "best_ask_match_rate": safe_mean([1.0 if c["best_ask_match"] else 0.0 for c in compare_results]),
        "top10_bid_avg_ratio": safe_mean([c["top10_bid_ratio"] for c in compare_results]),
        "top10_ask_avg_ratio": safe_mean([c["top10_ask_ratio"] for c in compare_results]),
        "top20_bid_avg_ratio": safe_mean([c["top20_bid_ratio"] for c in compare_results]),
        "top20_ask_avg_ratio": safe_mean([c["top20_ask_ratio"] for c in compare_results]),
        "top50_bid_avg_ratio": safe_mean([c["top50_bid_ratio"] for c in compare_results]),
        "top50_ask_avg_ratio": safe_mean([c["top50_ask_ratio"] for c in compare_results]),
        "top100_bid_avg_ratio": safe_mean([c["top100_bid_ratio"] for c in compare_results]),
        "top100_ask_avg_ratio": safe_mean([c["top100_ask_ratio"] for c in compare_results]),
        "avg_diffs_applied_per_compare": safe_mean([float(c["diffs_applied"]) for c in compare_results]),
        "ask_side_weaker_than_bid_top50_count": sum(1 for c in compare_results if c["ask_weaker_than_bid_top50"]),
        "ask_side_weaker_than_bid_top100_count": sum(1 for c in compare_results if c["ask_weaker_than_bid_top100"]),
        "avg_live_only_bid_distance_bps": safe_mean([c["live_only_bid_distance_bps_avg"] for c in compare_results]),
        "avg_live_only_ask_distance_bps": safe_mean([c["live_only_ask_distance_bps_avg"] for c in compare_results]),
        "avg_snapshot_only_bid_distance_bps": safe_mean([c["snapshot_only_bid_distance_bps_avg"] for c in compare_results]),
        "avg_snapshot_only_ask_distance_bps": safe_mean([c["snapshot_only_ask_distance_bps_avg"] for c in compare_results]),
        "max_observed_mismatch_distance_bps": max(
            [c["max_mismatch_distance_bps"] for c in compare_results if c["max_mismatch_distance_bps"] is not None],
            default=None,
        ),
        "snapshot_gap_diff_avg": safe_mean(snapshot_gap_diff_counts[1:] if len(snapshot_gap_diff_counts) > 1 else snapshot_gap_diff_counts),
    }

    worst_cases = sorted(
        compare_results,
        key=lambda c: (
            c["top50_bid_ratio"] + c["top50_ask_ratio"] + c["top100_bid_ratio"] + c["top100_ask_ratio"]
        ),
    )[:12]

    result = {
        "symbol": SYMBOL,
        "snapshot_channel": SNAPSHOT_CHANNEL,
        "diff_channel": DIFF_CHANNEL,
        "ssl_verify": SSL_VERIFY,
        "started_at": utc_now_iso(),
        "max_seconds": MAX_SECONDS,
        "message_count": message_count,
        "snapshot_count": snapshot_count,
        "diff_count": diff_count,
        "first_snapshot_index": first_snapshot_index,
        "diffs_before_first_snapshot": diffs_before_first_snapshot,
        "first_orders": first_orders,
        "compare_count": compare_count,
        "summary": summary,
        "diff_update_density_all": dict(diff_density_all),
        "diff_update_density_by_side": {
            "bid": dict(diff_density_by_side["bid"]),
            "ask": dict(diff_density_by_side["ask"]),
        },
        "diff_distance_samples_summary_bps": {
            "bid_avg": safe_mean(diff_distance_samples_bps["bid"]),
            "ask_avg": safe_mean(diff_distance_samples_bps["ask"]),
            "bid_median": statistics.median(diff_distance_samples_bps["bid"]) if diff_distance_samples_bps["bid"] else None,
            "ask_median": statistics.median(diff_distance_samples_bps["ask"]) if diff_distance_samples_bps["ask"] else None,
        },
        "snapshot_gap_diff_counts": snapshot_gap_diff_counts,
        "worst_cases": worst_cases,
        "compare_results": compare_results,
        "ok": True,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()