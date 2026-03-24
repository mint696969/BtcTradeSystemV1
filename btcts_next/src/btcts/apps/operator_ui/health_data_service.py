# path: ./btcts_next/src/btcts/apps/operator_ui/health_data_service.py
# desc: Operator UI Health タブ向けに collector / audit / market_state を統合し、短期監視用の時系列を返す。

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from btcts.apps.operator_ui.collector_state_service import load_state
from btcts.apps.operator_ui.market_state_service import (
    load_latest_market_state,
    market_state_diagnostics,
)
from btcts.core import io
from btcts.core import paths as core_paths


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _audit_log_path() -> Path:
    return core_paths.logs_dir(ensure=False) / "audit.jsonl"


def _read_recent_audit_rows(*, max_lines: int = 4000) -> list[dict[str, Any]]:
    path = _audit_log_path()
    return io.read_jsonl_tail(path, max_lines=max_lines)


def _bucket_floor_minute(dt: datetime) -> datetime:
    return dt.replace(second=0, microsecond=0)


def _empty_minute_buckets(window_minutes: int) -> list[datetime]:
    now = _bucket_floor_minute(_now_utc())
    start = now - timedelta(minutes=window_minutes - 1)
    return [start + timedelta(minutes=i) for i in range(window_minutes)]


def _classify_row(row: dict[str, Any]) -> dict[str, bool]:
    event = str(row.get("event") or "").lower()
    payload = row.get("payload") or {}
    topic = str(payload.get("topic") or "").lower()
    provider = str(payload.get("provider") or "").lower()
    reason = str(payload.get("reason") or "").lower()
    error = str(payload.get("error") or "").lower()

    text = " ".join([event, topic, provider, reason, error])

    is_rest = ("rest" in text) or ("http" in text)
    is_ws = ("ws" in text) or ("websocket" in text)
    is_429 = "429" in text or "retry_after" in text
    is_gap = "gap" in text
    is_resync = "resync" in text
    is_warn_or_error = any(word in text for word in ["warn", "error", "failed", "exception"])
    is_rate_mode = any(word in text for word in ["crit", "recovery", "throttle", "utilization"])

    return {
        "is_rest": is_rest,
        "is_ws": is_ws,
        "is_429": is_429,
        "is_gap": is_gap,
        "is_resync": is_resync,
        "is_warn_or_error": is_warn_or_error,
        "is_rate_mode": is_rate_mode,
    }


