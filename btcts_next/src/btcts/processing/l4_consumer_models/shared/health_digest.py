# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/health_digest.py
# desc: Shared wording-free health digest bundle for L4 consumer models.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class HealthDigest:
    digest_type: str
    digest_version: str
    source_kind: str
    exchange: str | None
    symbol_raw: str | None
    market_uid: str | None
    event_ts: str | None
    freshness: str
    is_stale: bool | None
    collector_runtime: dict[str, Any] = field(default_factory=dict)
    api_runtime: dict[str, Any] = field(default_factory=dict)
    ws_runtime: dict[str, Any] = field(default_factory=dict)
    market_runtime: dict[str, Any] = field(default_factory=dict)
    semantic_usage: dict[str, Any] = field(default_factory=dict)
    orderbook_runtime: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HealthDigestBuildInput:
    collector_state: dict[str, Any] | None = None
    market_state_row: dict[str, Any] | None = None
    market_diagnostics: dict[str, Any] | None = None
    semantic_usage_summary: dict[str, Any] | None = None
    semantic_usage_rows: list[dict[str, Any]] | None = None
    runtime_contract_summary: dict[str, Any] | None = None
    orderbook_runtime_summary: dict[str, Any] | None = None
    source_kind: str | None = None


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _safe_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def _normalize_source_kind(value: Any) -> str:
    return _safe_str(value) or "unknown"


def _resolve_freshness(market_diagnostics: dict[str, Any]) -> str:
    return _safe_str(market_diagnostics.get("preferred_row_freshness")) or "UNKNOWN"


def _resolve_is_stale(freshness: str) -> bool | None:
    if freshness == "UNKNOWN":
        return None
    return freshness == "STALE"


def _pick_event_ts(market_state_row: dict[str, Any]) -> str | None:
    return _safe_str(market_state_row.get("collector_ts")) or _safe_str(
        market_state_row.get("exchange_ts")
    )


def _normalize_collector_runtime(collector_state: dict[str, Any]) -> dict[str, Any]:
    status_payload = collector_state.get("status") or {}
    health_payload = collector_state.get("health") or {}

    return {
        "mode": _safe_str(collector_state.get("mode")),
        "ok": _safe_bool(health_payload.get("ok")),
        "runtime_kind": _safe_str(status_payload.get("runtime_kind")),
        "daemon_runtime_kind": _safe_str(status_payload.get("daemon_runtime_kind")),
        "status_source": _safe_str(status_payload.get("source_kind")) or "collector_state",
    }


def _normalize_api_runtime(collector_state: dict[str, Any]) -> dict[str, Any]:
    rate_items = ((collector_state.get("rate") or {}).get("items") or {})
    bitflyer = rate_items.get("bitflyer") or {}
    rate_domains = (bitflyer.get("domains") or {}) if isinstance(bitflyer, dict) else {}
    market_data_rate = (rate_domains.get("market_data") or {}) if isinstance(rate_domains, dict) else {}
    rate_view = market_data_rate or bitflyer

    return {
        "provider": _safe_str(rate_view.get("provider")) or "bitflyer",
        "mode": _safe_str(rate_view.get("mode")),
        "utilization": _safe_float(rate_view.get("utilization")),
        "target_utilization": _safe_float(rate_view.get("target_utilization")),
        "hard_cap_utilization": _safe_float(rate_view.get("hard_cap_utilization")),
        "requests_60s": int(rate_view.get("requests_60s") or 0),
        "requests_300s": int(rate_view.get("requests_300s") or 0),
        "last_429_ts": _safe_str(rate_view.get("last_429_ts")),
    }


def _normalize_ws_runtime(collector_state: dict[str, Any]) -> dict[str, Any]:
    status_payload = collector_state.get("status") or {}
    ws_board_lane = status_payload.get("ws_board_lane") or {}
    ws_executions_lane = status_payload.get("ws_executions_lane") or {}

    return {
        "board_state": _safe_str(ws_board_lane.get("state")),
        "board_last_error": _safe_str(ws_board_lane.get("last_error")),
        "executions_state": _safe_str(ws_executions_lane.get("state")),
        "executions_last_error": _safe_str(ws_executions_lane.get("last_error")),
        "board_freshness": _safe_str(ws_board_lane.get("freshness")),
        "executions_freshness": _safe_str(ws_executions_lane.get("freshness")),
    }


def _normalize_market_runtime(
    market_state_row: dict[str, Any],
    market_diagnostics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trust_state": _safe_str(
            market_state_row.get("trust_state")
            or market_diagnostics.get("preferred_row_trust_state")
        ),
        "continuity_state": _safe_str(
            market_state_row.get("continuity_state")
            or market_diagnostics.get("preferred_row_continuity_state")
        ),
        "interpretation_bucket": _safe_str(
            market_state_row.get("interpretation_bucket")
            or market_diagnostics.get("preferred_row_interpretation_bucket")
        ),
        "interpretation_reason": _safe_str(market_state_row.get("interpretation_reason")),
        "source_series_id": _safe_str(
            market_state_row.get("source_series_id")
            or market_diagnostics.get("preferred_row_source_series_id")
        ),
        "freshness": _resolve_freshness(market_diagnostics),
    }


