# path: ./btcts_next/src/btcts/market_engine/market_state/schema.py
# desc: Stable outward market_state schema for UI and downstream consumers of Market Engine output.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.market_engine.types import BoundaryReason, TrustState


@dataclass
class MarketStateRecord:
    market_uid: str
    exchange: str
    symbol_raw: str
    collector_ts: str | None
    exchange_ts: str | None
    trust_state: TrustState
    boundary_reason: BoundaryReason
    continuity_state: str | None
    interpretation_bucket: str | None
    interpretation_reason: str | None
    interpretation_policy: dict[str, Any]
    best_bid: float | None
    best_ask: float | None
    spread: float | None
    mid_price: float | None
    near_zone_bids: list[dict[str, Any]] = field(default_factory=list)
    near_zone_asks: list[dict[str, Any]] = field(default_factory=list)
    top_book_summary: dict[str, Any] = field(default_factory=dict)
    near_zone_liquidity_summary: dict[str, Any] = field(default_factory=dict)
    imbalance_summary: dict[str, Any] = field(default_factory=dict)
    zone_density_metadata: dict[str, Any] = field(default_factory=dict)
    source_series_id: str | None = None
    source_stream_session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "market_uid": self.market_uid,
            "exchange": self.exchange,
            "symbol_raw": self.symbol_raw,
            "collector_ts": self.collector_ts,
            "exchange_ts": self.exchange_ts,
            "trust_state": self.trust_state.value,
            "boundary_reason": self.boundary_reason.value,
            "continuity_state": self.continuity_state,
            "interpretation_bucket": self.interpretation_bucket,
            "interpretation_reason": self.interpretation_reason,
            "interpretation_policy": self.interpretation_policy,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "spread": self.spread,
            "mid_price": self.mid_price,
            "near_zone_bids": self.near_zone_bids,
            "near_zone_asks": self.near_zone_asks,
            "top_book_summary": self.top_book_summary,
            "near_zone_liquidity_summary": self.near_zone_liquidity_summary,
            "imbalance_summary": self.imbalance_summary,
            "zone_density_metadata": self.zone_density_metadata,
            "source_series_id": self.source_series_id,
            "source_stream_session_id": self.source_stream_session_id,
        }