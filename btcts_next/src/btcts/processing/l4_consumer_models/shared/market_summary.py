# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py
# desc: Shared market summary bundle and thin builder for L4 consumer models.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MarketSummary:
    summary_type: str
    exchange: str | None
    symbol_raw: str | None
    market_uid: str | None
    source_kind: str
    source_series_id: str | None
    event_ts: str | None
    age_sec: float | None
    freshness: str
    is_stale: bool | None
    trust_state: str | None
    continuity_state: str | None
    interpretation_bucket: str | None
    interpretation_reason: str | None
    market_state_label: str | None
    participation_state: str | None
    liquidity_bias: str | None
    semantic_summary_source: str = "unknown"
    semantic_contract_source: str = "unknown"
    semantic_meaning_version: str = "unknown"
    semantic_observer_status: str = "unknown"
    semantic_observer_present: bool = False
    semantic_usage_summary_present: bool = False
    semantic_contract_rows_present: bool = False
    semantic_contract_rows_count: int = 0
    semantic_runtime_wiring_status: str = "missing"
    semantic_total_rows: int = 0
    semantic_active_event_count: int = 0
    semantic_mapped_event_count: int = 0
    semantic_unknown_event_count: int = 0
    semantic_event_family_distribution: dict[str, int] = field(default_factory=dict)
    semantic_trust_bucket_distribution: dict[str, int] = field(default_factory=dict)
    semantic_interpretation_bucket_distribution: dict[str, int] = field(default_factory=dict)
    semantic_consumer_distribution: dict[str, int] = field(default_factory=dict)
    semantic_usage_contract_rows: list[dict[str, Any]] = field(default_factory=list)
    orderbook_active_event_contracts: list[dict[str, Any]] = field(default_factory=list)
    orderbook_active_event_names: list[str] = field(default_factory=list)
    orderbook_active_event_count: int = 0
    orderbook_summary_slots_present: list[str] = field(default_factory=list)
    orderbook_summary_slots_count: int = 0
    orderbook_near_wall_present: bool = False
    orderbook_support_present: bool = False
    orderbook_resistance_present: bool = False
    orderbook_persistence_present: bool = False
    orderbook_wiring_status: str = "missing"
    orderbook_contract_status_source: str = "unknown"
    orderbook_persistence_observable: bool = False
    notable_events: list[str] = field(default_factory=list)
    alert_candidates: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MarketSummaryBuildInput:
    market_state_row: dict[str, Any] | None = None
    diagnostics: dict[str, Any] | None = None
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


def _pick_event_ts(row: dict[str, Any]) -> str | None:
    return _safe_str(row.get("collector_ts")) or _safe_str(row.get("exchange_ts"))


def _resolve_freshness(age_sec: float | None) -> str:
    if age_sec is None:
        return "UNKNOWN"
    if age_sec <= 30.0:
        return "LIVE"
    if age_sec <= 120.0:
        return "QUIET"
    return "STALE"


def _resolve_is_stale(freshness: str) -> bool | None:
    if freshness == "UNKNOWN":
        return None
    return freshness == "STALE"


def _normalize_source_kind(value: Any) -> str:
    normalized = _safe_str(value)
    return normalized or "unknown"


def _normalize_semantic_usage_contract_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw_rows = row.get("semantic_usage_contract_rows")
    if not isinstance(raw_rows, list):
        return []

    out: list[dict[str, Any]] = []
    for item in raw_rows:
        if not isinstance(item, dict):
            continue
        event_family = _safe_str(item.get("event_family"))
        if event_family is None:
            continue
        out.append(
            {
                "contract_source": _safe_str(item.get("contract_source")) or "unknown",
                "interpretation_bucket": _safe_str(item.get("interpretation_bucket")),
                "meaning_version": _safe_str(item.get("meaning_version")) or "unknown",
                "event_family": event_family,
                "usage_grade": _safe_str(item.get("usage_grade")) or "unknown",
            }
        )
    return out


