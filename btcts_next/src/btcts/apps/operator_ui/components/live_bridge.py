# path: ./btcts_next/src/btcts/apps/operator_ui/components/live_bridge.py
# desc: Collector UI / War Room 用の live state / audit / canonical 読み込みブリッジ。

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from btcts.core import paths as core_paths
from btcts.core.sharded_jsonl import latest_part_path


def logs_path() -> Path:
    logs_root = core_paths.logs_dir(ensure=False)
    collector_vnext_path = logs_root / "collector_vnext" / "audit.jsonl"
    if collector_vnext_path.exists():
        return collector_vnext_path
    return logs_root / "audit.jsonl"


def data_root() -> Path:
    return core_paths.data_dir(ensure=False)


def state_root() -> Path:
    return core_paths.logs_dir(ensure=False).parent / "state" / "collector_vnext"


def _read_json(path: Path) -> Optional[dict]:
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_json_first(paths: list[Path]) -> Optional[dict]:
    for path in paths:
        data = _read_json(path)
        if data:
            return data
    return None


def _read_recent_jsonl_objects(path: Path, *, lines: int = 80) -> list[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return []

    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()

            block = 4096
            data = b""

            while size > 0 and data.count(b"\n") < lines:
                step = min(block, size)
                size -= step
                f.seek(size)
                data = f.read(step) + data
    except Exception:
        return []

    rows: list[dict[str, Any]] = []
    for line in data.splitlines()[-lines:]:
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                rows.append(obj)
        except Exception:
            continue
    return rows


def _utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _latest_available_date_dir(base_dir: Path) -> Optional[str]:
    if not base_dir.exists() or not base_dir.is_dir():
        return None

    candidates: list[str] = []
    try:
        for child in base_dir.iterdir():
            if child.is_dir() and child.name.startswith("date="):
                candidates.append(child.name.removeprefix("date="))
    except Exception:
        return None

    if not candidates:
        return None

    candidates.sort()
    return candidates[-1]


def _market_type_path(
    *,
    exchange: str,
    symbol: str,
    record_type: str,
    date: str | None = None,
) -> Path:
    type_root = (
        data_root()
        / "market_data"
        / f"exchange={exchange}"
        / f"symbol={symbol}"
        / f"type={record_type}"
    )

    target_date = date
    if not target_date:
        latest_date = _latest_available_date_dir(type_root)
        target_date = latest_date or _utc_today()

    date_dir = type_root / f"date={target_date}"
    return latest_part_path(date_dir) or date_dir / "part-00001.jsonl"


def load_status() -> Optional[dict]:
    return _read_json_first(
        [
            state_root() / "unified_status.json",
            state_root() / "exploration_status.json",
            state_root() / "status.json",
        ]
    )


def load_health() -> Optional[dict]:
    return _read_json_first(
        [
            state_root() / "unified_daemon_health.json",
            state_root() / "unified_health.json",
            state_root() / "exploration_daemon_health.json",
            state_root() / "exploration_health.json",
            state_root() / "daemon_health.json",
            state_root() / "health.json",
        ]
    )


def load_daemon_health() -> Optional[dict]:
    return _read_json_first(
        [
            state_root() / "unified_daemon_health.json",
            state_root() / "unified_health.json",
            state_root() / "exploration_daemon_health.json",
            state_root() / "exploration_health.json",
            state_root() / "daemon_health.json",
            state_root() / "health.json",
        ]
    )


def load_checkpoint() -> Optional[dict]:
    return _read_json_first(
        [
            state_root() / "unified_checkpoint.json",
            state_root() / "exploration_checkpoint.json",
            state_root() / "checkpoint.json",
        ]
    )


def load_origin_status() -> Optional[dict]:
    return _read_json_first(
        [
            state_root() / "unified_origin_status.json",
            state_root() / "origin_status.json",
        ]
    )


def read_recent_audit_events(lines: int = 80) -> list[dict]:
    log_path = logs_path()
    if not log_path.exists():
        return []

    rows: list[dict] = []
    for obj in _read_recent_jsonl_objects(log_path, lines=lines):
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
                "payload": payload,
                "level": obj.get("level"),
                "feature": obj.get("feature"),
                "reason": payload.get("reason"),
            }
        )

    return rows


