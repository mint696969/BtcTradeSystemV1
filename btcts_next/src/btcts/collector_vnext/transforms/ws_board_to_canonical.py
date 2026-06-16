# path: ./btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py
# desc: Collector runtime adapter from venue-normalized WS board levels to L2 canonical orderbook payloads.

from __future__ import annotations

from typing import Any, Dict, Protocol

from btcts.collector_vnext.venue_adapters.bitflyer_board import NormalizedBoardLevels
from btcts.ingestion.l2_canonical import make_orderbook_event_payload


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

    return make_orderbook_event_payload(
        event_type="snapshot" if snapshot else "delta",
        bids=levels.bids,
        asks=levels.asks,
    )