def _normalize_orderbook_active_event_contracts(row: dict[str, Any]) -> list[dict[str, Any]]:
    summary = row.get("orderbook_semantics_summary")
    if not isinstance(summary, dict):
        return []

    raw_rows = summary.get("active_event_contracts")
    if not isinstance(raw_rows, list):
        return []

    out: list[dict[str, Any]] = []
    for item in raw_rows:
        if not isinstance(item, dict):
            continue
        event_name = _safe_str(item.get("event_name"))
        if event_name is None:
            continue
        raw_consumer_allowed = item.get("consumer_allowed")
        consumer_allowed = list(raw_consumer_allowed) if isinstance(raw_consumer_allowed, list) else []

        raw_invalidates_on = item.get("invalidates_on")
        invalidates_on = list(raw_invalidates_on) if isinstance(raw_invalidates_on, list) else []

        raw_evidence_refs = item.get("evidence_refs")
        evidence_refs = list(raw_evidence_refs) if isinstance(raw_evidence_refs, list) else []

        out.append(
            {
                "contract_source": _safe_str(item.get("contract_source")) or "l3_event_usage_policy",
                "event_name": event_name,
                "event_family": _safe_str(item.get("event_family")) or "unknown",
                "usage_grade": _safe_str(item.get("usage_grade")) or "unknown",
                "interpretation_bucket": _safe_str(item.get("interpretation_bucket")),
                "meaning_version": _safe_str(item.get("meaning_version")) or "unknown",
                "confidence": item.get("confidence"),
                "trust_bucket": _safe_str(item.get("trust_bucket")) or "unknown",
                "consumer_allowed": consumer_allowed,
                "actionability": _safe_str(item.get("actionability")) or "unknown",
                "forecast_horizon_hint": _safe_str(item.get("forecast_horizon_hint")) or "unknown",
                "half_life_sec": item.get("half_life_sec"),
                "invalidates_on": invalidates_on,
                "evidence_refs": evidence_refs,
                "side": _safe_str(item.get("side")),
            }
        )
    return out


def _normalize_orderbook_active_event_names(row: dict[str, Any]) -> list[str]:
    summary = row.get("orderbook_semantics_summary")
    if not isinstance(summary, dict):
        return []

    out: list[str] = []

    raw_names = summary.get("active_event_names")
    if isinstance(raw_names, list):
        for item in raw_names:
            name = _safe_str(item)
            if name is not None:
                out.append(name)

    if out:
        return out

    raw_rows = summary.get("active_event_contracts")
    if not isinstance(raw_rows, list):
        return []

    for item in raw_rows:
        if not isinstance(item, dict):
            continue
        name = _safe_str(item.get("event_name"))
        if name is not None:
            out.append(name)

    return out


def _normalize_distribution(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}

    out: dict[str, int] = {}
    for key, raw_value in value.items():
        normalized_key = _safe_str(key)
        if normalized_key is None:
            continue
        try:
            out[normalized_key] = int(raw_value)
        except Exception:
            continue
    return out


def _normalize_semantic_runtime_fields(
    row: dict[str, Any],
    *,
    semantic_usage_contract_rows_count: int,
) -> tuple[
    str,
    str,
    str,
    str,
    bool,
    bool,
    bool,
    int,
    str,
    int,
    int,
    int,
    int,
    dict[str, int],
    dict[str, int],
    dict[str, int],
    dict[str, int],
]:
    summary = row.get("semantic_usage_summary")
    if not isinstance(summary, dict):
        summary = {}

    summary_source = _safe_str(summary.get("source_kind")) or "unknown"
    contract_source = _safe_str(summary.get("contract_source")) or "unknown"
    meaning_version = _safe_str(summary.get("meaning_version")) or "unknown"
    observer_status = (
        _safe_str(row.get("semantic_observer_status"))
        or _safe_str(summary.get("observer_status"))
        or "unknown"
    )

    observer_present = _safe_str(row.get("semantic_observer_status")) is not None
    usage_summary_present = bool(summary)
    contract_rows_present = semantic_usage_contract_rows_count > 0
    contract_rows_count = int(semantic_usage_contract_rows_count)

    if observer_present and usage_summary_present:
        wiring_status = "wired"
    elif semantic_usage_contract_rows_count > 0:
        wiring_status = "partial"
    else:
        wiring_status = "missing"

    total_rows = int(summary.get("total_rows") or semantic_usage_contract_rows_count or 0)
    active_event_count = int(summary.get("active_event_count") or 0)
    mapped_event_count = int(summary.get("mapped_event_count") or 0)
    unknown_event_count = int(summary.get("unknown_event_count") or 0)
    event_family_distribution = _normalize_distribution(summary.get("event_family_distribution"))
    trust_bucket_distribution = _normalize_distribution(summary.get("trust_bucket_distribution"))
    interpretation_bucket_distribution = _normalize_distribution(
        summary.get("interpretation_bucket_distribution")
    )
    consumer_distribution = _normalize_distribution(summary.get("consumer_distribution"))

    return (
        summary_source,
        contract_source,
        meaning_version,
        observer_status,
        observer_present,
        usage_summary_present,
        contract_rows_present,
        contract_rows_count,
        wiring_status,
        total_rows,
        active_event_count,
        mapped_event_count,
        unknown_event_count,
        event_family_distribution,
        trust_bucket_distribution,
        interpretation_bucket_distribution,
        consumer_distribution,
    )


