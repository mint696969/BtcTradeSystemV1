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
from btcts.core import io
from btcts.core import paths as core_paths


def _audit_log_path() -> Path:
    return core_paths.logs_dir(ensure=False) / "audit.jsonl"


def _read_recent_audit_rows(*, max_lines: int = 4000) -> list[dict[str, Any]]:
    path = _audit_log_path()
    return io.read_jsonl_tail(path, max_lines=max_lines)


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
) -> list[dict[str, Any]]:
    cfg = range_config(range_key)
    window_minutes = int(cfg["window_minutes"])
    bucket_minutes = int(cfg["bucket_minutes"])

    buckets = time_buckets(window_minutes, bucket_minutes)
    target_buckets = display_buckets(buckets, include_in_progress=include_in_progress)
    rows = _read_recent_audit_rows(max_lines=4000)

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


def _build_continuity_rail(
    *,
    range_key: str,
    row_specs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    state = load_state()
    rows = _read_recent_audit_rows(max_lines=4000)

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


def build_api_continuity_rail(*, range_key: str = "1h") -> list[dict[str, Any]]:
    return _build_continuity_rail(
        range_key=range_key,
        row_specs=[
            {
                "venue": "bitflyer_api_market_data",
                "activity_key": "api_events",
                "use_gap": False,
                "use_resync": False,
                "use_warn": True,
                "current_truth": lambda: api_current_truth(load_state()),
            }
        ],
    )


def build_ws_continuity_rail(*, range_key: str = "1h") -> list[dict[str, Any]]:
    state = load_state()
    status_payload = state.get("status") or {}
    origin_payload = state.get("origin") or {}
    executions_payload = state.get("executions") or {}

    ws_board_lane = status_payload.get("ws_board_lane") or {}
    ws_executions_lane = status_payload.get("ws_executions_lane") or {}

    return _build_continuity_rail(
        range_key=range_key,
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


def build_recent_anomaly_rows(*, max_items: int = 12) -> list[dict[str, Any]]:
    rows = _read_recent_audit_rows(max_lines=1200)

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


def load_health_snapshot(*, range_key: str = "1h") -> dict[str, Any]:
    state = load_state()
    market_latest = load_latest_market_state()
    market_diag = market_state_diagnostics()

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
        "selected_range_key": range_key,
        "range_presets": HEALTH_RANGE_PRESETS,
        "api_ws_series": build_recent_api_ws_series(range_key=range_key, include_in_progress=False),
        "rate_overlay": build_rate_limit_overlay(range_key=range_key, include_in_progress=False),
        "layer3_series": build_recent_layer3_series(range_key=range_key, include_in_progress=False),
        "api_continuity_rail": build_api_continuity_rail(range_key=range_key),
        "ws_continuity_rail": build_ws_continuity_rail(range_key=range_key),
        "recent_anomalies": build_recent_anomaly_rows(max_items=12),
        "paths": {
            "logs_dir": str(core_paths.logs_dir(ensure=False)),
            "data_dir": str(core_paths.data_dir(ensure=False)),
            "config_dir": str(core_paths.config_dir(ensure=False)),
        },
    }