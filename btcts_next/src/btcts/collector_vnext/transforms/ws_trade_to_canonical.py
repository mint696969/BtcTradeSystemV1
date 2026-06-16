# path: ./btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py
# desc: Collector runtime adapter from WS executions message to L2 canonical trade payload.

from __future__ import annotations

from typing import Any, Dict, Optional

from btcts.ingestion.l2_canonical import make_trade_event_payload


def canonical_ws_trade(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return make_trade_event_payload(
        trade_id=msg.get("id"),
        side=msg.get("side"),
        price=msg.get("price"),
        size=msg.get("size"),
        trade_ts=msg.get("exec_date"),
        liquidity_role="taker",
    )