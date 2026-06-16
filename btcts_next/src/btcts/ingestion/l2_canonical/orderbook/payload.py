# path: ./btcts_next/src/btcts/ingestion/l2_canonical/orderbook/payload.py
# desc: L2 canonical orderbook payload shape builders.

from __future__ import annotations

from typing import Any, Dict, List


def normalize_orderbook_levels(items: Any, *, depth: int | None = None) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []
    if not isinstance(items, list):
        return out

    rows = items if depth is None else items[: max(depth, 0)]
    for row in rows:
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


def make_orderbook_snapshot_payload(
    *,
    bids: Any,
    asks: Any,
    snapshot_id: str | None,
    depth: int | None = None,
    snapshot_reason: str = "periodic_rest_snapshot",
) -> Dict[str, Any]:
    return {
        "event_type": "snapshot",
        "snapshot_id": snapshot_id,
        "prev_snapshot_id": None,
        "prev_event_id": None,
        "base_snapshot_id": snapshot_id,
        "bids": normalize_orderbook_levels(bids, depth=depth),
        "asks": normalize_orderbook_levels(asks, depth=depth),
        "snapshot_reason": snapshot_reason,
        "is_resync_snapshot": False,
        "continuity_state": "unknown",
        "rebuild_required": False,
        "is_gap_fill": False,
        "is_resync": False,
    }


def make_orderbook_event_payload(
    *,
    event_type: str,
    bids: Any,
    asks: Any,
) -> Dict[str, Any]:
    if event_type not in {"snapshot", "delta"}:
        raise ValueError(f"unsupported orderbook event_type: {event_type}")

    return {
        "event_type": event_type,
        "snapshot_id": None,
        "base_snapshot_id": None,
        "prev_event_id": None,
        "continuity_state": "unknown",
        "rebuild_required": False,
        "is_gap_fill": False,
        "is_resync": False,
        "bids": normalize_orderbook_levels(bids),
        "asks": normalize_orderbook_levels(asks),
    }