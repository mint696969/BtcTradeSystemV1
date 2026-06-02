# path: ./btcts_next/src/btcts/apps/operator_ui/health_data_service.py
# desc: Operator UI Health タブ向けに collector / audit / market_state を統合し、短期監視用の時系列を返す。

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btcts.apps.operator_ui.collector_state_service import load_state
from btcts.apps.operator_ui.health_ranges import (
    HEALTH_RANGE_PRESETS,
    bucket_end,
    bucket_floor,
    display_buckets,
    range_config,
    time_buckets,
)
from btcts.apps.operator_ui.health_truth import (
    age_seconds_from_ts,
    api_current_truth,
    parse_ts,
    ws_current_truth,
)
from btcts.apps.operator_ui.market_state_service import (
    load_latest_market_state,
    market_state_diagnostics,
)
from btcts.apps.operator_ui.hot_cold_retention_safety_service import (
    load_hot_cold_retention_safety_payload,
)
from btcts.core import io
from btcts.core import paths as core_paths
from btcts.processing.l3_market_semantics import (
    build_event_usage_contract_rows,
    build_event_usage_summary,
)
from btcts.processing.l4_consumer_models.shared import (
    HealthDigestBuildInput,
    build_health_digest,
)


def _audit_log_path() -> Path:
    return core_paths.logs_dir(ensure=False) / "audit.jsonl"


def _read_recent_audit_rows(*, max_lines: int = 4000) -> list[dict[str, Any]]:
    path = _audit_log_path()
    return io.read_jsonl_tail(path, max_lines=max_lines)


def _audit_max_lines_for_range(range_key: str) -> int:
    if range_key == "1h":
        return 50000
    if range_key == "24h":
        return 120000
    if range_key == "1w":
        return 240000
    return 50000


def _audit_coverage_meta(
    *,
    rows: list[dict[str, Any]],
    oldest_bucket: datetime,
) -> dict[str, Any]:
    earliest_ts: datetime | None = None

    for row in rows:
        dt = parse_ts(row.get("ts"))
        if dt is None:
            continue
        dt_utc = dt.astimezone(timezone.utc)
        if earliest_ts is None or dt_utc < earliest_ts:
            earliest_ts = dt_utc

    coverage_complete = earliest_ts is not None and earliest_ts <= oldest_bucket
    coverage_warning = None
    if not coverage_complete:
        coverage_warning = "audit_tail_did_not_cover_full_window"

    return {
        "coverage_complete": coverage_complete,
        "coverage_warning": coverage_warning,
        "coverage_oldest_available_ts": (
            earliest_ts.isoformat().replace("+00:00", "Z")
            if earliest_ts is not None
            else None
        ),
        "coverage_window_start_ts": oldest_bucket.isoformat().replace("+00:00", "Z"),
    }


def _api_chart_spec(range_key: str) -> dict[str, Any]:
    if range_key == "1h":
        return {
            "metric_mode": "short",
            "chart_fields": [
                "api_events",
                "api_rolling_5m",
                "api_limit_5m",
                "events_429_marker",
            ],
            "chart_label_keys": {
                "api_events": "health_chart_api_events",
                "api_rolling_5m": "health_chart_api_rolling_5m",
                "api_limit_5m": "health_chart_api_limit_5m",
                "events_429_marker": "health_chart_429_events",
            },
        }

    return {
        "metric_mode": "long",
        "chart_fields": [
            "api_events",
            "warn_error_events",
            "events_429",
        ],
        "chart_label_keys": {
            "api_events": "health_chart_api_events",
            "warn_error_events": "health_chart_warn_error_events",
            "events_429": "health_chart_429_events",
        },
    }


def _classify_row(row: dict[str, Any]) -> dict[str, bool]:
    event = str(row.get("event") or "").lower()
    payload = row.get("payload") or {}
    topic = str(payload.get("topic") or "").lower()
    provider = str(payload.get("provider") or "").lower()
    reason = str(payload.get("reason") or "").lower()
    error = str(payload.get("error") or "").lower()

    text = " ".join([event, topic, provider, reason, error])

    is_exploration = event.startswith("collector_vnext.exploration.")
    is_unified = event.startswith("collector_vnext.unified.")
    is_unified_ws = event.startswith("collector_vnext.unified.ws_board.") or event.startswith(
        "collector_vnext.unified.ws_executions."
    )
    is_exploration_ws = event.startswith("collector_vnext.exploration.ws.")
    is_rest = (
        ("rest" in text)
        or ("http" in text)
        or (is_exploration and not is_exploration_ws)
        or (is_unified and not is_unified_ws)
    )
    is_ws = ("ws" in text) or ("websocket" in text) or is_unified_ws or is_exploration_ws
    is_429 = "429" in text or "retry_after" in text
    is_gap = "gap" in text
    is_resync = "resync" in text
    is_warn_or_error = any(word in text for word in ["warn", "error", "failed", "exception"])
    is_ws_exec = (
        "ws_executions" in text
        or "executions_ws" in text
        or event.startswith("collector_vnext.unified.ws_executions.")
    )
    is_rate_mode = (is_exploration or is_unified) and (
        event.endswith(".mode.changed")
        or any(word in text for word in ["crit", "recovery", "throttle", "utilization"])
    )

    return {
        "is_rest": is_rest,
        "is_ws": is_ws,
        "is_ws_exec": is_ws_exec,
        "is_429": is_429,
        "is_gap": is_gap,
        "is_resync": is_resync,
        "is_warn_or_error": is_warn_or_error,
        "is_rate_mode": is_rate_mode,
    }


