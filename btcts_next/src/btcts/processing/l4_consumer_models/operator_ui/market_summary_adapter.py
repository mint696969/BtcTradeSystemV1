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
    semantic_wiring_key: str
    semantic_observer_status_key: str = "unknown"
    semantic_observer_present_key: str = "false"
    semantic_usage_summary_present_key: str = "false"
    semantic_contract_rows_present_key: str = "false"
    semantic_summary_source_key: str = "unknown"
    semantic_contract_source_key: str = "unknown"
    semantic_meaning_version_key: str = "unknown"
    orderbook_wiring_key: str = "missing"
    orderbook_contract_status_source_key: str = "unknown"
    semantic_rows_count: int = 0
    semantic_total_rows: int = 0
    semantic_active_event_count: int = 0
    semantic_mapped_event_count: int = 0
    semantic_unknown_event_count: int = 0
    semantic_event_family_distribution: dict[str, int] = field(default_factory=dict)
    semantic_trust_bucket_distribution: dict[str, int] = field(default_factory=dict)
    semantic_interpretation_bucket_distribution: dict[str, int] = field(default_factory=dict)
    semantic_consumer_distribution: dict[str, int] = field(default_factory=dict)
    summary_slots_count: int = 0
    orderbook_summary_slots_present: list[str] = field(default_factory=list)
    orderbook_near_wall_present_key: str = "false"
    orderbook_support_present_key: str = "false"
    orderbook_resistance_present_key: str = "false"
    active_event_count: int = 0
    orderbook_active_event_names: list[str] = field(default_factory=list)
    persistence_present_key: str = "false"
    persistence_observable_key: str = "false"
    headline_key: str | None = None
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
            semantic_wiring_key="missing",
            semantic_observer_status_key="unknown",
            semantic_observer_present_key="false",
            semantic_usage_summary_present_key="false",
            semantic_contract_rows_present_key="false",
            semantic_summary_source_key="unknown",
            semantic_contract_source_key="unknown",
            semantic_meaning_version_key="unknown",
            orderbook_wiring_key="missing",
            orderbook_contract_status_source_key="unknown",
            semantic_rows_count=0,
            semantic_total_rows=0,
            semantic_active_event_count=0,
            semantic_mapped_event_count=0,
            semantic_unknown_event_count=0,
            semantic_event_family_distribution={},
            semantic_trust_bucket_distribution={},
            semantic_interpretation_bucket_distribution={},
            semantic_consumer_distribution={},
            summary_slots_count=0,
            orderbook_summary_slots_present=[],
            orderbook_near_wall_present_key="false",
            orderbook_support_present_key="false",
            orderbook_resistance_present_key="false",
            active_event_count=0,
            orderbook_active_event_names=[],
            persistence_present_key="false",
            persistence_observable_key="false",
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
        semantic_wiring_key=_key(summary.semantic_runtime_wiring_status, fallback="missing") or "missing",
        semantic_observer_status_key=_key(summary.semantic_observer_status, fallback="unknown") or "unknown",
        semantic_observer_present_key="true" if summary.semantic_observer_present else "false",
        semantic_usage_summary_present_key="true" if summary.semantic_usage_summary_present else "false",
        semantic_contract_rows_present_key="true" if summary.semantic_contract_rows_present else "false",
        semantic_summary_source_key=_key(summary.semantic_summary_source, fallback="unknown") or "unknown",
        semantic_contract_source_key=_key(summary.semantic_contract_source, fallback="unknown") or "unknown",
        semantic_meaning_version_key=_key(summary.semantic_meaning_version, fallback="unknown") or "unknown",
        orderbook_wiring_key=_key(summary.orderbook_wiring_status, fallback="missing") or "missing",
        orderbook_contract_status_source_key=(
            _key(summary.orderbook_contract_status_source, fallback="unknown") or "unknown"
        ),
        semantic_rows_count=len(summary.semantic_usage_contract_rows),
        semantic_total_rows=int(summary.semantic_total_rows),
        semantic_active_event_count=int(summary.semantic_active_event_count),
        semantic_mapped_event_count=int(summary.semantic_mapped_event_count),
        semantic_unknown_event_count=int(summary.semantic_unknown_event_count),
        semantic_event_family_distribution=dict(summary.semantic_event_family_distribution),
        semantic_trust_bucket_distribution=dict(summary.semantic_trust_bucket_distribution),
        semantic_interpretation_bucket_distribution=dict(
            summary.semantic_interpretation_bucket_distribution
        ),
        semantic_consumer_distribution=dict(summary.semantic_consumer_distribution),
        summary_slots_count=int(summary.orderbook_summary_slots_count),
        orderbook_summary_slots_present=list(summary.orderbook_summary_slots_present),
        orderbook_near_wall_present_key="true" if summary.orderbook_near_wall_present else "false",
        orderbook_support_present_key="true" if summary.orderbook_support_present else "false",
        orderbook_resistance_present_key="true" if summary.orderbook_resistance_present else "false",
        active_event_count=int(summary.orderbook_active_event_count),
        orderbook_active_event_names=list(summary.orderbook_active_event_names),
        persistence_present_key="true" if summary.orderbook_persistence_present else "false",
        persistence_observable_key="true" if summary.orderbook_persistence_observable else "false",
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
        "semantic_summary_source": str(summary.semantic_summary_source),
        "semantic_contract_source": str(summary.semantic_contract_source),
        "semantic_meaning_version": str(summary.semantic_meaning_version),
        "semantic_observer_status": str(summary.semantic_observer_status),
        "semantic_observer_present": bool(summary.semantic_observer_present),
        "semantic_usage_summary_present": bool(summary.semantic_usage_summary_present),
        "semantic_contract_rows_present": bool(summary.semantic_contract_rows_present),
        "semantic_contract_rows_count": int(summary.semantic_contract_rows_count),
        "semantic_runtime_wiring_status": str(summary.semantic_runtime_wiring_status),
        "semantic_total_rows": int(summary.semantic_total_rows),
        "semantic_active_event_count": int(summary.semantic_active_event_count),
        "semantic_mapped_event_count": int(summary.semantic_mapped_event_count),
        "semantic_unknown_event_count": int(summary.semantic_unknown_event_count),
        "semantic_event_family_distribution": dict(summary.semantic_event_family_distribution),
        "semantic_trust_bucket_distribution": dict(summary.semantic_trust_bucket_distribution),
        "semantic_interpretation_bucket_distribution": dict(
            summary.semantic_interpretation_bucket_distribution
        ),
        "semantic_consumer_distribution": dict(summary.semantic_consumer_distribution),
        "semantic_usage_contract_rows_kind": "event_family_contract_rows",
        "semantic_usage_contract_rows_count": len(semantic_usage_contract_rows),
        "semantic_usage_contract_rows": semantic_usage_contract_rows,
        "orderbook_summary_slots_kind": "summary_slot_names",
        "orderbook_summary_slots_count": summary.orderbook_summary_slots_count,
        "orderbook_wiring_status": str(summary.orderbook_wiring_status),
        "orderbook_contract_status_source": str(summary.orderbook_contract_status_source),
        "orderbook_persistence_observable": bool(summary.orderbook_persistence_observable),
        "orderbook_near_wall_present": bool(summary.orderbook_near_wall_present),
        "orderbook_support_present": bool(summary.orderbook_support_present),
        "orderbook_resistance_present": bool(summary.orderbook_resistance_present),
        "orderbook_persistence_present": bool(summary.orderbook_persistence_present),
        "orderbook_summary_slots_present": orderbook_summary_slots_present,
        "orderbook_active_event_names": list(summary.orderbook_active_event_names),
        "orderbook_active_event_count": int(summary.orderbook_active_event_count),
        "orderbook_active_event_contracts_kind": "active_event_contract_rows",
        "orderbook_active_event_contracts_count": len(orderbook_active_event_contracts),
        "orderbook_active_event_contracts": orderbook_active_event_contracts,
        "notable_events": list(summary.notable_events),
        "alert_candidates": list(summary.alert_candidates),
        "diagnostics": dict(summary.diagnostics),
    }