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
        notable_events=notable_events,
        alert_candidates=alert_candidates,
        diagnostics=diagnostics,
    )