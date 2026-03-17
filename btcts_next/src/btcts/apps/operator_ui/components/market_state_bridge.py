# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py
# desc: Thin UI bridge for reading and summarizing stable market_state records.

from __future__ import annotations

from typing import Any

from btcts.apps.operator_ui.market_state_service import load_latest_market_state


def load_market_overview(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
) -> dict[str, Any]:
    return load_latest_market_state(
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type="market.overview",
    )


def market_monitor_metrics(state: dict[str, Any] | None) -> dict[str, Any]:
    if not state:
        return {}

    top = state.get("top_book_summary") or {}
    near = state.get("near_zone_liquidity_summary") or {}
    imbalance = state.get("imbalance_summary") or {}

    return {
        "best_bid": state.get("best_bid", top.get("best_bid")),
        "best_ask": state.get("best_ask", top.get("best_ask")),
        "spread": state.get("spread", top.get("spread")),
        "bid_depth": near.get("bid_size_total"),
        "ask_depth": near.get("ask_size_total"),
        "imbalance": imbalance.get("near_size_imbalance"),
        "event_ts": state.get("exchange_ts") or state.get("collector_ts"),
        "trust_state": state.get("trust_state"),
        "boundary_reason": state.get("boundary_reason"),
    }


def market_state_status_caption(state: dict[str, Any] | None) -> str:
    if not state:
        return "market_state unavailable"

    trust = state.get("trust_state") or "-"
    boundary = state.get("boundary_reason") or "-"
    series_id = state.get("source_series_id") or "-"
    return f"trust={trust} / boundary={boundary} / series={series_id}"