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


_EVENT_MEANING_VERSION = "l3_event_usage_policy.v1alpha1"

_EVENT_FAMILY_FORECAST_HORIZON_HINT: dict[str, str] = {
    "pressure": "micro",
    "wall": "short",
    "support_resistance": "short",
    "pull": "micro",
    "depth": "short",
    "spread": "micro",
    "sweep": "micro",
    "absorption": "micro",
}

_EVENT_FAMILY_HALF_LIFE_SEC: dict[str, int] = {
    "pressure": 5,
    "wall": 30,
    "support_resistance": 30,
    "pull": 10,
    "depth": 20,
    "spread": 10,
    "sweep": 5,
    "absorption": 5,
}

_USAGE_GRADE_CONFIDENCE: dict[str, float] = {
    "strong": 0.85,
    "watch": 0.55,
    "watch_weak": 0.40,
    "tentative": 0.30,
    "invalid": 0.0,
    "unknown": 0.10,
}


def resolve_confidence(
    interpretation_bucket: str | None,
    event_family: str | None,
) -> float:
    usage_grade = resolve_usage_grade(interpretation_bucket, event_family)
    return float(_USAGE_GRADE_CONFIDENCE.get(usage_grade, 0.10))


def resolve_trust_bucket(trust_state: str | None) -> str:
    state = str(trust_state or "").strip().lower()

    if state == "trusted":
        return "trusted"
    if state in {"provisional", "degraded"}:
        return "degraded"
    if state in {"broken", "quarantined"}:
        return "blocked"

    return "unknown"


def resolve_consumer_allowed(
    interpretation_bucket: str | None,
) -> list[str]:
    bucket = str(interpretation_bucket or "").strip()

    if bucket == "allow_structural_use":
        return ["ui", "alert", "ai", "strategy", "execution"]
    if bucket == "observe_only":
        return ["ui", "alert", "ai"]
    if bucket == "reanchor_required":
        return ["ui", "alert"]

    return ["ui"]


def resolve_actionability(
    interpretation_bucket: str | None,
    event_family: str | None,
) -> str:
    bucket = str(interpretation_bucket or "").strip()
    family = str(event_family or "").strip()

    if bucket == "allow_structural_use":
        return "actionable"
    if bucket == "observe_only":
        if family == "pressure":
            return "observe"
        if family in {"wall", "pull", "support_resistance", "depth", "spread"}:
            return "review"
        if family in {"sweep", "absorption"}:
            return "tentative"
        return "review"
    if bucket == "reanchor_required":
        return "blocked"

    return "unknown"


def resolve_forecast_horizon_hint(event_family: str | None) -> str:
    family = str(event_family or "").strip()
    return str(_EVENT_FAMILY_FORECAST_HORIZON_HINT.get(family, "unknown"))


def resolve_half_life_sec(event_family: str | None) -> int | None:
    family = str(event_family or "").strip()
    return _EVENT_FAMILY_HALF_LIFE_SEC.get(family)


