# path: ./btcts_next/src/btcts/market_engine/onboarding/stream_classifier.py
# desc: Classify normalized market events into onboarding message families for exchange profile discovery.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


@dataclass(frozen=True)
class ClassifiedEvent:
    family: str
    record_type: str
    continuity_state: str | None
    source_event_id: str | None
    stream_session_id: str | None
    sequence_id: int | None


class StreamClassifier:
    def classify(self, normalized_event: dict[str, Any]) -> ClassifiedEvent:
        record_type = str(normalized_event.get("record_type") or "")
        payload = _payload(normalized_event)
        continuity_state = payload.get("continuity_state")
        source_event_id = normalized_event.get("source_event_id")
        stream_session_id = normalized_event.get("stream_session_id")
        sequence_id = normalized_event.get("sequence_id")

        family = self._family(record_type=record_type, payload=payload)

        return ClassifiedEvent(
            family=family,
            record_type=record_type,
            continuity_state=str(continuity_state) if continuity_state else None,
            source_event_id=str(source_event_id) if source_event_id else None,
            stream_session_id=str(stream_session_id) if stream_session_id else None,
            sequence_id=int(sequence_id) if sequence_id is not None else None,
        )

    def _family(self, *, record_type: str, payload: dict[str, Any]) -> str:
        event_type = str(payload.get("event_type") or "")

        if record_type.startswith("stream."):
            return "boundary"
        if record_type == "market.orderbook.snapshot":
            return "snapshot"
        if record_type == "market.orderbook.diff":
            return "diff"
        if record_type == "market.trade":
            return "trade"
        if event_type:
            return event_type
        return "unknown"