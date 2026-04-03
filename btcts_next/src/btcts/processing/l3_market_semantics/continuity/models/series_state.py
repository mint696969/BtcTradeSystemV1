# path: ./btcts_next/src/btcts/market_engine/assembler/models/series_state.py
# desc: Series state model for deterministic segmentation of normalized_capture streams.

from __future__ import annotations

from dataclasses import dataclass

from btcts.market_engine.types import BoundaryReason, MarketUID, SeriesID, StreamSessionID, TrustState
from .boundary_state import BoundaryState


@dataclass
class SeriesState:
    market_uid: MarketUID
    stream_session_id: StreamSessionID
    series_id: SeriesID
    anchor_event_id: str | None
    start_sequence: int | None
    end_sequence: int | None
    boundary_reason: BoundaryReason
    trust_state: TrustState
    last_source_event_id: str | None = None
    last_stream_event_no: int | None = None
    boundary: BoundaryState | None = None