# path: ./btcts_next/src/btcts/market_engine/assembler/models/boundary_state.py
# desc: Boundary state model describing series splits, trust breaks, and anchor replacement events.

from __future__ import annotations

from dataclasses import dataclass

from btcts.market_engine.types import BoundaryReason


@dataclass(frozen=True)
class BoundaryState:
    boundary_type: str
    source_event_id: str | None
    stream_sequence: int | None
    reason: BoundaryReason