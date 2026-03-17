# path: ./btcts_next/src/btcts/market_engine/onboarding/capture_probe.py
# desc: Capture and summarize normalized event samples for exchange onboarding analysis.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.market_engine.onboarding.stream_classifier import StreamClassifier


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


@dataclass(frozen=True)
class CaptureProbeRow:
    record_type: str
    family: str
    stream_session_id: str | None
    sequence_id: int | None
    source_event_id: str | None
    continuity_state: str | None
    event_type: str | None


class CaptureProbe:
    def __init__(self) -> None:
        self._classifier = StreamClassifier()

    def sample_rows(self, normalized_events: list[dict[str, Any]], *, limit: int = 20) -> list[CaptureProbeRow]:
        rows: list[CaptureProbeRow] = []

        for event in normalized_events[: max(0, limit)]:
            classified = self._classifier.classify(event)
            payload = _payload(event)
            rows.append(
                CaptureProbeRow(
                    record_type=classified.record_type,
                    family=classified.family,
                    stream_session_id=classified.stream_session_id,
                    sequence_id=classified.sequence_id,
                    source_event_id=classified.source_event_id,
                    continuity_state=classified.continuity_state,
                    event_type=str(payload.get("event_type")) if payload.get("event_type") else None,
                )
            )

        return rows

    def sample_dicts(self, normalized_events: list[dict[str, Any]], *, limit: int = 20) -> list[dict[str, Any]]:
        return [
            {
                "record_type": row.record_type,
                "family": row.family,
                "stream_session_id": row.stream_session_id,
                "sequence_id": row.sequence_id,
                "source_event_id": row.source_event_id,
                "continuity_state": row.continuity_state,
                "event_type": row.event_type,
            }
            for row in self.sample_rows(normalized_events, limit=limit)
        ]