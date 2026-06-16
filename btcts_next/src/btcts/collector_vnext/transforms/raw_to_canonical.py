# path: ./btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py
# desc: Collector runtime adapters for REST board canonical payloads.

from __future__ import annotations

from typing import Any, Dict

from btcts.ingestion.l2_canonical import make_orderbook_snapshot_payload


def canonical_board_snapshot(
    source_payload: Dict[str, Any],
    *,
    depth: int = 50,
    snapshot_id: str | None = None,
) -> Dict[str, Any]:
    return make_orderbook_snapshot_payload(
        bids=source_payload.get("bids"),
        asks=source_payload.get("asks"),
        depth=depth,
        snapshot_id=snapshot_id,
        snapshot_reason="periodic_rest_snapshot",
    )