# path: ./btcts_next/src/btcts/processing/l3_market_semantics/continuity/series_engine.py
# desc: Deterministic series segmentation engine for continuity and boundary semantics.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l3_market_semantics.continuity.models import BoundaryState
from btcts.processing.l3_market_semantics.continuity.models import SeriesState
from btcts.market_engine.types import BoundaryReason, MarketUID, SeriesID, StreamSessionID, TrustState


def _as_market_uid(value: str) -> MarketUID:
    return MarketUID(value)


def _as_stream_session_id(value: str) -> StreamSessionID:
    return StreamSessionID(value)


def _as_series_id(value: str) -> SeriesID:
    return SeriesID(value)


def _event_record_type(event: dict[str, Any]) -> str:
    return str(event.get("record_type") or "")


def _event_stream_session_id(event: dict[str, Any]) -> str:
    return str(event.get("stream_session_id") or "")


def _event_market_uid(event: dict[str, Any]) -> str:
    payload = event.get("payload")
    if isinstance(payload, dict):
        hinted = payload.get("market_uid")
        if hinted:
            return str(hinted)

    instrument_id = str(event.get("instrument_id") or "").strip()
    if instrument_id:
        return instrument_id

    exchange = str(event.get("exchange") or "").strip()
    symbol = str(event.get("symbol") or "").strip()
    if exchange and symbol:
        return f"{exchange}.spot.{symbol}"

    return "unknown.market"


def _event_sequence(event: dict[str, Any]) -> int | None:
    value = event.get("sequence_id")
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except Exception:
        return None


def _event_source_event_id(event: dict[str, Any]) -> str | None:
    value = event.get("source_event_id")
    return str(value) if value else None


def _event_stream_event_no(event: dict[str, Any]) -> int | None:
    payload = event.get("payload")
    if not isinstance(payload, dict):
        return None
    value = payload.get("stream_event_no")
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except Exception:
        return None


def _event_payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


def _boundary_reason_from_record_type(record_type: str) -> BoundaryReason:
    mapping = {
        "stream.started": BoundaryReason.STREAM_STARTED,
        "stream.gap_detected": BoundaryReason.GAP_DETECTED,
        "stream.resync_started": BoundaryReason.RESYNC_STARTED,
        "stream.resync_completed": BoundaryReason.RESYNC_COMPLETED,
    }
    return mapping.get(record_type, BoundaryReason.UNKNOWN)


def _series_id_for_event(event: dict[str, Any], *, sequence: int | None) -> SeriesID:
    stream_session_id = _event_stream_session_id(event) or "unknown-stream"
    seq_text = str(sequence) if sequence is not None else "unknown-seq"
    return _as_series_id(f"{stream_session_id}:series:{seq_text}")


@dataclass(frozen=True)
class SeriesStepResult:
    series_state: SeriesState
    boundary: BoundaryState | None
    started_new_series: bool


class SeriesEngine:
    def __init__(self, profile: Any) -> None:
        self._profile = profile

    def start_series(self, normalized_event: dict[str, Any]) -> SeriesState:
        sequence = _event_sequence(normalized_event)
        source_event_id = _event_source_event_id(normalized_event)
        stream_event_no = _event_stream_event_no(normalized_event)
        market_uid = _as_market_uid(_event_market_uid(normalized_event))
        stream_session_id = _as_stream_session_id(_event_stream_session_id(normalized_event))

        anchor_event_id = source_event_id if self._profile.is_anchor_candidate(normalized_event) else None

        return SeriesState(
            market_uid=market_uid,
            stream_session_id=stream_session_id,
            series_id=_series_id_for_event(normalized_event, sequence=sequence),
            anchor_event_id=anchor_event_id,
            start_sequence=sequence,
            end_sequence=sequence,
            boundary_reason=BoundaryReason.NONE,
            trust_state=TrustState.PROVISIONAL,
            last_source_event_id=source_event_id,
            last_stream_event_no=stream_event_no,
            boundary=None,
        )

    def advance(
        self,
        current: SeriesState | None,
        normalized_event: dict[str, Any],
    ) -> SeriesStepResult:
        if current is None:
            started = self.start_series(normalized_event)
            return SeriesStepResult(
                series_state=started,
                boundary=None,
                started_new_series=True,
            )

        record_type = _event_record_type(normalized_event)
        stream_session_id = _event_stream_session_id(normalized_event)
        sequence = _event_sequence(normalized_event)
        source_event_id = _event_source_event_id(normalized_event)
        stream_event_no = _event_stream_event_no(normalized_event)

        if stream_session_id and stream_session_id != str(current.stream_session_id):
            boundary = BoundaryState(
                boundary_type="new_stream_session",
                source_event_id=source_event_id,
                stream_sequence=sequence,
                reason=BoundaryReason.NEW_STREAM_SESSION,
            )
            started = self.start_series(normalized_event)
            started.boundary = boundary
            started.boundary_reason = boundary.reason
            started.trust_state = TrustState.PROVISIONAL
            return SeriesStepResult(
                series_state=started,
                boundary=boundary,
                started_new_series=True,
            )

        if record_type.startswith("stream."):
            reason = _boundary_reason_from_record_type(record_type)
            boundary = BoundaryState(
                boundary_type=record_type,
                source_event_id=source_event_id,
                stream_sequence=sequence,
                reason=reason,
            )
            started = self.start_series(normalized_event)
            started.boundary = boundary
            started.boundary_reason = reason
            started.trust_state = TrustState.PROVISIONAL
            return SeriesStepResult(
                series_state=started,
                boundary=boundary,
                started_new_series=True,
            )

        if self._profile.is_boundary_event(normalized_event):
            reason = self._profile.boundary_reason(normalized_event)
            boundary = BoundaryState(
                boundary_type="profile_boundary",
                source_event_id=source_event_id,
                stream_sequence=sequence,
                reason=reason,
            )
            started = self.start_series(normalized_event)
            started.boundary = boundary
            started.boundary_reason = reason
            started.trust_state = TrustState.PROVISIONAL
            return SeriesStepResult(
                series_state=started,
                boundary=boundary,
                started_new_series=True,
            )

        current.end_sequence = sequence
        current.last_source_event_id = source_event_id
        current.last_stream_event_no = stream_event_no

        if self._profile.is_anchor_candidate(normalized_event):
            current.anchor_event_id = source_event_id

        payload = _event_payload(normalized_event)
        continuity_state = str(payload.get("continuity_state") or "").strip()

        if continuity_state == "continuous":
            current.trust_state = TrustState.TRUSTED
            current.boundary_reason = BoundaryReason.NONE
        elif continuity_state in {"unknown", "resynced"}:
            current.trust_state = TrustState.PROVISIONAL
            current.boundary_reason = BoundaryReason.NONE
        elif continuity_state == "gap_detected":
            current.trust_state = TrustState.BROKEN
            current.boundary_reason = BoundaryReason.GAP_DETECTED

        return SeriesStepResult(
            series_state=current,
            boundary=None,
            started_new_series=False,
        )