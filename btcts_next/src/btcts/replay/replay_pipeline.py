# path: ./btcts_next/src/btcts/replay/replay_pipeline.py
# desc: Replay pipeline that rebuilds orderbook state and recomputes liquidity signals/events.

from __future__ import annotations

from typing import Dict, List, Optional

from btcts.ingestion.event_types import EventType
from btcts.ingestion.l2_canonical.orderbook.book_rebuilder import OrderBookRebuilder
from btcts.market_engine.profiles.base import ExchangeProfile
from btcts.processing.l3_market_semantics.orderbook import (
    SignalState,
    build_liquidity_payload,
    build_signal_events,
    resolve_orderbook_semantic_policy,
)


class ReplayPipeline:
    def __init__(
        self,
        *,
        semantic_policy: Optional[Dict] = None,
        exchange_profile: ExchangeProfile | None = None,
    ):
        self.rebuilder = OrderBookRebuilder()
        self.signal_state = SignalState()
        self.exchange_profile = exchange_profile
        baseline_policy = None
        if self.exchange_profile is not None:
            baseline_policy = self.exchange_profile.orderbook_semantic_policy()

        self.semantic_policy = resolve_orderbook_semantic_policy(
            baseline_policy=baseline_policy,
            override_policy=semantic_policy,
        )

    def process_record(self, record: Dict) -> Optional[Dict]:
        record_type = str(record.get("record_type") or "")
        payload = record.get("payload")

        if not isinstance(payload, dict):
            return None

        if record_type not in {
            EventType.MARKET_ORDERBOOK_SNAPSHOT,
            EventType.MARKET_ORDERBOOK_DIFF,
        }:
            return None

        prev_signal = self.signal_state.get()

        signal_payload = build_liquidity_payload(
            self.rebuilder,
            payload,
            levels=10,
            wall_levels=20,
            semantic_policy=self.semantic_policy,
        )

        if signal_payload is None:
            return None

        events = build_signal_events(prev_signal, signal_payload)
        self.signal_state.update(signal_payload)

        return {
            "record_type": record_type,
            "record_id": record.get("record_id"),
            "event_ts": record.get("event_ts"),
            "signal": signal_payload,
            "events": events,
            "best_bid": self.rebuilder.best_bid(),
            "best_ask": self.rebuilder.best_ask(),
        }

    def process_records(self, records: List[Dict]) -> List[Dict]:
        out: List[Dict] = []

        for record in records:
            result = self.process_record(record)
            if result is not None:
                out.append(result)

        return out