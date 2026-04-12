# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py
# desc: Thin operator UI adapter over shared L4 MarketSummary bundle.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.processing.l4_consumer_models.shared import MarketSummary


@dataclass(frozen=True)
class MarketSummaryWidgetModel:
    widget_kind: str
    freshness_key: str
    trust_key: str | None
    continuity_key: str | None
    interpretation_key: str | None
    headline_key: str | None
    notable_tags: list[str] = field(default_factory=list)
    alert_tags: list[str] = field(default_factory=list)
    age_sec: float | None = None
    event_ts: str | None = None
    source_kind: str = "unknown"
    source_series_id: str | None = None


def _key(value: Any, *, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def market_summary_widget_model(summary: MarketSummary | None) -> MarketSummaryWidgetModel:
    if summary is None:
        return MarketSummaryWidgetModel(
            widget_kind="market_summary",
            freshness_key="UNKNOWN",
            trust_key="unknown",
            continuity_key="unknown",
            interpretation_key="unknown",
            headline_key=None,
            notable_tags=[],
            alert_tags=[],
            age_sec=None,
            event_ts=None,
            source_kind="unknown",
            source_series_id=None,
        )

    return MarketSummaryWidgetModel(
        widget_kind=summary.summary_type,
        freshness_key=_key(summary.freshness, fallback="UNKNOWN") or "UNKNOWN",
        trust_key=_key(summary.trust_state, fallback="unknown"),
        continuity_key=_key(summary.continuity_state, fallback="unknown"),
        interpretation_key=_key(summary.interpretation_bucket, fallback="unknown"),
        headline_key=_key(summary.market_state_label),
        notable_tags=list(summary.notable_events),
        alert_tags=list(summary.alert_candidates),
        age_sec=summary.age_sec,
        event_ts=summary.event_ts,
        source_kind=_key(summary.source_kind, fallback="unknown") or "unknown",
        source_series_id=_key(summary.source_series_id),
    )


def market_summary_status_payload(summary: MarketSummary | None) -> dict[str, Any]:
    if summary is None:
        return {}

    semantic_usage_contract_rows = list(summary.semantic_usage_contract_rows)
    orderbook_active_event_contracts = list(summary.orderbook_active_event_contracts)
    orderbook_summary_slots_present = list(summary.orderbook_summary_slots_present)

    return {
        "summary_type": summary.summary_type,
        "exchange": summary.exchange,
        "symbol_raw": summary.symbol_raw,
        "market_uid": summary.market_uid,
        "source_kind": summary.source_kind,
        "source_series_id": summary.source_series_id,
        "event_ts": summary.event_ts,
        "age_sec": summary.age_sec,
        "freshness": summary.freshness,
        "is_stale": summary.is_stale,
        "trust_state": summary.trust_state,
        "continuity_state": summary.continuity_state,
        "interpretation_bucket": summary.interpretation_bucket,
        "interpretation_reason": summary.interpretation_reason,
        "market_state_label": summary.market_state_label,
        "participation_state": summary.participation_state,
        "liquidity_bias": summary.liquidity_bias,
        "semantic_usage_contract_rows_kind": "event_family_contract_rows",
        "semantic_usage_contract_rows_count": len(semantic_usage_contract_rows),
        "semantic_usage_contract_rows": semantic_usage_contract_rows,
        "orderbook_summary_slots_kind": "summary_slot_names",
        "orderbook_summary_slots_count": summary.orderbook_summary_slots_count,
        "orderbook_wiring_status": str(summary.orderbook_wiring_status),
        "orderbook_contract_status_source": str(summary.orderbook_contract_status_source),
        "orderbook_summary_slots_present": orderbook_summary_slots_present,
        "orderbook_active_event_contracts_kind": "active_event_contract_rows",
        "orderbook_active_event_contracts_count": len(orderbook_active_event_contracts),
        "orderbook_active_event_contracts": orderbook_active_event_contracts,
        "notable_events": list(summary.notable_events),
        "alert_candidates": list(summary.alert_candidates),
        "diagnostics": dict(summary.diagnostics),
    }