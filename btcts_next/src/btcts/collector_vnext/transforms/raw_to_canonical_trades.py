# path: ./btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py
# desc: Collector runtime adapter from REST executions payload to L2 canonical trade payloads.

from __future__ import annotations

from typing import Any, Dict, List

from btcts.ingestion.l2_canonical import make_trade_event_payload


def canonical_trades(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = source_payload.get("items", [])
    out: List[Dict[str, Any]] = []

    if not isinstance(items, list):
        return out

    for row in items:
        if not isinstance(row, dict):
            continue

        trade = make_trade_event_payload(
            trade_id=row.get("id"),
            side=row.get("side"),
            price=row.get("price"),
            size=row.get("size"),
            trade_ts=row.get("exec_date"),
            liquidity_role="taker",
        )
        if trade is not None:
            out.append(trade)

    return out