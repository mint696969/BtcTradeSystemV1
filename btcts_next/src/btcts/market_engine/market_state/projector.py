# path: ./btcts_next/src/btcts/market_engine/market_state/projector.py
# desc: Project internal assembler state into stable outward market_state records.

from __future__ import annotations

from typing import Any

from btcts.market_engine.assembler.models.book_state import BookState
from btcts.market_engine.assembler.models.series_state import SeriesState
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord


def _level_notional(levels: list[dict[str, Any]]) -> float:
    total = 0.0
    for level in levels:
        try:
            total += float(level.get("price", 0.0)) * float(level.get("size", 0.0))
        except Exception:
            continue
    return total


def _level_size(levels: list[dict[str, Any]]) -> float:
    total = 0.0
    for level in levels:
        try:
            total += float(level.get("size", 0.0))
        except Exception:
            continue
    return total


def _top_book_summary(book_state: BookState) -> dict[str, Any]:
    return {
        "best_bid": book_state.best_bid,
        "best_ask": book_state.best_ask,
        "spread": book_state.spread,
        "mid_price": book_state.mid_price,
        "bid_levels_visible": len(book_state.bids_near),
        "ask_levels_visible": len(book_state.asks_near),
    }


def _near_zone_liquidity_summary(book_state: BookState) -> dict[str, Any]:
    bid_size = _level_size(book_state.bids_near)
    ask_size = _level_size(book_state.asks_near)
    bid_notional = _level_notional(book_state.bids_near)
    ask_notional = _level_notional(book_state.asks_near)

    return {
        "bid_size_total": bid_size,
        "ask_size_total": ask_size,
        "bid_notional_total": bid_notional,
        "ask_notional_total": ask_notional,
    }


def _imbalance_summary(book_state: BookState) -> dict[str, Any]:
    bid_size = _level_size(book_state.bids_near)
    ask_size = _level_size(book_state.asks_near)
    total = bid_size + ask_size
    imbalance = 0.0 if total == 0 else (bid_size - ask_size) / total

    return {
        "near_size_imbalance": imbalance,
        "bid_size_total": bid_size,
        "ask_size_total": ask_size,
    }


class MarketStateProjector:
    def project(
        self,
        *,
        cfg: MarketEngineConfig,
        book_state: BookState,
        series_state: SeriesState,
        zone_metadata: dict[str, Any],
    ) -> MarketStateRecord:
        return MarketStateRecord(
            market_uid=cfg.market_uid,
            exchange=cfg.exchange,
            symbol_raw=cfg.symbol_raw,
            collector_ts=book_state.collector_ts,
            exchange_ts=book_state.exchange_ts,
            trust_state=book_state.trust_state,
            boundary_reason=book_state.boundary_reason,
            continuity_state=book_state.continuity_state,
            best_bid=book_state.best_bid,
            best_ask=book_state.best_ask,
            spread=book_state.spread,
            mid_price=book_state.mid_price,
            near_zone_bids=list(book_state.bids_near),
            near_zone_asks=list(book_state.asks_near),
            top_book_summary=_top_book_summary(book_state),
            near_zone_liquidity_summary=_near_zone_liquidity_summary(book_state),
            imbalance_summary=_imbalance_summary(book_state),
            zone_density_metadata=dict(zone_metadata),
            source_series_id=str(series_state.series_id),
            source_stream_session_id=str(series_state.stream_session_id),
        )