# path: ./tools/test_collector_vnext_board_ws_sequence.py
# desc: Diagnose bitFlyer board_ws startup ordering and reconnect bias.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import time
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from btcts.collector_vnext.providers.bitflyer_ws_board import connect_and_stream_board


SYMBOL = "BTC_JPY"
SSL_VERIFY = False


@dataclass
class MessageDigest:
    index: int
    kind: str
    received_ts: Optional[str]
    bid_levels: int
    ask_levels: int
    best_bid: Optional[float]
    best_ask: Optional[float]


def _kind_from_channel(channel: str) -> str:
    if "snapshot" in channel:
        return "snapshot"
    return "diff"


def _best_price(side: Any, *, reverse: bool) -> Optional[float]:
    if not isinstance(side, list) or not side:
        return None
    prices: List[float] = []
    for row in side:
        if isinstance(row, dict):
            price = row.get("price")
            if isinstance(price, (int, float)):
                prices.append(float(price))
    if not prices:
        return None
    return max(prices) if reverse else min(prices)


def _digest_message(index: int, msg: Any) -> MessageDigest:
    payload = msg.payload if isinstance(msg.payload, dict) else {}
    bids = payload.get("bids") if isinstance(payload.get("bids"), list) else []
    asks = payload.get("asks") if isinstance(payload.get("asks"), list) else []

    return MessageDigest(
        index=index,
        kind=_kind_from_channel(msg.channel),
        received_ts=msg.received_ts,
        bid_levels=len(bids),
        ask_levels=len(asks),
        best_bid=_best_price(bids, reverse=True),
        best_ask=_best_price(asks, reverse=False),
    )


def observe_single_session(
    *,
    symbol: str,
    ssl_verify: bool,
    max_messages: int = 40,
    max_seconds: float = 20.0,
) -> Dict[str, Any]:
    started = time.time()
    digests: List[MessageDigest] = []
    first_snapshot_index: Optional[int] = None
    first_diff_index: Optional[int] = None
    diffs_before_first_snapshot = 0

    try:
        stream = connect_and_stream_board(symbol, ssl_verify=ssl_verify)
        for idx, msg in enumerate(stream, start=1):
            digest = _digest_message(idx, msg)
            digests.append(digest)

            if digest.kind == "snapshot" and first_snapshot_index is None:
                first_snapshot_index = idx

            if digest.kind == "diff":
                if first_diff_index is None:
                    first_diff_index = idx
                if first_snapshot_index is None:
                    diffs_before_first_snapshot += 1

            if idx >= max_messages:
                break
            if (time.time() - started) >= max_seconds:
                break

    except Exception as exc:
        return {
            "ok": False,
            "error": f"{exc.__class__.__name__}: {exc}",
            "messages": [asdict(x) for x in digests],
        }

    counts = Counter(x.kind for x in digests)
    order = "unknown"
    if first_snapshot_index is None and first_diff_index is None:
        order = "none"
    elif first_snapshot_index is None:
        order = "diff_only"
    elif first_diff_index is None:
        order = "snapshot_only"
    elif first_diff_index < first_snapshot_index:
        order = "diff_first"
    elif first_snapshot_index < first_diff_index:
        order = "snapshot_first"
    else:
        order = "same_index"

    return {
        "ok": True,
        "order": order,
        "first_snapshot_index": first_snapshot_index,
        "first_diff_index": first_diff_index,
        "diffs_before_first_snapshot": diffs_before_first_snapshot,
        "message_count": len(digests),
        "counts": dict(counts),
        "messages": [asdict(x) for x in digests],
    }


def observe_repeated_short_sessions(
    *,
    symbol: str,
    ssl_verify: bool,
    trials: int = 8,
    max_messages: int = 8,
    max_seconds: float = 6.0,
) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    order_counts: Counter[str] = Counter()

    for trial in range(1, trials + 1):
        one = observe_single_session(
            symbol=symbol,
            ssl_verify=ssl_verify,
            max_messages=max_messages,
            max_seconds=max_seconds,
        )
        one["trial"] = trial
        results.append(one)
        if one.get("ok"):
            order_counts[str(one.get("order"))] += 1
        else:
            order_counts["error"] += 1

        time.sleep(0.5)

    return {
        "trial_count": trials,
        "order_counts": dict(order_counts),
        "trials": results,
    }


def main() -> int:
    summary = {
        "symbol": SYMBOL,
        "ssl_verify": SSL_VERIFY,
        "long_session": observe_single_session(
            symbol=SYMBOL,
            ssl_verify=SSL_VERIFY,
            max_messages=40,
            max_seconds=20.0,
        ),
        "repeated_short_sessions": observe_repeated_short_sessions(
            symbol=SYMBOL,
            ssl_verify=SSL_VERIFY,
            trials=8,
            max_messages=8,
            max_seconds=6.0,
        ),
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())