def read_recent_live_trade_rows(
    *,
    exchange: str = "bitflyer",
    symbol: str = "BTC_JPY",
    date: str | None = None,
    lines: int = 80,
) -> list[dict[str, Any]]:
    path = _market_type_path(
        exchange=exchange,
        symbol=symbol,
        record_type="market.trade",
        date=date,
    )
    return _read_recent_jsonl_objects(path, lines=lines)


def recent_live_tradeflow_metrics(
    *,
    exchange: str = "bitflyer",
    symbol: str = "BTC_JPY",
    date: str | None = None,
    lines: int = 80,
) -> dict[str, Any]:
    rows = read_recent_live_trade_rows(
        exchange=exchange,
        symbol=symbol,
        date=date,
        lines=lines,
    )
    if not rows:
        return {}

    buy_size = 0.0
    sell_size = 0.0
    buy_count = 0
    sell_count = 0
    prices: list[float] = []
    latest_ts: str | None = None

    for row in rows:
        payload = row.get("payload", {}) or {}
        side = str(payload.get("side") or "").upper()
        size = payload.get("size")
        price = payload.get("price")
        event_ts = row.get("event_ts") or row.get("collector_ts")

        try:
            size_f = float(size)
        except Exception:
            size_f = 0.0

        try:
            price_f = float(price)
            prices.append(price_f)
        except Exception:
            price_f = None

        if side == "BUY":
            buy_size += size_f
            buy_count += 1
        elif side == "SELL":
            sell_size += size_f
            sell_count += 1

        if event_ts:
            latest_ts = str(event_ts)

    total_count = buy_count + sell_count
    total_size = buy_size + sell_size
    delta = buy_size - sell_size
    last_price = prices[-1] if prices else None

    return {
        "source": "live_canonical",
        "event_ts": latest_ts,
        "buy_size": round(buy_size, 8),
        "sell_size": round(sell_size, 8),
        "delta": round(delta, 8),
        "trade_count": total_count,
        "buy_count": buy_count,
        "sell_count": sell_count,
        "total_size": round(total_size, 8),
        "last_price": last_price,
    }


def read_recent_live_stream_events(
    *,
    exchange: str = "bitflyer",
    symbol: str = "BTC_JPY",
    date: str | None = None,
    lines: int = 40,
) -> list[dict[str, Any]]:
    record_types = [
        "stream.started",
        "stream.gap_detected",
        "stream.resync_started",
        "stream.resync_completed",
    ]

    rows: list[dict[str, Any]] = []
    for record_type in record_types:
        path = _market_type_path(
            exchange=exchange,
            symbol=symbol,
            record_type=record_type,
            date=date,
        )
        rows.extend(_read_recent_jsonl_objects(path, lines=lines))

    rows.sort(
        key=lambda row: str(
            row.get("event_ts")
            or row.get("collector_ts")
            or row.get("ingest_ts")
            or ""
        )
    )
    return rows[-lines:]


def read_recent_live_board_rows(
    *,
    exchange: str = "bitflyer",
    symbol: str = "BTC_JPY",
    date: str | None = None,
    lines: int = 20,
) -> list[dict[str, Any]]:
    path = _market_type_path(
        exchange=exchange,
        symbol=symbol,
        record_type="market.orderbook.snapshot",
        date=date,
    )
    return _read_recent_jsonl_objects(path, lines=lines)


