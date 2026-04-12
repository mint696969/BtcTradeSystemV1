# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/health_digest_adapter.py
# desc: Thin operator UI adapter over shared L4 HealthDigest bundle.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared import HealthDigest


@dataclass(frozen=True)
class HealthDigestWidgetModel:
    widget_kind: str
    freshness_key: str
    collector_ok: bool | None
    collector_mode_key: str | None
    api_mode_key: str | None
    ws_board_state_key: str | None
    ws_executions_state_key: str | None
    trust_key: str | None
    continuity_key: str | None
    interpretation_key: str | None
    semantic_wiring_key: str | None
    orderbook_wiring_key: str | None
    semantic_contract_rows_count: int
    orderbook_summary_slots_count: int
    active_event_count: int
    age_sec: float | None
    event_ts: str | None
    source_kind: str


def _key(value: Any, *, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _number(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def health_digest_widget_model(digest: HealthDigest | None) -> HealthDigestWidgetModel:
    if digest is None:
        return HealthDigestWidgetModel(
            widget_kind="health_digest",
            freshness_key="UNKNOWN",
            collector_ok=None,
            collector_mode_key="unknown",
            api_mode_key="unknown",
            ws_board_state_key="unknown",
            ws_executions_state_key="unknown",
            trust_key="unknown",
            continuity_key="unknown",
            interpretation_key="unknown",
            semantic_wiring_key="missing",
            orderbook_wiring_key="missing",
            semantic_contract_rows_count=0,
            orderbook_summary_slots_count=0,
            active_event_count=0,
            age_sec=None,
            event_ts=None,
            source_kind="unknown",
        )

    collector_runtime = dict(digest.collector_runtime or {})
    api_runtime = dict(digest.api_runtime or {})
    ws_runtime = dict(digest.ws_runtime or {})
    market_runtime = dict(digest.market_runtime or {})
    semantic_usage = dict(digest.semantic_usage or {})
    orderbook_runtime = dict(digest.orderbook_runtime or {})
    diagnostics = dict(digest.diagnostics or {})

    return HealthDigestWidgetModel(
        widget_kind=digest.digest_type,
        freshness_key=_key(digest.freshness, fallback="UNKNOWN") or "UNKNOWN",
        collector_ok=digest.collector_runtime.get("ok"),
        collector_mode_key=_key(collector_runtime.get("mode"), fallback="unknown"),
        api_mode_key=_key(api_runtime.get("mode"), fallback="unknown"),
        ws_board_state_key=_key(ws_runtime.get("board_state"), fallback="unknown"),
        ws_executions_state_key=_key(ws_runtime.get("executions_state"), fallback="unknown"),
        trust_key=_key(market_runtime.get("trust_state"), fallback="unknown"),
        continuity_key=_key(market_runtime.get("continuity_state"), fallback="unknown"),
        interpretation_key=_key(market_runtime.get("interpretation_bucket"), fallback="unknown"),
        semantic_wiring_key=_key(semantic_usage.get("runtime_wiring_status"), fallback="missing"),
        orderbook_wiring_key=_key(orderbook_runtime.get("wiring_status"), fallback="missing"),
        semantic_contract_rows_count=_number(semantic_usage.get("contract_rows_count")),
        orderbook_summary_slots_count=_number(orderbook_runtime.get("summary_slots_count")),
        active_event_count=_number(orderbook_runtime.get("active_event_count")),
        age_sec=_float_or_none(diagnostics.get("preferred_row_age_sec")),
        event_ts=digest.event_ts,
        source_kind=_key(digest.source_kind, fallback="unknown") or "unknown",
    )


def health_digest_status_payload(digest: HealthDigest | None) -> dict[str, Any]:
    if digest is None:
        return {}

    collector_runtime = dict(digest.collector_runtime or {})
    api_runtime = dict(digest.api_runtime or {})
    ws_runtime = dict(digest.ws_runtime or {})
    market_runtime = dict(digest.market_runtime or {})
    semantic_usage = dict(digest.semantic_usage or {})
    orderbook_runtime = dict(digest.orderbook_runtime or {})
    diagnostics = dict(digest.diagnostics or {})

    semantic_contract_rows = list(semantic_usage.get("contract_rows") or [])
    orderbook_summary_slots_present = list(orderbook_runtime.get("summary_slots_present") or [])
    orderbook_active_event_contracts = list(orderbook_runtime.get("active_event_contracts") or [])

    return {
        "digest_type": digest.digest_type,
        "digest_version": digest.digest_version,
        "source_kind": digest.source_kind,
        "exchange": digest.exchange,
        "symbol_raw": digest.symbol_raw,
        "market_uid": digest.market_uid,
        "event_ts": digest.event_ts,
        "freshness": digest.freshness,
        "is_stale": digest.is_stale,
        "collector_runtime": collector_runtime,
        "api_runtime": api_runtime,
        "ws_runtime": ws_runtime,
        "market_runtime": market_runtime,
        "semantic_usage_summary_source": semantic_usage.get("summary_source"),
        "semantic_usage_observer_status": semantic_usage.get("observer_status"),
        "semantic_usage_runtime_wiring_status": semantic_usage.get("runtime_wiring_status"),
        "semantic_usage_contract_rows_kind": "event_family_contract_rows",
        "semantic_usage_contract_rows_count": _number(semantic_usage.get("contract_rows_count")),
        "semantic_usage_contract_rows": semantic_contract_rows,
        "orderbook_runtime_wiring_status": orderbook_runtime.get("wiring_status"),
        "orderbook_summary_slots_kind": "summary_slot_names",
        "orderbook_summary_slots_count": _number(orderbook_runtime.get("summary_slots_count")),
        "orderbook_summary_slots_present": orderbook_summary_slots_present,
        "orderbook_active_event_contracts_kind": "active_event_contract_rows",
        "orderbook_active_event_contracts_count": _number(orderbook_runtime.get("active_event_count")),
        "orderbook_active_event_contracts": orderbook_active_event_contracts,
        "diagnostics": diagnostics,
    }