# path: ./btcts_next/src/btcts/processing/l3_market_semantics/continuity/models/book_state.py
# desc: Book state model for assembled market truth with near/far zone separation and trust metadata.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.market_engine.types import BoundaryReason, TrustState


@dataclass
class BookState:
    best_bid: float | None
    best_ask: float | None
    spread: float | None
    mid_price: float | None = None
    continuity_state: str | None = None
    bids_near: list[dict[str, Any]] = field(default_factory=list)
    asks_near: list[dict[str, Any]] = field(default_factory=list)
    bids_far: list[dict[str, Any]] = field(default_factory=list)
    asks_far: list[dict[str, Any]] = field(default_factory=list)
    collector_ts: str | None = None
    exchange_ts: str | None = None
    trust_state: TrustState = TrustState.PROVISIONAL
    boundary_reason: BoundaryReason = BoundaryReason.NONE
    interpretation_bucket: str | None = None
    interpretation_reason: str | None = None
    interpretation_policy: dict[str, Any] = field(default_factory=dict)
    anchor_event_id: str | None = None
    last_source_event_id: str | None = None
    source_stream_session_id: str | None = None