def _normalize_orderbook_summary_slots(row: dict[str, Any]) -> tuple[list[str], int]:
    summary = row.get("orderbook_semantics_summary")
    if not isinstance(summary, dict):
        return [], 0

    canonical_slot_names = (
        "near_wall",
        "support",
        "resistance",
        "persistence",
    )

    raw_slots = summary.get("summary_slots_present")
    if isinstance(raw_slots, list):
        raw_slot_names = {
            str(name).strip()
            for name in raw_slots
            if str(name).strip() in canonical_slot_names
        }
        slots_present = [
            slot_name
            for slot_name in canonical_slot_names
            if slot_name in raw_slot_names
        ]
    else:
        slots_present = [
            slot_name
            for slot_name in canonical_slot_names
            if summary.get(slot_name) is not None
        ]

    return slots_present, len(slots_present)


def _slot_present(slot_name: str, slots_present: list[str]) -> bool:
    return slot_name in set(slots_present)


def _normalize_orderbook_active_event_count(
    row: dict[str, Any],
    *,
    active_event_names_count: int,
    active_event_contracts_count: int,
) -> int:
    summary = row.get("orderbook_semantics_summary")
    if isinstance(summary, dict):
        raw_count = summary.get("active_event_count")
        try:
            return int(raw_count)
        except Exception:
            pass

    return max(active_event_names_count, active_event_contracts_count)


def _normalize_orderbook_wiring_status(
    row: dict[str, Any],
    *,
    summary_slots_count: int,
    active_event_contracts_count: int,
) -> tuple[str, str]:
    explicit_status = _safe_str(row.get("orderbook_semantics_contract_status"))
    inferred_status = "missing"
    if summary_slots_count >= 4:
        inferred_status = "wired"
    elif summary_slots_count > 0 or active_event_contracts_count > 0:
        inferred_status = "partial"

    if explicit_status is None:
        return inferred_status, "orderbook_summary_inference"

    if explicit_status == "missing" and inferred_status in {"partial", "wired"}:
        return inferred_status, "orderbook_summary_inference_overrode_missing"

    return explicit_status, "market_state_orderbook_contract_status"


def _collect_notable_events(
    *,
    freshness: str,
    trust_state: str | None,
    continuity_state: str | None,
    interpretation_bucket: str | None,
) -> list[str]:
    out: list[str] = []

    if freshness == "LIVE":
        out.append("fresh_source")
    elif freshness == "STALE":
        out.append("stale_source")

    if trust_state not in {None, "trusted"}:
        out.append("trust_degraded")

    if continuity_state == "resynced":
        out.append("resync_recent")

    if interpretation_bucket == "observe_only":
        out.append("review_required")
    elif interpretation_bucket == "reanchor_required":
        out.append("unsafe_interpretation")

    return out


def _collect_alert_candidates(
    *,
    freshness: str,
    trust_state: str | None,
    interpretation_bucket: str | None,
) -> list[str]:
    out: list[str] = []

    if freshness == "STALE":
        out.append("stale_market_state")

    if trust_state not in {None, "trusted"}:
        out.append("trust_not_trusted")

    if interpretation_bucket in {"observe_only", "reanchor_required"}:
        out.append("interpretation_review_required")

    if interpretation_bucket == "reanchor_required":
        out.append("reanchor_required")

    return out


