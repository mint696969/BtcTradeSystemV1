# path: ./btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py
# desc: Convert WS board snapshot/diff to canonical orderbook delta events.

from __future__ import annotations

from typing import Any, Dict, List


def _levels(rows: Any) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []

    if not isinstance(rows, list):
        return out

    for r in rows:
        if not isinstance(r, dict):
            continue

        try:
            price = float(r["price"])
            size = float(r["size"])
        except Exception:
            continue

        out.append(
            {
                "price": price,
                "size": size,
            }
        )

    return out


def canonical_board_event(
    payload: Dict[str, Any],
    *,
    snapshot: bool,
) -> Dict[str, Any]:
    bids = _levels(payload.get("bids"))
    asks = _levels(payload.get("asks"))

    return {
        "event_type": "snapshot" if snapshot else "delta",
        "snapshot_id": None,
        "base_snapshot_id": None,
        "prev_event_id": None,
        "continuity_state": "unknown",
        "rebuild_required": False,
        "is_gap_fill": False,
        "is_resync": False,
        "bids": bids,
        "asks": asks,
    }