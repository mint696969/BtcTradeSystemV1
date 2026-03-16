# path: ./btcts_next/src/btcts/collector_vnext/transforms/raw_to_compact.py
# desc: Compact record transforms for Collector vNext.

from __future__ import annotations

from typing import Any, Dict, List


def _top_levels(items: Any, depth: int) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []
    if not isinstance(items, list):
        return out

    for row in items[: max(depth, 0)]:
        if not isinstance(row, dict):
            continue
        try:
            out.append(
                {
                    "price": float(row.get("price")),
                    "size": float(row.get("size")),
                }
            )
        except Exception:
            continue
    return out


def compact_board_snapshot(source_payload: Dict[str, Any], *, depth: int = 10) -> Dict[str, Any]:
    bids = _top_levels(source_payload.get("bids"), depth)
    asks = _top_levels(source_payload.get("asks"), depth)

    best_bid = bids[0]["price"] if bids else None
    best_ask = asks[0]["price"] if asks else None
    mid = (best_bid + best_ask) / 2.0 if best_bid is not None and best_ask is not None else None
    spread = (best_ask - best_bid) if best_bid is not None and best_ask is not None else None

    return {
        "snapshot_id": None,
        "depth": depth,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid": mid,
        "spread": spread,
        "bids": bids,
        "asks": asks,
        "snapshot_reason": "periodic_rest_snapshot",
        "is_resync_snapshot": False,
    }