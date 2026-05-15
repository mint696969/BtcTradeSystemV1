# path: ./btcts_next/src/btcts/ingestion/l2_canonical/tradeflow/payload.py
# desc: L2 canonical trade payload shape builders.

from __future__ import annotations

from typing import Any, Dict, Optional


def make_trade_event_payload(
    *,
    trade_id: Any,
    side: Any,
    price: Any,
    size: Any,
    trade_ts: Any = None,
    liquidity_role: str = "taker",
) -> Optional[Dict[str, Any]]:
    try:
        price_f = float(price)
        size_f = float(size)
    except Exception:
        return None

    return {
        "trade_id": trade_id,
        "side": side,
        "price": price_f,
        "size": size_f,
        "notional": price_f * size_f,
        "liquidity_role": liquidity_role,
        "trade_ts": trade_ts,
    }