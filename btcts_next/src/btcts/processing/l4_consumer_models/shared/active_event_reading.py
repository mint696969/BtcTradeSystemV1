# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/active_event_reading.py
# desc: Wording-free compact active-event reading rows for L4 consumer bundles.

from __future__ import annotations

from typing import Any

from btcts.processing.l4_consumer_models.shared._value_utils import safe_str


ACTIVE_EVENT_STABLE_KEYS = (
    "contract_source",
    "event_name",
    "event_family",
    "meaning_version",
    "usage_grade",
    "interpretation_bucket",
    "trust_bucket",
    "actionability",
    "forecast_horizon_hint",
    "half_life_sec",
    "side",
)


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def _normalize_active_event_compact_row(
    row: dict[str, Any],
) -> dict[str, Any] | None:
    event_name = safe_str(row.get("event_name"))
    if event_name is None:
        return None

    return {
        "contract_source": safe_str(row.get("contract_source")) or "unknown",
        "event_name": event_name,
        "event_family": safe_str(row.get("event_family")) or "unknown",
        "meaning_version": safe_str(row.get("meaning_version")) or "unknown",
        "usage_grade": safe_str(row.get("usage_grade")) or "unknown",
        "interpretation_bucket": safe_str(row.get("interpretation_bucket")) or "unknown",
        "trust_bucket": safe_str(row.get("trust_bucket")) or "unknown",
        "actionability": safe_str(row.get("actionability")) or "unknown",
        "forecast_horizon_hint": safe_str(row.get("forecast_horizon_hint")) or "unknown",
        "half_life_sec": _safe_int(row.get("half_life_sec")),
        "side": safe_str(row.get("side")) or "unknown",
    }


def build_active_event_compact_rows(
    rows: Any,
) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []

    out: list[dict[str, Any]] = []
    for item in rows:
        if not isinstance(item, dict):
            continue

        normalized = _normalize_active_event_compact_row(item)
        if normalized is not None:
            out.append(normalized)

    return out