# path: ./btcts_next/src/btcts/ingestion/event_types.py
# desc: Canonical event type definitions shared by ingestion and replay paths.

from __future__ import annotations

from enum import StrEnum


class EventType(StrEnum):
    MARKET_ORDERBOOK_SNAPSHOT = "market.orderbook.snapshot"
    MARKET_ORDERBOOK_DIFF = "market.orderbook.diff"
    MARKET_TRADE = "market.trade"

    STREAM_STARTED = "stream.started"
    STREAM_RECONNECTED = "stream.reconnected"
    STREAM_GAP_DETECTED = "stream.gap_detected"
    STREAM_RESYNC_STARTED = "stream.resync_started"
    STREAM_RESYNC_COMPLETED = "stream.resync_completed"

    SYSTEM_PROVIDER_ERROR = "system.provider_error"