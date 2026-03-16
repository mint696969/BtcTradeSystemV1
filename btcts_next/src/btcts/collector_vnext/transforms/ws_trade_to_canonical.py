# path: ./btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py
# desc: Transform WS executions message to canonical trade.

from __future__ import annotations

from typing import Dict


def canonical_ws_trade(msg: Dict):

    try:

        price = float(msg["price"])
        size = float(msg["size"])
        side = msg["side"]
        exec_id = msg["id"]

    except Exception:
        return None

    return {
        "trade_id": exec_id,
        "side": side,
        "price": price,
        "size": size,
        "notional": price * size,
        "liquidity_role": "taker",
        "trade_ts": msg.get("exec_date"),
    }