def latest_live_board_metrics(
    *,
    exchange: str = "bitflyer",
    symbol: str = "BTC_JPY",
    date: str | None = None,
) -> dict[str, Any]:
    rows = read_recent_live_board_rows(
        exchange=exchange,
        symbol=symbol,
        date=date,
        lines=8,
    )
    if not rows:
        return {}

    row = rows[-1]
    payload = row.get("payload", {}) or {}

    bids = payload.get("bids") or []
    asks = payload.get("asks") or []

    best_bid = None
    best_ask = None

    if bids:
        try:
            best_bid = float((bids[0] or {}).get("price"))
        except Exception:
            best_bid = None

    if asks:
        try:
            best_ask = float((asks[0] or {}).get("price"))
        except Exception:
            best_ask = None

    spread = None
    if best_bid is not None and best_ask is not None:
        spread = best_ask - best_bid

    bid_depth = 0.0
    ask_depth = 0.0

    for level in bids[:10]:
        try:
            bid_depth += float((level or {}).get("size") or 0.0)
        except Exception:
            continue

    for level in asks[:10]:
        try:
            ask_depth += float((level or {}).get("size") or 0.0)
        except Exception:
            continue

    return {
        "source": "live_canonical",
        "event_ts": row.get("event_ts") or row.get("collector_ts"),
        "record_type": row.get("record_type"),
        "stream_session_id": row.get("stream_session_id"),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": spread,
        "bid_levels": len(bids),
        "ask_levels": len(asks),
        "bid_depth": round(bid_depth, 8),
        "ask_depth": round(ask_depth, 8),
        "continuity_state": payload.get("continuity_state"),
        "is_resync": payload.get("is_resync"),
    }


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


def _timestamp_age_seconds(value: object) -> Optional[float]:
    ts = _parse_iso_utc(str(value) if value is not None else None)
    if ts is None:
        return None
    now = datetime.now(timezone.utc)
    age = (now - ts).total_seconds()
    return max(age, 0.0)


def _origin_continuity_feed_state(
    status: dict | None,
    *,
    live_threshold_sec: int = 30,
    stale_threshold_sec: int = 120,
) -> Optional[str]:
    if not isinstance(status, dict):
        return None

    origin = status.get("origin_continuity")
    if not isinstance(origin, dict) or not origin:
        return None

    ws_state = str(origin.get("ws_state") or "").upper()
    status_age = _payload_age_seconds(status)

    if ws_state != "LIVE":
        return "STALE"

    if status_age is None:
        return "UNKNOWN"

    if status_age <= live_threshold_sec:
        return "LIVE"

    if status_age <= stale_threshold_sec:
        return "QUIET"

    return "STALE"


def _origin_status_feed_state(
    origin_status: dict | None,
    *,
    live_threshold_sec: int = 30,
    stale_threshold_sec: int = 120,
) -> Optional[str]:
    if not isinstance(origin_status, dict) or not origin_status:
        return None

    ws_state = str(origin_status.get("ws_state") or "").upper()
    event_age = _timestamp_age_seconds(origin_status.get("last_event_ts") or origin_status.get("ts"))

    if ws_state != "LIVE":
        return "STALE"

    if event_age is None:
        return "UNKNOWN"

    if event_age <= live_threshold_sec:
        return "LIVE"

    if event_age <= stale_threshold_sec:
        return "QUIET"

    return "STALE"


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


def _resolve_feed_state(status: dict, origin_status: dict, audit_rows: list[dict]) -> str:
    origin_feed = _origin_status_feed_state(origin_status)
    if origin_feed is not None:
        return origin_feed

    continuity_feed = _origin_continuity_feed_state(status)
    if continuity_feed is not None:
        return continuity_feed

    return _feed_state(audit_rows)


def feed_state_from_events(events: list[dict]) -> str:
    return _feed_state(events)


def _build_live_summary(
    *,
    status: dict,
    health: dict,
    daemon_health: dict,
    checkpoint: dict,
    origin_status: dict,
    audit_rows: list[dict],
) -> dict:
    status_mode = str(status.get("mode") or "UNKNOWN").upper()
    health_status = str(health.get("status") or "unknown").lower()
    daemon_status = str(daemon_health.get("status") or "unknown").lower()

    consecutive_failures = int(status.get("consecutive_failures") or daemon_health.get("consecutive_failures") or 0)
    ws_warn_streak = int(status.get("ws_trades_warn_streak") or daemon_health.get("ws_trades_warn_streak") or 0)

    health_checks = health.get("checks") or []
    warn_count = sum(1 for check in health_checks if check.get("result") != "ok")

    feed_state = _resolve_feed_state(status, origin_status, audit_rows)

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
    origin_status = load_origin_status() or {}
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

    feed_state = _resolve_feed_state(status, origin_status, audit_rows)

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
        origin_status=origin_status,
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
        "origin_status": origin_status,
        "live_summary": live_summary,
    }
