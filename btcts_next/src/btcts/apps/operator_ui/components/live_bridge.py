# path: ./btcts_next/src/btcts/apps/operator_ui/components/live_bridge.py
# desc: Collector UI 用の live state / audit 読み込みブリッジ。state.json / health.json / checkpoint.json / audit.jsonl を統一的に扱う。

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from btcts.core import paths as core_paths


def logs_path() -> Path:
    return core_paths.logs_dir(ensure=False) / "audit.jsonl"


def state_root() -> Path:
    return core_paths.logs_dir(ensure=False).parent / "state" / "collector_vnext"


def _read_json(path: Path) -> Optional[dict]:
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_status() -> Optional[dict]:
    return _read_json(state_root() / "status.json")


def load_health() -> Optional[dict]:
    return _read_json(state_root() / "health.json")


def load_daemon_health() -> Optional[dict]:
    return _read_json(state_root() / "daemon_health.json")


def load_checkpoint() -> Optional[dict]:
    return _read_json(state_root() / "checkpoint.json")


def read_recent_audit_events(lines: int = 80) -> list[dict]:
    log_path = logs_path()
    if not log_path.exists():
        return []

    with open(log_path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()

        block = 4096
        data = b""

        while size > 0 and data.count(b"\n") < lines:
            step = min(block, size)
            size -= step
            f.seek(size)
            data = f.read(step) + data

    rows: list[dict] = []

    for line in data.splitlines()[-lines:]:
        try:
            obj = json.loads(line)
            payload = obj.get("payload", {}) or {}

            rows.append(
                {
                    "ts": obj.get("ts"),
                    "event": obj.get("event"),
                    "exchange": payload.get("exchange"),
                    "topic": payload.get("topic"),
                    "latency_ms": payload.get("elapsed_ms"),
                    "bytes": payload.get("bytes"),
                    "stream_session_id": payload.get("stream_session_id"),
                    "source": "audit",
                    "ok": payload.get("ok"),
                    "session_id": payload.get("session_id"),
                }
            )
        except Exception:
            continue

    return rows


def average_latency(events: list[dict]) -> float | None:
    values = [
        float(row["latency_ms"])
        for row in events
        if row.get("latency_ms") is not None
    ]
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def latest_event(events: list[dict]) -> Optional[dict]:
    if not events:
        return None
    return events[-1]


def _parse_iso_utc(value: str | None) -> Optional[datetime]:
    if not value:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _event_age_seconds(event: dict | None) -> Optional[float]:
    if not event:
        return None

    ts = _parse_iso_utc(event.get("ts"))
    if ts is None:
        return None

    now = datetime.now(timezone.utc)
    age = (now - ts).total_seconds()
    return max(age, 0.0)


def _payload_age_seconds(payload: dict | None) -> Optional[float]:
    if not payload:
        return None

    ts = _parse_iso_utc(payload.get("ts"))
    if ts is None:
        return None

    now = datetime.now(timezone.utc)
    age = (now - ts).total_seconds()
    return max(age, 0.0)


def _format_age(age: Optional[float]) -> str:
    if age is None:
        return "-"

    sec = int(age)
    if sec < 60:
        return f"{sec}s"

    minute = sec // 60
    remain = sec % 60
    if minute < 60:
        return f"{minute}m {remain}s"

    hour = minute // 60
    minute = minute % 60
    return f"{hour}h {minute}m"


def _feed_state(events: list[dict], *, live_threshold_sec: int = 30, stale_threshold_sec: int = 120) -> str:
    latest = latest_event(events)
    age = _event_age_seconds(latest)

    if latest is None or age is None:
        return "UNKNOWN"

    event_name = str(latest.get("event") or "").lower()
    ok_value = latest.get("ok")

    if ok_value is False or "failed" in event_name or "error" in event_name:
        if age <= stale_threshold_sec:
            return "DEGRADED"
        return "STALE"

    if age <= live_threshold_sec:
        return "LIVE"

    if age <= stale_threshold_sec:
        return "QUIET"

    return "STALE"


def feed_state_from_events(events: list[dict]) -> str:
    return _feed_state(events)


def _build_live_summary(
    *,
    status: dict,
    health: dict,
    daemon_health: dict,
    checkpoint: dict,
    audit_rows: list[dict],
) -> dict:
    status_mode = str(status.get("mode") or "UNKNOWN").upper()
    health_status = str(health.get("status") or "unknown").lower()
    daemon_status = str(daemon_health.get("status") or "unknown").lower()

    consecutive_failures = int(status.get("consecutive_failures") or daemon_health.get("consecutive_failures") or 0)
    ws_warn_streak = int(status.get("ws_trades_warn_streak") or daemon_health.get("ws_trades_warn_streak") or 0)

    health_checks = health.get("checks") or []
    warn_count = sum(1 for check in health_checks if check.get("result") != "ok")

    feed_state = _feed_state(audit_rows)

    status_age = _payload_age_seconds(status)
    health_age = _payload_age_seconds(health)
    daemon_age = _payload_age_seconds(daemon_health)
    checkpoint_age = _payload_age_seconds(checkpoint)

    overall = "UNKNOWN"
    reason = "live state unavailable"

    if status_mode == "STOPPED" or daemon_status == "stopped":
        overall = "STOPPED"
        reason = "collector stopped"

    elif consecutive_failures > 0:
        overall = "DEGRADED"
        reason = f"consecutive_failures={consecutive_failures}"

    elif ws_warn_streak >= 2:
        overall = "DEGRADED"
        reason = f"ws_trades_warn_streak={ws_warn_streak}"

    elif status_mode in {"DEGRADED", "RECOVERING"}:
        overall = "DEGRADED"
        reason = f"status.mode={status_mode}"

    elif daemon_status in {"degraded", "recovering"}:
        overall = "DEGRADED"
        reason = f"daemon.status={daemon_status}"

    elif health_status != "healthy":
        overall = "DEGRADED"
        reason = f"health.status={health_status}"

    elif warn_count > 0:
        overall = "DEGRADED"
        reason = f"health warn_count={warn_count}"

    elif feed_state in {"DEGRADED", "STALE"}:
        overall = "DEGRADED"
        reason = f"feed={feed_state}"

    elif status_mode == "RUNNING" and health_status == "healthy" and daemon_status == "healthy":
        overall = "RUNNING"
        reason = "all live checks aligned"

    return {
        "overall_state": overall,
        "overall_reason": reason,
        "status_mode": status_mode,
        "health_status": health_status,
        "daemon_status": daemon_status,
        "feed_state": feed_state,
        "consecutive_failures": consecutive_failures,
        "ws_trades_warn_streak": ws_warn_streak,
        "health_warn_count": warn_count,
        "status_age_sec": status_age,
        "health_age_sec": health_age,
        "daemon_age_sec": daemon_age,
        "checkpoint_age_sec": checkpoint_age,
        "status_age_label": _format_age(status_age),
        "health_age_label": _format_age(health_age),
        "daemon_age_label": _format_age(daemon_age),
        "checkpoint_age_label": _format_age(checkpoint_age),
    }


def collector_runtime_snapshot() -> dict:
    status = load_status() or {}
    health = load_health() or {}
    daemon_health = load_daemon_health() or {}
    checkpoint = load_checkpoint() or {}
    audit_rows = read_recent_audit_events(lines=80)

    mode = str(status.get("mode") or "UNKNOWN").upper()
    health_status = str(health.get("status") or "unknown").lower()

    checks = health.get("checks") or []
    warn_count = sum(1 for check in checks if check.get("result") != "ok")

    daemon_status = str(daemon_health.get("status") or "").lower()

    exchange_state = "UNKNOWN"
    if mode == "STOPPED":
        exchange_state = "STOPPED"
    elif warn_count > 0:
        exchange_state = "DEGRADED"
    elif checks:
        exchange_state = "CONNECTED"
    elif mode in {"DEGRADED", "RECOVERING"} or daemon_status in {"degraded", "recovering"}:
        exchange_state = "DEGRADED"
    elif mode == "RUNNING" and health_status == "healthy":
        exchange_state = "CONNECTED"

    feed_state = _feed_state(audit_rows)

    active_topics = len(
        {
            row.get("topic")
            for row in audit_rows
            if row.get("topic")
        }
    )

    stream_sessions = len(
        {
            row.get("stream_session_id")
            for row in audit_rows
            if row.get("stream_session_id")
        }
    )

    live_summary = _build_live_summary(
        status=status,
        health=health,
        daemon_health=daemon_health,
        checkpoint=checkpoint,
        audit_rows=audit_rows,
    )

    return {
        "mode": mode,
        "health_status": health_status,
        "exchange_state": exchange_state,
        "feed_state": feed_state,
        "last_sequence_id": checkpoint.get("last_sequence_id"),
        "avg_latency_ms": average_latency(audit_rows),
        "audit_rows": audit_rows,
        "active_topics": active_topics,
        "stream_sessions": stream_sessions,
        "status": status,
        "health": health,
        "daemon_health": daemon_health,
        "checkpoint": checkpoint,
        "live_summary": live_summary,
    }