def build_market_summary(inp: MarketSummaryBuildInput) -> MarketSummary:
    row = dict(inp.market_state_row or {})
    diagnostics = dict(inp.diagnostics or {})

    event_ts = _pick_event_ts(row)
    age_sec = _safe_float(diagnostics.get("preferred_row_age_sec"))
    if age_sec is None:
        age_sec = _safe_float(diagnostics.get("age_sec"))

    freshness = _resolve_freshness(age_sec)
    if age_sec is None:
        diagnostics_freshness = _safe_str(
            diagnostics.get("preferred_row_freshness") or diagnostics.get("freshness")
        )
        if diagnostics_freshness is not None:
            freshness = diagnostics_freshness

    is_stale = _resolve_is_stale(freshness)

    trust_state = _safe_str(row.get("trust_state"))
    continuity_state = _safe_str(row.get("continuity_state"))
    interpretation_bucket = _safe_str(row.get("interpretation_bucket"))
    interpretation_reason = _safe_str(row.get("interpretation_reason"))

    source_kind = _normalize_source_kind(inp.source_kind or diagnostics.get("source_kind"))
    source_series_id = _safe_str(
        row.get("source_series_id") or diagnostics.get("preferred_row_source_series_id")
    )

    semantic_usage_contract_rows = _normalize_semantic_usage_contract_rows(row)
    (
        semantic_summary_source,
        semantic_contract_source,
        semantic_meaning_version,
        semantic_observer_status,
        semantic_observer_present,
        semantic_usage_summary_present,
        semantic_contract_rows_present,
        semantic_contract_rows_count,
        semantic_runtime_wiring_status,
        semantic_total_rows,
        semantic_active_event_count,
        semantic_mapped_event_count,
        semantic_unknown_event_count,
        semantic_event_family_distribution,
        semantic_trust_bucket_distribution,
        semantic_interpretation_bucket_distribution,
        semantic_consumer_distribution,
    ) = _normalize_semantic_runtime_fields(
        row,
        semantic_usage_contract_rows_count=len(semantic_usage_contract_rows),
    )
    orderbook_active_event_contracts = _normalize_orderbook_active_event_contracts(row)
    orderbook_active_event_names = _normalize_orderbook_active_event_names(row)
    orderbook_active_event_count = _normalize_orderbook_active_event_count(
        row,
        active_event_names_count=len(orderbook_active_event_names),
        active_event_contracts_count=len(orderbook_active_event_contracts),
    )
    (
        orderbook_summary_slots_present,
        orderbook_summary_slots_count,
    ) = _normalize_orderbook_summary_slots(row)
    orderbook_near_wall_present = _slot_present("near_wall", orderbook_summary_slots_present)
    orderbook_support_present = _slot_present("support", orderbook_summary_slots_present)
    orderbook_resistance_present = _slot_present("resistance", orderbook_summary_slots_present)
    orderbook_persistence_present = _slot_present("persistence", orderbook_summary_slots_present)
    (
        orderbook_wiring_status,
        orderbook_contract_status_source,
    ) = _normalize_orderbook_wiring_status(
        row,
        summary_slots_count=orderbook_summary_slots_count,
        active_event_contracts_count=len(orderbook_active_event_contracts),
    )
    orderbook_persistence_observable = bool(row.get("orderbook_persistence_observable"))

    notable_events = _collect_notable_events(
        freshness=freshness,
        trust_state=trust_state,
        continuity_state=continuity_state,
        interpretation_bucket=interpretation_bucket,
    )
    alert_candidates = _collect_alert_candidates(
        freshness=freshness,
        trust_state=trust_state,
        interpretation_bucket=interpretation_bucket,
    )

    return MarketSummary(
        summary_type="market_summary",
        exchange=_safe_str(row.get("exchange")),
        symbol_raw=_safe_str(row.get("symbol_raw") or row.get("symbol")),
        market_uid=_safe_str(row.get("market_uid")),
        source_kind=source_kind,
        source_series_id=source_series_id,
        event_ts=event_ts,
        age_sec=age_sec,
        freshness=freshness,
        is_stale=is_stale,
        trust_state=trust_state,
        continuity_state=continuity_state,
        interpretation_bucket=interpretation_bucket,
        interpretation_reason=interpretation_reason,
        market_state_label=_safe_str(row.get("market_state_label")),
        participation_state=_safe_str(row.get("participation_state")),
        liquidity_bias=_safe_str(row.get("liquidity_bias")),
        semantic_summary_source=semantic_summary_source,
        semantic_contract_source=semantic_contract_source,
        semantic_meaning_version=semantic_meaning_version,
        semantic_observer_status=semantic_observer_status,
        semantic_observer_present=semantic_observer_present,
        semantic_usage_summary_present=semantic_usage_summary_present,
        semantic_contract_rows_present=semantic_contract_rows_present,
        semantic_contract_rows_count=semantic_contract_rows_count,
        semantic_runtime_wiring_status=semantic_runtime_wiring_status,
        semantic_total_rows=semantic_total_rows,
        semantic_active_event_count=semantic_active_event_count,
        semantic_mapped_event_count=semantic_mapped_event_count,
        semantic_unknown_event_count=semantic_unknown_event_count,
        semantic_event_family_distribution=semantic_event_family_distribution,
        semantic_trust_bucket_distribution=semantic_trust_bucket_distribution,
        semantic_interpretation_bucket_distribution=semantic_interpretation_bucket_distribution,
        semantic_consumer_distribution=semantic_consumer_distribution,
        semantic_usage_contract_rows=semantic_usage_contract_rows,
        orderbook_active_event_contracts=orderbook_active_event_contracts,
        orderbook_active_event_names=orderbook_active_event_names,
        orderbook_active_event_count=orderbook_active_event_count,
        orderbook_summary_slots_present=orderbook_summary_slots_present,
        orderbook_summary_slots_count=orderbook_summary_slots_count,
        orderbook_near_wall_present=orderbook_near_wall_present,
        orderbook_support_present=orderbook_support_present,
        orderbook_resistance_present=orderbook_resistance_present,
        orderbook_persistence_present=orderbook_persistence_present,
        orderbook_wiring_status=orderbook_wiring_status,
        orderbook_contract_status_source=orderbook_contract_status_source,
        orderbook_persistence_observable=orderbook_persistence_observable,
        notable_events=notable_events,
        alert_candidates=alert_candidates,
        diagnostics=diagnostics,
    )