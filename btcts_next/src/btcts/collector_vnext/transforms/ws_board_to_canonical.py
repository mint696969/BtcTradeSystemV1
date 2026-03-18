# path: ./btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py
# desc: Convert adapter-normalized WS board levels to canonical orderbook events.

from __future__ import annotations

from typing import Any, Dict, Protocol

from btcts.collector_vnext.venue_adapters.bitflyer_board import NormalizedBoardLevels


class BoardLevelsAdapter(Protocol):
    def extract_board_levels(self, payload: Dict[str, Any]) -> NormalizedBoardLevels:
        ...


def canonical_board_event(
    payload: Dict[str, Any],
    *,
    snapshot: bool,
    adapter: BoardLevelsAdapter,
) -> Dict[str, Any]:
    levels = adapter.extract_board_levels(payload)
    bids = levels.bids
    asks = levels.asks

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