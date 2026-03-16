# path: ./btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py
# desc: Canonical trade transforms (1 trade = 1 event).

from __future__ import annotations

from typing import Any, Dict, List


def canonical_trades(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = source_payload.get("items", [])
    out: List[Dict[str, Any]] = []

    if not isinstance(items, list):
        return out

    for row in items:
        if not isinstance(row, dict):
            continue

        try:
            side = row.get("side")
            price = float(row.get("price"))
            size = float(row.get("size"))
            exec_id = row.get("id")
        except Exception:
            continue

        out.append(
            {
                "trade_id": exec_id,
                "side": side,
                "price": price,
                "size": size,
                "notional": price * size,
                "liquidity_role": "taker",
                "trade_ts": row.get("exec_date"),
            }
        )

    return out