def build_recent_api_ws_series(*, window_minutes: int = 60) -> list[dict[str, Any]]:
    buckets = _empty_minute_buckets(window_minutes)
    rows = _read_recent_audit_rows(max_lines=4000)

    per_minute: dict[datetime, dict[str, float]] = defaultdict(
        lambda: {
            "api_events": 0.0,
            "ws_events": 0.0,
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
        dt = _parse_ts(row.get("ts"))
        if dt is None:
            continue
        if dt < oldest:
            continue

        bucket = _bucket_floor_minute(dt.astimezone(timezone.utc))
        if bucket not in bucket_set:
            continue

        flags = _classify_row(row)
        payload = row.get("payload") or {}

        if flags["is_rest"]:
            per_minute[bucket]["api_events"] += 1.0
        if flags["is_ws"]:
            per_minute[bucket]["ws_events"] += 1.0
        if flags["is_429"]:
            per_minute[bucket]["events_429"] += 1.0
        if flags["is_gap"]:
            per_minute[bucket]["gap_events"] += 1.0
        if flags["is_resync"]:
            per_minute[bucket]["resync_events"] += 1.0
        if flags["is_warn_or_error"]:
            per_minute[bucket]["warn_error_events"] += 1.0

        elapsed_ms = payload.get("elapsed_ms")
        if elapsed_ms is not None:
            try:
                per_minute[bucket]["latency_ms_sum"] += float(elapsed_ms)
                per_minute[bucket]["latency_ms_count"] += 1.0
            except Exception:
                pass

    out: list[dict[str, Any]] = []
    api_event_history: list[float] = []

    for bucket in buckets:
        item = dict(per_minute[bucket])
        avg_latency = None
        if item["latency_ms_count"] > 0:
            avg_latency = item["latency_ms_sum"] / item["latency_ms_count"]

        api_events = float(item["api_events"])
        api_event_history.append(api_events)
        api_rolling_5m = sum(api_event_history[-5:])

        out.append(
            {
                "ts": bucket.isoformat().replace("+00:00", "Z"),
                "api_events": api_events,
                "api_rolling_5m": api_rolling_5m,
                "api_limit_5m": 500.0,
                "events_429": item["events_429"],
                "events_429_marker": 500.0 if item["events_429"] > 0 else None,
                "ws_events": item["ws_events"],
                "gap_events": item["gap_events"],
                "resync_events": item["resync_events"],
                "warn_error_events": item["warn_error_events"],
                "avg_latency_ms": avg_latency,
            }
        )

    return out


def build_rate_limit_overlay(*, window_minutes: int = 60) -> list[dict[str, Any]]:
    state = load_state()
    rate_items = (state.get("rate") or {}).get("items") or {}
    bitflyer = rate_items.get("bitflyer") or {}

    budget = bitflyer.get("budget") or {}
    budget_60s = budget.get("budget_60s")
    budget_300s = budget.get("budget_300s")

    requests_60s = bitflyer.get("requests_60s")
    requests_300s = bitflyer.get("requests_300s")
    utilization = bitflyer.get("utilization")
    active_target_ratio = bitflyer.get("active_target_ratio")
    target_utilization = bitflyer.get("target_utilization")
    hard_cap_utilization = bitflyer.get("hard_cap_utilization")

    buckets = _empty_minute_buckets(window_minutes)
    out: list[dict[str, Any]] = []

    for bucket in buckets:
        out.append(
            {
                "ts": bucket.isoformat().replace("+00:00", "Z"),
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


def build_recent_layer3_series(*, window_minutes: int = 60) -> list[dict[str, Any]]:
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

    buckets = _empty_minute_buckets(window_minutes)
    out: list[dict[str, Any]] = []

    for bucket in buckets:
        out.append(
            {
                "ts": bucket.isoformat().replace("+00:00", "Z"),
                "trust_score": trust_score,
                "continuity_score": continuity_score,
                "interpretation_score": interpretation_score,
                "freshness_score": freshness_score,
            }
        )

    return out


def _build_continuity_rail(
    *,
    window_minutes: int,
    venue: str,
    use_api: bool,
    use_ws: bool,
    use_gap: bool,
    use_resync: bool,
    use_warn: bool,
) -> list[dict[str, Any]]:
    state = load_state()
    rows = _read_recent_audit_rows(max_lines=4000)
    buckets = _empty_minute_buckets(window_minutes)

    health_payload = state.get("health") or {}

    per_minute: dict[datetime, dict[str, float]] = defaultdict(
        lambda: {
            "api_events": 0.0,
            "ws_events": 0.0,
            "gap_events": 0.0,
            "resync_events": 0.0,
            "warn_error_events": 0.0,
        }
    )

    bucket_set = set(buckets)
    oldest = buckets[0]

    for row in rows:
        dt = _parse_ts(row.get("ts"))
        if dt is None:
            continue
        if dt < oldest:
            continue

        bucket = _bucket_floor_minute(dt.astimezone(timezone.utc))
        if bucket not in bucket_set:
            continue

        flags = _classify_row(row)
        if flags["is_rest"]:
            per_minute[bucket]["api_events"] += 1.0
        if flags["is_ws"]:
            per_minute[bucket]["ws_events"] += 1.0
        if flags["is_gap"]:
            per_minute[bucket]["gap_events"] += 1.0
        if flags["is_resync"]:
            per_minute[bucket]["resync_events"] += 1.0
        if flags["is_warn_or_error"]:
            per_minute[bucket]["warn_error_events"] += 1.0

    cells: list[dict[str, Any]] = []

    def _evaluate_bucket(idx: int) -> tuple[str, str]:
        bucket = buckets[idx]
        item = per_minute[bucket]
        prev_item = per_minute[buckets[idx - 1]] if idx > 0 else None

        level = "gray"
        reason = "health_continuity_reason_no_data"

        gap_repeated = bool(
            item["gap_events"] > 0 and prev_item and prev_item["gap_events"] > 0
        )
        warn_repeated = bool(
            item["warn_error_events"] > 0 and prev_item and prev_item["warn_error_events"] > 0
        )

        warn_count = item["warn_error_events"] if use_warn else 0.0
        gap_count = item["gap_events"] if use_gap else 0.0
        resync_count = item["resync_events"] if use_resync else 0.0
        ws_count = item["ws_events"] if use_ws else 0.0
        api_count = item["api_events"] if use_api else 0.0

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
        elif ws_count > 0 or api_count > 0:
            level = "green"
            reason = "health_continuity_reason_steady"

        return level, reason

    display_bucket_count = len(buckets) - 1 if len(buckets) >= 2 else len(buckets)

    for idx, bucket in enumerate(buckets[:display_bucket_count]):
        level, reason = _evaluate_bucket(idx)
        cells.append(
            {
                "ts": bucket.isoformat().replace("+00:00", "Z"),
                "level": level,
                "reason": reason,
            }
        )

    latest_level = "gray"
    latest_reason = "health_continuity_reason_no_data"

    settled_idx = display_bucket_count - 1
    if settled_idx >= 0:
        latest_level, latest_reason = _evaluate_bucket(settled_idx)

    ok = health_payload.get("ok")
    if ok is False:
        latest_level = "red"
        latest_reason = "health_continuity_reason_health_not_ok"

    return [
        {
            "venue": venue,
            "cells": cells,
            "current_level": latest_level,
            "current_reason": latest_reason,
        }
    ]


def build_api_continuity_rail(*, window_minutes: int = 60) -> list[dict[str, Any]]:
    return _build_continuity_rail(
        window_minutes=window_minutes,
        venue="bitflyer_api",
        use_api=True,
        use_ws=False,
        use_gap=False,
        use_resync=False,
        use_warn=True,
    )


def build_ws_continuity_rail(*, window_minutes: int = 60) -> list[dict[str, Any]]:
    return _build_continuity_rail(
        window_minutes=window_minutes,
        venue="bitflyer_ws",
        use_api=False,
        use_ws=True,
        use_gap=True,
        use_resync=True,
        use_warn=True,
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


def load_health_snapshot() -> dict[str, Any]:
    state = load_state()
    market_latest = load_latest_market_state()
    market_diag = market_state_diagnostics()

    return {
        "collector_state": state,
        "market_latest": market_latest,
        "market_diag": market_diag,
        "api_ws_series_1h": build_recent_api_ws_series(window_minutes=60),
        "rate_overlay_1h": build_rate_limit_overlay(window_minutes=60),
        "layer3_series_1h": build_recent_layer3_series(window_minutes=60),
        "api_continuity_rail_1h": build_api_continuity_rail(window_minutes=60),
        "ws_continuity_rail_1h": build_ws_continuity_rail(window_minutes=60),
        "recent_anomalies": build_recent_anomaly_rows(max_items=12),
        "paths": {
            "logs_dir": str(core_paths.logs_dir(ensure=False)),
            "data_dir": str(core_paths.data_dir(ensure=False)),
            "config_dir": str(core_paths.config_dir(ensure=False)),
        },
    }