def resolve_invalidates_on(
    interpretation_bucket: str | None,
    event_family: str | None,
) -> list[str]:
    _ = str(event_family or "").strip()
    bucket = str(interpretation_bucket or "").strip()

    out = ["series_boundary", "reanchor_required"]
    if bucket == "reanchor_required":
        out.append("current_row_invalid")

    deduped: list[str] = []
    seen: set[str] = set()
    for item in out:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def build_event_contract_row(
    event_name: str | None,
    interpretation_bucket: str | None,
    *,
    trust_state: str | None = None,
    side: str | None = None,
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    normalized_event_name = str(event_name or "").strip()
    event_family = resolve_event_family(normalized_event_name)
    usage_grade = resolve_usage_grade(interpretation_bucket, event_family)

    refs = list(evidence_refs or [])

    return {
        "event_name": normalized_event_name,
        "event_family": event_family,
        "usage_grade": usage_grade,
        "interpretation_bucket": str(interpretation_bucket or "").strip() or None,
        "meaning_version": _EVENT_MEANING_VERSION,
        "confidence": resolve_confidence(interpretation_bucket, event_family),
        "trust_bucket": resolve_trust_bucket(trust_state),
        "consumer_allowed": resolve_consumer_allowed(interpretation_bucket),
        "actionability": resolve_actionability(interpretation_bucket, event_family),
        "forecast_horizon_hint": resolve_forecast_horizon_hint(event_family),
        "half_life_sec": resolve_half_life_sec(event_family),
        "invalidates_on": resolve_invalidates_on(interpretation_bucket, event_family),
        "evidence_refs": refs,
        "side": side,
    }


def enrich_event_contract(event: dict[str, Any]) -> dict[str, Any]:
    out = dict(event)
    out["event_family"] = resolve_event_family(str(out.get("event_name") or ""))
    return out


def enrich_event_contracts(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [enrich_event_contract(event) for event in events]


def enrich_event_contract_for_bucket(
    event: dict[str, Any],
    interpretation_bucket: str | None,
    trust_state: str | None = None,
) -> dict[str, Any]:
    out = dict(event)
    event_name = str(out.get("event_name") or "").strip()
    side = out.get("side")
    raw_refs = out.get("evidence_refs")
    evidence_refs = list(raw_refs) if isinstance(raw_refs, list) else None

    contract_row = build_event_contract_row(
        event_name,
        interpretation_bucket,
        trust_state=trust_state,
        side=side,
        evidence_refs=evidence_refs,
    )
    out.update(contract_row)
    return out


def enrich_event_contracts_for_bucket(
    events: list[dict[str, Any]],
    interpretation_bucket: str | None,
    trust_state: str | None = None,
) -> list[dict[str, Any]]:
    return [
        enrich_event_contract_for_bucket(
            event,
            interpretation_bucket,
            trust_state=trust_state,
        )
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
                "meaning_version": _EVENT_MEANING_VERSION,
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


def _summarize_event_name_mapping(
    event_names: list[str] | None,
) -> dict[str, Any]:
    names = [str(name).strip() for name in (event_names or []) if str(name).strip()]

    family_distribution: dict[str, int] = {}
    unknown_event_count = 0

    for name in names:
        family = resolve_event_family(name)
        family_distribution[family] = family_distribution.get(family, 0) + 1
        if family == "unknown":
            unknown_event_count += 1

    mapped_event_count = len(names) - unknown_event_count

    return {
        "active_event_count": len(names),
        "mapped_event_count": mapped_event_count,
        "unknown_event_count": unknown_event_count,
        "event_family_distribution": family_distribution,
    }


def _distribution_counts(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return counts


def _summarize_active_event_contracts(
    active_event_contracts: list[dict[str, Any]] | None,
) -> dict[str, dict[str, int]]:
    rows = active_event_contracts or []

    trust_buckets = [
        str(row.get("trust_bucket") or "").strip()
        for row in rows
        if isinstance(row, dict)
    ]
    interpretation_buckets = [
        str(row.get("interpretation_bucket") or "").strip()
        for row in rows
        if isinstance(row, dict)
    ]

    consumer_values = [
        str(consumer).strip()
        for row in rows
        if isinstance(row, dict)
        for consumer in (row.get("consumer_allowed") or [])
        if str(consumer).strip()
    ]

    return {
        "trust_bucket_distribution": _distribution_counts(trust_buckets),
        "interpretation_bucket_distribution": _distribution_counts(
            interpretation_buckets
        ),
        "consumer_distribution": _distribution_counts(consumer_values),
    }


def build_event_usage_summary(
    interpretation_bucket: str | None,
    *,
    event_families: list[str] | None = None,
    event_names: list[str] | None = None,
    active_event_contracts: list[dict[str, Any]] | None = None,
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
    mapping_summary = _summarize_event_name_mapping(event_names)
    contract_summary = _summarize_active_event_contracts(active_event_contracts)

    return {
        "interpretation_bucket": bucket,
        "contract_source": "l3_event_usage_policy",
        "meaning_version": _EVENT_MEANING_VERSION,
        "observer_status": resolve_semantic_observer_status(bucket),
        "event_families": families,
        "total_rows": len(families),
        "active_event_count": mapping_summary["active_event_count"],
        "mapped_event_count": mapping_summary["mapped_event_count"],
        "unknown_event_count": mapping_summary["unknown_event_count"],
        "event_family_distribution": mapping_summary["event_family_distribution"],
        "trust_bucket_distribution": contract_summary["trust_bucket_distribution"],
        "interpretation_bucket_distribution": contract_summary[
            "interpretation_bucket_distribution"
        ],
        "consumer_distribution": contract_summary["consumer_distribution"],
        "strong_count": counts.get("strong", 0),
        "watch_count": counts.get("watch", 0),
        "watch_weak_count": counts.get("watch_weak", 0),
        "tentative_count": counts.get("tentative", 0),
        "invalid_count": counts.get("invalid", 0),
        "unknown_count": counts.get("unknown", 0),
    }