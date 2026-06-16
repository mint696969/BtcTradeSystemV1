# path: ./btcts_next/src/btcts/replay/replay_tradeflow.py
# desc: Replay-side tradeflow aggregation and metric generation from canonical trade records.

from __future__ import annotations

from typing import Dict, List, Optional

from btcts.ingestion.event_types import EventType
from btcts.processing.features.tradeflow import trade_metrics
from btcts.processing.l3_market_semantics.tradeflow import trade_flow_events


class ReplayTradeFlow:
    def __init__(self):
        self.buffer: List[Dict] = []

    def add_record(self, record: Dict) -> Optional[Dict]:
        record_type = str(record.get("record_type") or "")
        payload = record.get("payload")

        if record_type != EventType.MARKET_TRADE:
            return None

        if not isinstance(payload, dict):
            return None

        self.buffer.append(payload)
        return None

    def flush(self) -> Optional[Dict]:
        if not self.buffer:
            return None

        metrics = trade_metrics(self.buffer)
        events = trade_flow_events(metrics)

        out = {
            "trade_count": metrics["trade_count"],
            "buy_volume": metrics["buy_volume"],
            "sell_volume": metrics["sell_volume"],
            "trade_delta": metrics["trade_delta"],
            "avg_price": metrics["avg_price"],
            "events": events,
        }

        self.buffer = []
        return out