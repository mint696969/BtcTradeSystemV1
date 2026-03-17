# path: ./tools/test_collector_vnext_board_ws_rebuild_zone_diagnose.py
# desc: Diagnose WS board rebuild by best-distance zones and mismatch modes to decide usable range versus likely fixable issues.

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


SYMBOL = "BTC_JPY"
SSL_VERIFY = False

DEFAULT_MAX_SECONDS = 300.0
DEFAULT_MAX_COMPARE_COUNT = 50

ZONE_LEVELS = (5, 10, 20, 50, 100)
WORST_CASE_KEEP = 16


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

    bid_zone_ratios: Dict[str, float]
    ask_zone_ratios: Dict[str, float]

    bid_zone_match_counts: Dict[str, int]
    ask_zone_match_counts: Dict[str, int]

    only_in_live_bid_levels: int
    only_in_live_ask_levels: int
    only_in_snapshot_bid_levels: int
    only_in_snapshot_ask_levels: int

    live_best_bid: Optional[float]
    live_best_ask: Optional[float]
    snap_best_bid: Optional[float]
    snap_best_ask: Optional[float]

    mismatch_mode: str
    score: float


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except Exception:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


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


def _side_zone_match_counts(
    live_side: List[Tuple[float, float]],
    snap_side: List[Tuple[float, float]],
) -> Tuple[Dict[str, int], Dict[str, float]]:
    match_counts: Dict[str, int] = {}
    ratios: Dict[str, float] = {}
    for n in ZONE_LEVELS:
        live_top = live_side[:n]
        snap_top = snap_side[:n]
        count = 0
        for live_row, snap_row in zip(live_top, snap_top):
            if live_row[0] == snap_row[0] and live_row[1] == snap_row[1]:
                count += 1
        match_counts[str(n)] = count
        ratios[str(n)] = count / float(n)
    return match_counts, ratios


def _diff_level_gap_counts(
    live_side: List[Tuple[float, float]],
    snap_side: List[Tuple[float, float]],
) -> Tuple[int, int]:
    live_prices = {price for price, _ in live_side}
    snap_prices = {price for price, _ in snap_side}
    only_in_live = len(live_prices - snap_prices)
    only_in_snapshot = len(snap_prices - live_prices)
    return only_in_live, only_in_snapshot


def _classify_mismatch_mode(
    *,
    best_bid_match: bool,
    best_ask_match: bool,
    bid_zone_ratios: Dict[str, float],
    ask_zone_ratios: Dict[str, float],
) -> str:
    bid5 = float(bid_zone_ratios.get("5") or 0.0)
    ask5 = float(ask_zone_ratios.get("5") or 0.0)
    bid10 = float(bid_zone_ratios.get("10") or 0.0)
    ask10 = float(ask_zone_ratios.get("10") or 0.0)
    bid20 = float(bid_zone_ratios.get("20") or 0.0)
    ask20 = float(ask_zone_ratios.get("20") or 0.0)

    if best_bid_match and best_ask_match and bid10 >= 0.9 and ask10 >= 0.9:
        return "aligned_near_book"

    if bid5 <= 0.2 and ask5 <= 0.2:
        return "full_near_book_break"

    if bid10 >= 0.8 and ask10 <= 0.2:
        return "ask_side_break"
    if ask10 >= 0.8 and bid10 <= 0.2:
        return "bid_side_break"

    if best_bid_match and best_ask_match and (bid20 <= 0.2 or ask20 <= 0.2):
        return "best_ok_but_depth_break"

    if (not best_bid_match) and (not best_ask_match):
        return "both_best_mismatch"

    if (not best_bid_match) and best_ask_match:
        return "bid_best_mismatch_only"

    if best_bid_match and (not best_ask_match):
        return "ask_best_mismatch_only"

    return "mixed_partial_break"


def _score_compare(
    *,
    bid_zone_ratios: Dict[str, float],
    ask_zone_ratios: Dict[str, float],
    best_bid_match: bool,
    best_ask_match: bool,
    only_in_live_bid_levels: int,
    only_in_live_ask_levels: int,
    only_in_snapshot_bid_levels: int,
    only_in_snapshot_ask_levels: int,
) -> float:
    weights = {
        "5": 5.0,
        "10": 4.0,
        "20": 3.0,
        "50": 2.0,
        "100": 1.0,
    }
    base = 0.0
    for key, weight in weights.items():
        base += float(bid_zone_ratios.get(key) or 0.0) * weight
        base += float(ask_zone_ratios.get(key) or 0.0) * weight

    if best_bid_match:
        base += 2.0
    if best_ask_match:
        base += 2.0

    penalty = (
        only_in_live_bid_levels
        + only_in_live_ask_levels
        + only_in_snapshot_bid_levels
        + only_in_snapshot_ask_levels
    ) * 0.02
    return round(base - penalty, 6)