def _normalize_semantic_usage(
    semantic_usage_summary: dict[str, Any],
    semantic_usage_rows: list[dict[str, Any]],
    runtime_contract_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_source": _safe_str(semantic_usage_summary.get("source_kind")) or "unknown",
        "observer_status": _safe_str(semantic_usage_summary.get("observer_status")) or "unknown",
        "summary": dict(semantic_usage_summary),
        "contract_rows": list(semantic_usage_rows),
        "runtime_wiring_status": _safe_str(runtime_contract_summary.get("wiring_status")) or "missing",
        "observer_present": bool(runtime_contract_summary.get("observer_present")),
        "usage_summary_present": bool(runtime_contract_summary.get("usage_summary_present")),
        "contract_rows_present": bool(runtime_contract_summary.get("contract_rows_present")),
        "contract_rows_count": int(runtime_contract_summary.get("contract_rows_count") or 0),
        "source_series_present": bool(runtime_contract_summary.get("source_series_present")),
    }


def _normalize_orderbook_runtime(orderbook_runtime_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_status_source": _safe_str(orderbook_runtime_summary.get("contract_status_source"))
        or "unknown",
        "wiring_status": _safe_str(orderbook_runtime_summary.get("wiring_status")) or "missing",
        "freshness": _safe_str(orderbook_runtime_summary.get("freshness")) or "UNKNOWN",
        "summary_slots_present": list(orderbook_runtime_summary.get("summary_slots_present") or []),
        "summary_slots_count": int(
            orderbook_runtime_summary.get("summary_slots_count")
            or orderbook_runtime_summary.get("present_count")
            or 0
        ),
        "near_wall_present": bool(orderbook_runtime_summary.get("near_wall_present")),
        "support_present": bool(orderbook_runtime_summary.get("support_present")),
        "resistance_present": bool(orderbook_runtime_summary.get("resistance_present")),
        "persistence_present": bool(orderbook_runtime_summary.get("persistence_present")),
        "persistence_observable": bool(orderbook_runtime_summary.get("persistence_observable")),
        "active_event_count": int(orderbook_runtime_summary.get("active_event_count") or 0),
        "active_event_names": list(orderbook_runtime_summary.get("active_event_names") or []),
        "active_event_contracts": list(orderbook_runtime_summary.get("active_event_contracts") or []),
    }


def build_health_digest(inp: HealthDigestBuildInput) -> HealthDigest:
    collector_state = dict(inp.collector_state or {})
    market_state_row = dict(inp.market_state_row or {})
    market_diagnostics = dict(inp.market_diagnostics or {})
    semantic_usage_summary = dict(inp.semantic_usage_summary or {})
    semantic_usage_rows = list(inp.semantic_usage_rows or [])
    runtime_contract_summary = dict(inp.runtime_contract_summary or {})
    orderbook_runtime_summary = dict(inp.orderbook_runtime_summary or {})

    freshness = _resolve_freshness(market_diagnostics)

    diagnostics = {
        "market_diag_source_kind": _safe_str(market_diagnostics.get("source_kind")),
        "preferred_row_age_sec": _safe_float(market_diagnostics.get("preferred_row_age_sec")),
        "preferred_row_freshness": _safe_str(market_diagnostics.get("preferred_row_freshness")),
    }

    return HealthDigest(
        digest_type="health_digest",
        digest_version="v1alpha1",
        source_kind=_normalize_source_kind(inp.source_kind or "health_data_service"),
        exchange=_safe_str(market_state_row.get("exchange")),
        symbol_raw=_safe_str(market_state_row.get("symbol_raw") or market_state_row.get("symbol")),
        market_uid=_safe_str(market_state_row.get("market_uid")),
        event_ts=_pick_event_ts(market_state_row),
        freshness=freshness,
        is_stale=_resolve_is_stale(freshness),
        collector_runtime=_normalize_collector_runtime(collector_state),
        api_runtime=_normalize_api_runtime(collector_state),
        ws_runtime=_normalize_ws_runtime(collector_state),
        market_runtime=_normalize_market_runtime(market_state_row, market_diagnostics),
        semantic_usage=_normalize_semantic_usage(
            semantic_usage_summary,
            semantic_usage_rows,
            runtime_contract_summary,
        ),
        orderbook_runtime=_normalize_orderbook_runtime(orderbook_runtime_summary),
        diagnostics=diagnostics,
    )