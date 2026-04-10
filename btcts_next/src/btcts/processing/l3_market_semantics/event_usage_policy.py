# path: ./btcts_next/src/btcts/processing/l3_market_semantics/event_usage_policy.py
# desc: Minimal L3 event usage policy and event-family enrichment helpers.

from __future__ import annotations

from typing import Any


_EVENT_NAME_TO_FAMILY: dict[str, str] = {
    "pressure_shift": "pressure",
    "imbalance_flip_to_bid": "pressure",
    "imbalance_flip_to_ask": "pressure",
    "wall_created": "wall",
    "wall_removed": "wall",
    "wall_side_shift": "wall",
    "near_wall_created": "wall",
    "near_wall_removed": "wall",
    "near_wall_continued": "wall",
    "wall_strengthened": "wall",
    "wall_weakened": "wall",
    "support_candidate": "support_resistance",
    "resistance_candidate": "support_resistance",
    "support_continued": "support_resistance",
    "resistance_continued": "support_resistance",
    "bid_liquidity_pulled": "pull",
    "ask_liquidity_pulled": "pull",
    "sweep_candidate": "sweep",
    "absorption_candidate": "absorption",
    "bid_liquidity_added": "depth",
    "bid_liquidity_removed": "depth",
    "ask_liquidity_added": "depth",
    "ask_liquidity_removed": "depth",
    "spread_expansion": "spread",
    "spread_compression": "spread",
}


def resolve_event_family(event_name: str | None) -> str:
    if event_name is None:
        return "unknown"

    text = str(event_name).strip()
    if not text:
        return "unknown"

    return _EVENT_NAME_TO_FAMILY.get(text, "unknown")


def resolve_usage_grade(
    interpretation_bucket: str | None,
    event_family: str | None,
) -> str:
    bucket = str(interpretation_bucket or "").strip()
    family = str(event_family or "").strip()

    if bucket == "allow_structural_use":
        return "strong"

    if bucket == "observe_only":
        if family == "pressure":
            return "watch_weak"
        if family in {"wall", "pull", "support_resistance", "depth", "spread"}:
            return "watch"
        if family in {"sweep", "absorption"}:
            return "tentative"
        return "watch"

    if bucket == "reanchor_required":
        return "invalid"

    return "unknown"


def enrich_event_contract(event: dict[str, Any]) -> dict[str, Any]:
    out = dict(event)
    out["event_family"] = resolve_event_family(str(out.get("event_name") or ""))
    return out


def enrich_event_contracts(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [enrich_event_contract(event) for event in events]


def enrich_event_contract_for_bucket(
    event: dict[str, Any],
    interpretation_bucket: str | None,
) -> dict[str, Any]:
    out = enrich_event_contract(event)
    out["usage_grade"] = resolve_usage_grade(
        interpretation_bucket,
        str(out.get("event_family") or ""),
    )
    return out


def enrich_event_contracts_for_bucket(
    events: list[dict[str, Any]],
    interpretation_bucket: str | None,
) -> list[dict[str, Any]]:
    return [
        enrich_event_contract_for_bucket(event, interpretation_bucket)
        for event in events
    ]


_DEFAULT_EVENT_FAMILIES: list[str] = [
    "pressure",
    "wall",
    "support_resistance",
    "pull",
    "depth",
    "spread",
    "sweep",
    "absorption",
]


def build_event_usage_contract_rows(
    interpretation_bucket: str | None,
    *,
    event_families: list[str] | None = None,
) -> list[dict[str, Any]]:
    families = list(event_families or _DEFAULT_EVENT_FAMILIES)
    rows: list[dict[str, Any]] = []

    for event_family in families:
        rows.append(
            {
                "event_family": str(event_family),
                "usage_grade": resolve_usage_grade(interpretation_bucket, event_family),
            }
        )

    return rows


def resolve_semantic_observer_status(interpretation_bucket: str | None) -> str:
    bucket = str(interpretation_bucket or "").strip()

    if bucket == "allow_structural_use":
        return "healthy"
    if bucket == "observe_only":
        return "caution"
    if bucket == "reanchor_required":
        return "broken"
    return "unknown"


def build_event_usage_summary(
    interpretation_bucket: str | None,
    *,
    event_families: list[str] | None = None,
) -> dict[str, Any]:
    families = list(event_families or _DEFAULT_EVENT_FAMILIES)
    counts = {
        "strong": 0,
        "watch": 0,
        "watch_weak": 0,
        "tentative": 0,
        "invalid": 0,
        "unknown": 0,
    }

    for event_family in families:
        grade = resolve_usage_grade(interpretation_bucket, event_family)
        counts[grade] = counts.get(grade, 0) + 1

    bucket = str(interpretation_bucket or "").strip() or None

    return {
        "interpretation_bucket": bucket,
        "observer_status": resolve_semantic_observer_status(bucket),
        "event_families": families,
        "total_rows": len(families),
        "strong_count": counts.get("strong", 0),
        "watch_count": counts.get("watch", 0),
        "watch_weak_count": counts.get("watch_weak", 0),
        "tentative_count": counts.get("tentative", 0),
        "invalid_count": counts.get("invalid", 0),
        "unknown_count": counts.get("unknown", 0),
    }