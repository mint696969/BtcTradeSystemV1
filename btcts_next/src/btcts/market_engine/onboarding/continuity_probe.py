# path: ./btcts_next/src/btcts/market_engine/onboarding/continuity_probe.py
# desc: Summarize continuity and boundary behavior from normalized events for exchange onboarding analysis.

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from btcts.market_engine.onboarding.stream_classifier import StreamClassifier


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


@dataclass(frozen=True)
class ContinuityProbeSummary:
    total_events: int
    family_counts: dict[str, int]
    continuity_counts: dict[str, int]
    stream_session_counts: dict[str, int]
    first_sequence_id: int | None
    last_sequence_id: int | None
    gap_detected_count: int
    resync_like_count: int
    unknown_continuity_count: int
    boundary_event_count: int
    stream_started_count: int
    expected_discontinuity_count: int


class ContinuityProbe:
    def __init__(self) -> None:
        self._classifier = StreamClassifier()

    def summarize(self, normalized_events: list[dict[str, Any]]) -> ContinuityProbeSummary:
        family_counts = Counter()
        continuity_counts = Counter()
        stream_session_counts = Counter()

        first_sequence_id: int | None = None
        last_sequence_id: int | None = None
        stream_started_count = 0
        expected_discontinuity_count = 0

        for event in normalized_events:
            classified = self._classifier.classify(event)
            payload = _payload(event)

            family_counts[classified.family] += 1

            continuity_state = str(payload.get("continuity_state") or "missing")
            continuity_counts[continuity_state] += 1

            if classified.record_type == "stream.started":
                stream_started_count += 1
                if payload.get("expected_continuity") is False:
                    expected_discontinuity_count += 1

            stream_session_id = classified.stream_session_id or "missing"
            stream_session_counts[stream_session_id] += 1

            seq = classified.sequence_id
            if seq is not None:
                if first_sequence_id is None or seq < first_sequence_id:
                    first_sequence_id = seq
                if last_sequence_id is None or seq > last_sequence_id:
                    last_sequence_id = seq

        return ContinuityProbeSummary(
            total_events=len(normalized_events),
            family_counts=dict(family_counts),
            continuity_counts=dict(continuity_counts),
            stream_session_counts=dict(stream_session_counts),
            first_sequence_id=first_sequence_id,
            last_sequence_id=last_sequence_id,
            gap_detected_count=continuity_counts.get("gap_detected", 0),
            resync_like_count=continuity_counts.get("resynced", 0) + continuity_counts.get("resync_started", 0),
            unknown_continuity_count=continuity_counts.get("unknown", 0) + continuity_counts.get("missing", 0),
            boundary_event_count=family_counts.get("boundary", 0),
            stream_started_count=stream_started_count,
            expected_discontinuity_count=expected_discontinuity_count,
        )