def _compare_live_vs_snapshot(
    *,
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

    bid_match_counts, bid_ratios = _side_zone_match_counts(live_bids, snap_bids)
    ask_match_counts, ask_ratios = _side_zone_match_counts(live_asks, snap_asks)

    only_in_live_bid_levels, only_in_snapshot_bid_levels = _diff_level_gap_counts(live_bids, snap_bids)
    only_in_live_ask_levels, only_in_snapshot_ask_levels = _diff_level_gap_counts(live_asks, snap_asks)

    live_best_bid = rebuilder.best_bid()
    live_best_ask = rebuilder.best_ask()
    snap_best_bid = _best_price(snap_bids)
    snap_best_ask = _best_price(snap_asks)

    best_bid_match = live_best_bid == snap_best_bid
    best_ask_match = live_best_ask == snap_best_ask

    mismatch_mode = _classify_mismatch_mode(
        best_bid_match=best_bid_match,
        best_ask_match=best_ask_match,
        bid_zone_ratios=bid_ratios,
        ask_zone_ratios=ask_ratios,
    )
    score = _score_compare(
        bid_zone_ratios=bid_ratios,
        ask_zone_ratios=ask_ratios,
        best_bid_match=best_bid_match,
        best_ask_match=best_ask_match,
        only_in_live_bid_levels=only_in_live_bid_levels,
        only_in_live_ask_levels=only_in_live_ask_levels,
        only_in_snapshot_bid_levels=only_in_snapshot_bid_levels,
        only_in_snapshot_ask_levels=only_in_snapshot_ask_levels,
    )

    return CompareResult(
        compare_no=compare_no,
        snapshot_from_index=from_snapshot.index,
        snapshot_to_index=to_snapshot.index,
        diffs_applied=diffs_applied,
        best_bid_match=best_bid_match,
        best_ask_match=best_ask_match,
        bid_zone_ratios=bid_ratios,
        ask_zone_ratios=ask_ratios,
        bid_zone_match_counts=bid_match_counts,
        ask_zone_match_counts=ask_match_counts,
        only_in_live_bid_levels=only_in_live_bid_levels,
        only_in_live_ask_levels=only_in_live_ask_levels,
        only_in_snapshot_bid_levels=only_in_snapshot_bid_levels,
        only_in_snapshot_ask_levels=only_in_snapshot_ask_levels,
        live_best_bid=live_best_bid,
        live_best_ask=live_best_ask,
        snap_best_bid=snap_best_bid,
        snap_best_ask=snap_best_ask,
        mismatch_mode=mismatch_mode,
        score=score,
    )


def _avg(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def _zone_summary(compare_results: List[CompareResult]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for zone in ZONE_LEVELS:
        key = str(zone)
        out[f"bid_top{key}_avg_ratio"] = _avg([float(x.bid_zone_ratios.get(key) or 0.0) for x in compare_results])
        out[f"ask_top{key}_avg_ratio"] = _avg([float(x.ask_zone_ratios.get(key) or 0.0) for x in compare_results])
    return out


def _mode_summary(compare_results: List[CompareResult]) -> Dict[str, int]:
    c = Counter(x.mismatch_mode for x in compare_results)
    return {str(k): int(v) for k, v in sorted(c.items(), key=lambda x: x[0])}


def _build_interpretation(compare_results: List[CompareResult]) -> Dict[str, Any]:
    zone = _zone_summary(compare_results)
    mode_counts = _mode_summary(compare_results)
    compare_count = len(compare_results)

    bid5 = float(zone.get("bid_top5_avg_ratio") or 0.0)
    ask5 = float(zone.get("ask_top5_avg_ratio") or 0.0)
    bid10 = float(zone.get("bid_top10_avg_ratio") or 0.0)
    ask10 = float(zone.get("ask_top10_avg_ratio") or 0.0)
    bid20 = float(zone.get("bid_top20_avg_ratio") or 0.0)
    ask20 = float(zone.get("ask_top20_avg_ratio") or 0.0)
    bid50 = float(zone.get("bid_top50_avg_ratio") or 0.0)
    ask50 = float(zone.get("ask_top50_avg_ratio") or 0.0)
    bid100 = float(zone.get("bid_top100_avg_ratio") or 0.0)
    ask100 = float(zone.get("ask_top100_avg_ratio") or 0.0)

    aligned = int(mode_counts.get("aligned_near_book", 0))
    full_break = int(mode_counts.get("full_near_book_break", 0))
    ask_break = int(mode_counts.get("ask_side_break", 0))
    bid_break = int(mode_counts.get("bid_side_break", 0))
    depth_break = int(mode_counts.get("best_ok_but_depth_break", 0))

    notes: List[str] = []

    if bid10 >= 0.80 and ask10 >= 0.80:
        notes.append("near book looks strong on average")
    elif bid5 >= 0.75 and ask5 >= 0.75:
        notes.append("best-adjacent zone may be usable but wider near zone is unstable")
    else:
        notes.append("near book is not yet stable enough for trust without further investigation")

    if (bid50 < bid20) or (ask50 < ask20) or (bid100 < bid50) or (ask100 < ask50):
        notes.append("deeper zones weaken with distance from best price")

    if ask_break > bid_break:
        notes.append("ask-side-only collapse appears more often than bid-side-only collapse")
    elif bid_break > ask_break:
        notes.append("bid-side-only collapse appears more often than ask-side-only collapse")

    if full_break > 0:
        notes.append("there are full near-book break cases; simple fixed-depth trust is unsafe")

    if depth_break > 0:
        notes.append("some cases keep best prices while deeper levels diverge")

    if aligned > 0 and compare_count > 0:
        notes.append("there are fully aligned windows, so the stream is not uniformly unusable")

    if bid10 >= 0.80 and ask10 >= 0.80 and bid50 < 0.65 and ask50 < 0.65:
        diagnosis = "exchange_side_or_comparison_limited_but_near_book_usable"
        usable_range = {
            "top5": "usable",
            "top10": "usable",
            "top20": "conditional",
            "top50": "reference_only",
            "top100": "not_for_truth_use",
        }
    elif bid5 >= 0.75 and ask5 >= 0.75 and (full_break == 0):
        diagnosis = "near_book_conditionally_usable_but_semantics_need_work"
        usable_range = {
            "top5": "conditional",
            "top10": "conditional",
            "top20": "not_yet_trusted",
            "top50": "not_yet_trusted",
            "top100": "not_yet_trusted",
        }
    else:
        diagnosis = "collector_side_or_comparison_fix_needed"
        usable_range = {
            "top5": "not_yet_trusted",
            "top10": "not_yet_trusted",
            "top20": "not_yet_trusted",
            "top50": "not_yet_trusted",
            "top100": "not_yet_trusted",
        }

    return {
        "diagnosis": diagnosis,
        "mode_counts": mode_counts,
        "zone_summary": zone,
        "usable_range": usable_range,
        "notes": notes,
    }


def observe_zone_diagnose(
    *,
    symbol: str = SYMBOL,
    ssl_verify: bool = SSL_VERIFY,
    max_seconds: float = DEFAULT_MAX_SECONDS,
    max_compare_count: int = DEFAULT_MAX_COMPARE_COUNT,
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
    stream = connect_and_stream_board(
        symbol=symbol,
        ssl_verify=ssl_verify,
    )

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
                result = _compare_live_vs_snapshot(
                    compare_no=compare_no,
                    from_snapshot=last_snapshot_digest,
                    to_snapshot=current_digest,
                    rebuilder=rebuilder,
                    snapshot_payload=payload,
                    diffs_applied=diffs_since_last_snapshot,
                )
                compare_results.append(result)

                rebuilder.apply_event(_event_from_payload("snapshot", payload))
                last_snapshot_digest = current_digest
                diffs_since_last_snapshot = 0

        if len(compare_results) >= max_compare_count:
            break
        if (time.time() - started) >= max_seconds:
            break

    compare_dicts = [asdict(x) for x in compare_results]
    worst_cases = sorted(compare_dicts, key=lambda x: x["score"])[:WORST_CASE_KEEP]
    interpretation = _build_interpretation(compare_results)

    return {
        "ok": True,
        "symbol": symbol,
        "ssl_verify": ssl_verify,
        "elapsed_sec": round(time.time() - started, 3),
        "max_seconds": max_seconds,
        "max_compare_count": max_compare_count,
        "message_count": message_count,
        "snapshot_count": snapshot_count,
        "diff_count": diff_count,
        "first_snapshot_index": first_snapshot_index,
        "diffs_before_first_snapshot": diffs_before_first_snapshot,
        "compare_count": len(compare_results),
        "mode_counts": interpretation["mode_counts"],
        "zone_summary": interpretation["zone_summary"],
        "usable_range": interpretation["usable_range"],
        "notes": interpretation["notes"],
        "diagnosis": interpretation["diagnosis"],
        "worst_cases": worst_cases,
        "compare_results": compare_dicts,
    }


def main() -> int:
    max_seconds = _env_float("BTCTS_WS_REBUILD_ZONE_SECONDS", DEFAULT_MAX_SECONDS)
    max_compare_count = _env_int("BTCTS_WS_REBUILD_ZONE_COMPARE_COUNT", DEFAULT_MAX_COMPARE_COUNT)

    result = observe_zone_diagnose(
        max_seconds=max_seconds,
        max_compare_count=max_compare_count,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())