def build_recent_api_ws_series(
    *,
    range_key: str = "1h",
    include_in_progress: bool = False,
    audit_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    cfg = range_config(range_key)
    window_minutes = int(cfg["window_minutes"])
    bucket_minutes = int(cfg["bucket_minutes"])

    buckets = time_buckets(window_minutes, bucket_minutes)
    target_buckets = display_buckets(buckets, include_in_progress=include_in_progress)
    rows = (
        list(audit_rows)
        if audit_rows is not None
        else _read_recent_audit_rows(
            max_lines=_audit_max_lines_for_range(range_key)
        )
    )

    per_bucket: dict[datetime, dict[str, float]] = defaultdict(
        lambda: {
            "api_events": 0.0,
            "ws_events": 0.0,
            "ws_exec_events": 0.0,
            "events_429": 0.0,
            "gap_events": 0.0,
            "resync_events": 0.0,
            "warn_error_events": 0.0,
            "latency_ms_sum": 0.0,
            "latency_ms_count": 0.0,
        }
    )

    bucket_set = set(buckets)
    oldest = buckets[0]

    coverage_meta = _audit_coverage_meta(
        rows=rows,
        oldest_bucket=oldest,
    )

    for row in rows:
        dt = parse_ts(row.get("ts"))
        if dt is None:
            continue
        dt_utc = dt.astimezone(timezone.utc)
        if dt_utc < oldest:
            continue

        bucket = bucket_floor(dt_utc, bucket_minutes)
        if bucket not in bucket_set:
            continue

        flags = _classify_row(row)
        payload = row.get("payload") or {}

        if flags["is_rest"]:
            per_bucket[bucket]["api_events"] += 1.0
        if flags["is_ws"]:
            per_bucket[bucket]["ws_events"] += 1.0
        if flags["is_ws_exec"]:
            per_bucket[bucket]["ws_exec_events"] += 1.0
        if flags["is_429"]:
            per_bucket[bucket]["events_429"] += 1.0
        if flags["is_gap"]:
            per_bucket[bucket]["gap_events"] += 1.0
        if flags["is_resync"]:
            per_bucket[bucket]["resync_events"] += 1.0
        if flags["is_warn_or_error"] or flags["is_rate_mode"]:
            per_bucket[bucket]["warn_error_events"] += 1.0

        elapsed_ms = payload.get("elapsed_ms")
        if elapsed_ms is not None:
            try:
                per_bucket[bucket]["latency_ms_sum"] += float(elapsed_ms)
                per_bucket[bucket]["latency_ms_count"] += 1.0
            except Exception:
                pass

    chart_spec = _api_chart_spec(range_key)

    out: list[dict[str, Any]] = []
    api_event_history: list[float] = []

    for bucket in target_buckets:
        item = dict(per_bucket[bucket])

        avg_latency = None
        if item["latency_ms_count"] > 0:
            avg_latency = item["latency_ms_sum"] / item["latency_ms_count"]

        api_events = float(item["api_events"])
        api_event_history.append(api_events)

        buckets_per_5m = max(1, int(5 / bucket_minutes)) if bucket_minutes <= 5 else 1
        api_rolling_5m = sum(api_event_history[-buckets_per_5m:])

        out.append(
            {
                "ts": bucket.isoformat().replace("+00:00", "Z"),
                "start_ts": bucket.isoformat().replace("+00:00", "Z"),
                "end_ts": bucket_end(bucket, bucket_minutes).isoformat().replace("+00:00", "Z"),
                "range_key": range_key,
                "bucket_minutes": bucket_minutes,
                "in_progress": False,
                "source_kind": "audit_activity_series",
                "api_metric_mode": chart_spec["metric_mode"],
                "api_chart_fields": list(chart_spec["chart_fields"]),
                "api_events": api_events,
                "api_rolling_5m": api_rolling_5m,
                "api_limit_5m": 500.0,
                "events_429": item["events_429"],
                "events_429_marker": 500.0 if item["events_429"] > 0 else None,
                "ws_events": item["ws_events"],
                "ws_exec_events": item["ws_exec_events"],
                "gap_events": item["gap_events"],
                "resync_events": item["resync_events"],
                "warn_error_events": item["warn_error_events"],
                "avg_latency_ms": avg_latency,
                "coverage_complete": coverage_meta["coverage_complete"],
                "coverage_warning": coverage_meta["coverage_warning"],
                "coverage_oldest_available_ts": coverage_meta["coverage_oldest_available_ts"],
                "coverage_window_start_ts": coverage_meta["coverage_window_start_ts"],
            }
        )

    return out


def build_rate_limit_overlay(
    *,
    range_key: str = "1h",
    include_in_progress: bool = False,
) -> list[dict[str, Any]]:
    state = load_state()
    rate_items = (state.get("rate") or {}).get("items") or {}
    bitflyer = rate_items.get("bitflyer") or {}
    rate_domains = (bitflyer.get("domains") or {}) if isinstance(bitflyer, dict) else {}
    market_data_rate = (rate_domains.get("market_data") or {}) if isinstance(rate_domains, dict) else {}
    rate_view = market_data_rate or bitflyer

    budget = rate_view.get("budget") or {}
    budget_60s = budget.get("budget_60s")
    budget_300s = budget.get("budget_300s")

    requests_60s = rate_view.get("requests_60s")
    requests_300s = rate_view.get("requests_300s")
    utilization = rate_view.get("utilization")
    active_target_ratio = rate_view.get("active_target_ratio")
    target_utilization = rate_view.get("target_utilization")
    hard_cap_utilization = rate_view.get("hard_cap_utilization")

    cfg = range_config(range_key)
    window_minutes = int(cfg["window_minutes"])
    bucket_minutes = int(cfg["bucket_minutes"])

    buckets = time_buckets(window_minutes, bucket_minutes)
    target_buckets = display_buckets(buckets, include_in_progress=include_in_progress)

    out: list[dict[str, Any]] = []

    for bucket in target_buckets:
        out.append(
            {
                "ts": bucket.isoformat().replace("+00:00", "Z"),
                "start_ts": bucket.isoformat().replace("+00:00", "Z"),
                "end_ts": bucket_end(bucket, bucket_minutes).isoformat().replace("+00:00", "Z"),
                "range_key": range_key,
                "bucket_minutes": bucket_minutes,
                "in_progress": False,
                "source_kind": "rate_state_overlay",
                "budget_60s": budget_60s,
                "budget_300s": budget_300s,
                "requests_60s": requests_60s,
                "requests_300s": requests_300s,
                "utilization": utilization,
                "active_target_ratio": active_target_ratio,
                "target_utilization": target_utilization,
                "hard_cap_utilization": hard_cap_utilization,
            }
        )

    return out


def build_recent_layer3_series(
    *,
    range_key: str = "1h",
    include_in_progress: bool = False,
) -> list[dict[str, Any]]:
    latest = load_latest_market_state()
    diagnostics = market_state_diagnostics()

    trust_state = str(latest.get("trust_state") or diagnostics.get("preferred_row_trust_state") or "")
    continuity_state = str(
        latest.get("continuity_state") or diagnostics.get("preferred_row_continuity_state") or ""
    )
    interpretation_bucket = str(
        latest.get("interpretation_bucket")
        or diagnostics.get("preferred_row_interpretation_bucket")
        or ""
    )
    freshness = str(diagnostics.get("preferred_row_freshness") or "UNKNOWN")

    trust_score = 0
    if trust_state == "trusted":
        trust_score = 2
    elif trust_state in {"provisional", "broken", "quarantined"}:
        trust_score = 0
    elif trust_state:
        trust_score = 1

    continuity_score = 2 if continuity_state == "continuous" else 0
    interpretation_score = 2 if interpretation_bucket == "allow_structural_use" else 0
    freshness_score = {"LIVE": 2, "QUIET": 1, "STALE": 0}.get(freshness, 0)

    cfg = range_config(range_key)
    window_minutes = int(cfg["window_minutes"])
    bucket_minutes = int(cfg["bucket_minutes"])

    buckets = time_buckets(window_minutes, bucket_minutes)
    target_buckets = display_buckets(buckets, include_in_progress=include_in_progress)

    out: list[dict[str, Any]] = []

    for bucket in target_buckets:
        out.append(
            {
                "ts": bucket.isoformat().replace("+00:00", "Z"),
                "start_ts": bucket.isoformat().replace("+00:00", "Z"),
                "end_ts": bucket_end(bucket, bucket_minutes).isoformat().replace("+00:00", "Z"),
                "range_key": range_key,
                "bucket_minutes": bucket_minutes,
                "in_progress": False,
                "source_kind": "market_state_snapshot_overlay",
                "trust_score": trust_score,
                "continuity_score": continuity_score,
                "interpretation_score": interpretation_score,
                "freshness_score": freshness_score,
            }
        )

    return out



def build_layer3_semantic_usage_rows(
    *,
    interpretation_bucket: str | None,
    market_latest: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    bucket = str(interpretation_bucket or "").strip() or None
    latest = dict(market_latest or {})
    default_meaning_version = str(
        build_event_usage_summary(bucket).get("meaning_version") or "unknown"
    )

    live_rows = latest.get("semantic_usage_contract_rows")
    if isinstance(live_rows, list) and live_rows:
        out: list[dict[str, Any]] = []
        for row in live_rows:
            if not isinstance(row, dict):
                continue
            event_family = str(row.get("event_family") or "").strip()
            if not event_family:
                continue
            out.append(
                {
                    "source_kind": "market_state_semantic_usage_contract_rows",
                    "contract_source": str(row.get("contract_source") or "l3_event_usage_policy"),
                    "interpretation_bucket": str(
                        row.get("interpretation_bucket")
                        or bucket
                        or ""
                    ).strip() or None,
                    "meaning_version": str(
                        row.get("meaning_version") or default_meaning_version
                    ),
                    "event_family": event_family,
                    "usage_grade": str(row.get("usage_grade") or "unknown"),
                }
            )
        if out:
            return out

    return [
        {
            "source_kind": "layer3_semantic_usage_observer",
            "contract_source": str(
                row.get("contract_source") or "l3_event_usage_policy"
            ),
            "interpretation_bucket": (
                str(row.get("interpretation_bucket") or bucket or "").strip() or None
            ),
            "meaning_version": str(
                row.get("meaning_version") or default_meaning_version
            ),
            "event_family": str(row.get("event_family") or ""),
            "usage_grade": str(row.get("usage_grade") or "unknown"),
        }
        for row in build_event_usage_contract_rows(bucket)
    ]



def build_layer3_semantic_usage_summary(
    *,
    interpretation_bucket: str | None,
    market_latest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    latest = dict(market_latest or {})
    latest_summary = latest.get("semantic_usage_summary")
    latest_observer_status = latest.get("semantic_observer_status")
    default_meaning_version = str(
        build_event_usage_summary(interpretation_bucket).get("meaning_version")
        or "unknown"
    )

    if isinstance(latest_summary, dict) and latest_summary:
        return {
            "source_kind": "market_state_semantic_usage_summary",
            **latest_summary,
            "meaning_version": str(
                latest_summary.get("meaning_version") or default_meaning_version
            ),
            "observer_status": (
                latest_observer_status
                or latest_summary.get("observer_status")
                or "unknown"
            ),
        }

    summary = build_event_usage_summary(
        interpretation_bucket,
    )
    return {
        "source_kind": "layer3_semantic_usage_summary",
        **summary,
    }


def build_layer3_runtime_contract_summary(
    *,
    market_latest: dict[str, Any] | None = None,
    market_diag: dict[str, Any] | None = None,
    semantic_usage_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    latest = dict(market_latest or {})
    diag = dict(market_diag or {})
    semantic_summary = dict(semantic_usage_summary or {})

    observer_present = latest.get("semantic_observer_status") is not None
    usage_summary_present = isinstance(latest.get("semantic_usage_summary"), dict) and bool(
        latest.get("semantic_usage_summary")
    )

    contract_rows = latest.get("semantic_usage_contract_rows")
    contract_rows_present = isinstance(contract_rows, list) and bool(contract_rows)
    contract_rows_count = len(contract_rows) if isinstance(contract_rows, list) else 0

    source_series_present = bool(latest.get("source_series_id"))
    freshness = str(diag.get("preferred_row_freshness") or "UNKNOWN")

    wiring_status = "missing"
    if observer_present and usage_summary_present:
        wiring_status = "wired"
    elif contract_rows_present or source_series_present:
        wiring_status = "partial"
    elif semantic_summary.get("source_kind") == "layer3_semantic_usage_summary":
        wiring_status = "fallback"

    return {
        "source_kind": "layer3_runtime_contract_summary",
        "wiring_status": wiring_status,
        "observer_present": observer_present,
        "usage_summary_present": usage_summary_present,
        "contract_rows_present": contract_rows_present,
        "contract_rows_count": contract_rows_count,
        "source_series_present": source_series_present,
        "freshness": freshness,
        "semantic_summary_source": str(semantic_summary.get("source_kind") or "unknown"),
    }


def build_layer3_orderbook_runtime_summary(
    *,
    market_latest: dict[str, Any] | None = None,
    market_diag: dict[str, Any] | None = None,
) -> dict[str, Any]:
    latest = dict(market_latest or {})
    diag = dict(market_diag or {})

    semantics_summary = latest.get("orderbook_semantics_summary")
    if not isinstance(semantics_summary, dict):
        semantics_summary = {}

    near_wall_present = bool(semantics_summary.get("near_wall"))
    support_present = bool(semantics_summary.get("support"))
    resistance_present = bool(semantics_summary.get("resistance"))
    persistence_present = bool(semantics_summary.get("persistence"))

    canonical_summary_slots = (
        "near_wall",
        "support",
        "resistance",
        "persistence",
    )
    inferred_summary_slots_present = [
        slot_name
        for slot_name, slot_present in (
            ("near_wall", near_wall_present),
            ("support", support_present),
            ("resistance", resistance_present),
            ("persistence", persistence_present),
        )
        if slot_present
    ]

    raw_summary_slots_present = semantics_summary.get("summary_slots_present")
    if isinstance(raw_summary_slots_present, list):
        raw_slot_names = {
            str(name).strip()
            for name in raw_summary_slots_present
            if str(name).strip() in canonical_summary_slots
        }
        summary_slots_present = [
            slot_name for slot_name in canonical_summary_slots if slot_name in raw_slot_names
        ]
    else:
        summary_slots_present = list(inferred_summary_slots_present)

    if not summary_slots_present:
        summary_slots_present = list(inferred_summary_slots_present)

    summary_slots_count = int(semantics_summary.get("summary_slots_count") or len(summary_slots_present))
    present_count = len(summary_slots_present)

    explicit_contract_status = str(latest.get("orderbook_semantics_contract_status") or "").strip()
    contract_status_source = "market_state_orderbook_contract_status"

    active_event_names = semantics_summary.get("active_event_names")
    if not isinstance(active_event_names, list):
        active_event_names = []
    active_event_names = [str(name) for name in active_event_names if str(name).strip()]

    active_event_contracts = semantics_summary.get("active_event_contracts")
    if not isinstance(active_event_contracts, list):
        active_event_contracts = []

    normalized_active_event_contracts: list[dict[str, Any]] = []
    for event in active_event_contracts:
        if not isinstance(event, dict):
            continue
        event_name = str(event.get("event_name") or "").strip()
        if not event_name:
            continue
        raw_consumer_allowed = event.get("consumer_allowed")
        consumer_allowed = list(raw_consumer_allowed) if isinstance(raw_consumer_allowed, list) else []

        raw_invalidates_on = event.get("invalidates_on")
        invalidates_on = list(raw_invalidates_on) if isinstance(raw_invalidates_on, list) else []

        raw_evidence_refs = event.get("evidence_refs")
        evidence_refs = list(raw_evidence_refs) if isinstance(raw_evidence_refs, list) else []

        normalized_active_event_contracts.append(
            {
                "contract_source": str(event.get("contract_source") or "l3_event_usage_policy"),
                "event_name": event_name,
                "event_family": str(event.get("event_family") or "unknown"),
                "usage_grade": str(event.get("usage_grade") or "unknown"),
                "interpretation_bucket": str(event.get("interpretation_bucket") or "").strip() or None,
                "meaning_version": str(event.get("meaning_version") or "unknown"),
                "confidence": event.get("confidence"),
                "trust_bucket": str(event.get("trust_bucket") or "unknown"),
                "consumer_allowed": consumer_allowed,
                "actionability": str(event.get("actionability") or "unknown"),
                "forecast_horizon_hint": str(event.get("forecast_horizon_hint") or "unknown"),
                "half_life_sec": event.get("half_life_sec"),
                "invalidates_on": invalidates_on,
                "evidence_refs": evidence_refs,
                "side": event.get("side"),
            }
        )

    if not active_event_names:
        active_event_names = [
            str(event.get("event_name"))
            for event in normalized_active_event_contracts
            if str(event.get("event_name") or "").strip()
        ]

    active_event_count = int(
        semantics_summary.get("active_event_count")
        or len(normalized_active_event_contracts)
        or len(active_event_names)
    )

    inferred_wiring_status = "missing"
    if present_count >= 4:
        inferred_wiring_status = "wired"
    elif present_count > 0 or active_event_count > 0:
        inferred_wiring_status = "partial"

    wiring_status = explicit_contract_status
    if not wiring_status:
        contract_status_source = "orderbook_summary_inference"
        wiring_status = inferred_wiring_status
    elif explicit_contract_status == "missing" and inferred_wiring_status in {"partial", "wired"}:
        contract_status_source = "orderbook_summary_inference_overrode_missing"
        wiring_status = inferred_wiring_status

    return {
        "source_kind": "layer3_orderbook_runtime_summary",
        "contract_status_source": contract_status_source,
        "wiring_status": wiring_status,
        "freshness": str(diag.get("preferred_row_freshness") or "UNKNOWN"),
        "near_wall_present": near_wall_present,
        "near_wall_side": (semantics_summary.get("near_wall") or {}).get("side"),
        "support_present": support_present,
        "support_side": (semantics_summary.get("support") or {}).get("side"),
        "resistance_present": resistance_present,
        "resistance_side": (semantics_summary.get("resistance") or {}).get("side"),
        "persistence_present": persistence_present,
        "persistence_event_name": (semantics_summary.get("persistence") or {}).get("event_name"),
        "persistence_side": (semantics_summary.get("persistence") or {}).get("side"),
        "persistence_observable": bool(latest.get("orderbook_persistence_observable")),
        "present_count": present_count,
        "summary_slots_count": summary_slots_count,
        "summary_slots_present": summary_slots_present,
        "active_event_count": active_event_count,
        "active_event_names": active_event_names,
        "active_event_contracts": normalized_active_event_contracts,
    }


def _build_continuity_rail(
    *,
    range_key: str,
    row_specs: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    rows = (
        list(audit_rows)
        if audit_rows is not None
        else _read_recent_audit_rows(
            max_lines=_audit_max_lines_for_range(range_key)
        )
    )

    cfg = range_config(range_key)
    window_minutes = int(cfg["window_minutes"])
    bucket_minutes = int(cfg["bucket_minutes"])

    buckets = time_buckets(window_minutes, bucket_minutes)
    target_buckets = display_buckets(buckets, include_in_progress=False)

    per_bucket: dict[datetime, dict[str, float]] = defaultdict(
        lambda: {
            "api_events": 0.0,
            "ws_events": 0.0,
            "ws_exec_events": 0.0,
            "gap_events": 0.0,
            "resync_events": 0.0,
            "warn_error_events": 0.0,
        }
    )

    bucket_set = set(buckets)
    oldest = buckets[0]

    coverage_meta = _audit_coverage_meta(
        rows=rows,
        oldest_bucket=oldest,
    )

    for row in rows:
        dt = parse_ts(row.get("ts"))
        if dt is None:
            continue

        dt_utc = dt.astimezone(timezone.utc)
        if dt_utc < oldest:
            continue

        bucket = bucket_floor(dt_utc, bucket_minutes)
        if bucket not in bucket_set:
            continue

        flags = _classify_row(row)
        if flags["is_rest"]:
            per_bucket[bucket]["api_events"] += 1.0
        if flags["is_ws"]:
            per_bucket[bucket]["ws_events"] += 1.0
        if flags["is_ws_exec"]:
            per_bucket[bucket]["ws_exec_events"] += 1.0
        if flags["is_gap"]:
            per_bucket[bucket]["gap_events"] += 1.0
        if flags["is_resync"]:
            per_bucket[bucket]["resync_events"] += 1.0
        if flags["is_warn_or_error"] or flags["is_rate_mode"]:
            per_bucket[bucket]["warn_error_events"] += 1.0

    out_rows: list[dict[str, Any]] = []

    for row_spec in row_specs:
        venue = str(row_spec["venue"])
        activity_key = str(row_spec["activity_key"])
        use_gap = bool(row_spec.get("use_gap", False))
        use_resync = bool(row_spec.get("use_resync", False))
        use_warn = bool(row_spec.get("use_warn", False))
        current_truth = row_spec["current_truth"]

        cells: list[dict[str, Any]] = []

        for idx, bucket in enumerate(target_buckets):
            item = per_bucket[bucket]
            prev_item = per_bucket[target_buckets[idx - 1]] if idx > 0 else None

            activity_count = float(item.get(activity_key, 0.0))
            gap_count = item["gap_events"] if use_gap else 0.0
            resync_count = item["resync_events"] if use_resync else 0.0
            warn_count = item["warn_error_events"] if use_warn else 0.0

            gap_repeated = bool(
                gap_count > 0
                and prev_item
                and ((prev_item["gap_events"] if use_gap else 0.0) > 0)
            )
            warn_repeated = bool(
                warn_count > 0
                and prev_item
                and ((prev_item["warn_error_events"] if use_warn else 0.0) > 0)
            )

            level = "gray"
            reason = "health_continuity_reason_no_data"

            if warn_count > 0:
                level = "orange"
                reason = "health_continuity_reason_warn_error"
                if warn_repeated:
                    level = "red"
            elif gap_count > 0:
                level = "yellow"
                reason = "health_continuity_reason_gap_single"
                if gap_repeated:
                    level = "orange"
                    reason = "health_continuity_reason_gap_repeated"
            elif resync_count > 0:
                level = "green"
                reason = "health_continuity_reason_resync_recovered"
            elif activity_count > 0:
                level = "green"
                reason = "health_continuity_reason_steady"

            cells.append(
                {
                    "ts": bucket.isoformat().replace("+00:00", "Z"),
                    "start_ts": bucket.isoformat().replace("+00:00", "Z"),
                    "end_ts": bucket_end(bucket, bucket_minutes).isoformat().replace("+00:00", "Z"),
                    "range_key": range_key,
                    "bucket_minutes": bucket_minutes,
                    "in_progress": False,
                    "source_kind": "audit_continuity_rail",
                    "level": level,
                    "reason": reason,
                    "coverage_complete": coverage_meta["coverage_complete"],
                    "coverage_warning": coverage_meta["coverage_warning"],
                    "coverage_oldest_available_ts": coverage_meta["coverage_oldest_available_ts"],
                    "coverage_window_start_ts": coverage_meta["coverage_window_start_ts"],
                }
            )

        current_level, current_reason = current_truth()

        out_rows.append(
            {
                "venue": venue,
                "cells": cells,
                "current_level": current_level,
                "current_reason": current_reason,
            }
        )

    return out_rows


def build_api_continuity_rail(
    *,
    range_key: str = "1h",
    audit_rows: list[dict[str, Any]] | None = None,
    state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    resolved_state = dict(state or load_state())
    return _build_continuity_rail(
        range_key=range_key,
        audit_rows=audit_rows,
        row_specs=[
            {
                "venue": "bitflyer_api_market_data",
                "activity_key": "api_events",
                "use_gap": False,
                "use_resync": False,
                "use_warn": True,
                "current_truth": lambda: api_current_truth(resolved_state),
            }
        ],
    )


def build_ws_continuity_rail(
    *,
    range_key: str = "1h",
    audit_rows: list[dict[str, Any]] | None = None,
    state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    resolved_state = dict(state or load_state())
    status_payload = resolved_state.get("status") or {}
    origin_payload = resolved_state.get("origin") or {}
    executions_payload = resolved_state.get("executions") or {}

    ws_board_lane = status_payload.get("ws_board_lane") or {}
    ws_executions_lane = status_payload.get("ws_executions_lane") or {}

    return _build_continuity_rail(
        range_key=range_key,
        audit_rows=audit_rows,
        row_specs=[
            {
                "venue": "bitflyer_ws_board",
                "activity_key": "ws_events",
                "use_gap": True,
                "use_resync": True,
                "use_warn": True,
                "current_truth": lambda: ws_current_truth(
                    lane_payload=ws_board_lane,
                    fallback_payload=origin_payload,
                ),
            },
            {
                "venue": "bitflyer_ws_executions",
                "activity_key": "ws_exec_events",
                "use_gap": False,
                "use_resync": False,
                "use_warn": True,
                "current_truth": lambda: ws_current_truth(
                    lane_payload=ws_executions_lane,
                    fallback_payload=executions_payload,
                ),
            },
        ],
    )


def build_recent_anomaly_rows(
    *,
    max_items: int = 12,
    audit_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    rows = (
        list(audit_rows)
        if audit_rows is not None
        else _read_recent_audit_rows(max_lines=1200)
    )

    out: list[dict[str, Any]] = []
    for row in reversed(rows):
        flags = _classify_row(row)
        if not any(
            [
                flags["is_429"],
                flags["is_gap"],
                flags["is_resync"],
                flags["is_warn_or_error"],
                flags["is_rate_mode"],
            ]
        ):
            continue

        payload = row.get("payload") or {}
        out.append(
            {
                "ts": row.get("ts"),
                "event": row.get("event"),
                "topic": payload.get("topic"),
                "reason": payload.get("reason"),
                "exchange": payload.get("exchange"),
            }
        )
        if len(out) >= max_items:
            break

    return out


def _build_health_current_state_bundle(
    *,
    state: dict[str, Any],
    market_latest: dict[str, Any],
    market_diag: dict[str, Any],
) -> dict[str, Any]:
    layer3_interpretation_bucket = (
        market_latest.get("interpretation_bucket")
        or market_diag.get("preferred_row_interpretation_bucket")
    )
    layer3_semantic_usage_summary = build_layer3_semantic_usage_summary(
        interpretation_bucket=layer3_interpretation_bucket,
        market_latest=market_latest,
    )
    layer3_semantic_usage_rows = build_layer3_semantic_usage_rows(
        interpretation_bucket=layer3_interpretation_bucket,
        market_latest=market_latest,
    )
    layer3_runtime_contract_summary = build_layer3_runtime_contract_summary(
        market_latest=market_latest,
        market_diag=market_diag,
        semantic_usage_summary=layer3_semantic_usage_summary,
    )
    layer3_orderbook_runtime_summary = build_layer3_orderbook_runtime_summary(
        market_latest=market_latest,
        market_diag=market_diag,
    )
    hot_cold_retention_safety_payload = load_hot_cold_retention_safety_payload()

    health_digest = build_health_digest(
        HealthDigestBuildInput(
            collector_state=state,
            market_state_row=market_latest,
            market_diagnostics=market_diag,
            semantic_usage_summary=layer3_semantic_usage_summary,
            semantic_usage_rows=layer3_semantic_usage_rows,
            runtime_contract_summary=layer3_runtime_contract_summary,
            orderbook_runtime_summary=layer3_orderbook_runtime_summary,
            source_kind="health_data_service",
        )
    )

    rate_domains = state.get("rate_domains") or {}
    domain_names = list(state.get("domain_names") or [])
    shared_ip = state.get("shared_ip") or {}
    shared_ip_budget = state.get("shared_ip_budget") or {}
    shared_ip_remaining_60s = int(shared_ip_budget.get("remaining_60s") or 0)
    domain_counts = {
        name: {
            "requests_60s": int((rate_domains.get(name) or {}).get("requests_60s") or 0),
            "requests_300s": int((rate_domains.get(name) or {}).get("requests_300s") or 0),
            "success_60s": int((rate_domains.get(name) or {}).get("success_60s") or 0),
            "fail_60s": int((rate_domains.get(name) or {}).get("fail_60s") or 0),
            "status_429_300s": int((rate_domains.get(name) or {}).get("status_429_300s") or 0),
        }
        for name in domain_names
    }

    return {
        "collector_state": state,
        "rate_domains": rate_domains,
        "domain_names": domain_names,
        "domain_counts": domain_counts,
        "shared_ip": shared_ip,
        "shared_ip_budget": shared_ip_budget,
        "shared_ip_remaining_60s": shared_ip_remaining_60s,
        "market_latest": market_latest,
        "market_diag": market_diag,
        "layer3_semantic_usage_rows": layer3_semantic_usage_rows,
        "layer3_semantic_usage_summary": layer3_semantic_usage_summary,
        "layer3_runtime_contract_summary": layer3_runtime_contract_summary,
        "layer3_orderbook_runtime_summary": layer3_orderbook_runtime_summary,
        "health_digest": health_digest,
        "hot_cold_retention_safety_payload": hot_cold_retention_safety_payload,
        "hot_cold_retention_safety": hot_cold_retention_safety_payload,
        "operational_readiness_hot_cold_retention_safety": hot_cold_retention_safety_payload,
    }


def _build_health_timeline_bundle(
    *,
    range_key: str,
    audit_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "api_ws_series": build_recent_api_ws_series(
            range_key=range_key,
            include_in_progress=False,
            audit_rows=audit_rows,
        ),
        "rate_overlay": build_rate_limit_overlay(
            range_key=range_key,
            include_in_progress=False,
        ),
        "layer3_series": build_recent_layer3_series(
            range_key=range_key,
            include_in_progress=False,
        ),
    }


def _build_health_continuity_bundle(
    *,
    range_key: str,
    audit_rows: list[dict[str, Any]] | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    builders_are_patched = (
        getattr(build_api_continuity_rail, "__module__", __name__) != __name__
        or getattr(build_ws_continuity_rail, "__module__", __name__) != __name__
    )
    if (audit_rows is None and state is None) or builders_are_patched:
        kwargs: dict[str, Any] = {"range_key": range_key}
        if audit_rows is not None:
            kwargs["audit_rows"] = audit_rows
        if state is not None:
            kwargs["state"] = state
        return {
            "api_continuity_rail": build_api_continuity_rail(**kwargs),
            "ws_continuity_rail": build_ws_continuity_rail(**kwargs),
        }

    resolved_state = dict(state or load_state())
    status_payload = resolved_state.get("status") or {}
    origin_payload = resolved_state.get("origin") or {}
    executions_payload = resolved_state.get("executions") or {}
    ws_board_lane = status_payload.get("ws_board_lane") or {}
    ws_executions_lane = status_payload.get("ws_executions_lane") or {}

    combined_rails = _build_continuity_rail(
        range_key=range_key,
        audit_rows=audit_rows,
        row_specs=[
            {
                "venue": "bitflyer_api_market_data",
                "activity_key": "api_events",
                "use_gap": False,
                "use_resync": False,
                "use_warn": True,
                "current_truth": lambda: api_current_truth(resolved_state),
            },
            {
                "venue": "bitflyer_ws_board",
                "activity_key": "ws_events",
                "use_gap": True,
                "use_resync": True,
                "use_warn": True,
                "current_truth": lambda: ws_current_truth(
                    lane_payload=ws_board_lane,
                    fallback_payload=origin_payload,
                ),
            },
            {
                "venue": "bitflyer_ws_executions",
                "activity_key": "ws_exec_events",
                "use_gap": False,
                "use_resync": False,
                "use_warn": True,
                "current_truth": lambda: ws_current_truth(
                    lane_payload=ws_executions_lane,
                    fallback_payload=executions_payload,
                ),
            },
        ],
    )
    return {
        "api_continuity_rail": combined_rails[:1],
        "ws_continuity_rail": combined_rails[1:],
    }


def _build_health_anomaly_bundle(
    *,
    max_items: int = 12,
    audit_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    items = build_recent_anomaly_rows(
        max_items=max_items,
        audit_rows=audit_rows,
    )
    return {
        "source_kind": "audit_recent_anomaly_feed",
        "feed_kind": "health_recent_anomalies",
        "max_items": max_items,
        "items": items,
        "recent_anomalies": items,
    }


def _build_health_page_meta_bundle(*, range_key: str) -> dict[str, Any]:
    return {
        "selected_range_key": range_key,
        "range_presets": HEALTH_RANGE_PRESETS,
        "paths": {
            "logs_dir": str(core_paths.logs_dir(ensure=False)),
            "data_dir": str(core_paths.data_dir(ensure=False)),
            "config_dir": str(core_paths.config_dir(ensure=False)),
        },
    }


def load_health_current_state_bundle(
    *,
    state: dict[str, Any] | None = None,
    market_latest: dict[str, Any] | None = None,
    market_diag: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_state = dict(state or load_state())
    resolved_market_latest = dict(market_latest or load_latest_market_state())
    resolved_market_diag = dict(market_diag or market_state_diagnostics())
    return _build_health_current_state_bundle(
        state=resolved_state,
        market_latest=resolved_market_latest,
        market_diag=resolved_market_diag,
    )


def load_health_timeline_bundle(
    *,
    range_key: str = "1h",
    audit_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return _build_health_timeline_bundle(
        range_key=range_key,
        audit_rows=audit_rows,
    )


def load_health_continuity_bundle(
    *,
    range_key: str = "1h",
    audit_rows: list[dict[str, Any]] | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _build_health_continuity_bundle(
        range_key=range_key,
        audit_rows=audit_rows,
        state=state,
    )


def load_health_anomaly_bundle(
    *,
    max_items: int = 12,
    audit_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return _build_health_anomaly_bundle(
        max_items=max_items,
        audit_rows=audit_rows,
    )


def load_health_page_meta_bundle(*, range_key: str = "1h") -> dict[str, Any]:
    return _build_health_page_meta_bundle(range_key=range_key)


def load_health_snapshot(*, range_key: str = "1h") -> dict[str, Any]:
    audit_rows = _read_recent_audit_rows(
        max_lines=_audit_max_lines_for_range(range_key)
    )
    current_state_bundle = load_health_current_state_bundle()
    collector_state = dict(current_state_bundle.get("collector_state") or {})
    timeline_bundle = load_health_timeline_bundle(
        range_key=range_key,
        audit_rows=audit_rows,
    )
    continuity_bundle = load_health_continuity_bundle(
        range_key=range_key,
        audit_rows=audit_rows,
        state=collector_state,
    )
    anomaly_bundle = load_health_anomaly_bundle(
        max_items=12,
        audit_rows=audit_rows,
    )
    page_meta_bundle = load_health_page_meta_bundle(range_key=range_key)

    snapshot: dict[str, Any] = {}
    snapshot.update(current_state_bundle)
    snapshot.update(timeline_bundle)
    snapshot.update(continuity_bundle)
    snapshot.update(anomaly_bundle)
    snapshot.update(page_meta_bundle)

    snapshot["current_state_bundle"] = current_state_bundle
    snapshot["timeline_bundle"] = timeline_bundle
    snapshot["continuity_bundle"] = continuity_bundle
    snapshot["anomaly_bundle"] = anomaly_bundle
    snapshot["page_meta_bundle"] = page_meta_bundle
    return snapshot
