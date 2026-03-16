# path: ./btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py
# desc: Canonical record transforms for Collector vNext.

from __future__ import annotations

from typing import Any, Dict, List


def _levels(items: Any, depth: int) -> List[Dict[str, float]]:
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


def canonical_board_snapshot(
    source_payload: Dict[str, Any],
    *,
    depth: int = 50,
    snapshot_id: str | None = None,
) -> Dict[str, Any]:
    bids = _levels(source_payload.get("bids"), depth)
    asks = _levels(source_payload.get("asks"), depth)

    return {
        "snapshot_id": snapshot_id,
        "prev_snapshot_id": None,
        "prev_event_id": None,
        "base_snapshot_id": snapshot_id,
        "bids": bids,
        "asks": asks,
        "snapshot_reason": "periodic_rest_snapshot",
        "is_resync_snapshot": False,
        "continuity_state": "unknown",
        "rebuild_required": False,
        "is_gap_fill": False,
        "is_resync": False,
    }