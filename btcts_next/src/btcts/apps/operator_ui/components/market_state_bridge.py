# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py
# desc: Thin UI bridge for reading and summarizing stable market_state records.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from btcts.apps.operator_ui.market_state_service import (
    load_latest_market_state,
    load_latest_market_summary,
)
from btcts.processing.l4_consumer_models.operator_ui import (
    MarketSummaryWidgetModel,
    market_summary_status_payload,
    market_summary_widget_model,
)
from btcts.processing.l4_consumer_models.shared import MarketSummary


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


def load_market_summary_bundle(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
) -> MarketSummary:
    return load_latest_market_summary(
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type="market.overview",
    )


def load_market_summary_status_payload(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
) -> dict[str, Any]:
    summary = load_market_summary_bundle(
        exchange=exchange,
        symbol_raw=symbol_raw,
    )
    return market_summary_status_payload(summary)


def load_market_summary_widget_model(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
) -> MarketSummaryWidgetModel:
    summary = load_market_summary_bundle(
        exchange=exchange,
        symbol_raw=symbol_raw,
    )
    return market_summary_widget_model(summary)


def market_state_age_seconds(state: dict[str, Any] | None) -> float | None:
    if not state:
        return None

    ts = state.get("collector_ts") or state.get("exchange_ts")
    if not isinstance(ts, str) or not ts:
        return None

    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None

    return max((datetime.now(timezone.utc) - dt).total_seconds(), 0.0)


def market_state_freshness_label(
    state: dict[str, Any] | None,
    *,
    live_sec: float = 30.0,
    stale_sec: float = 120.0,
) -> str:
    if not state:
        return "UNAVAILABLE"

    age = market_state_age_seconds(state)
    if age is None:
        return "UNKNOWN"

    if age <= live_sec:
        return "LIVE"

    if age <= stale_sec:
        return "QUIET"

    return "STALE"


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
        "continuity_state": state.get("continuity_state"),
        "interpretation_bucket": state.get("interpretation_bucket"),
        "interpretation_reason": state.get("interpretation_reason"),
    }


def market_state_status_caption(state: dict[str, Any] | None) -> str:
    if not state:
        return "market_state unavailable"

    trust = state.get("trust_state") or "-"
    boundary = state.get("boundary_reason") or "-"
    continuity = state.get("continuity_state") or "-"
    interpretation = state.get("interpretation_bucket") or "-"
    series_id = state.get("source_series_id") or "-"
    freshness = market_state_freshness_label(state)
    age = market_state_age_seconds(state)

    age_text = "-" if age is None else f"{age:.1f}s"
    return (
        f"freshness={freshness} / age={age_text} / trust={trust} / "
        f"boundary={boundary} / continuity={continuity} / "
        f"interpretation={interpretation} / series={series_id}"
    )


def market_summary_status_caption(summary: MarketSummary | None) -> str:
    if summary is None:
        return "market_summary unavailable"

    trust = summary.trust_state or "-"
    continuity = summary.continuity_state or "-"
    interpretation = summary.interpretation_bucket or "-"
    series_id = summary.source_series_id or "-"
    freshness = summary.freshness or "UNKNOWN"
    semantic_rows_count = len(summary.semantic_usage_contract_rows)
    active_event_rows_count = len(summary.orderbook_active_event_contracts)

    age_text = "-" if summary.age_sec is None else f"{summary.age_sec:.1f}s"
    return (
        f"freshness={freshness} / age={age_text} / trust={trust} / "
        f"continuity={continuity} / interpretation={interpretation} / "
        f"family_rows={semantic_rows_count} / active_event_rows={active_event_rows_count} / "
        f"series={series_id}"
    )